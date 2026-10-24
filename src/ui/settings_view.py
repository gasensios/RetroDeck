"""
Settings View for RetroSNES.
Configures emulator backend, video effects, audio, and folder management.
"""

import os
import subprocess
import pygame
from pathlib import Path
from typing import Optional
from src.ui.retro_theme import PALETTE
from src.core.platform_utils import open_folder

class SettingsView:
    def __init__(self, theme, sound_manager, config_manager, rom_manager, emulator_runner, system_manager=None):
        self.theme = theme
        self.sound = sound_manager
        self.config = config_manager
        self.rom_mgr = rom_manager
        self.runner = emulator_runner
        self.sys_mgr = system_manager
        
        self.selected_index = 0
        self.notification_msg = ""
        self.notification_timer = 0

    def _get_items(self):
        backend_val = self.config.get("emulator", "backend", default="internal")
        labels = {
            "internal": "MOTOR PROPIO (RETRODECK)",
            "flatpak_snes9x": "SNES9X (FLATPAK)",
            "snes9x": "SNES9X NATIVO",
            "retroarch": "RETROARCH",
            "custom": "PERSONALIZADO"
        }
        backend = labels.get(backend_val, backend_val.upper())
        fs = "ACTIVADO" if self.config.get("emulator", "fullscreen_on_launch", default=True) else "DESACTIVADO"
        crt = "ACTIVADO" if self.config.get("video", "crt_filter", default=True) else "DESACTIVADO"
        crt_int = f"{self.config.get('video', 'crt_scanline_intensity', default=45)}%"
        sfx = "ACTIVADO" if self.config.get("audio", "sound_effects_enabled", default=True) else "DESACTIVADO"
        vol = f"{int(self.config.get('audio', 'volume', default=0.8) * 100)}%"

        return [
            ("MOTOR EMULADOR (CORE)", backend, "Selecciona el motor de ejecución (Motor Propio o externo)"),
            ("PANTALLA COMPLETA AL JUGAR", fs, "Inicia los juegos a pantalla completa automáticamente"),
            ("FILTRO RETRO CRT (SCANLINES)", crt, "Activa el efecto visual de televisor de tubo clásico"),
            ("INTENSIDAD SCANLINES CRT", crt_int, "Ajusta la oscuridad de las líneas de escaneado"),
            ("EFECTOS DE SONIDO", sfx, "Activa los pitidos y chimes retro de la interfaz"),
            ("VOLUMEN GENERAL", vol, "Ajusta el volumen del sonido de la interfaz"),
            ("ABRIR CARPETA DE ROMS", "[ EJECUTAR ]", "Abre el explorador de archivos en la carpeta de ROMs"),
            ("ABRIR CARPETA DE GUARDADOS", "[ EJECUTAR ]", "Abre la carpeta con tus partidas (.srm) y guardados"),
            ("REESCANEAR JUEGOS Y PORTADAS", "[ RECARGAR ]", "Vuelve a escanear todos los juegos en la carpeta roms/snes"),
            ("VOLVER AL MENÚ PRINCIPAL", "", "Regresar al selector de juegos")
        ]

    def handle_input(self, action: str) -> Optional[str]:
        items = self._get_items()
        num_items = len(items)

        if action == "UP":
            self.selected_index = (self.selected_index - 1) % num_items
            self.sound.play("nav")
            return None

        elif action == "DOWN":
            self.selected_index = (self.selected_index + 1) % num_items
            self.sound.play("nav")
            return None

        elif action == "LEFT" or action == "RIGHT":
            self._adjust_option(self.selected_index, direction=1 if action == "RIGHT" else -1)
            return None

        elif action == "A" or action == "START":
            if self.selected_index == 9: # Volver
                self.sound.play("back")
                return "BACK_TO_BROWSER"
            elif self.selected_index in [6, 7, 8]:
                self._execute_action(self.selected_index)
            else:
                self._adjust_option(self.selected_index, direction=1)
            return None

        elif action == "B" or action == "MENU":
            self.sound.play("back")
            return "BACK_TO_BROWSER"

        return None

    def _adjust_option(self, idx: int, direction: int):
        self.sound.play("select")
        
        # 0: Backend
        if idx == 0:
            backends = ["internal", "flatpak_snes9x", "snes9x", "retroarch", "custom"]
            curr = self.config.get("emulator", "backend", default="internal")
            curr_idx = backends.index(curr) if curr in backends else 0
            new_idx = (curr_idx + direction) % len(backends)
            self.config.set("emulator", "backend", backends[new_idx])

        # 1: Fullscreen
        elif idx == 1:
            curr = self.config.get("emulator", "fullscreen_on_launch", default=True)
            self.config.set("emulator", "fullscreen_on_launch", not curr)

        # 2: CRT Filter
        elif idx == 2:
            curr = self.config.get("video", "crt_filter", default=True)
            self.config.set("video", "crt_filter", not curr)

        # 3: CRT Intensity
        elif idx == 3:
            intensities = [25, 45, 65, 85]
            curr = self.config.get("video", "crt_scanline_intensity", default=45)
            curr_i = intensities.index(curr) if curr in intensities else 1
            new_i = (curr_i + direction) % len(intensities)
            self.config.set("video", "crt_scanline_intensity", intensities[new_i])

        # 4: Sound Effects
        elif idx == 4:
            curr = self.config.get("audio", "sound_effects_enabled", default=True)
            new_val = not curr
            self.config.set("audio", "sound_effects_enabled", new_val)
            self.sound.enabled = new_val

        # 5: Volume
        elif idx == 5:
            volumes = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
            curr = round(self.config.get("audio", "volume", default=0.8), 1)
            curr_i = volumes.index(curr) if curr in volumes else 4
            new_i = max(0, min(len(volumes) - 1, curr_i + direction))
            self.config.set("audio", "volume", volumes[new_i])
            self.sound.set_volume(volumes[new_i])

    def _execute_action(self, idx: int):
        # 6: Open ROMs folder
        if idx == 6:
            path = Path(self.config.get("paths", "roms")).resolve()
            try:
                open_folder(path)
                self._notify("Abriendo carpeta de ROMs...")
                self.sound.play("select")
            except Exception as e:
                self._notify(f"Error al abrir: {e}")

        # 7: Open Saves folder
        elif idx == 7:
            path = Path(self.config.get("paths", "saves")).resolve()
            try:
                open_folder(path)
                self._notify("Abriendo carpeta de partidas...")
                self.sound.play("select")
            except Exception as e:
                self._notify(f"Error al abrir: {e}")

        # 8: Rescan ROMs
        elif idx == 8:
            if self.sys_mgr:
                active_sys = self.sys_mgr.get_active_system()
                roms = self.rom_mgr.scan_system(active_sys)
                sys_label = getattr(active_sys, "short", getattr(active_sys, "name", "SISTEMA")).upper()
                self._notify(f"Escaneo {sys_label}: {len(roms)} juegos detectados.")
            else:
                roms = self.rom_mgr.scan_roms()
                self._notify(f"Escaneo completado: {len(roms)} juegos detectados.")
            self.sound.play("launch")

    def _notify(self, msg: str):
        self.notification_msg = msg
        self.notification_timer = 180 # 3 seconds at 60 FPS

    def draw(self, surface: pygame.Surface):
        w, h = surface.get_size()
        items = self._get_items()

        # Update notification timer
        if self.notification_timer > 0:
            self.notification_timer -= 1

        # Header
        header_rect = pygame.Rect(16, 12, w - 32, 54)
        self.theme.draw_retro_box(surface, header_rect, bg_color=(25, 22, 38))
        
        title = self.theme.render_text("AJUSTES Y CONFIGURACIÓN", 14, PALETTE["gold_highlight"], (0, 0, 0))
        surface.blit(title, (header_rect.x + 16, header_rect.y + 12))
        
        sub = self.theme.render_text("PREFERENCIAS DE EMULACIÓN, VÍDEO Y AUDIO", 8, PALETTE["accent_lavender"])
        surface.blit(sub, (header_rect.x + 16, header_rect.y + 32))

        # Main Layout
        main_y = header_rect.bottom + 12
        main_h = h - main_y - 56

        # Options Table Panel
        panel_rect = pygame.Rect(16, main_y, w - 32, main_h)
        self.theme.draw_retro_box(surface, panel_rect)

        # Draw rows
        row_h = max(26, int((main_h - 60) / len(items)))
        curr_desc = ""

        for i, (name, val, desc) in enumerate(items):
            is_sel = (i == self.selected_index)
            if is_sel:
                curr_desc = desc

            row_y = panel_rect.y + 12 + i * row_h
            row_rect = pygame.Rect(panel_rect.x + 12, row_y, panel_rect.width - 24, row_h - 4)

            row_bg = PALETTE["bg_card_selected"] if is_sel else (32, 30, 48)
            self.theme.draw_retro_box(surface, row_rect, bg_color=row_bg, selected=is_sel)

            # Left Name
            name_col = PALETTE["gold_highlight"] if is_sel else PALETTE["text_white"]
            prefix = "> " if is_sel else "  "
            name_surf = self.theme.render_text(f"{prefix}{name}", 8, name_col)
            surface.blit(name_surf, (row_rect.x + 8, row_rect.y + (row_rect.height - name_surf.get_height()) // 2))

            # Right Value
            if val:
                val_col = PALETTE["accent_lavender"] if is_sel else PALETTE["text_gray"]
                val_surf = self.theme.render_text(val, 8, val_col)
                surface.blit(val_surf, (row_rect.right - val_surf.get_width() - 14, row_rect.y + (row_rect.height - val_surf.get_height()) // 2))

        # Description / Notification Box at Bottom of Panel
        desc_box_y = panel_rect.bottom - 42
        desc_box_rect = pygame.Rect(panel_rect.x + 12, desc_box_y, panel_rect.width - 24, 30)
        self.theme.draw_retro_box(surface, desc_box_rect, bg_color=(20, 18, 30))

        if self.notification_timer > 0 and self.notification_msg:
            notif_surf = self.theme.render_text(self.notification_msg, 8, PALETTE["gold_highlight"])
            surface.blit(notif_surf, (desc_box_rect.x + (desc_box_rect.width - notif_surf.get_width()) // 2, desc_box_rect.y + 9))
        elif curr_desc:
            desc_surf = self.theme.render_text(curr_desc, 7, PALETTE["accent_lavender"])
            surface.blit(desc_surf, (desc_box_rect.x + 12, desc_box_rect.y + 10))

        # Footer
        footer_rect = pygame.Rect(16, h - 42, w - 32, 32)
        self.theme.draw_retro_box(surface, footer_rect, bg_color=(20, 18, 30))
        f_txt = "[A / ENTER] CAMBIAR   [IZQ/DER] AJUSTAR   [B / ESC] VOLVER"
        f_surf = self.theme.render_text(f_txt, 8, PALETTE["gold_highlight"])
        surface.blit(f_surf, (footer_rect.x + (footer_rect.width - f_surf.get_width()) // 2, footer_rect.y + 10))
