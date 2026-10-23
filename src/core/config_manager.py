"""
Configuration Manager for RetroDeck Frontend.
Manages persistent configuration, input mappings, and paths.
"""

import os
import json
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = BASE_DIR / "config"
ROMS_DIR = BASE_DIR / "roms" / "snes"
SAVES_DIR = BASE_DIR / "saves" / "snes"
STATES_DIR = BASE_DIR / "states" / "snes"
BOXART_DIR = BASE_DIR / "boxart" / "snes"
CONFIG_FILE = CONFIG_DIR / "settings.json"

DEFAULT_CONFIG = {
    "version": "1.1.0",
    "emulator": {
        "backend": "internal",
        "custom_command": "",
        "fullscreen_on_launch": True,
        "sync_saves": True
    },
    "video": {
        "width": 1024,
        "height": 720,
        "fullscreen": False,
        "crt_filter": True,
        "crt_scanline_intensity": 45,  # 0 to 100
        "fps_target": 60
    },
    "audio": {
        "sound_effects_enabled": True,
        "volume": 0.8
    },
    "paths": {
        "roms": str(ROMS_DIR),
        "saves": str(SAVES_DIR),
        "states": str(STATES_DIR),
        "boxart": str(BOXART_DIR)
    },
    "input": {
        "snes": {
            "keyboard": {
                "UP": "UP",
                "DOWN": "DOWN",
                "LEFT": "LEFT",
                "RIGHT": "RIGHT",
                "B": "Z",
                "A": "X",
                "Y": "A",
                "X": "S",
                "L": "Q",
                "R": "W",
                "START": "RETURN",
                "SELECT": "RSHIFT",
                "MENU": "ESCAPE"
            },
            "gamepad": {
                "B": 0,
                "A": 1,
                "Y": 2,
                "X": 3,
                "L": 4,
                "R": 5,
                "SELECT": 6,
                "START": 7,
                "MENU": 8,
                "dpad_axis_x": 0,
                "dpad_axis_y": 1
            }
        },
        "megadrive": {
            "keyboard": {
                "UP": "UP",
                "DOWN": "DOWN",
                "LEFT": "LEFT",
                "RIGHT": "RIGHT",
                "A": "A",
                "B": "S",
                "C": "D",
                "X": "Q",
                "Y": "W",
                "Z": "E",
                "START": "RETURN",
                "MODE": "RSHIFT",
                "MENU": "ESCAPE"
            },
            "gamepad": {
                "A": 2,
                "B": 0,
                "C": 1,
                "X": 3,
                "Y": 4,
                "Z": 5,
                "START": 7,
                "MODE": 6,
                "MENU": 8,
                "dpad_axis_x": 0,
                "dpad_axis_y": 1
            }
        }
    }
}

class ConfigManager:
    def __init__(self):
        self.config_dir = CONFIG_DIR
        self.config_file = CONFIG_FILE
        self.config = self._load()
        self._ensure_directories()

    def _ensure_directories(self):
        for path in [ROMS_DIR, SAVES_DIR, STATES_DIR, BOXART_DIR, CONFIG_DIR]:
            path.mkdir(parents=True, exist_ok=True)

    def _load(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    # Migration: if input is in old flat format, migrate to per-system
                    if "input" in data and isinstance(data["input"], dict):
                        inp = data["input"]
                        if "snes" not in inp and ("keyboard" in inp or "gamepad" in inp):
                            old_kb = inp.get("keyboard", {})
                            old_gp = inp.get("gamepad", {})
                            data["input"] = {
                                "snes": {
                                    "keyboard": old_kb,
                                    "gamepad": old_gp
                                },
                                "megadrive": json.loads(json.dumps(DEFAULT_CONFIG["input"]["megadrive"]))
                            }
                    
                    # Merge with default config to ensure all keys exist
                    return self._merge_dict(DEFAULT_CONFIG, data)
            except Exception as e:
                print(f"[Config] Error loading settings: {e}. Using defaults.")
        return json.loads(json.dumps(DEFAULT_CONFIG))

    def _merge_dict(self, default, custom):
        merged = default.copy()
        for k, v in custom.items():
            if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
                merged[k] = self._merge_dict(merged[k], v)
            else:
                merged[k] = v
        return merged

    def save(self):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"[Config] Error saving settings: {e}")
            return False

    def get(self, *keys, default=None):
        val = self.config
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    def get_input_map(self, system_id: str, input_type: str) -> dict:
        sys_key = "megadrive" if system_id == "megadrive" else "snes"
        val = self.get("input", sys_key, input_type)
        if isinstance(val, dict):
            return val
        return DEFAULT_CONFIG.get("input", {}).get(sys_key, {}).get(input_type, {})

    def set(self, *keys_and_value):
        if len(keys_and_value) < 2:
            return
        keys = keys_and_value[:-1]
        value = keys_and_value[-1]

        target = self.config
        for k in keys[:-1]:
            if k not in target or not isinstance(target[k], dict):
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
        self.save()
