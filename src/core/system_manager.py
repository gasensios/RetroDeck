"""
System Manager for RetroDeck.
Manages supported retro consoles: Super Nintendo and Sega Mega Drive / Genesis.
"""

from pathlib import Path
from typing import Dict, List, Optional

class SystemInfo:
    def __init__(self, sys_id: str, name: str, full_name: str, company: str, 
                 theme_color: tuple, accent_color: tuple, badge_color: tuple,
                 extensions: List[str], project_root: Path, short: str = ""):
        self.id = sys_id
        self.name = name
        self.full_name = full_name
        self.company = company
        self.short = short if short else name.upper()
        self.theme_color = theme_color
        self.accent_color = accent_color
        self.badge_color = badge_color
        self.extensions = set(extensions)
        
        self.roms_dir = project_root / "roms" / sys_id
        self.boxart_dir = project_root / "boxart" / sys_id
        self.saves_dir = project_root / "saves" / sys_id
        self.states_dir = project_root / "states" / sys_id
        
        self._ensure_dirs()

    def _ensure_dirs(self):
        for d in [self.roms_dir, self.boxart_dir, self.saves_dir, self.states_dir]:
            d.mkdir(parents=True, exist_ok=True)


class SystemManager:
    def __init__(self, project_root: Path, active_system_id: str = "snes"):
        self.project_root = Path(project_root).resolve()
        self.systems: Dict[str, SystemInfo] = {
            "snes": SystemInfo(
                sys_id="snes",
                name="Super Nintendo",
                full_name="Super Nintendo Entertainment System (16-Bit)",
                company="NINTENDO",
                short="SNES",
                theme_color=(108, 92, 231),   # SNES Purple
                accent_color=(162, 155, 254), # SNES Lilac
                badge_color=(255, 206, 84),   # Gold
                extensions=[".smc", ".sfc", ".fig", ".swc", ".zip", ".7z"],
                project_root=self.project_root
            ),
            "megadrive": SystemInfo(
                sys_id="megadrive",
                name="Mega Drive",
                full_name="Sega Mega Drive / Genesis (16-Bit)",
                company="SEGA",
                short="MEGADRIVE",
                theme_color=(0, 96, 190),     # Sega Blue
                accent_color=(79, 193, 233),  # Cyan
                badge_color=(255, 204, 0),    # Sonic Gold
                extensions=[".bin", ".gen", ".md", ".smd", ".zip", ".7z"],
                project_root=self.project_root
            )
        }
        self.system_order = ["snes", "megadrive"]
        self.active_system_id = active_system_id if active_system_id in self.systems else "snes"

    def get_active_system(self) -> SystemInfo:
        return self.systems[self.active_system_id]

    def set_system(self, sys_id: str) -> bool:
        if sys_id in self.systems:
            self.active_system_id = sys_id
            return True
        return False

    def next_system(self) -> SystemInfo:
        curr_idx = self.system_order.index(self.active_system_id)
        next_idx = (curr_idx + 1) % len(self.system_order)
        self.active_system_id = self.system_order[next_idx]
        return self.get_active_system()

    def prev_system(self) -> SystemInfo:
        curr_idx = self.system_order.index(self.active_system_id)
        prev_idx = (curr_idx - 1) % len(self.system_order)
        self.active_system_id = self.system_order[prev_idx]
        return self.get_active_system()
