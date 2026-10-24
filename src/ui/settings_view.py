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

    def _get_items_def(self):
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
        
        # FPS counter
        fps = "ACTIVADO" if self.config.get("video", "show_fps", default=False) else "DESACTIVADO"
        
        # Font size / scale
        fsize_val = self.config.get("video", "font_size", default="normal")
        fsize_labels = {
            "normal": "NORMAL (ESTÁNDAR)",
            "large": "GRANDE (+25%)",
            "xlarge": "EXTRA GRANDE (+50%)"
        }
        fsize = fsize_labels.get(fsize_val, "NORMAL (ESTÁNDAR)")
        
        # Font style
        fstyle_val = self.config.get("video", "font_style", default="retro")
        fstyle_labels = {
            "retro": "PIXEL RETRO (8-BIT)",
            "hd": "ALTA RESOLUCIÓN (HD)"
        }
        fstyle = fstyle_labels.get(fstyle_val, "PIXEL RETRO (8-BIT)")

        # CRT
        crt = "ACTIVADO" if self.config.get("video", "crt_filter", default=True) else "DESACTIVADO"
        crt_menus = "ACTIVADO (RETRO)" if self.config.get("video", "crt_filter_menus", default=False) else "DESACTIVADO (NÍTIDO)"
        crt_int = f"{self.config.get('video', 'crt_scanline_intensity', default=45)}%"
        sfx = "ACTIVADO" if self.config.get("audio", "sound_effects_enabled", default=True) else "DESACTIVADO"
        vol = f"{int(self.config.get('audio', 'volume', default=0.8) * 100)}%"

        return [
            ("backend", "MOTOR EMULADOR (CORE)", backend, "Selecciona el motor de ejecución (Motor Propio o externo)"),
            ("fullscreen", "PANTALLA COMPLETA AL JUGAR", fs, "Inicia los juegos a pantalla completa automáticamente"),
            ("show_fps", "CONTADOR DE FPS (HUD - F3)", fps, "Muestra los fotogramas por segundo en tiempo real para verificar caídas (Tecla F3)"),
            ("font_size", "TAMAÑO DE TEXTO (FUENTE)", fsize, "Aumenta el tamaño de la letra para pantallas de portátiles"),
            ("font_style", "ESTILO DE FUENTE", fstyle, "Alterna entre píxel arcade retro o tipografía nítida de alta resolución"),
            ("crt_filter", "FILTRO RETRO CRT (JUEGOS)", crt, "Activa el efecto de televisor de tubo clásico en los juegos"),
            ("crt_menus", "SCANLINES EN MENÚS", crt_menus, "Mantiene los menús limpios y nítidos o con efecto de tubo"),
            ("crt_intensity", "INTENSIDAD SCANLINES CRT", crt_int, "Ajusta la oscuridad de las líneas de escaneado"),
            ("sfx", "EFECTOS DE SONIDO", sfx, "Activa los efectos sonoros de navegación de la interfaz"),
            ("volume", "VOLUMEN GENERAL", vol, "Ajusta el volumen general del sonido de RetroDeck"),
            ("open_roms", "ABRIR CARPETA DE ROMS", "[ EJECUTAR ]", "Abre el explorador de archivos en la carpeta de ROMs"),
            ("open_saves", "ABRIR CARPETA DE GUARDADOS", "[ EJECUTAR ]", "Abre la carpeta con tus partidas (.srm) y guardados"),
            ("rescan", "REESCANEAR JUEGOS Y PORTADAS", "[ RECARGAR ]", "Vuelve a escanear todos los juegos de la consola activa"),
            ("back", "VOLVER AL MENÚ PRINCIPAL", "", "Regresar al selector de juegos")
        ]

    def _get_items(self):
        return [(name, val, desc) for _, name, val, desc in self._get_items_def()]

    def handle_input(self, action: str) -> Optional[str]:
        items_def = self._get_items_def()
        num_items = len(items_def)

        if action == "UP":
            self.selected_index = (self.selected_index - 1) % num_items
            self.sound.play("nav")
            return None

        elif action == "DOWN":
            self.selected_index = (self.selected_index + 1) % num_items
            self.sound.play("nav")
            return None

        elif action in ("LEFT", "RIGHT"):
            self._adjust_option(self.selected_index, direction=1 if action == "RIGHT" else -1)
            return None

        elif action in ("A", "START"):
            key = items_def[self.selected_index][0]
            if key == "back":
                self.sound.play("back")
                return "BACK_TO_BROWSER"
            elif key in ("open_roms", "open_saves", "rescan"):
                self._execute_action(key)
            else:
                self._adjust_option(self.selected_index, direction=1)
            return None

        elif action in ("B", "MENU"):
            self.sound.play("back")
            return "BACK_TO_BROWSER"

        return None

    def _adjust_option(self, idx: int, direction: int):
        self.sound.play("select")
        items_def = self._get_items_def()
        key = items_def[idx][0]
        
        # 0: Backend
        if key == "backend":
            backends = ["internal", "flatpak_snes9x", "snes9x", "retroarch", "custom"]
            curr = self.config.get("emulator", "backend", default="internal")
            curr_idx = backends.index(curr) if curr in backends else 0
            new_idx = (curr_idx + direction) % len(backends)
            self.config.set("emulator", "backend", backends[new_idx])

        # Fullscreen
        elif key == "fullscreen":
            curr = self.config.get("emulator", "fullscreen_on_launch", default=True)
            self.config.set("emulator", "fullscreen_on_launch", not curr)

        # Show FPS
        elif key == "show_fps":
            curr = self.config.get("video", "show_fps", default=False)
            new_val = not curr
            self.config.set("video", "show_fps", new_val)
            self._notify(f"Contador FPS: {'ACTIVADO' if new_val else 'DESACTIVADO'}")

        # Font size
        elif key == "font_size":
            sizes = ["normal", "large", "xlarge"]
            curr = self.config.get("video", "font_size", default="normal")
            curr_i = sizes.index(curr) if curr in sizes else 0
            new_i = (curr_i + direction) % len(sizes)
            new_size = sizes[new_i]
            self.config.set("video", "font_size", new_size)
            self.theme.set_font_preferences(
                font_style=self.config.get("video", "font_style", default="retro"),
                font_scale=new_size,
                antialias=self.config.get("video", "font_antialiasing", default=True)
            )
            labels = {"normal": "NORMAL", "large": "GRANDE (+25%)", "xlarge": "EXTRA GRANDE (+50%)"}
            self._notify(f"Tamaño de letra: {labels.get(new_size, new_size)}")

        # Font style
        elif key == "font_style":
            styles = ["retro", "hd"]
            curr = self.config.get("video", "font_style", default="retro")
            curr_i = styles.index(curr) if curr in styles else 0
            new_i = (curr_i + direction) % len(styles)
            new_style = styles[new_i]
            self.config.set("video", "font_style", new_style)
            self.theme.set_font_preferences(
                font_style=new_style,
                font_scale=self.config.get("video", "font_size", default="normal"),
                antialias=self.config.get("video", "font_antialiasing", default=True)
            )
            style_lbl = "ALTA RESOLUCIÓN (HD)" if new_style == "hd" else "PIXEL RETRO (8-BIT)"
            self._notify(f"Estilo fuente: {style_lbl}")

        # CRT Filter
        elif key == "crt_filter":
            curr = self.config.get("video", "crt_filter", default=True)
            self.config.set("video", "crt_filter", not curr)

        # CRT Menus
        elif key == "crt_menus":
            curr = self.config.get("video", "crt_filter_menus", default=False)
            new_val = not curr
            self.config.set("video", "crt_filter_menus", new_val)
            self._notify(f"Scanlines en menús: {'ACTIVADO' if new_val else 'DESACTIVADO'}")

        # CRT Intensity
        elif key == "crt_intensity":
            intensities = [25, 45, 65, 85]
            curr = self.config.get("video", "crt_scanline_intensity", default=45)
            curr_i = intensities.index(curr) if curr in intensities else 1
            new_i = (curr_i + direction) % len(intensities)
            self.config.set("video", "crt_scanline_intensity", intensities[new_i])

        # Sound Effects
        elif key == "sfx":
            curr = self.config.get("audio", "sound_effects_enabled", default=True)
            new_val = not curr
            self.config.set("audio", "sound_effects_enabled", new_val)
            self.sound.enabled = new_val

        # Volume
        elif key == "volume":
            volumes = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
            curr = round(self.config.get("audio", "volume", default=0.8), 1)
            curr_i = volumes.index(curr) if curr in volumes else 4
            new_i = max(0, min(len(volumes) - 1, curr_i + direction))
            self.config.set("audio", "volume", volumes[new_i])
            self.sound.set_volume(volumes[new_i])

    def _execute_action(self, key: str):
        # Open ROMs folder
        if key == "open_roms":
            path = Path(self.config.get("paths", "roms")).resolve()
            try:
                open_folder(path)
                self._notify("Abriendo carpeta de ROMs...")
                self.sound.play("select")
            except Exception as e:
                self._notify(f"Error al abrir: {e}")

        # Open Saves folder
        elif key == "open_saves":
            path = Path(self.config.get("paths", "saves")).resolve()
            try:
                open_folder(path)
                self._notify("Abriendo carpeta de partidas...")
                self.sound.play("select")
            except Exception as e:
                self._notify(f"Error al abrir: {e}")

        # Rescan ROMs
        elif key == "rescan":
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
        row_h = max(22, int((panel_rect.height - 54) / len(items)))
        curr_desc = ""

        for i, (name, val, desc) in enumerate(items):
            is_sel = (i == self.selected_index)
            if is_sel:
                curr_desc = desc

            row_y = panel_rect.y + 8 + i * row_h
            row_rect = pygame.Rect(panel_rect.x + 12, row_y, panel_rect.width - 24, row_h - 3)

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
