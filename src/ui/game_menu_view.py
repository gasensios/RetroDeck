"""
Per-Game Options and Customization View for RetroDeck.
Allows managing cover art (boxart), battery saves (SRAM backup/reset), stats, and quick actions.
"""

import os
import subprocess
import shutil
import pygame
from pathlib import Path
from typing import Optional, List
from src.ui.retro_theme import PALETTE
from src.core.rom_manager import RomInfo
from src.core.system_manager import SystemInfo
from src.core.platform_utils import open_folder, pick_image_file

class GameMenuView:
    def __init__(self, theme, sound_manager, rom_manager, config_manager):
        self.theme = theme
        self.sound = sound_manager
        self.rom_mgr = rom_manager
        self.config = config_manager
        
        self.rom: Optional[RomInfo] = None
        self.system: Optional[SystemInfo] = None
        self.selected_index = 0
        self.notification_msg = ""
        self.notification_timer = 0
        self.cached_cart_surf = None
        
        # Interactive click rectangles
        self.option_rects = []

    def set_rom(self, rom: RomInfo, system: SystemInfo):
        self.rom = rom
        self.system = system
        self.selected_index = 0
        self.notification_msg = ""
        self.notification_timer = 0
        self.cached_cart_surf = None

    def _notify(self, msg: str, duration: int = 180):
        self.notification_msg = msg
        self.notification_timer = duration

    def _get_menu_options(self) -> List[tuple]:
        is_fav = self.rom.is_favorite if self.rom else False
        has_custom_box = bool(self.rom and self.rom.custom_boxart)
        
        opts = [
            ("launch", ">> INICIAR JUEGO <<", "Cargar y jugar inmediatamente"),
            ("toggle_fav", f"Favorito: {'* SI (Destacado)' if is_fav else 'No'}", "Alternar estado de favorito"),
            ("pick_boxart_file", "Asignar Caratula (Selector de Archivos)", "Buscar imagen en el equipo (.png, .jpg, .webp, .bmp)"),
            ("open_boxart_dir", "Abrir Carpeta de Caratulas (boxart/)", "Abrir en el gestor de archivos para arrastrar imagenes"),
        ]

        if has_custom_box:
            opts.append(("remove_boxart", "Quitar Caratula Personalizada", "Restablecer al diseno de cartucho 3D original"))

        opts.extend([
            ("backup_sram", "Crear Copia de Seguridad (Backup Partida)", "Guardar copia con fecha y hora del archivo .srm"),
            ("delete_sram", "Borrar Partida de Bateria (Reiniciar Save)", "Borrar archivo .srm para empezar partida de cero"),
            ("open_rom_dir", "Abrir Carpeta de la ROM (roms/)", "Ver el archivo del juego en el explorador"),
            ("reset_stats", "Resetear Estadisticas de Juego", "Poner a cero el contador de partidas jugadas"),
            ("back", "< Volver al Catalogo", "Regresar al explorador principal"),
        ])
        return opts

    def handle_mouse_click(self, pos) -> Optional[str]:
        for idx, rect in enumerate(self.option_rects):
            if rect.collidepoint(pos):
                if self.selected_index == idx:
                    return self.handle_input("A")
                else:
                    self.selected_index = idx
                    self.sound.play("nav")
                return None
        return None

    def handle_input(self, action: str) -> Optional[str]:
        opts = self._get_menu_options()
        num_opts = len(opts)

        if action == "UP":
            if self.selected_index > 0:
                self.selected_index -= 1
            else:
                self.selected_index = num_opts - 1
            self.sound.play("nav")

        elif action == "DOWN":
            if self.selected_index < num_opts - 1:
                self.selected_index += 1
            else:
                self.selected_index = 0
            self.sound.play("nav")

        elif action in ("A", "START"):
            if 0 <= self.selected_index < num_opts:
                opt_key, _, _ = opts[self.selected_index]
                return self._execute_option(opt_key)

        elif action in ("B", "MENU"):
            self.sound.play("back")
            return "BACK_TO_BROWSER"

        return None

    def _execute_option(self, key: str) -> Optional[str]:
        if not self.rom or not self.system:
            return None

        # 1. Launch Game
        if key == "launch":
            self.sound.play("launch")
            return "LAUNCH_GAME"

        # 2. Toggle Favorite
        elif key == "toggle_fav":
            self.rom_mgr.toggle_favorite(self.rom)
            status = "anadido a favoritos" if self.rom.is_favorite else "quitado de favoritos"
            self._notify(f"Juego {status}.")
            self.sound.play("select")

        # 3. Pick Boxart File using system file picker
        elif key == "pick_boxart_file":
            picked_path = self._pick_image_dialog()
            if picked_path:
                self._apply_custom_boxart(picked_path)
            else:
                self._notify("Seleccion de imagen cancelada.")
                self.sound.play("back")

        # 4. Open Boxart Directory in OS file manager
        elif key == "open_boxart_dir":
            try:
                open_folder(self.system.boxart_dir)
                self._notify(f"Abriendo {self.system.boxart_dir.name}/...")
                self.sound.play("select")
            except Exception as e:
                self._notify(f"Error al abrir carpeta: {e}")

        # 5. Remove Custom Boxart
        elif key == "remove_boxart":
            self.rom_mgr.set_custom_boxart(self.rom, None)
            self._notify("Caratula personalizada eliminada.")
            self.sound.play("select")

        # 6. Backup Battery Save (.srm)
        elif key == "backup_sram":
            b_path = self.rom_mgr.backup_sram(self.rom, self.system)
            if b_path:
                self._notify(f"Backup creado: {b_path.name}")
                self.sound.play("select")
            else:
                self._notify("No existe partida guardada (.srm) que respaldar.")
                self.sound.play("back")

        # 7. Delete Battery Save (.srm)
        elif key == "delete_sram":
            deleted = self.rom_mgr.delete_sram(self.rom, self.system)
            if deleted:
                self._notify("Partida guardada de bateria eliminada.")
                self.sound.play("select")
            else:
                self._notify("No se encontro partida previa para borrar.")
                self.sound.play("back")

        # 8. Open ROM Directory
        elif key == "open_rom_dir":
            try:
                open_folder(self.system.roms_dir)
                self._notify(f"Abriendo {self.system.roms_dir.name}/...")
                self.sound.play("select")
            except Exception as e:
                self._notify(f"Error al abrir carpeta: {e}")

        # 9. Reset Play Stats
        elif key == "reset_stats":
            self.rom_mgr.reset_stats(self.rom)
            self._notify("Estadisticas y contador de partidas reseteados.")
            self.sound.play("select")

        # 10. Back to Browser
        elif key == "back":
            self.sound.play("back")
            return "BACK_TO_BROWSER"

        return None

    def _pick_image_dialog(self) -> Optional[str]:
        """Opens native file selection dialog for images (Linux / Windows / Mac)."""
        title = f"Seleccionar Caratula para {self.rom.title}" if self.rom else "Seleccionar Caratula"
        initial = self.system.boxart_dir if self.system else None
        return pick_image_file(title=title, initial_dir=initial)

    def _apply_custom_boxart(self, src_file: str):
        path = Path(src_file)
        if not path.exists():
            self._notify("El archivo seleccionado no existe.")
            return

        # Copy the image file to boxart/<system>/ with the stem of the ROM
        dest_dir = self.system.boxart_dir
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / f"{self.rom.stem}{path.suffix.lower()}"
        try:
            shutil.copy2(path, dest_path)
            self.rom_mgr.set_custom_boxart(self.rom, str(dest_path.resolve()))
            self._notify(f"Caratula asignada: {dest_path.name}")
            self.sound.play("launch")
        except Exception as e:
            self._notify(f"Error al copiar imagen: {e}")

    def draw(self, surface: pygame.Surface):
        w, h = surface.get_size()
        if not self.rom or not self.system:
            return

        if self.notification_timer > 0:
            self.notification_timer -= 1

        # 1. Top Header Marquee
        header_h = 58
        header_rect = pygame.Rect(16, 10, w - 32, header_h)
        self.theme.draw_retro_box(surface, header_rect, bg_color=(22, 20, 32), with_screws=True)

        badge_x = header_rect.x + 14
        badge_y = header_rect.y + 13
        if self.system.id == "neogeo":
            self.theme.draw_neogeo_badge(surface, badge_x, badge_y)
        elif self.system.id == "megadrive":
            self.theme.draw_megadrive_badge(surface, badge_x, badge_y)
        else:
            self.theme.draw_snes_badge(surface, badge_x, badge_y)

        title_x = badge_x + 115
        menu_title = self.theme.render_text("AJUSTES Y GESTION DEL JUEGO", 11, PALETTE["gold_highlight"], (0, 0, 0))
        surface.blit(menu_title, (title_x, header_rect.y + 12))

        sub_info = f"{self.rom.title} [{self.system.full_name.upper()}]"
        if len(sub_info) > 45:
            sub_info = sub_info[:43] + ".."
        sub_surf = self.theme.render_text(sub_info, 7, PALETTE["accent_lavender"])
        surface.blit(sub_surf, (title_x, header_rect.y + 36))

        # 2. Main Layout Split (45% Left: Cartridge & Info | 55% Right: Interactive Menu)
        margin = 16
        main_y = header_rect.bottom + 8
        main_h = h - main_y - 48

        left_w = int((w - margin * 3) * 0.44)
        right_w = (w - margin * 3) - left_w

        left_rect = pygame.Rect(margin, main_y, left_w, main_h)
        right_rect = pygame.Rect(left_rect.right + margin, main_y, right_w, main_h)

        # Draw Left Panel (Cartridge Showcase & Status)
        self.theme.draw_retro_box(surface, left_rect, bg_color=(20, 18, 30), with_screws=True)
        self._draw_left_panel(surface, left_rect)

        # Draw Right Panel (Options Menu List)
        self.theme.draw_retro_box(surface, right_rect, bg_color=(20, 18, 30), with_screws=True)
        self._draw_right_panel(surface, right_rect)

        # 3. Bottom Footer
        footer_rect = pygame.Rect(16, h - 36, w - 32, 28)
        self.theme.draw_retro_box(surface, footer_rect, bg_color=(18, 16, 26), with_screws=False)
        
        if self.notification_timer > 0 and self.notification_msg:
            f_txt = self.notification_msg
            f_surf = self.theme.render_text(f_txt, 7, PALETTE["gold_highlight"])
        else:
            f_txt = "[A / ENTER] EJECUTAR ACCION    [B / ESC] VOLVER AL CATALOGO"
            f_surf = self.theme.render_text(f_txt, 7, PALETTE["text_white"])
        surface.blit(f_surf, (footer_rect.x + (footer_rect.width - f_surf.get_width()) // 2, footer_rect.y + 8))

    def _draw_left_panel(self, surface: pygame.Surface, rect: pygame.Rect):
        # Section Header
        hdr = pygame.Rect(rect.x + 8, rect.y + 8, rect.width - 16, 26)
        pygame.draw.rect(surface, (32, 30, 46), hdr, border_radius=3)
        h_txt = self.theme.render_text(":: VISTA DEL CARTUCHO ::", 8, self.system.badge_color)
        surface.blit(h_txt, (hdr.x + (hdr.width - h_txt.get_width()) // 2, hdr.y + 8))

        inner_x = rect.x + 14
        inner_y = hdr.bottom + 8
        inner_w = rect.width - 28

        # 1. 3D Cartridge Box
        cart_bay_h = min(200, int(rect.height * 0.40))
        cart_bay = pygame.Rect(inner_x, inner_y, inner_w, cart_bay_h)

        # Soft backlight
        if self.system.id == "neogeo":
            backlight_col = (90, 20, 25, 80)
        elif self.system.id == "snes":
            backlight_col = (70, 30, 90, 80)
        else:
            backlight_col = (20, 50, 110, 80)
        backlight_surf = pygame.Surface((cart_bay.width, cart_bay.height), pygame.SRCALPHA)
        pygame.draw.ellipse(backlight_surf, backlight_col, (8, 8, cart_bay.width - 16, cart_bay.height - 16))
        surface.blit(backlight_surf, (cart_bay.x, cart_bay.y))

        # Boxart image
        custom_img = None
        if self.rom.boxart_path and self.rom.boxart_path.exists():
            try:
                custom_img = pygame.image.load(str(self.rom.boxart_path)).convert_alpha()
            except Exception:
                pass

        cart_w = min(cart_bay.width - 20, 260)
        cart_h = cart_bay_h - 14
        cart_rect = pygame.Rect(
            cart_bay.x + (cart_bay.width - cart_w) // 2,
            cart_bay.y + 6,
            cart_w,
            cart_h
        )
        self.theme.draw_cartridge(surface, cart_rect, system_id=self.system.id, title=self.rom.title, custom_image=custom_img)

        # 2. Battery SRAM Save Status Card
        curr_y = cart_bay.bottom + 8
        sram_info = self.rom_mgr.get_sram_info(self.rom, self.system)
        
        sram_card = pygame.Rect(inner_x, curr_y, inner_w, 75)
        pygame.draw.rect(surface, (24, 22, 36), sram_card, border_radius=4)
        pygame.draw.rect(surface, (45, 42, 60), sram_card, width=1, border_radius=4)

        card_title = self.theme.render_text("MEMORIA DE GUARDADO (SRAM):", 7, self.system.badge_color)
        surface.blit(card_title, (sram_card.x + 8, sram_card.y + 8))

        if sram_info["exists"]:
            st_txt = self.theme.render_text(f"Partida activa ({sram_info['size']})", 7, PALETTE["led_green"])
            mod_txt = self.theme.render_text(f"Fecha: {sram_info['mtime']}", 7, PALETTE["text_white"])
        else:
            st_txt = self.theme.render_text("Sin partida guardada", 7, PALETTE["text_gray"])
            mod_txt = self.theme.render_text("Se creara al guardar en el juego", 7, PALETTE["accent_lavender"])

        surface.blit(st_txt, (sram_card.x + 8, sram_card.y + 28))
        surface.blit(mod_txt, (sram_card.x + 8, sram_card.y + 48))

        # 3. Game Metadata & Statistics Card
        curr_y = sram_card.bottom + 8
        stats_card = pygame.Rect(inner_x, curr_y, inner_w, rect.bottom - curr_y - 12)
        pygame.draw.rect(surface, (24, 22, 36), stats_card, border_radius=4)
        pygame.draw.rect(surface, (45, 42, 60), stats_card, width=1, border_radius=4)

        stats_title = self.theme.render_text("REGISTRO Y ESTADISTICAS:", 7, self.system.badge_color)
        surface.blit(stats_title, (stats_card.x + 8, stats_card.y + 8))

        lines = [
            f"Archivo: {self.rom.filename}",
            f"Tamano: {self.rom.get_formatted_size()}",
            f"Partidas jugadas: {self.rom.play_count}",
            f"Ultima sesion: {self.rom.last_played if self.rom.last_played else 'Nunca'}",
        ]
        sy = stats_card.y + 26
        for line in lines:
            if len(line) > 34:
                line = line[:32] + ".."
            txt = self.theme.render_text(line, 7, PALETTE["text_white"])
            surface.blit(txt, (stats_card.x + 8, sy))
            sy += 16
            if sy >= stats_card.bottom - 10:
                break

    def _draw_right_panel(self, surface: pygame.Surface, rect: pygame.Rect):
        # Section Header
        hdr = pygame.Rect(rect.x + 8, rect.y + 8, rect.width - 16, 26)
        pygame.draw.rect(surface, (32, 30, 46), hdr, border_radius=3)
        h_txt = self.theme.render_text(":: OPCIONES DE CONFIGURACION ::", 8, self.system.badge_color)
        surface.blit(h_txt, (hdr.x + (hdr.width - h_txt.get_width()) // 2, hdr.y + 8))

        opts = self._get_menu_options()
        menu_top = hdr.bottom + 8
        menu_h = rect.bottom - menu_top - 10
        item_h = max(24, int(menu_h / len(opts)))

        self.option_rects = []
        for i, (key, label, desc) in enumerate(opts):
            is_sel = (i == self.selected_index)
            row_y = menu_top + i * item_h
            row_rect = pygame.Rect(rect.x + 10, row_y, rect.width - 20, item_h - 3)
            self.option_rects.append(row_rect)

            row_bg = PALETTE["bg_card_selected"] if is_sel else (26, 24, 38)
            self.theme.draw_retro_box(surface, row_rect, bg_color=row_bg, selected=is_sel, with_screws=False)

            # Pointer on selected
            text_x = row_rect.x + 8
            if is_sel:
                self.theme.draw_pointer(surface, row_rect.x + 6, row_rect.y + (row_rect.height - 10) // 2)
                text_x += 16

            txt_col = PALETTE["gold_highlight"] if is_sel else PALETTE["text_white"]
            lbl_surf = self.theme.render_text(label, 7, txt_col)
            surface.blit(lbl_surf, (text_x, row_rect.y + 6))

            # Small description below label
            desc_col = PALETTE["accent_lavender"] if is_sel else PALETTE["text_gray"]
            desc_surf = self.theme.render_text(desc, 6, desc_col)
            surface.blit(desc_surf, (text_x, row_rect.y + 19))
