"""
Help and Quick Guide View for RetroSNES.
Explains folders, ROM loading, and shortcuts.
"""

import pygame
from typing import Optional
from src.ui.retro_theme import PALETTE

class HelpView:
    def __init__(self, theme, sound_manager):
        self.theme = theme
        self.sound = sound_manager

    def handle_input(self, action: str) -> Optional[str]:
        if action in ["A", "B", "START", "MENU"]:
            self.sound.play("back")
            return "BACK_TO_BROWSER"
        return None

    def draw(self, surface: pygame.Surface):
        w, h = surface.get_size()

        # Header
        header_rect = pygame.Rect(16, 12, w - 32, 54)
        self.theme.draw_retro_box(surface, header_rect, bg_color=(25, 22, 38))
        
        title = self.theme.render_text("GUÍA RÁPIDA Y AYUDA", 14, PALETTE["gold_highlight"], (0, 0, 0))
        surface.blit(title, (header_rect.x + 16, header_rect.y + 12))
        
        sub = self.theme.render_text("CÓMO AÑADIR JUEGOS, CARPETAS Y CONTROLES", 8, PALETTE["accent_lavender"])
        surface.blit(sub, (header_rect.x + 16, header_rect.y + 32))

        # Main Layout
        main_y = header_rect.bottom + 12
        main_h = h - main_y - 56

        panel_rect = pygame.Rect(16, main_y, w - 32, main_h)
        self.theme.draw_retro_box(surface, panel_rect)

        # Content split in 2 columns
        col_w = (panel_rect.width - 48) // 2
        col1_x = panel_rect.x + 16
        col2_x = col1_x + col_w + 16
        curr_y = panel_rect.y + 16

        # Column 1: Estructura de Carpetas & Carga de ROMs
        c1_t = self.theme.render_text("[DIR] ESTRUCTURA MULTI-SISTEMA", 9, PALETTE["accent_lavender"])
        surface.blit(c1_t, (col1_x, curr_y))
        
        col1_lines = [
            ("- roms/snes/ & megadrive/", "Juegos SNES (.smc) y Mega Drive (.bin)"),
            ("- boxart/snes/ & megadrive/", "Portadas de juegos (.png, .jpg, .webp,"),
            (" ", ".bmp asignables desde el menu [X/M])"),
            ("- saves/snes/ & megadrive/", "Partidas guardadas de bateria (.srm)"),
            ("- states/snes/ & megadrive/", "Puntos de guardado rapido (Savestates)"),
            ("- config/", "Ajustes, favoritos y mapeo de controles"),
            ("- Multiplataforma:", "RetroDeck.sh (Linux), RetroDeck.bat (Win)"),
            ("- docs/ (WebAssembly)", "Edicion web para jugar en GitHub Pages"),
            ("", ""),
            ("[PAD] COMPATIBILIDAD CON MANDOS", ""),
            ("- Mandos USB/Bluetooth (Xbox, PS4/PS5,", ""),
            ("  8BitDo, mandos clasicos de PC, etc.)", ""),
            ("- Reasigna botones en la seccion [C] Controles.", ""),
        ]

        y_c1 = curr_y + 24
        for l1, l2 in col1_lines:
            if l1.startswith("[PAD]"):
                s1 = self.theme.render_text(l1, 9, PALETTE["accent_lavender"])
                surface.blit(s1, (col1_x, y_c1))
            else:
                s1 = self.theme.render_text(l1, 8, PALETTE["gold_highlight"])
                surface.blit(s1, (col1_x, y_c1))
                if l2:
                    s2 = self.theme.render_text(l2, 7, PALETTE["text_white"])
                    surface.blit(s2, (col1_x + 16, y_c1 + 14))
                    y_c1 += 14
            y_c1 += 18

        # Column 2: Teclas por defecto y atajos
        c2_t = self.theme.render_text("[KB] TECLAS POR DEFECTO (TECLADO)", 9, PALETTE["accent_lavender"])
        surface.blit(c2_t, (col2_x, curr_y))

        keys_table = [
            ("Flechas (Arriba/Abajo/Izq/Der)", "D-Pad (Ambos sistemas)"),
            ("SNES: Z, X, A, S, Q, W", "B, A, Y, X, L, R"),
            ("MEGA DRIVE: A, S, D", "Botones A, B, C (3 botones)"),
            ("MEGA DRIVE: Q, W, E", "Botones X, Y, Z (6 botones)"),
            ("ENTER / R-SHIFT", "Start / Select (Mode)"),
            ("ESCAPE", "Menu de Pausa / Atras"),
            ("", ""),
            ("ATAJOS EN EL MENU:", ""),
            ("- [TAB] o [L / R]: Cambiar consola (SNES / MD)", ""),
            ("- [C]: Configurar controles por consola", ""),
            ("- [A / Enter / Espacio]: Jugar al juego", ""),
            ("- [F3]: Activar / desactivar contador FPS", ""),
            ("- [F11] o [Alt+Enter]: Pantalla Completa", ""),
            ("- [X] o [M]: Menu de Opciones del Juego", ""),
            ("- [Y]: Marcar o desmarcar favorito", ""),
            ("- [S]: Ajustes (Fuentes, FPS, CRT, Sonido)", ""),
            ("- [H / F1]: Abrir esta pantalla de ayuda", ""),
        ]

        y_c2 = curr_y + 24
        for k, action in keys_table:
            if k.startswith("ATAJOS"):
                sk = self.theme.render_text(k, 9, PALETTE["accent_lavender"])
                surface.blit(sk, (col2_x, y_c2))
            elif action:
                sk = self.theme.render_text(k, 8, PALETTE["gold_highlight"])
                sa = self.theme.render_text(action, 8, PALETTE["text_white"])
                surface.blit(sk, (col2_x, y_c2))
                surface.blit(sa, (col2_x + 160, y_c2))
            else:
                sk = self.theme.render_text(k, 8, PALETTE["text_white"])
                surface.blit(sk, (col2_x, y_c2))
            y_c2 += 18

        # Footer
        footer_rect = pygame.Rect(16, h - 42, w - 32, 32)
        self.theme.draw_retro_box(surface, footer_rect, bg_color=(20, 18, 30))
        f_txt = "PULSA [CUALQUIER BOTÓN / ESC] PARA VOLVER AL MENÚ"
        f_surf = self.theme.render_text(f_txt, 8, PALETTE["gold_highlight"])
        surface.blit(f_surf, (footer_rect.x + (footer_rect.width - f_surf.get_width()) // 2, footer_rect.y + 10))
