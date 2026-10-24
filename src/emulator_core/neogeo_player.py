"""
Neo Geo MVS / AES Native Emulator Player.
Bridge to libneogeo_bridge.so / libneogeo_bridge.dll (FBAlpha 2012 Neo Geo core).
Provides 60 FPS arcade video, Yamaha YM2610 16-bit stereo audio, 4-button arcade controls, SRAM, and savestates.
"""

import os
import sys
import ctypes
from pathlib import Path
from typing import Optional
import pygame

# Neo Geo arcade button mappings in Libretro bridge:
# A (Red)    -> Libretro Y (1)
# B (Yellow) -> Libretro B (0)
# C (Green)  -> Libretro A (8)
# D (Blue)   -> Libretro X (9)
# SELECT     -> Libretro SELECT (2) [Coin / Select]
# START      -> Libretro START (3)
NG_BUTTON_MAP = {
    "UP": 4,
    "DOWN": 5,
    "LEFT": 6,
    "RIGHT": 7,
    "A": 1,
    "B": 0,
    "C": 8,
    "D": 9,
    "START": 3,
    "SELECT": 2,
    "COIN": 2,
    "MENU": 2,
}

class NeoGeoPlayer:
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

            # Preload core dependency (fbalpha2012_neogeo_libretro.dll) into memory
            core_dll = self.lib_path.parent / "fbalpha2012_neogeo_libretro.dll"
            if core_dll.exists():
                try:
                    ctypes.CDLL(str(core_dll))
                except Exception as e:
                    print(f"[NeoGeoPlayer] Preload {core_dll.name}: {e}")

        if self.is_available:
            try:
                self.lib = ctypes.CDLL(str(self.lib_path))
                self._setup_prototypes()
                self.is_initialized = self.lib.ng_init()
            except Exception as e:
                print(f"[NeoGeoPlayer] Error al cargar la libreria nativa {self.lib_path}: {e}")
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
        self.error_message = ""
        self.width = 304
        self.height = 224

        # Audio buffer for extraction (44.1 kHz stereo 16-bit)
        self.audio_max_samples = 4096 * 2
        self.audio_buf = (ctypes.c_int16 * self.audio_max_samples)()
        self.audio_bytes = b""
        self._surface = None
        self._pixel_view = None
        self._last_ptr = None

    def _setup_prototypes(self):
        self.lib.ng_init.restype = ctypes.c_bool
        self.lib.ng_deinit.restype = None
        
        self.lib.ng_set_system_dir.restype = None
        self.lib.ng_set_system_dir.argtypes = [ctypes.c_char_p]

        self.lib.ng_load_rom.restype = ctypes.c_bool
        self.lib.ng_load_rom.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_size_t]

        self.lib.ng_run_frame.restype = None
        self.lib.ng_reset.restype = None

        self.lib.ng_get_frame_info.restype = None
        self.lib.ng_get_frame_info.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

        self.lib.ng_get_pixels.restype = ctypes.c_void_p

        if hasattr(self.lib, "ng_get_samples"):
            self.lib.ng_get_samples.restype = ctypes.c_int
            self.lib.ng_get_samples.argtypes = [ctypes.POINTER(ctypes.c_int16), ctypes.c_int]

        self.lib.ng_set_button.restype = None
        self.lib.ng_set_button.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_bool]

        self.lib.ng_save_state.restype = ctypes.c_int
        self.lib.ng_save_state.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]

        self.lib.ng_load_state.restype = ctypes.c_bool
        self.lib.ng_load_state.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]

        self.lib.ng_save_sram.restype = ctypes.c_int
        self.lib.ng_save_sram.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]

        self.lib.ng_load_sram.restype = ctypes.c_bool
        self.lib.ng_load_sram.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]

    def load_rom(self, rom_path: Path, saves_dir: Path, states_dir: Path) -> bool:
        if not self.is_available or not self.lib:
            self.error_message = "LIBRERÍA NATIVA NO DISPONIBLE"
            return False

        self.rom_path = Path(rom_path).resolve()
        if not self.rom_path.exists():
            print(f"[NeoGeoPlayer] Error: ROM no encontrada en {self.rom_path}")
            self.error_message = "ROM NO ENCONTRADA"
            return False

        stem = self.rom_path.stem
        self.save_path = saves_dir / f"{stem}.srm"
        self.state_path = states_dir / f"{stem}.state"
        self.error_message = ""

        # Set system directory for neogeo.zip
        rom_dir = str(self.rom_path.parent)
        self.lib.ng_set_system_dir(rom_dir.encode("utf-8"))

        path_bytes = str(self.rom_path).encode("utf-8")
        success = self.lib.ng_load_rom(path_bytes, None, 0)
        
        if not success:
            # Check if neogeo.zip is present
            bios_present = (self.rom_path.parent / "neogeo.zip").exists()
            if not bios_present:
                print(f"[NeoGeoPlayer] AVISO LEGAL / BIOS: Falta neogeo.zip en {self.rom_path.parent}")
                self.error_message = "FALTA BIOS (neogeo.zip) EN roms/neogeo/"
            else:
                self.error_message = "ERROR AL CARGAR ROM DE NEOGEO"
            return False

        self.is_loaded = True
        self._load_sram()

        w = ctypes.c_int()
        h = ctypes.c_int()
        self.lib.ng_get_frame_info(ctypes.byref(w), ctypes.byref(h))
        self.width = w.value if w.value > 0 else 304
        self.height = h.value if h.value > 0 else 224

        print(f"[NeoGeoPlayer] {stem} cargado correctamente ({self.width}x{self.height} @ 60 FPS).")
        return True

    def unload(self):
        if self.is_loaded and self.lib:
            self._save_sram()
            self.lib.ng_deinit()
            self.is_loaded = False
            self.rom_path = None
            self.save_path = None
            self.state_path = None
            self.audio_bytes = b""
            self._surface = None
            self._pixel_view = None
            self._last_ptr = None

    def reset(self, hard: bool = False):
        if self.is_loaded and self.lib:
            self.lib.ng_reset()

    def step_frame(self, enable_audio: bool = True):
        if self.is_loaded and self.lib:
            self.lib.ng_run_frame()

            if enable_audio and hasattr(self.lib, "ng_get_samples"):
                count = self.lib.ng_get_samples(self.audio_buf, self.audio_max_samples)
                if count > 0:
                    byte_count = count * 2
                    self.audio_bytes = ctypes.string_at(self.audio_buf, byte_count)
                else:
                    self.audio_bytes = b""
            else:
                self.audio_bytes = b""

    def get_audio_bytes(self) -> bytes:
        return self.audio_bytes

    def get_surface(self) -> pygame.Surface:
        if not self.is_loaded or not self.lib:
            return pygame.Surface((self.width, self.height))

        w = ctypes.c_int()
        h = ctypes.c_int()
        self.lib.ng_get_frame_info(ctypes.byref(w), ctypes.byref(h))
        cur_w = w.value if w.value > 0 else self.width
        cur_h = h.value if h.value > 0 else self.height

        pixel_ptr = self.lib.ng_get_pixels()
        if not pixel_ptr:
            return pygame.Surface((cur_w, cur_h))

        if self._surface is None or self.width != cur_w or self.height != cur_h or self._last_ptr != pixel_ptr:
            self.width = cur_w
            self.height = cur_h
            self._last_ptr = pixel_ptr
            buf_size = cur_w * cur_h * 4
            self._pixel_view = (ctypes.c_uint8 * buf_size).from_address(pixel_ptr)
            self._surface = pygame.image.frombuffer(self._pixel_view, (cur_w, cur_h), "RGBA")

        return self._surface

    def set_button(self, player: int, btn_name: str, pressed: bool):
        if not self.is_loaded or not self.lib:
            return
        btn_id = NG_BUTTON_MAP.get(btn_name.upper())
        if btn_id is not None:
            self.lib.ng_set_button(player, btn_id, pressed)

    def save_state(self) -> bool:
        if not self.is_loaded or not self.lib or not self.state_path:
            return False
        max_sz = 16 * 1024 * 1024 # 16 MB max state buffer for Neo Geo
        buf = (ctypes.c_uint8 * max_sz)()
        written = self.lib.ng_save_state(buf, max_sz)
        if written > 0:
            try:
                self.state_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.state_path, "wb") as f:
                    f.write(bytes(buf[:written]))
                print(f"[NeoGeoPlayer] Estado guardado en {self.state_path} ({written} bytes).")
                return True
            except Exception as e:
                print(f"[NeoGeoPlayer] Error al escribir savestate: {e}")
        return False

    def load_state(self) -> bool:
        if not self.is_loaded or not self.lib or not self.state_path or not self.state_path.exists():
            return False
        try:
            with open(self.state_path, "rb") as f:
                data = f.read()
            sz = len(data)
            buf = (ctypes.c_uint8 * sz).from_buffer_copy(data)
            success = self.lib.ng_load_state(buf, sz)
            if success:
                print(f"[NeoGeoPlayer] Estado restaurado desde {self.state_path}.")
            return success
        except Exception as e:
            print(f"[NeoGeoPlayer] Error al cargar savestate: {e}")
            return False

    def _save_sram(self):
        if not self.is_loaded or not self.lib or not self.save_path:
            return
        max_sz = 512 * 1024
        buf = (ctypes.c_uint8 * max_sz)()
        written = self.lib.ng_save_sram(buf, max_sz)
        if written > 0:
            try:
                self.save_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.save_path, "wb") as f:
                    f.write(bytes(buf[:written]))
            except Exception as e:
                print(f"[NeoGeoPlayer] Error al guardar SRAM: {e}")

    def _load_sram(self):
        if not self.is_loaded or not self.lib or not self.save_path or not self.save_path.exists():
            return
        try:
            with open(self.save_path, "rb") as f:
                data = f.read()
            sz = len(data)
            buf = (ctypes.c_uint8 * sz).from_buffer_copy(data)
            self.lib.ng_load_sram(buf, sz)
        except Exception as e:
            print(f"[NeoGeoPlayer] Error al cargar SRAM: {e}")
