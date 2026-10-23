"""
Multi-System ROM Manager.
Scans ROM directories, parses headers (SNES & Sega Mega Drive), loads metadata and box art.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from src.core.system_manager import SystemInfo

class RomInfo:
    def __init__(self, filepath: Path, system_id: str):
        self.path = filepath
        self.system_id = system_id
        self.filename = filepath.name
        self.stem = filepath.stem
        self.extension = filepath.suffix.lower()
        self.filesize = filepath.stat().st_size
        self.title = self.stem.replace("_", " ").replace("-", " ")
        self.internal_title = ""
        self.rom_type = "Standard"
        self.region = "Unknown"
        self.boxart_path: Optional[Path] = None
        self.custom_boxart: Optional[str] = None
        self.custom_title: Optional[str] = None
        self.play_count = 0
        self.last_played = None
        self.is_favorite = False

        if system_id == "snes":
            self._parse_snes_header()
        elif system_id == "megadrive":
            self._parse_megadrive_header()

    def _parse_snes_header(self):
        if self.extension not in {".smc", ".sfc", ".fig", ".swc"}:
            return
        try:
            with open(self.path, "rb") as f:
                data = f.read(0x10200)
            if len(data) < 0x8000:
                return

            has_copier_header = (self.filesize % 1024) == 512
            offset_base = 512 if has_copier_header else 0

            lorom_offset = offset_base + 0x7FC0
            hirom_offset = offset_base + 0xFFC0

            header_offset = None
            for offset in (lorom_offset, hirom_offset):
                if len(data) >= offset + 48:
                    csum_comp = int.from_bytes(data[offset + 0x1C : offset + 0x1E], "little")
                    csum = int.from_bytes(data[offset + 0x1E : offset + 0x20], "little")
                    if (csum + csum_comp) == 0xFFFF and csum != 0:
                        header_offset = offset
                        self.rom_type = "HiROM" if offset == hirom_offset else "LoROM"
                        break

            if header_offset is None:
                header_offset = lorom_offset if len(data) >= lorom_offset + 32 else None
                self.rom_type = "LoROM"

            if header_offset and len(data) >= header_offset + 32:
                raw_title = data[header_offset : header_offset + 21]
                cleaned = "".join([chr(b) if 32 <= b <= 126 else "" for b in raw_title]).strip()
                if len(cleaned) >= 3:
                    self.internal_title = cleaned
                    if not self.title or len(self.title) < 3:
                        self.title = self.internal_title

                region_code = data[header_offset + 0x19]
                region_map = {
                    0: "Japan", 1: "USA / Canada", 2: "Europe",
                    3: "Scandinavia", 6: "France", 7: "Netherlands", 8: "Spain",
                    9: "Germany", 10: "Italy"
                }
                self.region = region_map.get(region_code, f"Region {region_code}")
        except Exception:
            pass

    def _parse_megadrive_header(self):
        """Parses Sega Mega Drive / Genesis standard cartridge header (0x100 - 0x200)."""
        if self.extension not in {".bin", ".gen", ".md", ".smd"}:
            return
        try:
            with open(self.path, "rb") as f:
                header_data = f.read(0x200)
            if len(header_data) < 0x200:
                return

            # Check system identifier at 0x100
            sys_id_bytes = header_data[0x100:0x110]
            sys_str = "".join([chr(b) if 32 <= b <= 126 else "" for b in sys_id_bytes]).strip()
            self.rom_type = "Mega Drive" if "MEGA" in sys_str else "Genesis"

            # Domestic & Overseas titles at 0x120 and 0x150 (48 bytes each)
            dom_title = "".join([chr(b) if 32 <= b <= 126 else "" for b in header_data[0x120:0x150]]).strip()
            overseas_title = "".join([chr(b) if 32 <= b <= 126 else "" for b in header_data[0x150:0x180]]).strip()
            
            chosen_title = overseas_title if len(overseas_title) >= 3 else dom_title
            if len(chosen_title) >= 3:
                self.internal_title = chosen_title
                if not self.title or len(self.title) < 3:
                    self.title = self.internal_title

            # Country/Region code at 0x1F0 (16 bytes)
            region_str = "".join([chr(b) if 32 <= b <= 126 else "" for b in header_data[0x1F0:0x200]]).strip()
            if "J" in region_str and "U" not in region_str and "E" not in region_str:
                self.region = "Japan"
            elif "E" in region_str and "U" not in region_str:
                self.region = "Europe"
            elif "U" in region_str:
                self.region = "USA / World"
            else:
                self.region = region_str if region_str else "World"
        except Exception:
            pass

    def get_formatted_size(self) -> str:
        size = self.filesize
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.2f} MB"


class RomManager:
    def __init__(self, config_dir: Path):
        self.config_dir = Path(config_dir)
        self.cache_file = self.config_dir / "gamelist_cache.json"
        self.roms: List[RomInfo] = []
        self.current_system: Optional[SystemInfo] = None
        self._load_cache()

    def _load_cache(self) -> dict:
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_cache(self, data: dict):
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def scan_system(self, system: SystemInfo) -> List[RomInfo]:
        """Scans the ROM directory for a specific system."""
        self.current_system = system
        self.roms.clear()
        cache = self._load_cache()

        if not system.roms_dir.exists():
            system.roms_dir.mkdir(parents=True, exist_ok=True)

        found_files = []
        for ext in system.extensions:
            found_files.extend(system.roms_dir.glob(f"*{ext}"))
            found_files.extend(system.roms_dir.glob(f"*{ext.upper()}"))

        unique_paths = sorted(list({p.resolve(): p for p in found_files}.values()), key=lambda p: p.name.lower())

        for p in unique_paths:
            rom = RomInfo(p, system.id)
            rel_key = f"{system.id}:{p.name}"

            if rel_key in cache:
                meta = cache[rel_key]
                rom.play_count = meta.get("play_count", 0)
                rom.last_played = meta.get("last_played", None)
                rom.is_favorite = meta.get("is_favorite", False)
                rom.custom_title = meta.get("custom_title", None)
                rom.custom_boxart = meta.get("custom_boxart", None)
                if rom.custom_title:
                    rom.title = rom.custom_title

            if rom.custom_boxart and Path(rom.custom_boxart).exists():
                rom.boxart_path = Path(rom.custom_boxart)
            else:
                rom.boxart_path = self._find_boxart(rom, system.boxart_dir)

            self.roms.append(rom)

        return self.roms

    def _find_boxart(self, rom: RomInfo, boxart_dir: Path) -> Optional[Path]:
        for ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"]:
            candidate = boxart_dir / f"{rom.stem}{ext}"
            if candidate.exists():
                return candidate
            if rom.internal_title:
                cand2 = boxart_dir / f"{rom.internal_title}{ext}"
                if cand2.exists():
                    return cand2
        return None

    def set_custom_boxart(self, rom: RomInfo, img_path: Optional[str]) -> bool:
        """Sets or clears a custom boxart image for this ROM."""
        rom.custom_boxart = img_path
        if img_path and Path(img_path).exists():
            rom.boxart_path = Path(img_path)
        else:
            base_dir = self.config_dir.parent
            from src.core.system_manager import SystemManager
            sys_mgr = SystemManager(base_dir)
            sys_info = sys_mgr.systems.get(rom.system_id)
            rom.boxart_path = self._find_boxart(rom, sys_info.boxart_dir) if sys_info else None

        cache = self._load_cache()
        key = f"{rom.system_id}:{rom.filename}"
        if key not in cache:
            cache[key] = {}
        cache[key]["custom_boxart"] = img_path
        self._save_cache(cache)
        return True

    def set_custom_title(self, rom: RomInfo, new_title: Optional[str]) -> bool:
        """Sets or clears a custom display title for this ROM."""
        rom.custom_title = new_title
        if new_title:
            rom.title = new_title
        else:
            rom.title = rom.stem.replace("_", " ").replace("-", " ")

        cache = self._load_cache()
        key = f"{rom.system_id}:{rom.filename}"
        if key not in cache:
            cache[key] = {}
        cache[key]["custom_title"] = new_title
        self._save_cache(cache)
        return True

    def reset_stats(self, rom: RomInfo):
        """Resets play count and last played timestamp."""
        rom.play_count = 0
        rom.last_played = None
        cache = self._load_cache()
        key = f"{rom.system_id}:{rom.filename}"
        if key in cache:
            cache[key]["play_count"] = 0
            cache[key]["last_played"] = None
            self._save_cache(cache)

    def backup_sram(self, rom: RomInfo, system: SystemInfo) -> Optional[Path]:
        """Creates a timestamped backup of the battery SRAM save file."""
        import shutil, datetime
        srm_path = system.saves_dir / f"{rom.stem}.srm"
        if not srm_path.exists():
            return None
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = system.saves_dir / f"{rom.stem}_backup_{timestamp}.srm"
        try:
            shutil.copy2(srm_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"[RomManager] Backup error: {e}")
            return None

    def delete_sram(self, rom: RomInfo, system: SystemInfo) -> bool:
        """Deletes the battery SRAM save file to start fresh."""
        srm_path = system.saves_dir / f"{rom.stem}.srm"
        if srm_path.exists():
            try:
                srm_path.unlink()
                return True
            except Exception as e:
                print(f"[RomManager] Delete error: {e}")
                return False
        return False

    def get_sram_info(self, rom: RomInfo, system: SystemInfo) -> dict:
        """Returns details about this game's SRAM battery save."""
        import datetime
        srm_path = system.saves_dir / f"{rom.stem}.srm"
        if srm_path.exists():
            stat = srm_path.stat()
            size_kb = f"{stat.st_size / 1024:.1f} KB"
            mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            return {"exists": True, "path": srm_path, "size": size_kb, "mtime": mtime}
        return {"exists": False, "path": None, "size": "0 KB", "mtime": "Sin partida guardada"}

    def update_rom_stats(self, rom: RomInfo):
        import datetime
        rom.play_count += 1
        rom.last_played = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        cache = self._load_cache()
        key = f"{rom.system_id}:{rom.filename}"
        cache[key] = {
            "play_count": rom.play_count,
            "last_played": rom.last_played,
            "is_favorite": rom.is_favorite
        }
        self._save_cache(cache)

    def toggle_favorite(self, rom: RomInfo):
        rom.is_favorite = not rom.is_favorite
        cache = self._load_cache()
        key = f"{rom.system_id}:{rom.filename}"
        if key not in cache:
            cache[key] = {}
        cache[key]["is_favorite"] = rom.is_favorite
        self._save_cache(cache)

    def scan_roms(self, system: Optional[SystemInfo] = None) -> List[RomInfo]:
        """Backward-compatible scan method for requested or current system."""
        if system is not None:
            return self.scan_system(system)
        if self.current_system is not None:
            return self.scan_system(self.current_system)
        base_dir = self.config_dir.parent
        from src.core.system_manager import SystemManager
        sys_mgr = SystemManager(base_dir)
        return self.scan_system(sys_mgr.get_active_system())

