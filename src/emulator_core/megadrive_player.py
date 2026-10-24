"""
Mega Drive / Genesis Native Emulator Player.
Bridge to libmegadrive_bridge.so (Genesis-Plus-GX core).
Provides 60 FPS video, audio, joypad, SRAM, and savestates.
"""

import os
import sys
import ctypes
from pathlib import Path
import pygame

# Mega Drive button mappings in bridge
MD_BUTTON_MAP = {
    # D-pad
    "UP": 4,
    "DOWN": 5,
    "LEFT": 6,
    "RIGHT": 7,
    # 3-button / 6-button
    "A": 1,     # Libretro Y
    "B": 0,     # Libretro B
    "C": 8,     # Libretro A
    "START": 3, # Libretro START
    "MODE": 2,  # Libretro SELECT
    "SELECT": 2,
    "X": 9,     # Libretro X
    "Y": 10,    # Libretro L
    "Z": 11,    # Libretro R
    "L": 10,
    "R": 11
}

class MegaDrivePlayer:
    def __init__(self, lib_path: Path):
        self.lib_path = Path(lib_path).resolve()
        self.is_available = self.lib_path.exists()

        if sys.platform == "win32":
            parent_dir = str(self.lib_path.parent)
            if hasattr(os, "add_dll_directory"):
                try:
                    os.add_dll_directory(parent_dir)
                except Exception:
                    pass
            os.environ["PATH"] = parent_dir + os.pathsep + os.environ.get("PATH", "")

            # Preload the core dependency (genesis_plus_gx_libretro.dll) into memory
            core_dll = self.lib_path.parent / "genesis_plus_gx_libretro.dll"
            if core_dll.exists():
                try:
                    ctypes.CDLL(str(core_dll))
                except Exception as e:
                    print(f"[MegaDrivePlayer] Preload {core_dll.name}: {e}")

        if self.is_available:
            try:
                self.lib = ctypes.CDLL(str(self.lib_path))
                self._setup_prototypes()
                self.is_initialized = self.lib.md_init()
            except Exception as e:
                print(f"[MegaDrivePlayer] Error al cargar la libreria nativa {self.lib_path}: {e}")
                self.lib = None
                self.is_available = False
                self.is_initialized = False
        else:
            self.lib = None
            self.is_initialized = False
        
        self.is_loaded = False
        self.rom_path = None
        self.save_path = None
        self.state_path = None
        self.width = 320
        self.height = 224

        # Audio buffer for extraction
        self.audio_max_samples = 4096 * 2
        self.audio_buf = (ctypes.c_int16 * self.audio_max_samples)()
        self.audio_bytes = b""

    def _setup_prototypes(self):
        self.lib.md_init.restype = ctypes.c_bool
        self.lib.md_deinit.restype = None
        
        self.lib.md_load_rom.restype = ctypes.c_bool
        self.lib.md_load_rom.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_size_t]

        self.lib.md_run_frame.restype = None
        self.lib.md_reset.restype = None

        self.lib.md_get_frame_info.restype = None
        self.lib.md_get_frame_info.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

        self.lib.md_get_pixels.restype = ctypes.POINTER(ctypes.c_uint8)

        if hasattr(self.lib, "md_get_samples"):
            self.lib.md_get_samples.restype = ctypes.c_int
            self.lib.md_get_samples.argtypes = [ctypes.POINTER(ctypes.c_int16), ctypes.c_int]

        self.lib.md_set_button.restype = None
        self.lib.md_set_button.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_bool]

        self.lib.md_save_state.restype = ctypes.c_int
        self.lib.md_save_state.argtypes = [ctypes.c_void_p, ctypes.c_size_t]

        self.lib.md_load_state.restype = ctypes.c_bool
        self.lib.md_load_state.argtypes = [ctypes.c_void_p, ctypes.c_size_t]

        self.lib.md_save_sram.restype = ctypes.c_int
        self.lib.md_save_sram.argtypes = [ctypes.c_void_p, ctypes.c_size_t]

        self.lib.md_load_sram.restype = ctypes.c_bool
        self.lib.md_load_sram.argtypes = [ctypes.c_void_p, ctypes.c_size_t]

    def load_rom(self, rom_path: Path, saves_dir: Path, states_dir: Path) -> bool:
        if not self.is_available or not self.is_initialized or self.lib is None:
            print(f"[MegaDrivePlayer] Error: Libreria nativa no disponible ({self.lib_path.name}).")
            return False
        self.unload()
        self.rom_path = Path(rom_path)
        self.save_path = Path(saves_dir) / f"{self.rom_path.stem}.srm"
        self.state_path = Path(states_dir) / f"{self.rom_path.stem}.state"

        try:
            with open(self.rom_path, "rb") as f:
                rom_bytes = f.read()
        except Exception as e:
            print(f"[MegaDrivePlayer] Error reading ROM file: {e}")
            return False

        abs_path = str(self.rom_path.resolve()).encode("utf-8")
        success = self.lib.md_load_rom(abs_path, rom_bytes, len(rom_bytes))
        if not success:
            print(f"[MegaDrivePlayer] Failed to load ROM: {self.rom_path.name}")
            return False

        # Load battery save if present
        if self.save_path.exists():
            try:
                with open(self.save_path, "rb") as sf:
                    save_data = sf.read()
                if save_data:
                    c_buf = (ctypes.c_uint8 * len(save_data)).from_buffer_copy(save_data)
                    self.lib.md_load_sram(ctypes.byref(c_buf), len(save_data))
            except Exception as e:
                print(f"[MegaDrivePlayer] Error loading SRAM: {e}")

        self.is_loaded = True
        return True

    def unload(self):
        if self.is_loaded:
            self.save_battery()
            self.lib.md_deinit()
            self.lib.md_init()
            self.is_loaded = False

    def reset(self, hard=False):
        if self.is_loaded:
            self.lib.md_reset()

    def set_button(self, player: int, button_name: str, pressed: bool):
        if not self.is_loaded:
            return
        btn_id = MD_BUTTON_MAP.get(button_name)
        if btn_id is not None:
            self.lib.md_set_button(player, btn_id, pressed)

    def step_frame(self, enable_audio=True):
        if not self.is_loaded:
            return
        self.lib.md_run_frame()
        if enable_audio and hasattr(self.lib, "md_get_samples"):
            count = self.lib.md_get_samples(self.audio_buf, self.audio_max_samples)
            if count > 0:
                self.audio_bytes = bytes(ctypes.string_at(self.audio_buf, count * 2))
            else:
                self.audio_bytes = b""
        else:
            self.audio_bytes = b""

    def get_audio_bytes(self) -> bytes:
        return self.audio_bytes

    def get_surface(self) -> pygame.Surface:
        w = ctypes.c_int(320)
        h = ctypes.c_int(224)
        self.lib.md_get_frame_info(ctypes.byref(w), ctypes.byref(h))
        self.width = max(256, min(640, w.value))
        self.height = max(192, min(480, h.value))

        ptr = self.lib.md_get_pixels()
        buf_size = self.width * self.height * 4
        raw = ctypes.string_at(ptr, buf_size)
        return pygame.image.frombuffer(raw, (self.width, self.height), "RGBX")

    def save_battery(self) -> bool:
        if not self.is_loaded or not self.save_path:
            return False
        try:
            buf = (ctypes.c_uint8 * 0x20000)() # 128KB SRAM buffer
            size = self.lib.md_save_sram(ctypes.byref(buf), 0x20000)
            if size > 0:
                self.save_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.save_path, "wb") as f:
                    f.write(bytes(buf[:size]))
                return True
        except Exception as e:
            print(f"[MegaDrivePlayer] Error saving SRAM: {e}")
        return False

    def save_state(self) -> bool:
        if not self.is_loaded or not self.state_path:
            return False
        try:
            buf = (ctypes.c_uint8 * 0x400000)() # 4MB state buffer
            size = self.lib.md_save_state(ctypes.byref(buf), 0x400000)
            if size > 0:
                self.state_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.state_path, "wb") as f:
                    f.write(bytes(buf[:size]))
                return True
        except Exception as e:
            print(f"[MegaDrivePlayer] Error saving state: {e}")
        return False

    def load_state(self) -> bool:
        if not self.is_loaded or not self.state_path or not self.state_path.exists():
            return False
        try:
            with open(self.state_path, "rb") as f:
                data = f.read()
            c_buf = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
            return self.lib.md_load_state(ctypes.byref(c_buf), len(data))
        except Exception as e:
            print(f"[MegaDrivePlayer] Error loading state: {e}")
            return False
