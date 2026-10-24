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
from src.emulator_core.neogeo_player import NeoGeoPlayer

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
        ng_sys = self.sys_mgr.next_system()
        self.assertEqual(ng_sys.id, "neogeo")
        self.assertEqual(ng_sys.company, "SNK")
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
            player.step_frame(enable_audio=True)
        surf = player.get_surface()
        self.assertEqual(surf.get_size(), (512, 480))
        audio = player.get_audio_bytes()
        self.assertEqual(len(audio), 735 * 4)
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
            player.step_frame(enable_audio=True)
        surf = player.get_surface()
        self.assertGreater(surf.get_width(), 200)
        self.assertGreater(surf.get_height(), 150)
        audio = player.get_audio_bytes()
        self.assertIsNotNone(audio)
        
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
        controls_view.toggle_system()
        self.assertEqual(controls_view.current_system, "neogeo")

        screen = pygame.Surface((1024, 720))
        # Draw Neo Geo controls
        controls_view.draw(screen)
        controls_view.toggle_system()
        # Draw SNES controls
        controls_view.draw(screen)
        controls_view.toggle_system()
        # Draw Mega Drive controls
        controls_view.draw(screen)

    def test_neogeo_system_and_player(self):
        ng_sys = self.sys_mgr.systems["neogeo"]
        self.assertEqual(ng_sys.id, "neogeo")
        self.assertEqual(ng_sys.company, "SNK")
        self.assertIn(".zip", ng_sys.extensions)

        # 1. Scan ROMs and verify demo detection
        ng_roms = self.rom_mgr.scan_system(ng_sys)
        self.assertGreater(len(ng_roms), 0, "Neo Geo demo ROM should be detected")
        demo_rom = next((r for r in ng_roms if "demo" in r.stem.lower()), None)
        self.assertIsNotNone(demo_rom)
        self.assertEqual(demo_rom.title, "Neo Geo Arcade Homebrew Demo")

        # 2. Test neogeo.zip is ignored as a game
        fake_bios = ng_sys.roms_dir / "neogeo.zip"
        try:
            fake_bios.touch()
            scanned_after_bios = self.rom_mgr.scan_system(ng_sys)
            bios_in_roms = any(r.filename.lower() == "neogeo.zip" for r in scanned_after_bios)
            self.assertFalse(bios_in_roms, "neogeo.zip must NEVER be added to playable games")
        finally:
            if fake_bios.exists():
                fake_bios.unlink()

        # 3. Test NeoGeoPlayer initialization
        ng_lib = PROJECT_ROOT / "src" / "emulator_core" / "libneogeo_bridge.so"
        player = NeoGeoPlayer(ng_lib)
        self.assertTrue(player.is_available)
        self.assertTrue(player.is_initialized)

        # 4. Test button layouts
        ng_btns = [b[0] for b in get_system_buttons("neogeo")]
        self.assertIn("A", ng_btns)
        self.assertIn("B", ng_btns)
        self.assertIn("C", ng_btns)
        self.assertIn("D", ng_btns)
        self.assertIn("START", ng_btns)
        self.assertIn("SELECT", ng_btns)

        # 5. Visual theme drawing for Neo Geo
        theme = RetroTheme(PROJECT_ROOT / "assets")
        screen = pygame.Surface((1024, 720))
        theme.draw_animated_retro_bg(screen, "neogeo", 120)
        theme.draw_neogeo_badge(screen, 10, 10)
        cart_rect = pygame.Rect(100, 100, 240, 220)
        theme.draw_cartridge(screen, cart_rect, system_id="neogeo", title="Metal Slug")
        theme.draw_neogeo_controller_preview(screen, 500, 400, highlight_btn="A")

        player.unload()

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

    def test_font_preferences_and_resolution(self):
        theme = RetroTheme(PROJECT_ROOT / "assets")
        
        # 1. Retro mode (normal scale)
        theme.set_font_preferences(font_style="retro", font_scale="normal", antialias=True)
        s_norm = theme.render_text("RETRO FONT TEST", 8, (255, 255, 255))
        self.assertGreater(s_norm.get_width(), 50)
        self.assertEqual(s_norm.get_height(), 8)

        # 2. Retro mode (large scale)
        theme.set_font_preferences(font_style="retro", font_scale="large", antialias=True)
        s_large = theme.render_text("RETRO FONT TEST", 8, (255, 255, 255))
        self.assertGreater(s_large.get_width(), s_norm.get_width())
        self.assertGreater(s_large.get_height(), s_norm.get_height())

        # 3. Retro mode (extra large scale)
        theme.set_font_preferences(font_style="retro", font_scale="xlarge", antialias=True)
        s_xlarge = theme.render_text("RETRO FONT TEST", 8, (255, 255, 255))
        self.assertGreater(s_xlarge.get_width(), s_large.get_width())

        # 4. HD High-Definition clean font mode
        theme.set_font_preferences(font_style="hd", font_scale="normal", antialias=True)
        s_hd = theme.render_text("RETRO FONT TEST", 8, (255, 255, 255))
        self.assertGreater(s_hd.get_height(), 10)
        self.assertGreater(s_hd.get_width(), 40)

    def test_fps_hud_and_settings_adjustments(self):
        from src.ui.settings_view import SettingsView
        theme = RetroTheme(PROJECT_ROOT / "assets")
        sound = SoundManager(enabled=False, volume=0.8)
        settings_view = SettingsView(theme, sound, self.config, self.rom_mgr, None, self.sys_mgr)

        # 1. Test HUD rendering
        surf = pygame.Surface((1024, 720))
        theme.draw_fps_hud(surf, 60.0)
        theme.draw_fps_hud(surf, 50.0)
        theme.draw_fps_hud(surf, 30.0)

        # 2. Toggle FPS option in SettingsView
        items_def = settings_view._get_items_def()
        fps_idx = [i for i, item in enumerate(items_def) if item[0] == "show_fps"][0]
        initial_fps = self.config.get("video", "show_fps", default=False)
        settings_view.selected_index = fps_idx
        settings_view.handle_input("A")
        self.assertNotEqual(initial_fps, self.config.get("video", "show_fps"))

        # 3. Adjust Font Size option in SettingsView
        self.config.set("video", "font_size", "normal")
        theme.set_font_preferences(font_style="retro", font_scale="normal")
        font_size_idx = [i for i, item in enumerate(items_def) if item[0] == "font_size"][0]
        settings_view.selected_index = font_size_idx
        settings_view.handle_input("RIGHT")
        self.assertEqual(self.config.get("video", "font_size"), "large")
        self.assertEqual(theme.font_scale, "large")

        # 4. Adjust Font Style (HD / Retro)
        self.config.set("video", "font_style", "retro")
        theme.set_font_preferences(font_style="retro", font_scale="large")
        font_style_idx = [i for i, item in enumerate(items_def) if item[0] == "font_style"][0]
        settings_view.selected_index = font_style_idx
        settings_view.handle_input("RIGHT")
        self.assertEqual(self.config.get("video", "font_style"), "hd")
        self.assertEqual(theme.font_style, "hd")

if __name__ == "__main__":
    unittest.main()
