"""
Emulator Runner for RetroSNES.
Supports Internal Native C Core (libretrosnes.so) as primary engine,
with fallback options for Snes9x or RetroArch.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Tuple, Dict

class EmulatorRunner:
    def __init__(self, config_manager):
        self.config = config_manager
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.internal_lib = self.project_root / "src" / "emulator_core" / "libretrosnes.so"
        self.flatpak_id = "com.snes9x.Snes9x"
        self.flatpak_config_dir = Path.home() / ".var" / "app" / self.flatpak_id / "config" / "snes9x"
        self.flatpak_conf_file = self.flatpak_config_dir / "snes9x.conf"

    def detect_backends(self) -> Dict[str, bool]:
        """Detect which SNES emulators are available on the system."""
        results = {
            "internal": self.internal_lib.exists(),
            "flatpak_snes9x": False,
            "snes9x": False,
            "retroarch": False,
            "custom": bool(self.config.get("emulator", "custom_command"))
        }

        # Check Flatpak Snes9x
        try:
            res = subprocess.run(
                ["flatpak", "info", "--user", self.flatpak_id],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            if res.returncode == 0:
                results["flatpak_snes9x"] = True
            else:
                res2 = subprocess.run(
                    ["flatpak", "info", self.flatpak_id],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                results["flatpak_snes9x"] = (res2.returncode == 0)
        except Exception:
            pass

        # Check native snes9x or snes9x-gtk
        if shutil.which("snes9x") or shutil.which("snes9x-gtk"):
            results["snes9x"] = True

        # Check retroarch
        if shutil.which("retroarch"):
            results["retroarch"] = True

        return results

    def get_active_backend(self) -> str:
        chosen = self.config.get("emulator", "backend", default="internal")
        available = self.detect_backends()

        if chosen in available and available[chosen]:
            return chosen

        # Prioritize Internal core
        if available.get("internal"):
            return "internal"
        if available.get("flatpak_snes9x"):
            return "flatpak_snes9x"
        if available.get("snes9x"):
            return "snes9x"
        if available.get("retroarch"):
            return "retroarch"
        if available.get("custom"):
            return "custom"

        return "none"

    def is_internal(self) -> bool:
        return self.get_active_backend() == "internal"
