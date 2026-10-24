"""
Multi-System Game Browser View for RetroDeck.
Displays 80s/90s arcade marquee, ROM list with pulsing cursors, cartridge bay, and tech specs.
"""

import pygame
import math
from pathlib import Path
from typing import Optional
from src.ui.retro_theme import PALETTE

class BrowserView:
    def __init__(self, theme, sound_manager, rom_manager, system_manager):
        self.theme = theme
        self.sound = sound_manager
        self.rom_mgr = rom_manager
        self.sys_mgr = system_manager
        
        self.selected_index = 0
        self.scroll_offset = 0
        self.boxart_cache = {}

        # Interactive Click Rectangles
        self.snes_tab_rect = pygame.Rect(0, 0, 0, 0)
        self.md_tab_rect = pygame.Rect(0, 0, 0, 0)
        self.launch_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.item_rects = []

        self.notification_msg = ""
        self.notification_timer = 0

    def notify(self, msg: str, duration: int = 150):
        self.notification_msg = msg
        self.notification_timer = duration

    def get_selected_rom(self):
        if not self.rom_mgr.roms:
            return None
        self.selected_index = max(0, min(len(self.rom_mgr.roms) - 1, self.selected_index))
        return self.rom_mgr.roms[self.selected_index]

    def switch_system(self):
        new_sys = self.sys_mgr.next_system()
        self.rom_mgr.scan_system(new_sys)
        self.selected_index = 0
        self.scroll_offset = 0
        self.sound.play("launch")

    def handle_mouse_click(self, pos) -> Optional[str]:
        # Click System Switcher
        if self.snes_tab_rect.collidepoint(pos) and self.sys_mgr.get_active_system().id != "snes":
            self.switch_system()
            return None
        elif self.md_tab_rect.collidepoint(pos) and self.sys_mgr.get_active_system().id != "megadrive":
            self.switch_system()
            return None

        # Click Launch Button
        if self.launch_btn_rect.collidepoint(pos):
            return self.handle_input("A")

        # Click on ROM list item
        for idx, rect in enumerate(self.item_rects):
            if rect.collidepoint(pos):
                actual_idx = self.scroll_offset + idx
                if actual_idx < len(self.rom_mgr.roms):
                    if self.selected_index == actual_idx:
                        return self.handle_input("A")
                    else:
                        self.selected_index = actual_idx
                        self.sound.play("nav")
                return None

        return None

    def handle_input(self, action: str) -> Optional[str]:
        if action == "SWITCH_SYSTEM":
            self.switch_system()
            return None

        num_roms = len(self.rom_mgr.roms)
        if num_roms == 0:
            if action in ("A", "START"):
                self.rom_mgr.scan_system(self.sys_mgr.get_active_system())
                self.sound.play("select")
            return None

        if action == "UP":
            if self.selected_index > 0:
                self.selected_index -= 1
            else:
                self.selected_index = num_roms - 1
            self.sound.play("nav")

        elif action == "DOWN":
            if self.selected_index < num_roms - 1:
                self.selected_index += 1
            else:
                self.selected_index = 0
            self.sound.play("nav")

        elif action == "LEFT":
            self.selected_index = max(0, self.selected_index - 5)
            self.sound.play("nav")

        elif action == "RIGHT":
            self.selected_index = min(num_roms - 1, self.selected_index + 5)
            self.sound.play("nav")

        elif action in ("A", "START"):
            rom = self.get_selected_rom()
            if rom:
                self.sound.play("launch")
                self.rom_mgr.update_rom_stats(rom)
                return "LAUNCH_GAME"

        elif action == "Y":
            rom = self.get_selected_rom()
            if rom:
                self.rom_mgr.toggle_favorite(rom)
                self.sound.play("select")

        elif action == "X":
            if self.get_selected_rom():
                self.sound.play("select")
                return "OPEN_GAME_MENU"

        return None

    def draw(self, surface: pygame.Surface):
        w, h = surface.get_size()
        active_sys = self.sys_mgr.get_active_system()
        roms = self.rom_mgr.roms
        num_roms = len(roms)

        # 1. Top Arcade Marquee Header Bar
        header_h = 62
        header_rect = pygame.Rect(16, 10, w - 32, header_h)
        self.theme.draw_retro_box(surface, header_rect, bg_color=(22, 20, 32), with_screws=True)

        # Draw Brand Badge on Left
        badge_x = header_rect.x + 14
        badge_y = header_rect.y + 15
        if active_sys.id == "snes":
            self.theme.draw_snes_badge(surface, badge_x, badge_y)
        else:
            self.theme.draw_megadrive_badge(surface, badge_x, badge_y)

        # Station Title & Marquee in Center
        title_x = badge_x + 115
        station_title = self.theme.render_text("RETRODECK ARCADE STATION", 11, PALETTE["gold_highlight"], (0, 0, 0))
        surface.blit(station_title, (title_x, header_rect.y + 12))

        # Hardware Glowing LED Indicators
        led_y = header_rect.y + 40
        self.theme.draw_led(surface, title_x + 6, led_y, "POWER", is_on=True, color="green")
        self.theme.draw_led(surface, title_x + 95, led_y, "60Hz NTSC", is_on=True, color="green")
        self.theme.draw_led(surface, title_x + 205, led_y, "16-BIT STEREO", is_on=True, color="green")

        # Right Side: Interactive System Tabs [★ SNES] [★ MEGADRIVE]
        snes_active = (active_sys.id == "snes")
        tab_w = 125
        tab_h = 32
        tab_y = header_rect.y + 15

        self.snes_tab_rect = pygame.Rect(header_rect.right - (tab_w * 2) - 20, tab_y, tab_w, tab_h)
        self.md_tab_rect = pygame.Rect(header_rect.right - tab_w - 10, tab_y, tab_w, tab_h)

        self.theme.draw_retro_box(surface, self.snes_tab_rect,
                                  bg_color=(45, 40, 65) if snes_active else (28, 25, 40),
                                  selected=snes_active, with_screws=False)
        self.theme.draw_retro_box(surface, self.md_tab_rect,
                                  bg_color=(45, 40, 65) if not snes_active else (28, 25, 40),
                                  selected=not snes_active, with_screws=False)

        snes_col = PALETTE["gold_highlight"] if snes_active else PALETTE["text_gray"]
        md_col = PALETTE["gold_highlight"] if not snes_active else PALETTE["text_gray"]
        snes_lbl = self.theme.render_text("* SNES", 8, snes_col)
        md_lbl = self.theme.render_text("* MEGADRIVE", 8, md_col)

        surface.blit(snes_lbl, (self.snes_tab_rect.x + (tab_w - snes_lbl.get_width()) // 2, self.snes_tab_rect.y + 10))
        surface.blit(md_lbl, (self.md_tab_rect.x + (tab_w - md_lbl.get_width()) // 2, self.md_tab_rect.y + 10))

        # 2. Main Layout Split
        margin = 16
        main_y = header_rect.bottom + 8
        main_h = h - main_y - 48

        list_w = int((w - margin * 3) * 0.46)
        details_w = (w - margin * 3) - list_w

        list_rect = pygame.Rect(margin, main_y, list_w, main_h)
        details_rect = pygame.Rect(list_rect.right + margin, main_y, details_w, main_h)

        # Draw Left Panel (ROM List)
        self.theme.draw_retro_box(surface, list_rect, bg_color=(20, 18, 30), with_screws=True)
        self._draw_rom_list(surface, list_rect, roms, active_sys)

        # Draw Right Panel (Cartridge Bay & Specifications)
        self.theme.draw_retro_box(surface, details_rect, bg_color=(20, 18, 30), with_screws=True)
        self._draw_rom_details(surface, details_rect, self.get_selected_rom(), active_sys)

        # 3. Bottom Footer Bar (Arcade Legend)
        footer_rect = pygame.Rect(16, h - 36, w - 32, 28)
        self.theme.draw_retro_box(surface, footer_rect, bg_color=(18, 16, 26), with_screws=False)
        self._draw_footer(surface, footer_rect)

        # 4. Global Notification Toast
        if self.notification_timer > 0:
            self.notification_timer -= 1
            toast_w = min(w - 60, 640)
            toast_rect = pygame.Rect((w - toast_w) // 2, h - 90, toast_w, 40)
            self.theme.draw_retro_box(surface, toast_rect, bg_color=(180, 20, 20), selected=True, with_screws=False)
            toast_txt = self.theme.render_text(self.notification_msg, 9, PALETTE["text_white"], (0, 0, 0))
            surface.blit(toast_txt, (toast_rect.x + (toast_rect.width - toast_txt.get_width()) // 2, toast_rect.y + 13))

    def _draw_rom_list(self, surface: pygame.Surface, rect: pygame.Rect, roms, active_sys):
        # Section Header Plate
        header_strip = pygame.Rect(rect.x + 8, rect.y + 8, rect.width - 16, 26)
        pygame.draw.rect(surface, (32, 30, 46), header_strip, border_radius=3)
        h_title = self.theme.render_text(f":: CATALOGO DE CARTUCHOS [{len(roms)}] ::", 8, active_sys.badge_color)
        surface.blit(h_title, (header_strip.x + (header_strip.width - h_title.get_width()) // 2, header_strip.y + 8))

        if not roms:
            msg1 = self.theme.render_text("SIN JUEGOS ENCONTRADOS", 9, active_sys.badge_color)
            msg2 = self.theme.render_text("Copia tus ROMs a la carpeta:", 7, PALETTE["text_gray"])
            msg3 = self.theme.render_text(f"roms/{active_sys.id}/", 8, PALETTE["gold_highlight"])
            msg4 = self.theme.render_text("Pulsa [A] para reescanear", 7, PALETTE["text_white"])
            
            cy = rect.y + rect.height // 2 - 35
            surface.blit(msg1, (rect.x + (rect.width - msg1.get_width()) // 2, cy))
            surface.blit(msg2, (rect.x + (rect.width - msg2.get_width()) // 2, cy + 22))
            surface.blit(msg3, (rect.x + (rect.width - msg3.get_width()) // 2, cy + 40))
            surface.blit(msg4, (rect.x + (rect.width - msg4.get_width()) // 2, cy + 62))
            return

        item_height = 42
        list_top = header_strip.bottom + 8
        visible_items = max(1, (rect.bottom - list_top - 12) // item_height)
        
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + visible_items:
            self.scroll_offset = self.selected_index - visible_items + 1

        start_idx = self.scroll_offset
        end_idx = min(len(roms), start_idx + visible_items)

        ticks = pygame.time.get_ticks()
        bob = int(math.sin(ticks * 0.012) * 2.5) # Bobbing cursor

        self.item_rects = []
        for i in range(start_idx, end_idx):
            rom = roms[i]
            is_selected = (i == self.selected_index)
            item_y = list_top + (i - start_idx) * item_height
            item_rect = pygame.Rect(rect.x + 8, item_y, rect.width - 16, item_height - 4)
            self.item_rects.append(item_rect)

            row_bg = PALETTE["bg_card_selected"] if is_selected else (28, 26, 40)
            self.theme.draw_retro_box(surface, item_rect, bg_color=row_bg, selected=is_selected, with_screws=False)

            # Pulsing Animated Retro Cursor on Selected
            text_x = item_rect.x + 10
            if is_selected:
                self.theme.draw_pointer(surface, item_rect.x + 6 + bob, item_rect.y + 15)
                text_x += 16

            # Favorite Star Indicator
            if rom.is_favorite:
                self.theme.draw_star(surface, text_x + 5, item_rect.y + 20, radius=5)
                text_x += 16

            # Game Title
            max_chars = max(12, int((item_rect.width - (text_x - item_rect.x) - 55) / 8.5))
            disp_title = rom.title
            if len(disp_title) > max_chars:
                disp_title = disp_title[:max_chars - 2] + ".."

            text_col = PALETTE["text_white"] if not is_selected else PALETTE["gold_highlight"]
            txt_surf = self.theme.render_text(disp_title, 8, text_col, shadow_color=(0, 0, 0) if is_selected else None)
            surface.blit(txt_surf, (text_x, item_rect.y + 14))

            # Region / Type Tag Badge
            tag_text = rom.region if rom.region != "Unknown" else rom.rom_type
            if tag_text:
                tag_surf = self.theme.render_text(tag_text[:7].upper(), 7, active_sys.accent_color)
                tag_badge_w = tag_surf.get_width() + 8
                tag_rect = pygame.Rect(item_rect.right - tag_badge_w - 6, item_rect.y + 12, tag_badge_w, 16)
                pygame.draw.rect(surface, (20, 20, 28), tag_rect, border_radius=2)
                pygame.draw.rect(surface, (45, 48, 62), tag_rect, width=1, border_radius=2)
                surface.blit(tag_surf, (tag_rect.x + 4, tag_rect.y + 3))

    def _draw_rom_details(self, surface: pygame.Surface, rect: pygame.Rect, rom, active_sys):
        # Section Header Plate
        header_strip = pygame.Rect(rect.x + 8, rect.y + 8, rect.width - 16, 26)
        pygame.draw.rect(surface, (32, 30, 46), header_strip, border_radius=3)
        h_title = self.theme.render_text(":: CARTRIDGE BAY & TECH SPECS ::", 8, active_sys.badge_color)
        surface.blit(h_title, (header_strip.x + (header_strip.width - h_title.get_width()) // 2, header_strip.y + 8))

        if not rom:
            placeholder = self.theme.render_text(f"RANURA DE CARTUCHO VACÍA", 8, PALETTE["text_gray"])
            surface.blit(placeholder, (rect.x + (rect.width - placeholder.get_width()) // 2, rect.y + rect.height // 2))
            return

        inner_x = rect.x + 16
        inner_y = header_strip.bottom + 8
        inner_w = rect.width - 32

        # 1. Backlit Cartridge Bay Pedestal
        box_area_h = min(210, int(rect.height * 0.42))
        bay_rect = pygame.Rect(inner_x, inner_y, inner_w, box_area_h)
        
        # Soft glowing backlight behind cartridge
        backlight_col = (70, 30, 90, 80) if active_sys.id == "snes" else (20, 50, 110, 80)
        backlight_surf = pygame.Surface((bay_rect.width, bay_rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(backlight_surf, backlight_col, (10, 10, bay_rect.width - 20, bay_rect.height - 20))
        surface.blit(backlight_surf, (bay_rect.x, bay_rect.y))

        # Retrieve Boxart image if available
        box_image = None
        if rom.boxart_path and rom.boxart_path.exists():
            str_path = str(rom.boxart_path)
            if str_path not in self.boxart_cache:
                try:
                    loaded = pygame.image.load(str_path).convert_alpha()
                    self.boxart_cache[str_path] = loaded
                except Exception:
                    self.boxart_cache[str_path] = None
            box_image = self.boxart_cache.get(str_path)

        cart_w = min(bay_rect.width - 24, 275)
        cart_h = box_area_h - 14
        cart_rect = pygame.Rect(
            bay_rect.x + (bay_rect.width - cart_w) // 2,
            bay_rect.y + 6,
            cart_w,
            cart_h
        )
        self.theme.draw_cartridge(surface, cart_rect, system_id=active_sys.id, title=rom.title, custom_image=box_image)

        # 2. Game Title Plate
        curr_y = bay_rect.bottom + 10
        title_surf = self.theme.render_text(rom.title, 11, active_sys.badge_color, (0, 0, 0))
        surface.blit(title_surf, (inner_x, curr_y))

        curr_y += title_surf.get_height() + 6
        pygame.draw.line(surface, active_sys.theme_color, (inner_x, curr_y), (rect.right - 16, curr_y), 2)
        curr_y += 10

        # 3. Technical Specifications Table
        specs_box = pygame.Rect(inner_x, curr_y, inner_w, rect.bottom - curr_y - 52)
        pygame.draw.rect(surface, (24, 22, 34), specs_box, border_radius=4)
        pygame.draw.rect(surface, (45, 42, 60), specs_box, width=1, border_radius=4)

        meta_items = [
            ("SISTEMA:", active_sys.full_name),
            ("ARCHIVO:", rom.filename),
            ("TAMAÑO:", rom.get_formatted_size()),
            ("FORMATO:", rom.rom_type),
            ("REGIÓN:", rom.region),
            ("PARTIDAS:", f"{rom.play_count} partidas jugadas"),
            ("ÚLTIMA VEZ:", rom.last_played if rom.last_played else "Sin iniciar"),
            ("FAVORITO:", "* Si (Destacado)" if rom.is_favorite else "No"),
        ]

        row_y = specs_box.y + 8
        for label, val in meta_items:
            lbl_surf = self.theme.render_text(label, 7, active_sys.accent_color)
            val_surf = self.theme.render_text(val, 7, PALETTE["text_white"])
            surface.blit(lbl_surf, (specs_box.x + 10, row_y))
            surface.blit(val_surf, (specs_box.x + 95, row_y))
            row_y += 17
            if row_y >= specs_box.bottom - 12:
                break

        # 4. Big Arcade Launch Button (Pulsing Neon Border)
        btn_h = 34
        self.launch_btn_rect = pygame.Rect(inner_x, rect.bottom - btn_h - 10, inner_w, btn_h)
        btn_bg = PALETTE["btn_a_red"] if active_sys.id == "snes" else PALETTE["sega_blue"]
        self.theme.draw_retro_box(surface, self.launch_btn_rect, bg_color=btn_bg, selected=True, with_screws=False)
        
        short_name = getattr(active_sys, "short", getattr(active_sys, "name", "SISTEMA")).upper()
        btn_txt = self.theme.render_text(f">> INICIAR EN {short_name} [A / ENTER] <<", 8, PALETTE["text_white"], (0, 0, 0))
        surface.blit(btn_txt, (self.launch_btn_rect.x + (self.launch_btn_rect.width - btn_txt.get_width()) // 2, self.launch_btn_rect.y + 11))

    def _draw_footer(self, surface: pygame.Surface, rect: pygame.Rect):
        guide = "[A/ENTER] JUGAR   [X / M] MENU JUEGO   [TAB] CONSOLA   [Y] FAVORITO   [C] CONTROLES   [S] AJUSTES   [ESC] SALIR"
        guide_surf = self.theme.render_text(guide, 7, PALETTE["gold_highlight"])
        surface.blit(guide_surf, (rect.x + (rect.width - guide_surf.get_width()) // 2, rect.y + 8))
