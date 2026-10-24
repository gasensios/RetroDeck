"""
Gameplay View for RetroMultiSystem.
Runs SNES and Sega Mega Drive games directly using internal native cores.
Handles video, input, save states, SRAM saves, and in-game pause menu.
"""

import pygame
from pathlib import Path
from typing import Optional
from src.ui.retro_theme import PALETTE
from src.emulator_core.snes_player import SnesPlayer
from src.emulator_core.megadrive_player import MegaDrivePlayer
from src.core.platform_utils import get_core_library_path

class GameplayView:
    def __init__(self, theme, config_manager, input_manager, sound_manager):
        self.theme = theme
        self.config = config_manager
        self.input_mgr = input_manager
        self.sound = sound_manager
        
        project_root = Path(__file__).resolve().parent.parent.parent
        core_dir = project_root / "src" / "emulator_core"
        snes_lib = get_core_library_path(core_dir, "retrosnes")
        md_lib = get_core_library_path(core_dir, "megadrive_bridge")

        self.snes_player = SnesPlayer(snes_lib)
        self.md_player = MegaDrivePlayer(md_lib)
        self.current_player = None
        
        self.active_rom = None
        self.is_paused = False
        self.pause_selected_idx = 0
        self.pause_options = [
            "CONTINUAR",
            "GUARDAR ESTADO (F5)",
            "CARGAR ESTADO (F7)",
            "PANTALLA COMPLETA (F11)",
            "REINICIAR CONSOLA",
            "SALIR AL MENÚ PRINCIPAL"
        ]
        
        self.hud_message = ""
        self.hud_timer = 0

        # Emulator Audio Streaming
        self.audio_accumulator = bytearray()
        self.audio_chunk_size = 735 * 4 * 2  # 2 frames (5880 bytes ~ 33.3ms)
        self.emu_channel = None
        try:
            if pygame.mixer.get_init():
                self.emu_channel = pygame.mixer.Channel(0)
        except Exception:
            pass

    def start_game(self, rom_info) -> bool:
        self.active_rom = rom_info
        self.is_paused = False
        self.hud_message = ""
        self.hud_timer = 0
        self.audio_accumulator.clear()
        try:
            if pygame.mixer.get_init():
                if not self.emu_channel:
                    self.emu_channel = pygame.mixer.Channel(0)
                self.emu_channel.stop()
        except Exception:
            pass

        project_root = Path(__file__).resolve().parent.parent.parent
        saves_dir = project_root / "saves" / rom_info.system_id
        states_dir = project_root / "states" / rom_info.system_id
        saves_dir.mkdir(parents=True, exist_ok=True)
        states_dir.mkdir(parents=True, exist_ok=True)

        if rom_info.system_id == "megadrive":
            self.current_player = self.md_player
        else:
            self.current_player = self.snes_player

        if not self.current_player or not getattr(self.current_player, "is_available", False):
            sys_label = "Sega Mega Drive" if rom_info.system_id == "megadrive" else "Super Nintendo"
            dll_name = "libmegadrive_bridge.dll" if rom_info.system_id == "megadrive" else "libretrosnes.dll"
            self._notify(f"FALTA NÚCLEO NATIVO ({dll_name})", 180)
            print(f"[RetroDeck] Error: El núcleo para {sys_label} no está compilado ({dll_name}).")
            print("Para compilar en Windows ejecuta: windows\\compile_cores.bat")
            return False

        success = self.current_player.load_rom(rom_info.path, saves_dir, states_dir)
        if success:
            sys_name = "SEGA MEGA DRIVE" if rom_info.system_id == "megadrive" else "SUPER NINTENDO"
            self._notify(f"{sys_name} INICIADO - [ESC] MENÚ PAUSA", 180)
        return success

    def stop_game(self):
        if self.emu_channel:
            try:
                self.emu_channel.stop()
            except Exception:
                pass
        self.audio_accumulator.clear()
        if self.current_player and self.current_player.is_loaded:
            self.current_player.unload()
        self.active_rom = None
        self.current_player = None

    def _notify(self, msg: str, duration: int = 120):
        self.hud_message = msg
        self.hud_timer = duration

    def handle_event(self, event) -> Optional[str]:
        # Handle Global/System Keys
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F5:
                if self.current_player and self.current_player.save_state():
                    self._notify("★ ESTADO GUARDADO (F5)", 120)
                    self.sound.play("select")
                return None
            elif event.key == pygame.K_F7:
                if self.current_player and self.current_player.load_state():
                    self._notify("⚡ ESTADO CARGADO (F7)", 120)
                    self.sound.play("select")
                else:
                    self._notify("NO HAY ESTADO GUARDADO", 120)
                return None
            elif event.key == pygame.K_ESCAPE:
                self.is_paused = not self.is_paused
                self.sound.play("select" if self.is_paused else "back")
                return None

        # IF IN PAUSE MENU
        if self.is_paused:
            return self._handle_pause_menu(event)

        # NORMAL GAMEPLAY: Update controller states
        self._update_controller_input(event)
        return None

    def _handle_pause_menu(self, event) -> Optional[str]:
        sys_id = self.active_rom.system_id if self.active_rom else "snes"
        action = self.input_mgr.process_event(event, system_id=sys_id)
        if not action:
            return None

        if action == "UP":
            self.pause_selected_idx = (self.pause_selected_idx - 1) % len(self.pause_options)
            self.sound.play("nav")
        elif action == "DOWN":
            self.pause_selected_idx = (self.pause_selected_idx + 1) % len(self.pause_options)
            self.sound.play("nav")
        elif action in ("A", "START"):
            idx = self.pause_selected_idx
            if idx == 0: # Continuar
                self.is_paused = False
                self.sound.play("select")
            elif idx == 1: # Guardar Estado
                if self.current_player and self.current_player.save_state():
                    self._notify("★ ESTADO GUARDADO", 120)
                    self.sound.play("select")
                self.is_paused = False
            elif idx == 2: # Cargar Estado
                if self.current_player and self.current_player.load_state():
                    self._notify("⚡ ESTADO CARGADO", 120)
                    self.sound.play("select")
                else:
                    self._notify("NO EXISTE ESTADO PREVIO", 120)
                self.is_paused = False
            elif idx == 3: # Pantalla Completa
                self.is_paused = False
                self.sound.play("select")
                return "TOGGLE_FULLSCREEN"
            elif idx == 4: # Reiniciar
                if self.current_player:
                    self.current_player.reset(hard=True)
                self._notify("CONSOLA REINICIADA", 120)
                self.is_paused = False
                self.sound.play("select")
            elif idx == 5: # Salir al Menú
                self.stop_game()
                self.sound.play("back")
                return "EXIT_TO_MENU"

        elif action in ("B", "MENU"):
            self.is_paused = False
            self.sound.play("back")

        return None

    def _update_controller_input(self, event):
        if not self.current_player or not self.current_player.is_loaded:
            return

        sys_id = self.active_rom.system_id if self.active_rom else "snes"

        # Keyboard press/release mapping
        if event.type in (pygame.KEYDOWN, pygame.KEYUP):
            pressed = (event.type == pygame.KEYDOWN)
            key_name = pygame.key.name(event.key).upper()
            kb_map = self.config.get_input_map(sys_id, "keyboard")

            for btn_key, mapped_k in kb_map.items():
                if key_name == str(mapped_k).upper():
                    self.current_player.set_button(1, btn_key, pressed)

        # Gamepad Button press/release
        elif event.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP):
            pressed = (event.type == pygame.JOYBUTTONDOWN)
            btn_idx = event.button
            gp_map = self.config.get_input_map(sys_id, "gamepad")

            for btn_key, mapped_idx in gp_map.items():
                if isinstance(mapped_idx, int) and mapped_idx == btn_idx:
                    self.current_player.set_button(1, btn_key, pressed)

        # D-pad Hat motion
        elif event.type == pygame.JOYHATMOTION:
            hat_x, hat_y = event.value
            self.current_player.set_button(1, "UP", hat_y == 1)
            self.current_player.set_button(1, "DOWN", hat_y == -1)
            self.current_player.set_button(1, "LEFT", hat_x == -1)
            self.current_player.set_button(1, "RIGHT", hat_x == 1)

        # Analog Stick
        elif event.type == pygame.JOYAXISMOTION:
            if event.axis == 1:
                self.current_player.set_button(1, "UP", event.value < -0.5)
                self.current_player.set_button(1, "DOWN", event.value > 0.5)
            elif event.axis == 0:
                self.current_player.set_button(1, "LEFT", event.value < -0.5)
                self.current_player.set_button(1, "RIGHT", event.value > 0.5)

    def update_frame(self):
        if not self.is_paused and self.current_player and self.current_player.is_loaded:
            # 1. Step hardware emulation frame with audio enabled
            self.current_player.step_frame(enable_audio=True)

            # 2. Stream audio to Pygame mixer if available
            if hasattr(self.current_player, "get_audio_bytes") and self.emu_channel:
                try:
                    raw_audio = self.current_player.get_audio_bytes()
                    if raw_audio and len(raw_audio) > 0:
                        self.audio_accumulator.extend(raw_audio)

                        if len(self.audio_accumulator) >= self.audio_chunk_size:
                            chunk = bytes(self.audio_accumulator[:self.audio_chunk_size])
                            self.audio_accumulator = self.audio_accumulator[self.audio_chunk_size:]

                            snd = pygame.mixer.Sound(buffer=chunk)
                            vol = self.config.get("audio", "volume", default=0.8)
                            snd.set_volume(vol)

                            if not self.emu_channel.get_busy():
                                self.emu_channel.play(snd)
                            elif not self.emu_channel.get_queue():
                                self.emu_channel.queue(snd)
                except Exception:
                    pass

    def draw(self, surface: pygame.Surface):
        w, h = surface.get_size()
        surface.fill((0, 0, 0))

        # 1. Render Framebuffer (preserving 4:3 Aspect Ratio)
        if self.current_player and self.current_player.is_loaded:
            frame_surf = self.current_player.get_surface()

            target_ratio = 4.0 / 3.0
            screen_ratio = w / h if h > 0 else target_ratio

            if screen_ratio > target_ratio:
                dest_h = h
                dest_w = int(h * target_ratio)
            else:
                dest_w = w
                dest_h = int(w / target_ratio)

            dest_x = (w - dest_w) // 2
            dest_y = (h - dest_h) // 2

            scaled_frame = pygame.transform.scale(frame_surf, (dest_w, dest_h))
            surface.blit(scaled_frame, (dest_x, dest_y))

        # 2. On-Screen HUD Notification
        if self.hud_timer > 0 and self.hud_message:
            self.hud_timer -= 1
            hud_surf = self.theme.render_text(self.hud_message, 9, PALETTE["gold_highlight"], (0, 0, 0))
            badge_rect = pygame.Rect(
                (w - hud_surf.get_width()) // 2 - 16,
                24,
                hud_surf.get_width() + 32,
                30
            )
            self.theme.draw_retro_box(surface, badge_rect, bg_color=(20, 18, 30))
            surface.blit(hud_surf, (badge_rect.x + 16, badge_rect.y + 8))

        # 3. Pause Menu Overlay
        if self.is_paused:
            self._draw_pause_overlay(surface, w, h)

    def _draw_pause_overlay(self, surface: pygame.Surface, w: int, h: int):
        dim_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        dim_surf.fill((10, 8, 16, 210))
        surface.blit(dim_surf, (0, 0))

        card_w = min(420, w - 40)
        card_h = 320
        card_x = (w - card_w) // 2
        card_y = (h - card_h) // 2
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        self.theme.draw_retro_box(surface, card_rect, bg_color=(25, 22, 38), selected=True)

        pause_txt = self.theme.render_text("PAUSA", 16, PALETTE["gold_highlight"], (0, 0, 0))
        surface.blit(pause_txt, (card_rect.x + (card_w - pause_txt.get_width()) // 2, card_rect.y + 20))

        if self.active_rom:
            sys_tag = "[SEGA MEGADRIVE]" if self.active_rom.system_id == "megadrive" else "[SUPER NINTENDO]"
            tag_surf = self.theme.render_text(sys_tag, 7, PALETTE["accent_lavender"])
            surface.blit(tag_surf, (card_rect.x + (card_w - tag_surf.get_width()) // 2, card_rect.y + 44))

            title_txt = self.theme.render_text(self.active_rom.title[:24], 8, PALETTE["text_white"])
            surface.blit(title_txt, (card_rect.x + (card_w - title_txt.get_width()) // 2, card_rect.y + 60))

        pygame.draw.line(surface, PALETTE["accent_purple"], (card_rect.x + 20, card_rect.y + 78), (card_rect.right - 20, card_rect.y + 78), 2)

        opt_y = card_rect.y + 90
        for i, opt in enumerate(self.pause_options):
            is_sel = (i == self.pause_selected_idx)
            row_rect = pygame.Rect(card_rect.x + 20, opt_y, card_w - 40, 32)

            row_bg = PALETTE["bg_card_selected"] if is_sel else (32, 30, 48)
            self.theme.draw_retro_box(surface, row_rect, bg_color=row_bg, selected=is_sel)

            prefix = "> " if is_sel else "  "
            col = PALETTE["gold_highlight"] if is_sel else PALETTE["text_white"]
            txt = self.theme.render_text(f"{prefix}{opt}", 8, col)
            surface.blit(txt, (row_rect.x + 12, row_rect.y + (row_rect.height - txt.get_height()) // 2))

            opt_y += 38

        tip = self.theme.render_text("[F5] GUARDAR   [F7] CARGAR   [ESC] REANUDAR", 7, PALETTE["text_gray"])
        surface.blit(tip, (card_rect.x + (card_w - tip.get_width()) // 2, card_rect.bottom - 20))
