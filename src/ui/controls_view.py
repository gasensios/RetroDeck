"""
Controls Configuration View for RetroDeck.
Allows per-system (SNES & Mega Drive) remapping of keyboard and gamepad buttons with visual feedback.
"""

import pygame
from typing import Optional
from src.ui.retro_theme import PALETTE
from src.core.input_manager import get_system_buttons
from src.core.config_manager import DEFAULT_CONFIG

class ControlsView:
    def __init__(self, theme, sound_manager, input_manager, config_manager):
        self.theme = theme
        self.sound = sound_manager
        self.input_mgr = input_manager
        self.config = config_manager
        
        self.current_system = "snes" # 'snes' or 'megadrive'
        self.selected_index = 0
        self.current_tab = "keyboard" # 'keyboard' or 'gamepad'
        self.waiting_input = False
        self.waiting_btn_key = None

        # Interactive UI Rectangles for Mouse Clicks
        self.snes_tab_rect = pygame.Rect(0, 0, 0, 0)
        self.md_tab_rect = pygame.Rect(0, 0, 0, 0)
        self.kb_tab_rect = pygame.Rect(0, 0, 0, 0)
        self.gp_tab_rect = pygame.Rect(0, 0, 0, 0)
        self.button_row_rects = []

    def set_system(self, system_id: str):
        if system_id in ("snes", "megadrive"):
            self.current_system = system_id
            self.selected_index = 0
            self.waiting_input = False
            self.waiting_btn_key = None

    def toggle_system(self):
        self.current_system = "megadrive" if self.current_system == "snes" else "snes"
        self.selected_index = 0
        self.waiting_input = False
        self.waiting_btn_key = None
        self.sound.play("nav")

    def handle_mouse_click(self, pos) -> Optional[str]:
        if self.waiting_input:
            return None

        # Click Console Tabs
        if self.snes_tab_rect.collidepoint(pos) and self.current_system != "snes":
            self.set_system("snes")
            self.sound.play("nav")
            return None
        elif self.md_tab_rect.collidepoint(pos) and self.current_system != "megadrive":
            self.set_system("megadrive")
            self.sound.play("nav")
            return None

        # Click Input Device Tabs
        if self.kb_tab_rect.collidepoint(pos) and self.current_tab != "keyboard":
            self.current_tab = "keyboard"
            self.sound.play("nav")
            return None
        elif self.gp_tab_rect.collidepoint(pos) and self.current_tab != "gamepad":
            self.current_tab = "gamepad"
            self.sound.play("nav")
            return None

        # Click on Button List Row
        for idx, rect in enumerate(self.button_row_rects):
            if rect.collidepoint(pos):
                if self.selected_index == idx:
                    # Double click / click on already selected starts remap
                    return self.handle_input("A")
                else:
                    self.selected_index = idx
                    self.sound.play("nav")
                return None

        return None

    def handle_input(self, action: str, raw_event=None) -> Optional[str]:
        # If currently waiting for a button press, input_manager handles remapping
        if self.waiting_input:
            if action == "MAPPED":
                self.waiting_input = False
                self.waiting_btn_key = None
                self.sound.play("select")
                return None
            elif action == "CANCEL":
                self.waiting_input = False
                self.waiting_btn_key = None
                self.sound.play("back")
                return None
            return None

        # System Switching via Shoulders
        if action in ("L", "R"):
            self.toggle_system()
            return None

        # Input Type Switching (Keyboard / Gamepad)
        if action in ("LEFT", "RIGHT"):
            self.current_tab = "gamepad" if self.current_tab == "keyboard" else "keyboard"
            self.sound.play("nav")
            return None

        # Navigation in buttons list
        buttons = get_system_buttons(self.current_system)
        num_buttons = len(buttons)

        if action == "UP":
            if self.selected_index > 0:
                self.selected_index -= 1
            else:
                self.selected_index = num_buttons - 1
            self.sound.play("nav")

        elif action == "DOWN":
            if self.selected_index < num_buttons - 1:
                self.selected_index += 1
            else:
                self.selected_index = 0
            self.sound.play("nav")

        elif action in ("A", "START"):
            # Start remapping selected button
            if 0 <= self.selected_index < len(buttons):
                target_key, _ = buttons[self.selected_index]
                self.waiting_input = True
                self.waiting_btn_key = target_key
                self.sound.play("select")
                self.input_mgr.start_remap(self.current_system, self.current_tab, target_key, self._on_remapped)

        elif action in ("B", "MENU"):
            self.sound.play("back")
            return "BACK_TO_BROWSER"

        elif action == "X":
            # Reset defaults for active system and active device
            self._reset_defaults()
            self.sound.play("select")

        return None

    def _on_remapped(self, btn, val):
        self.waiting_input = False
        self.waiting_btn_key = None

    def _reset_defaults(self):
        def_map = DEFAULT_CONFIG["input"].get(self.current_system, {}).get(self.current_tab, {})
        self.config.set("input", self.current_system, self.current_tab, def_map)

    def draw(self, surface: pygame.Surface):
        w, h = surface.get_size()

        # Top Header (with console switcher and active device)
        header_rect = pygame.Rect(16, 10, w - 32, 54)
        self.theme.draw_retro_box(surface, header_rect, bg_color=(25, 22, 38))
        
        title = self.theme.render_text("CONFIGURACIÓN DE CONTROLES", 13, PALETTE["gold_highlight"], (0, 0, 0))
        surface.blit(title, (header_rect.x + 16, header_rect.y + 10))
        
        detected_pad = self.input_mgr.get_controller_name()
        sub = self.theme.render_text(f"DISPOSITIVO: {detected_pad.upper()}", 8, PALETTE["accent_lavender"])
        surface.blit(sub, (header_rect.x + 16, header_rect.y + 32))

        # Console Selection Tabs (Top Right of Header)
        cs_tab_w = 140
        cs_tab_h = 32
        self.snes_tab_rect = pygame.Rect(header_rect.right - (cs_tab_w * 2 + 20), header_rect.y + 11, cs_tab_w, cs_tab_h)
        self.md_tab_rect = pygame.Rect(header_rect.right - cs_tab_w - 10, header_rect.y + 11, cs_tab_w, cs_tab_h)

        is_snes = (self.current_system == "snes")
        self.theme.draw_retro_box(surface, self.snes_tab_rect, selected=is_snes,
                                  bg_color=(50, 48, 70) if is_snes else (28, 25, 40))
        self.theme.draw_retro_box(surface, self.md_tab_rect, selected=not is_snes,
                                  bg_color=(50, 48, 70) if not is_snes else (28, 25, 40))

        snes_txt = self.theme.render_text("* SNES", 8, PALETTE["gold_highlight"] if is_snes else PALETTE["text_gray"])
        md_txt = self.theme.render_text("* MEGA DRIVE", 8, PALETTE["gold_highlight"] if not is_snes else PALETTE["text_gray"])
        surface.blit(snes_txt, (self.snes_tab_rect.x + (cs_tab_w - snes_txt.get_width()) // 2, self.snes_tab_rect.y + 9))
        surface.blit(md_txt, (self.md_tab_rect.x + (cs_tab_w - md_txt.get_width()) // 2, self.md_tab_rect.y + 9))

        # Main Layout
        main_y = header_rect.bottom + 8
        main_h = h - main_y - 52

        # Device Tabs: [:: TECLADO ::] | [:: GAMEPAD ::]
        tab_w = 170
        tab_h = 30
        self.kb_tab_rect = pygame.Rect(16, main_y, tab_w, tab_h)
        self.gp_tab_rect = pygame.Rect(16 + tab_w + 8, main_y, tab_w, tab_h)

        is_kb = (self.current_tab == "keyboard")
        self.theme.draw_retro_box(surface, self.kb_tab_rect, selected=is_kb,
                                  bg_color=PALETTE["bg_card_selected"] if is_kb else (30, 28, 42))
        self.theme.draw_retro_box(surface, self.gp_tab_rect, selected=not is_kb,
                                  bg_color=PALETTE["bg_card_selected"] if not is_kb else (30, 28, 42))

        kb_txt = self.theme.render_text(":: TECLADO ::", 8, PALETTE["gold_highlight"] if is_kb else PALETTE["text_gray"])
        gp_txt = self.theme.render_text(":: GAMEPAD ::", 8, PALETTE["gold_highlight"] if not is_kb else PALETTE["text_gray"])
        surface.blit(kb_txt, (self.kb_tab_rect.x + (tab_w - kb_txt.get_width()) // 2, self.kb_tab_rect.y + 8))
        surface.blit(gp_txt, (self.gp_tab_rect.x + (tab_w - gp_txt.get_width()) // 2, self.gp_tab_rect.y + 8))

        # Hint on the right of device tabs
        hint_sys = "[TAB / L / R]: CONSOLA    [< / >]: DISPOSITIVO"
        hint_surf = self.theme.render_text(hint_sys, 7, PALETTE["accent_lavender"])
        surface.blit(hint_surf, (w - hint_surf.get_width() - 20, main_y + 9))

        content_y = main_y + tab_h + 6
        content_h = main_h - tab_h - 6

        # Left Column: Buttons List (48% width)
        list_w = int((w - 48) * 0.48)
        list_rect = pygame.Rect(16, content_y, list_w, content_h)
        self.theme.draw_retro_box(surface, list_rect)

        # Right Column: Visual Controller Diagram & Mapping Status (52% width)
        diagram_w = (w - 48) - list_w
        diagram_rect = pygame.Rect(list_rect.right + 16, content_y, diagram_w, content_h)
        self.theme.draw_retro_box(surface, diagram_rect)

        # Draw Buttons List for Current System
        buttons = get_system_buttons(self.current_system)
        num_buttons = len(buttons)
        if self.selected_index >= num_buttons:
            self.selected_index = max(0, num_buttons - 1)

        item_h = max(22, int((content_h - 16) / num_buttons))
        curr_highlight_btn, _ = buttons[self.selected_index] if buttons else ("UP", "")

        self.button_row_rects = []
        for i, (btn_key, btn_desc) in enumerate(buttons):
            is_sel = (i == self.selected_index)
            row_y = list_rect.y + 8 + i * item_h
            row_rect = pygame.Rect(list_rect.x + 8, row_y, list_rect.width - 16, item_h - 3)
            self.button_row_rects.append(row_rect)

            row_bg = PALETTE["bg_card_selected"] if is_sel else (32, 30, 48)
            self.theme.draw_retro_box(surface, row_rect, bg_color=row_bg, selected=is_sel)

            # Button Description
            text_col = PALETTE["gold_highlight"] if is_sel else PALETTE["text_white"]
            desc_surf = self.theme.render_text(btn_desc, 8, text_col)
            surface.blit(desc_surf, (row_rect.x + 8, row_rect.y + (row_rect.height - desc_surf.get_height()) // 2))

            # Current Mapping
            if self.waiting_input and self.waiting_btn_key == btn_key:
                val_str = "PULSA BOTÓN..."
                val_col = PALETTE["btn_a_red"]
            else:
                val_str = self.input_mgr.get_button_label(self.current_system, self.current_tab, btn_key)
                val_col = PALETTE["accent_lavender"] if is_sel else PALETTE["text_gray"]

            val_surf = self.theme.render_text(val_str, 8, val_col)
            surface.blit(val_surf, (row_rect.right - val_surf.get_width() - 10, row_rect.y + (row_rect.height - val_surf.get_height()) // 2))

        # Draw Controller Diagram on the Right Panel
        active_btn_to_show = self.waiting_btn_key if self.waiting_input else curr_highlight_btn
        center_diagram_x = diagram_rect.x + diagram_rect.width // 2
        center_diagram_y = diagram_rect.y + 110

        if self.current_system == "megadrive":
            self.theme.draw_megadrive_controller_preview(
                surface,
                center_diagram_x,
                center_diagram_y,
                highlight_btn=active_btn_to_show
            )
        else:
            self.theme.draw_snes_controller_preview(
                surface,
                center_diagram_x,
                center_diagram_y,
                highlight_btn=active_btn_to_show
            )

        # Mapping status box below controller
        helper_y = diagram_rect.y + 205
        helper_rect = pygame.Rect(diagram_rect.x + 16, helper_y, diagram_rect.width - 32, diagram_rect.bottom - helper_y - 12)
        self.theme.draw_retro_box(surface, helper_rect, bg_color=(22, 20, 34))

        if self.waiting_input:
            sys_label = "SEGA MEGA DRIVE" if self.current_system == "megadrive" else "SUPER NINTENDO"
            msg_hdr = self.theme.render_text("ESPERANDO ENTRADA...", 10, PALETTE["gold_highlight"])
            msg_sub = self.theme.render_text(f"Asignando botón: {active_btn_to_show} ({sys_label})", 8, PALETTE["text_white"])
            msg_tip = self.theme.render_text("Presiona la tecla o botón deseado.", 7, PALETTE["accent_lavender"])
            msg_esc = self.theme.render_text("Pulsa [ESC] para cancelar", 7, PALETTE["text_gray"])

            surface.blit(msg_hdr, (helper_rect.x + (helper_rect.width - msg_hdr.get_width()) // 2, helper_rect.y + 14))
            surface.blit(msg_sub, (helper_rect.x + (helper_rect.width - msg_sub.get_width()) // 2, helper_rect.y + 36))
            surface.blit(msg_tip, (helper_rect.x + (helper_rect.width - msg_tip.get_width()) // 2, helper_rect.y + 56))
            surface.blit(msg_esc, (helper_rect.x + (helper_rect.width - msg_esc.get_width()) // 2, helper_rect.y + 76))
        else:
            info1 = self.theme.render_text("INSTRUCCIONES DE CONFIGURACION:", 8, PALETTE["gold_highlight"])
            info2 = self.theme.render_text("- [TAB / L / R]: Cambiar consola (SNES <-> MEGA DRIVE)", 7, PALETTE["text_white"])
            info3 = self.theme.render_text("- [ENTER / A]: Asignar tecla o boton seleccionado", 7, PALETTE["text_white"])
            info4 = self.theme.render_text("- [< / >]: Alternar entre Teclado y Mando USB", 7, PALETTE["text_white"])
            
            if self.current_system == "megadrive":
                info5 = self.theme.render_text("- Mega Drive: A, B, C (fila inf.) | X, Y, Z (fila sup. 6 botones)", 7, PALETTE["accent_lavender"])
            else:
                info5 = self.theme.render_text("- SNES: Disposicion clasica en rombo B, A, Y, X + Gatillos L/R", 7, PALETTE["accent_lavender"])

            surface.blit(info1, (helper_rect.x + 16, helper_rect.y + 12))
            surface.blit(info2, (helper_rect.x + 16, helper_rect.y + 32))
            surface.blit(info3, (helper_rect.x + 16, helper_rect.y + 50))
            surface.blit(info4, (helper_rect.x + 16, helper_rect.y + 68))
            surface.blit(info5, (helper_rect.x + 16, helper_rect.y + 86))

        # Bottom Footer
        footer_rect = pygame.Rect(16, h - 38, w - 32, 28)
        self.theme.draw_retro_box(surface, footer_rect, bg_color=(20, 18, 30))
        f_txt = "[TAB] CONSOLA   [A / ENTER] ASIGNAR   [X] DEFECTO   [< / >] DISPOSITIVO   [B / ESC] VOLVER"
        f_surf = self.theme.render_text(f_txt, 7, PALETTE["gold_highlight"])
        surface.blit(f_surf, (footer_rect.x + (footer_rect.width - f_surf.get_width()) // 2, footer_rect.y + 8))
