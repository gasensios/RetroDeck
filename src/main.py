"""
RetroMultiSystem / RetroSNES - Linux Multi-System Retro Emulator (SNES & Sega Mega Drive).
Main entry point and application loop.
"""

import os
import sys
import pygame
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.config_manager import ConfigManager
from src.core.system_manager import SystemManager
from src.core.rom_manager import RomManager
from src.core.input_manager import InputManager
from src.core.sound_manager import SoundManager
from src.ui.retro_theme import RetroTheme, PALETTE
from src.ui.browser_view import BrowserView
from src.ui.controls_view import ControlsView
from src.ui.settings_view import SettingsView
from src.ui.help_view import HelpView
from src.ui.gameplay_view import GameplayView
from src.ui.game_menu_view import GameMenuView

class RetroApp:
    def __init__(self):
        # 1. Initialize Pygame
        pygame.init()
        pygame.font.init()

        # 2. Managers
        self.config = ConfigManager()
        
        # Audio
        sfx_enabled = self.config.get("audio", "sound_effects_enabled", default=True)
        vol = self.config.get("audio", "volume", default=0.8)
        self.sound = SoundManager(enabled=sfx_enabled, volume=vol)

        # Assets & Theme
        assets_dir = PROJECT_ROOT / "assets"
        self.theme = RetroTheme(assets_dir)

        # Systems & ROMs
        self.sys_mgr = SystemManager(PROJECT_ROOT, active_system_id="snes")
        config_dir = Path(self.config.config_dir)
        self.rom_mgr = RomManager(config_dir)
        self.rom_mgr.scan_system(self.sys_mgr.get_active_system())

        self.input_mgr = InputManager(self.config)

        # 3. Views
        self.browser_view = BrowserView(self.theme, self.sound, self.rom_mgr, self.sys_mgr)
        self.controls_view = ControlsView(self.theme, self.sound, self.input_mgr, self.config)
        self.settings_view = SettingsView(self.theme, self.sound, self.config, self.rom_mgr, None, self.sys_mgr)
        self.help_view = HelpView(self.theme, self.sound)
        self.gameplay_view = GameplayView(self.theme, self.config, self.input_mgr, self.sound)
        self.game_menu_view = GameMenuView(self.theme, self.sound, self.rom_mgr, self.config)

        # State: 'BROWSER', 'CONTROLS', 'SETTINGS', 'HELP', 'GAMEPLAY', 'GAME_MENU'
        self.current_state = "BROWSER"

        # 4. Display Window
        self.width = self.config.get("video", "width", default=1024)
        self.height = self.config.get("video", "height", default=720)
        self.fullscreen = self.config.get("video", "fullscreen", default=False)
        self.clock = pygame.time.Clock()
        self.running = True

        self._setup_display()

    def _setup_display(self):
        flags = pygame.RESIZABLE
        if self.fullscreen:
            flags |= pygame.FULLSCREEN
        
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        pygame.display.set_caption("RetroDeck - Multi-System Retro Station (SNES & Mega Drive)")

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.config.set("video", "fullscreen", self.fullscreen)
        self._setup_display()

    def run(self):
        while self.running:
            # 1. Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.current_state == "GAMEPLAY":
                        self.gameplay_view.stop_game()
                    self.running = False
                    break

                elif event.type == pygame.VIDEORESIZE:
                    self.width, self.height = event.w, event.h
                    self.config.set("video", "width", self.width)
                    self.config.set("video", "height", self.height)
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                    continue

                # Delegate to GAMEPLAY view if running
                if self.current_state == "GAMEPLAY":
                    res = self.gameplay_view.handle_event(event)
                    if res == "EXIT_TO_MENU":
                        self.current_state = "BROWSER"
                        self.rom_mgr.scan_system(self.sys_mgr.get_active_system())
                    continue

                # Pass to active view or input manager
                if self.current_state == "CONTROLS":
                    if self.controls_view.waiting_input:
                        res = self.input_mgr.process_event(event, system_id=self.controls_view.current_system)
                        self.controls_view.handle_input(res, raw_event=event)
                        continue
                    elif event.type == pygame.KEYDOWN and event.key in (pygame.K_TAB, pygame.K_t):
                        self.controls_view.toggle_system()
                        continue
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.controls_view.handle_mouse_click(event.pos)
                        continue

                elif self.current_state == "GAME_MENU":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        res = self.game_menu_view.handle_mouse_click(event.pos)
                        if res == "LAUNCH_GAME":
                            self._launch_rom(self.game_menu_view.rom)
                        elif res == "BACK_TO_BROWSER":
                            self.current_state = "BROWSER"
                        continue

                # Global Quick Keys & Mouse in Browser
                if self.current_state == "BROWSER":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        res = self.browser_view.handle_mouse_click(event.pos)
                        if res == "LAUNCH_GAME":
                            selected_rom = self.browser_view.get_selected_rom()
                            if selected_rom:
                                self._launch_rom(selected_rom)
                        continue
                    elif event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_TAB, pygame.K_t):
                            self.browser_view.switch_system()
                            continue
                        elif event.key in (pygame.K_m, pygame.K_o):
                            selected = self.browser_view.get_selected_rom()
                            if selected:
                                self.game_menu_view.set_rom(selected, self.sys_mgr.get_active_system())
                                self.current_state = "GAME_MENU"
                                self.sound.play("select")
                                continue
                        elif event.key == pygame.K_c:
                            self.current_state = "CONTROLS"
                            active_sys = self.sys_mgr.get_active_system()
                            if active_sys:
                                self.controls_view.set_system(active_sys.id)
                            self.sound.play("select")
                            continue
                        elif event.key == pygame.K_s:
                            self.current_state = "SETTINGS"
                            self.sound.play("select")
                            continue
                        elif event.key in (pygame.K_h, pygame.K_F1):
                            self.current_state = "HELP"
                            self.sound.play("select")
                            continue

                # Virtual action translation
                current_sys_id = self.controls_view.current_system if self.current_state == "CONTROLS" else self.sys_mgr.get_active_system().id
                action = self.input_mgr.process_event(event, system_id=current_sys_id)
                if action:
                    self._handle_action(action)

            # 2. Rendering & Frame Updates
            if self.current_state == "GAMEPLAY":
                self.gameplay_view.update_frame()
                self.gameplay_view.draw(self.screen)
            else:
                active_sys_id = self.controls_view.current_system if self.current_state == "CONTROLS" else self.sys_mgr.get_active_system().id
                self.theme.draw_animated_retro_bg(self.screen, active_sys_id, pygame.time.get_ticks())

                if self.current_state == "BROWSER":
                    self.browser_view.draw(self.screen)
                elif self.current_state == "CONTROLS":
                    self.controls_view.draw(self.screen)
                elif self.current_state == "SETTINGS":
                    self.settings_view.draw(self.screen)
                elif self.current_state == "HELP":
                    self.help_view.draw(self.screen)
                elif self.current_state == "GAME_MENU":
                    self.game_menu_view.draw(self.screen)

            # Optional CRT Scanlines Filter Overlay
            if self.config.get("video", "crt_filter", default=True):
                intensity = self.config.get("video", "crt_scanline_intensity", default=45)
                self.theme.draw_scanlines(self.screen, intensity)

            pygame.display.flip()
            self.clock.tick(self.config.get("video", "fps_target", default=60))

        if self.current_state == "GAMEPLAY":
            self.gameplay_view.stop_game()

        pygame.quit()

    def _handle_action(self, action: str):
        if self.current_state == "BROWSER":
            if action == "MENU": # Escape
                self.running = False
                return

            # Shoulder buttons L/R switch system in browser
            if action in ("L", "R"):
                self.browser_view.switch_system()
                return

            res = self.browser_view.handle_input(action)
            if res == "LAUNCH_GAME":
                selected_rom = self.browser_view.get_selected_rom()
                if selected_rom:
                    self._launch_rom(selected_rom)
            elif res == "OPEN_GAME_MENU":
                selected_rom = self.browser_view.get_selected_rom()
                if selected_rom:
                    self.game_menu_view.set_rom(selected_rom, self.sys_mgr.get_active_system())
                    self.current_state = "GAME_MENU"

        elif self.current_state == "GAME_MENU":
            res = self.game_menu_view.handle_input(action)
            if res == "LAUNCH_GAME":
                self._launch_rom(self.game_menu_view.rom)
            elif res == "BACK_TO_BROWSER":
                self.current_state = "BROWSER"

        elif self.current_state == "CONTROLS":
            res = self.controls_view.handle_input(action)
            if res == "BACK_TO_BROWSER":
                self.current_state = "BROWSER"

        elif self.current_state == "SETTINGS":
            res = self.settings_view.handle_input(action)
            if res == "BACK_TO_BROWSER":
                self.current_state = "BROWSER"

        elif self.current_state == "HELP":
            res = self.help_view.handle_input(action)
            if res == "BACK_TO_BROWSER":
                self.current_state = "BROWSER"

    def _launch_rom(self, rom):
        print(f"[RetroApp] Starting {rom.title} on {rom.system_id.upper()}...")
        if self.config.get("emulator", "fullscreen_on_launch", default=True) and not self.fullscreen:
            self.toggle_fullscreen()
        
        success = self.gameplay_view.start_game(rom)
        if success:
            self.current_state = "GAMEPLAY"
        else:
            print("[RetroApp] Error launching ROM in gameplay view.")


if __name__ == "__main__":
    app = RetroApp()
    app.run()
