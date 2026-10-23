"""
Internal SNES Emulator Player.
Direct bridge to our compiled C core (libretrosnes.so).
Runs games natively inside Pygame with 60 FPS rendering, audio, saves, and controls.
"""

import os
import sys
import ctypes
import time
from pathlib import Path
import pygame

# SNES Hardware Button Mapping in C core
CORE_BUTTON_MAP = {
    "B": 0,
    "Y": 1,
    "SELECT": 2,
    "START": 3,
    "UP": 4,
    "DOWN": 5,
    "LEFT": 6,
    "RIGHT": 7,
    "A": 8,
    "X": 9,
    "L": 10,
    "R": 11
}

class SnesPlayer:
    def __init__(self, lib_path: Path):
        self.lib_path = Path(lib_path).resolve()
        if not self.lib_path.exists():
            raise FileNotFoundError(f"Core library not found at: {self.lib_path}")

        self.lib = ctypes.CDLL(str(self.lib_path))
        self._setup_prototypes()
        
        self.snes_ptr = None
        self.is_loaded = False
        self.rom_path = None
        self.save_path = None
        self.state_path = None
        self.fps = 60
        self.samples_per_frame = 735 # 44100 / 60
        
        # Pixel buffer: 512x480 RGBA (983,040 bytes)
        self.pixel_buf_size = 512 * 480 * 4
        self.pixel_buf = (ctypes.c_uint8 * self.pixel_buf_size)()
        
        # Audio buffer: 735 stereo samples (1470 int16)
        self.audio_buf_size = self.samples_per_frame * 2
        self.audio_buf = (ctypes.c_int16 * self.audio_buf_size)()

        # Pygame surface for the frame
        self.frame_surface = pygame.Surface((512, 480))
        self.audio_channel = None

    def _setup_prototypes(self):
        self.lib.snes_init.restype = ctypes.c_void_p
        self.lib.snes_init.argtypes = []

        self.lib.snes_free.restype = None
        self.lib.snes_free.argtypes = [ctypes.c_void_p]

        self.lib.snes_reset.restype = None
        self.lib.snes_reset.argtypes = [ctypes.c_void_p, ctypes.c_bool]

        self.lib.snes_loadRom.restype = ctypes.c_bool
        self.lib.snes_loadRom.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]

        self.lib.snes_runFrame.restype = None
        self.lib.snes_runFrame.argtypes = [ctypes.c_void_p]

        self.lib.snes_setPixels.restype = None
        self.lib.snes_setPixels.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

        self.lib.snes_setPixelFormat.restype = None
        self.lib.snes_setPixelFormat.argtypes = [ctypes.c_void_p, ctypes.c_int]

        self.lib.snes_setSamples.restype = None
        self.lib.snes_setSamples.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]

        self.lib.snes_setButtonState.restype = None
        self.lib.snes_setButtonState.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_bool]

        self.lib.snes_saveBattery.restype = ctypes.c_int
        self.lib.snes_saveBattery.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

        self.lib.snes_loadBattery.restype = ctypes.c_bool
        self.lib.snes_loadBattery.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]

        self.lib.snes_saveState.restype = ctypes.c_int
        self.lib.snes_saveState.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

        self.lib.snes_loadState.restype = ctypes.c_bool
        self.lib.snes_loadState.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]

    def load_rom(self, rom_path: Path, saves_dir: Path, states_dir: Path) -> bool:
        self.unload()
        self.rom_path = Path(rom_path)
        self.save_path = Path(saves_dir) / f"{self.rom_path.stem}.srm"
        self.state_path = Path(states_dir) / f"{self.rom_path.stem}.state"

        try:
            with open(self.rom_path, "rb") as f:
                rom_bytes = f.read()
        except Exception as e:
            print(f"[SnesPlayer] Error reading ROM file: {e}")
            return False

        self.snes_ptr = self.lib.snes_init()
        if not self.snes_ptr:
            print("[SnesPlayer] Failed to initialize SNES core structure.")
            return False

        success = self.lib.snes_loadRom(self.snes_ptr, rom_bytes, len(rom_bytes))
        if not success:
            print(f"[SnesPlayer] Failed to load ROM into core: {self.rom_path.name}")
            self.unload()
            return False

        # Set pixel format: 1 = RGBX (compatible with Pygame RGBX surface buffers)
        self.lib.snes_setPixelFormat(self.snes_ptr, 1)

        # Load existing battery SRAM save if present
        if self.save_path.exists():
            try:
                with open(self.save_path, "rb") as sf:
                    save_data = sf.read()
                if save_data:
                    c_buf = (ctypes.c_uint8 * len(save_data)).from_buffer_copy(save_data)
                    self.lib.snes_loadBattery(self.snes_ptr, ctypes.byref(c_buf), len(save_data))
                    print(f"[SnesPlayer] Loaded battery save: {self.save_path.name}")
            except Exception as e:
                print(f"[SnesPlayer] Error loading battery save: {e}")

        self.is_loaded = True
        return True

    def unload(self):
        if self.is_loaded and self.snes_ptr:
            self.save_battery()
            self.lib.snes_free(self.snes_ptr)
            self.snes_ptr = None
            self.is_loaded = False

    def reset(self, hard=False):
        if self.is_loaded and self.snes_ptr:
            self.lib.snes_reset(self.snes_ptr, hard)

    def set_button(self, player: int, button_name: str, pressed: bool):
        if not self.is_loaded or not self.snes_ptr:
            return
        btn_id = CORE_BUTTON_MAP.get(button_name)
        if btn_id is not None:
            self.lib.snes_setButtonState(self.snes_ptr, player, btn_id, pressed)

    def step_frame(self, enable_audio=True):
        if not self.is_loaded or not self.snes_ptr:
            return

        # 1. Run 1 video frame in SNES hardware
        self.lib.snes_runFrame(self.snes_ptr)

        # 2. Extract framebuffer
        self.lib.snes_setPixels(self.snes_ptr, ctypes.byref(self.pixel_buf))

        # 3. Extract audio if requested
        if enable_audio:
            self.lib.snes_setSamples(self.snes_ptr, ctypes.byref(self.audio_buf), self.samples_per_frame)

    def get_surface(self) -> pygame.Surface:
        """Returns the current rendered frame as a Pygame Surface."""
        raw_bytes = bytes(self.pixel_buf)
        return pygame.image.frombuffer(raw_bytes, (512, 480), "RGBX")

    def get_audio_bytes(self) -> bytes:
        """Returns the raw 16-bit stereo PCM audio samples."""
        return bytes(self.audio_buf)

    def save_battery(self) -> bool:
        if not self.is_loaded or not self.snes_ptr or not self.save_path:
            return False
        
        try:
            # Query size first
            buf = (ctypes.c_uint8 * 0x40000)() # up to 256KB SRAM
            size = self.lib.snes_saveBattery(self.snes_ptr, ctypes.byref(buf))
            if size > 0:
                self.save_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.save_path, "wb") as f:
                    f.write(bytes(buf[:size]))
                return True
        except Exception as e:
            print(f"[SnesPlayer] Error saving battery SRAM: {e}")
        return False

    def save_state(self) -> bool:
        if not self.is_loaded or not self.snes_ptr or not self.state_path:
            return False

        try:
            buf = (ctypes.c_uint8 * 0x200000)() # 2MB buffer for savestate
            size = self.lib.snes_saveState(self.snes_ptr, ctypes.byref(buf))
            if size > 0:
                self.state_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.state_path, "wb") as f:
                    f.write(bytes(buf[:size]))
                print(f"[SnesPlayer] Saved state ({size} bytes) to {self.state_path.name}")
                return True
        except Exception as e:
            print(f"[SnesPlayer] Error saving state: {e}")
        return False

    def load_state(self) -> bool:
        if not self.is_loaded or not self.snes_ptr or not self.state_path or not self.state_path.exists():
            return False

        try:
            with open(self.state_path, "rb") as f:
                data = f.read()
            c_buf = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
            success = self.lib.snes_loadState(self.snes_ptr, ctypes.byref(c_buf), len(data))
            if success:
                print(f"[SnesPlayer] State loaded from {self.state_path.name}")
            return success
        except Exception as e:
            print(f"[SnesPlayer] Error loading state: {e}")
            return False
