"""
Unit and Integration Tests for RetroDeck (SNES & Sega Mega Drive).
"""

import unittest
from pathlib import Path
import os
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()

from src.core.config_manager import ConfigManager
from src.core.system_manager import SystemManager
from src.core.rom_manager import RomManager
from src.core.sound_manager import SoundManager
from src.core.input_manager import InputManager, get_system_buttons
from src.ui.retro_theme import RetroTheme
from src.ui.controls_view import ControlsView
from src.ui.gameplay_view import GameplayView
from src.emulator_core.snes_player import SnesPlayer
from src.emulator_core.megadrive_player import MegaDrivePlayer

class TestMultiSystem(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager()
        self.sys_mgr = SystemManager(PROJECT_ROOT)
        self.rom_mgr = RomManager(PROJECT_ROOT / "config")

    def test_system_manager(self):
        self.assertEqual(self.sys_mgr.get_active_system().id, "snes")
        next_sys = self.sys_mgr.next_system()
        self.assertEqual(next_sys.id, "megadrive")
        self.assertEqual(next_sys.company, "SEGA")
        back_snes = self.sys_mgr.next_system()
        self.assertEqual(back_snes.id, "snes")

    def test_snes_rom_scanning_and_emulation(self):
        snes_sys = self.sys_mgr.systems["snes"]
        snes_roms = self.rom_mgr.scan_system(snes_sys)
        self.assertGreater(len(snes_roms), 0)

        snes_lib = PROJECT_ROOT / "src" / "emulator_core" / "libretrosnes.so"
        player = SnesPlayer(snes_lib)
        loaded = player.load_rom(snes_roms[0].path, snes_sys.saves_dir, snes_sys.states_dir)
        self.assertTrue(loaded)
        for _ in range(30):
            player.step_frame()
        surf = player.get_surface()
        self.assertEqual(surf.get_size(), (512, 480))
        player.unload()

    def test_megadrive_rom_scanning_and_emulation(self):
        md_sys = self.sys_mgr.systems["megadrive"]
        md_roms = self.rom_mgr.scan_system(md_sys)
        self.assertGreater(len(md_roms), 0, "Mega Drive roms should be detected")

        md_lib = PROJECT_ROOT / "src" / "emulator_core" / "libmegadrive_bridge.so"
        player = MegaDrivePlayer(md_lib)
        loaded = player.load_rom(md_roms[0].path, md_sys.saves_dir, md_sys.states_dir)
        self.assertTrue(loaded)
        for _ in range(30):
            player.step_frame()
        surf = player.get_surface()
        self.assertGreater(surf.get_width(), 200)
        self.assertGreater(surf.get_height(), 150)
        
        # Test savestates on Mega Drive
        saved = player.save_state()
        self.assertTrue(saved)
        loaded_st = player.load_state()
        self.assertTrue(loaded_st)
        
        player.unload()

    def test_per_system_input_configuration(self):
        input_mgr = InputManager(self.config)
        
        # 1. Distinct button layouts
        snes_btns = [b[0] for b in get_system_buttons("snes")]
        md_btns = [b[0] for b in get_system_buttons("megadrive")]
        self.assertIn("L", snes_btns)
        self.assertIn("R", snes_btns)
        self.assertIn("C", md_btns)
        self.assertIn("Z", md_btns)
        self.assertIn("MODE", md_btns)

        # 2. Config separation
        snes_kb = self.config.get_input_map("snes", "keyboard")
        md_kb = self.config.get_input_map("megadrive", "keyboard")
        self.assertIn("A", snes_kb)
        self.assertIn("C", md_kb)

        # 3. Remap testing
        def dummy_cb(btn, val): pass
        input_mgr.start_remap("megadrive", "keyboard", "C", dummy_cb)
        evt = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_j)
        res = input_mgr.process_event(evt)
        self.assertEqual(res, "MAPPED")
        self.assertEqual(self.config.get("input", "megadrive", "keyboard", "C"), "J")

        # 4. ControlsView system switching & rendering
        theme = RetroTheme(PROJECT_ROOT / "assets")
        sound = SoundManager(enabled=False, volume=0.8)
        controls_view = ControlsView(theme, sound, input_mgr, self.config)
        
        self.assertEqual(controls_view.current_system, "snes")
        controls_view.toggle_system()
        self.assertEqual(controls_view.current_system, "megadrive")

        screen = pygame.Surface((1024, 720))
        # Draw Mega Drive controls
        controls_view.draw(screen)
        controls_view.toggle_system()
        # Draw SNES controls
        controls_view.draw(screen)

    def test_megadrive_controls_in_gameplay(self):
        theme = RetroTheme(PROJECT_ROOT / "assets")
        sound = SoundManager(enabled=False, volume=0.8)
        input_mgr = InputManager(self.config)
        gameplay = GameplayView(theme, self.config, input_mgr, sound)

        md_sys = self.sys_mgr.systems["megadrive"]
        md_roms = self.rom_mgr.scan_system(md_sys)
        self.assertTrue(len(md_roms) > 0)
        
        started = gameplay.start_game(md_roms[0])
        self.assertTrue(started)

        # Simulate pressing Mega Drive Button C (mapped to J from previous test)
        evt_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_j)
        gameplay.handle_event(evt_down)
        gameplay.update_frame()

        evt_up = pygame.event.Event(pygame.KEYUP, key=pygame.K_j)
        gameplay.handle_event(evt_up)
        gameplay.update_frame()

        gameplay.stop_game()

    def test_missing_core_graceful_handling(self):
        missing_snes = SnesPlayer(Path("/tmp/nonexistent_core.dll"))
        self.assertFalse(missing_snes.is_available)
        self.assertIsNone(missing_snes.lib)
        self.assertFalse(missing_snes.load_rom(Path("dummy.smc"), Path("/tmp"), Path("/tmp")))

        missing_md = MegaDrivePlayer(Path("/tmp/nonexistent_core.dll"))
        self.assertFalse(missing_md.is_available)
        self.assertIsNone(missing_md.lib)
        self.assertFalse(missing_md.load_rom(Path("dummy.bin"), Path("/tmp"), Path("/tmp")))

if __name__ == "__main__":
    unittest.main()
