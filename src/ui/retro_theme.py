"""
Retro Theme, Palette and Visual Effects for RetroDeck.
Authentic 80s/90s 16-bit arcade aesthetics, Mode 7 synthwave grid, starfield, CRT phosphor, and cartridges.
"""

import pygame
import math
import random
from pathlib import Path

PALETTE = {
    # Base Chassis & Backgrounds
    "bg_dark": (14, 12, 22),
    "bg_card": (26, 24, 38),
    "bg_card_selected": (42, 38, 64),
    "panel_inner": (18, 16, 26),
    "border_light": (140, 135, 175),
    "border_dark": (8, 6, 14),
    "border_steel": (75, 78, 92),
    "screw_head": (95, 98, 115),
    "screw_slot": (40, 42, 52),
    "screw_highlight": (180, 185, 205),
    
    # Highlights & Neons
    "gold_highlight": (255, 208, 60),
    "neon_amber": (255, 175, 20),
    "neon_cyan": (0, 235, 255),
    "neon_magenta": (255, 55, 165),
    "text_white": (248, 250, 255),
    "text_gray": (150, 158, 175),
    "text_dark": (35, 35, 45),
    
    # SNES Icons & Buttons
    "accent_purple": (118, 92, 235),
    "accent_lavender": (175, 165, 255),
    "snes_gray": (188, 190, 200),
    "snes_dark_gray": (92, 95, 108),
    "btn_a_red": (238, 65, 85),
    "btn_b_yellow": (250, 195, 45),
    "btn_x_blue": (60, 160, 245),
    "btn_y_green": (85, 205, 110),
    
    # Sega Mega Drive
    "sega_blue": (0, 105, 215),
    "sega_cyan": (60, 210, 245),
    "sega_black": (24, 24, 30),
    "sega_dark_gray": (48, 48, 56),
    "sega_red": (235, 45, 45),
    "sonic_gold": (255, 210, 30),
    
    # SNK Neo Geo
    "neogeo_red": (220, 38, 38),
    "neogeo_gold": (255, 208, 60),
    "neogeo_dark": (22, 12, 18),
    "neogeo_dark_gray": (42, 40, 48),
    "neogeo_btn_a": (235, 45, 45),     # Red
    "neogeo_btn_b": (250, 205, 35),    # Yellow
    "neogeo_btn_c": (50, 200, 90),     # Green
    "neogeo_btn_d": (45, 140, 245),    # Blue
    
    # LEDs
    "led_green": (60, 245, 100),
    "led_green_glow": (30, 160, 60, 90),
    "led_red": (255, 60, 60),
    "led_red_glow": (180, 20, 20, 90),
}


class RetroTheme:
    def __init__(self, assets_dir: Path):
        self.assets_dir = assets_dir
        
        # Locate PressStart2P.ttf with fallbacks
        candidates = [
            assets_dir / "fonts" / "PressStart2P.ttf",
            assets_dir.parent / "docs" / "assets" / "fonts" / "PressStart2P.ttf",
            assets_dir.parent / "assets" / "fonts" / "PressStart2P.ttf",
            Path(__file__).resolve().parent.parent.parent / "assets" / "fonts" / "PressStart2P.ttf",
            Path(__file__).resolve().parent.parent.parent / "docs" / "assets" / "fonts" / "PressStart2P.ttf",
        ]
        self.font_path = next((p for p in candidates if p.exists()), assets_dir / "fonts" / "PressStart2P.ttf")
        
        # Font preferences
        self.font_style = "retro"   # "retro" or "hd"
        self.font_scale = "normal"  # "normal", "large", "xlarge"
        self.antialias = True
        
        self._fonts = {}
        self._text_cache = {}
        self._scanline_surface = None
        self._vignette_surface = None
        self._grid_surface = None
        self._glow_surfaces = {}
        self._last_screen_size = None

        # Precompute 70 starry particles for the 80s synthwave sky
        random.seed(1989)
        self.stars = []
        for _ in range(70):
            rx = random.random()
            ry = random.random() * 0.56 # Keep in upper 56%
            color = random.choice([
                (255, 255, 255),
                (255, 225, 140),
                (140, 230, 255),
                (255, 160, 235),
            ])
            speed = random.uniform(0.002, 0.006)
            phase = random.uniform(0, math.pi * 2)
            self.stars.append((rx, ry, color, speed, phase))

    def set_font_preferences(self, font_style: str = "retro", font_scale: str = "normal", antialias: bool = True):
        """Updates typography styling and scaling, clearing font cache for instant hot-reload."""
        self.font_style = font_style if font_style in ("retro", "hd") else "retro"
        self.font_scale = font_scale if font_scale in ("normal", "large", "xlarge") else "normal"
        self.antialias = bool(antialias)
        self._fonts.clear()
        self._text_cache.clear()

    def _get_effective_size(self, size: int) -> int:
        scales = {"normal": 1.0, "large": 1.25, "xlarge": 1.5}
        factor = scales.get(self.font_scale, 1.0)
        
        if self.font_style == "hd":
            # HD vector fonts have wider glyph margins; increase base size so height matches visual expectations
            return max(11, int(size * 1.35 * factor))
        else:
            return max(6, int(round(size * factor)))

    def get_font(self, size: int) -> pygame.font.Font:
        effective_size = self._get_effective_size(size)
        key = (self.font_style, effective_size)
        if key not in self._fonts:
            if self.font_style == "hd":
                # High-definition clean vector font for maximum readability on laptop displays
                self._fonts[key] = pygame.font.SysFont("segoeui,arial,dejavusans,liberationsans,notosans,sans-serif", effective_size, bold=True)
            else:
                # Classic 8-bit arcade pixel font
                if self.font_path.exists():
                    try:
                        self._fonts[key] = pygame.font.Font(str(self.font_path), effective_size)
                    except Exception:
                        self._fonts[key] = pygame.font.SysFont("segoeui,arial,dejavusans,monospace", effective_size, bold=True)
                else:
                    self._fonts[key] = pygame.font.SysFont("segoeui,arial,dejavusans,monospace", effective_size, bold=True)
        return self._fonts[key]

    def render_text(self, text: str, size: int, color: tuple, shadow_color: tuple = None, antialias: bool = None) -> pygame.Surface:
        aa = self.antialias if antialias is None else antialias
        cache_key = (text, size, color, shadow_color, aa, self.font_style, self.font_scale)
        if cache_key in self._text_cache:
            return self._text_cache[cache_key]

        font = self.get_font(size)
        main_surf = font.render(text, aa, color)
        if shadow_color:
            shadow_surf = font.render(text, aa, shadow_color)
            offset = 1 if size <= 7 else 2
            w = main_surf.get_width() + offset
            h = main_surf.get_height() + offset
            combined = pygame.Surface((w, h), pygame.SRCALPHA)
            combined.blit(shadow_surf, (offset, offset))
            combined.blit(main_surf, (0, 0))
            result = combined
        else:
            result = main_surf

        if len(self._text_cache) > 512:
            self._text_cache.clear()
        self._text_cache[cache_key] = result
        return result

    def draw_fps_hud(self, surface: pygame.Surface, fps: float, x: int = None, y: int = None, is_ingame: bool = False):
        """
        Renders an authentic, stylish arcade FPS monitoring HUD badge.
        Color transitions automatically according to performance:
          - Green:  >= 57.0 FPS (Perfect 60 FPS lock)
          - Yellow: 45.0 - 56.9 FPS (Minor dip)
          - Red:    < 45.0 FPS (Severe frame drop alert)
        """
        w, h = surface.get_size()
        
        # Color & label coding
        if fps >= 57.0:
            status_col = PALETTE["led_green"]
        elif fps >= 45.0:
            status_col = PALETTE["sonic_gold"]
        else:
            status_col = PALETTE["led_red"]

        fps_text = f"{fps:4.1f} FPS"
        txt_surf = self.render_text(fps_text, 8, status_col, shadow_color=(0, 0, 0))
        
        box_w = txt_surf.get_width() + 24
        box_h = 24
        pos_x = (w - box_w - 16) if x is None else x
        pos_y = 14 if y is None else y

        # Translucent chassis backing (cached to eliminate per-frame allocations)
        if not hasattr(self, "_fps_bg_cache"):
            self._fps_bg_cache = {}
        bg_key = (box_w, box_h)
        if bg_key not in self._fps_bg_cache:
            bg_surf = pygame.Surface(bg_key, pygame.SRCALPHA)
            bg_surf.fill((14, 12, 22, 215))
            self._fps_bg_cache[bg_key] = bg_surf
        else:
            bg_surf = self._fps_bg_cache[bg_key]
        surface.blit(bg_surf, (pos_x, pos_y))

        # Glowing metallic/neon border
        hud_rect = pygame.Rect(pos_x, pos_y, box_w, box_h)
        pygame.draw.rect(surface, status_col, hud_rect, width=1, border_radius=4)

        # Pulsing status LED dot
        led_x = pos_x + 9
        led_y = pos_y + box_h // 2
        pygame.draw.circle(surface, status_col, (led_x, led_y), 3)

        # FPS Text
        surface.blit(txt_surf, (pos_x + 18, pos_y + (box_h - txt_surf.get_height()) // 2))

    def draw_star(self, surface: pygame.Surface, cx: int, cy: int, radius: int = 5, color=None):
        """Draws a crisp 5-point golden retro star."""
        c = color or PALETTE["sonic_gold"]
        points = []
        for i in range(10):
            r = radius if i % 2 == 0 else radius * 0.42
            angle = i * math.pi / 5 - math.pi / 2
            points.append((cx + int(math.cos(angle) * r), cy + int(math.sin(angle) * r)))
        pygame.draw.polygon(surface, c, points)
        pygame.draw.polygon(surface, (20, 20, 20), points, width=1)

    def draw_pointer(self, surface: pygame.Surface, x: int, y: int, color=None):
        """Draws a crisp retro arcade arrow pointer."""
        c = color or PALETTE["gold_highlight"]
        points = [(x, y), (x + 8, y + 5), (x, y + 10)]
        pygame.draw.polygon(surface, c, points)
        pygame.draw.polygon(surface, (0, 0, 0), points, width=1)

    def _get_horizon_glow_surf(self, w: int, glow_h: int, hor_glow: tuple) -> pygame.Surface:
        key = (w, glow_h, hor_glow)
        if key not in self._glow_surfaces:
            if len(self._glow_surfaces) > 12:
                self._glow_surfaces.clear()
            glow_surf = pygame.Surface((w, glow_h * 2), pygame.SRCALPHA)
            for i in range(glow_h * 2):
                dist = abs(i - glow_h) / float(glow_h)
                a = max(0, min(140, int((1.0 - dist) * 110)))
                pygame.draw.line(glow_surf, (hor_glow[0], hor_glow[1], hor_glow[2], a), (0, i), (w, i))
            self._glow_surfaces[key] = glow_surf
        return self._glow_surfaces[key]

    def draw_animated_retro_bg(self, surface: pygame.Surface, system_id: str, ticks: int):
        """
        Draws an authentic 80s/90s Mode-7 synthwave perspective grid and starfield.
        Adapts colors automatically:
          - SNES: Deep indigo nebula + neon magenta/purple grid floor.
          - Mega Drive: Deep obsidian space + electric cyan/Sega blue grid floor.
        """
        w, h = surface.get_size()
        horizon_y = int(h * 0.58)

        # 1. Upper Sky Gradient
        if system_id == "neogeo":
            top_sky = (22, 10, 16)
            hor_glow = (95, 20, 30)
        elif system_id == "megadrive":
            top_sky = (8, 10, 20)
            hor_glow = (18, 48, 105)
        else:
            top_sky = (14, 10, 26)
            hor_glow = (60, 18, 75)

        # Fill base sky
        surface.fill(top_sky)

        # Draw soft horizon glow (re-uses cached gradient surface to eliminate 140 line rasterizations/frame)
        glow_h = 70
        glow_surf = self._get_horizon_glow_surf(w, glow_h, hor_glow)
        surface.blit(glow_surf, (0, horizon_y - glow_h))

        # 2. Twinkling Starfield in Upper Sky
        for rx, ry, col, spd, ph in self.stars:
            sx = int(rx * w)
            sy = int(ry * h)
            tw = (math.sin(ticks * spd + ph) + 1.0) * 0.5
            if tw > 0.35:
                star_col = tuple(max(0, min(255, int(c * tw))) for c in col)
                surface.set_at((sx, sy), star_col)

        # 3. Mode 7 / 3D Synthwave Perspective Grid Floor (re-uses preallocated surface)
        floor_h = h - horizon_y
        if self._grid_surface is None or self._grid_surface.get_size() != (w, floor_h):
            self._grid_surface = pygame.Surface((w, floor_h), pygame.SRCALPHA)
        else:
            self._grid_surface.fill((0, 0, 0, 0))
        grid_surf = self._grid_surface

        # Floor base gradient (dark ground)
        if system_id == "neogeo":
            grid_col = (255, 60, 70)
        elif system_id == "megadrive":
            grid_col = (0, 220, 255)
        else:
            grid_col = (225, 45, 175)
        
        # Horizontal perspective grid lines scrolling forward
        scroll_offset = (ticks * 0.0007) % 1.0
        num_lines = 14
        for i in range(num_lines):
            p = (i + scroll_offset) / num_lines
            # Non-linear perspective spacing
            ly = int((p ** 2.2) * floor_h)
            if ly >= floor_h:
                continue
            alpha = max(10, min(180, int((p ** 1.5) * 190)))
            lw = 2 if p > 0.55 else 1
            pygame.draw.line(grid_surf, (grid_col[0], grid_col[1], grid_col[2], alpha), (0, ly), (w, ly), lw)

        # Radiating perspective vertical lines meeting at center horizon
        cx = w // 2
        line_spacing = 72
        v_alpha = 75 if system_id in ("megadrive", "neogeo") else 65
        for xb in range(-w // 2, w + w // 2, line_spacing):
            pygame.draw.line(
                grid_surf,
                (grid_col[0], grid_col[1], grid_col[2], v_alpha),
                (cx + int((xb - cx) * 0.05), 0),
                (xb, floor_h),
                1
            )

        surface.blit(grid_surf, (0, horizon_y))

        # 4. Bright Neon Horizon Strip
        if system_id == "neogeo":
            neon_strip_col = (255, 210, 60)
        elif system_id == "megadrive":
            neon_strip_col = (100, 230, 255)
        else:
            neon_strip_col = (255, 140, 230)
        pygame.draw.line(surface, neon_strip_col, (0, horizon_y), (w, horizon_y), 2)

    def draw_retro_box(self, surface: pygame.Surface, rect: pygame.Rect, bg_color=None, border_color=None, selected=False, with_screws=True):
        """
        Draws a 90s console chassis box with authentic 3D bevels, corner screws, and glowing active borders.
        """
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        bg = bg_color or (PALETTE["bg_card_selected"] if selected else PALETTE["bg_card"])
        pygame.draw.rect(surface, bg, rect)

        if selected:
            # Pulsing neon border
            ticks = pygame.time.get_ticks()
            pulse = (math.sin(ticks * 0.007) + 1.0) * 0.5
            hi_r = int(255 * (0.8 + 0.2 * pulse))
            hi_g = int(205 * (0.8 + 0.2 * pulse))
            hi_b = int(70 * (0.8 + 0.2 * pulse))
            glow_col = (hi_r, hi_g, hi_b)

            pygame.draw.rect(surface, glow_col, rect, width=2)
            pygame.draw.rect(surface, (hi_r, hi_g, hi_b, 60), (x - 1, y - 1, w + 2, h + 2), width=1)
        else:
            # 3D Metallic Beveled Edges
            b_light = border_color or PALETTE["border_light"]
            b_dark = PALETTE["border_dark"]
            
            # Top & Left bevel highlight
            pygame.draw.line(surface, b_light, (x, y), (x + w - 1, y), 2)
            pygame.draw.line(surface, b_light, (x, y), (x, y + h - 1), 2)
            
            # Bottom & Right bevel shadow
            pygame.draw.line(surface, b_dark, (x, y + h - 1), (x + w - 1, y + h - 1), 2)
            pygame.draw.line(surface, b_dark, (x + w - 1, y), (x + w - 1, y + h - 1), 2)

        # Industrial Chassis Screws in Corners (if box is large enough)
        if with_screws and w >= 80 and h >= 48:
            margin = 6
            screw_pts = [
                (x + margin, y + margin),
                (x + w - margin - 1, y + margin),
                (x + margin, y + h - margin - 1),
                (x + w - margin - 1, y + h - margin - 1),
            ]
            for sx, sy in screw_pts:
                # Screw rim & metallic slot
                pygame.draw.circle(surface, PALETTE["screw_slot"], (sx, sy), 3)
                pygame.draw.circle(surface, PALETTE["screw_head"], (sx, sy), 2)
                # Cross slot (+)
                surface.set_at((sx, sy), PALETTE["screw_slot"])
                surface.set_at((sx - 1, sy), PALETTE["screw_highlight"])
                surface.set_at((sx, sy - 1), PALETTE["screw_highlight"])

    def draw_snes_badge(self, surface: pygame.Surface, x: int, y: int):
        """Draws the iconic Super Famicom / PAL SNES 4-color diamond badge."""
        w, h = 100, 32
        badge_rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, (28, 26, 36), badge_rect, border_radius=4)
        pygame.draw.rect(surface, PALETTE["snes_gray"], badge_rect, width=1, border_radius=4)

        # 4 glossy circles in angled diamond formation
        cx, cy = x + 18, y + 16
        r = 5
        buttons = [
            (cx, cy - 6, PALETTE["btn_x_blue"]),
            (cx - 6, cy, PALETTE["btn_y_green"]),
            (cx, cy + 6, PALETTE["btn_b_yellow"]),
            (cx + 6, cy, PALETTE["btn_a_red"]),
        ]
        for bx, by, col in buttons:
            pygame.draw.circle(surface, col, (bx, by), r)
            pygame.draw.circle(surface, (20, 20, 20), (bx, by), r, width=1)
            # Gloss shine
            surface.set_at((bx - 1, by - 1), (255, 255, 255))

        lbl = self.render_text("16-BIT", 8, PALETTE["gold_highlight"])
        surface.blit(lbl, (x + 36, y + 11))

    def draw_megadrive_badge(self, surface: pygame.Surface, x: int, y: int):
        """Draws the iconic Sega Mega Drive golden '16-BIT' oval badge."""
        w, h = 100, 32
        badge_rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, (18, 20, 28), badge_rect, border_radius=4)
        pygame.draw.rect(surface, PALETTE["sonic_gold"], badge_rect, width=1, border_radius=4)

        # Golden oval ring
        cx, cy = x + 18, y + 16
        pygame.draw.ellipse(surface, PALETTE["sonic_gold"], (cx - 10, cy - 8, 20, 16), width=2)
        surface.blit(self.render_text("MD", 6, PALETTE["text_white"]), (cx - 6, cy - 4))

        lbl = self.render_text("16-BIT", 8, PALETTE["sega_cyan"])
        surface.blit(lbl, (x + 36, y + 11))

    def draw_neogeo_badge(self, surface: pygame.Surface, x: int, y: int):
        """Draws the iconic SNK Neo Geo MAX 330 MEGA arcade badge."""
        w, h = 100, 32
        badge_rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, (28, 12, 16), badge_rect, border_radius=4)
        pygame.draw.rect(surface, PALETTE["neogeo_gold"], badge_rect, width=1, border_radius=4)

        # 4 glossy arcade button dots in angled arc formation (A: Red, B: Yellow, C: Green, D: Blue)
        dots = [
            (x + 9, y + 21, PALETTE["neogeo_btn_a"]),
            (x + 15, y + 16, PALETTE["neogeo_btn_b"]),
            (x + 21, y + 13, PALETTE["neogeo_btn_c"]),
            (x + 27, y + 11, PALETTE["neogeo_btn_d"]),
        ]
        for bx, by, col in dots:
            pygame.draw.circle(surface, col, (bx, by), 3)
            pygame.draw.circle(surface, (10, 10, 10), (bx, by), 3, width=1)
            surface.set_at((bx - 1, by - 1), (255, 255, 255))

        lbl = self.render_text("NEO-GEO", 7, PALETTE["neogeo_gold"])
        surface.blit(lbl, (x + 34, y + 11))

    def draw_led(self, surface: pygame.Surface, x: int, y: int, label: str = "POWER", is_on: bool = True, color: str = "green"):
        """Draws an authentic glowing arcade console LED indicator."""
        led_col = PALETTE["led_green"] if color == "green" else PALETTE["led_red"]
        glow_col = PALETTE["led_green_glow"] if color == "green" else PALETTE["led_red_glow"]

        # Outer bloom glow
        if is_on:
            bloom_surf = pygame.Surface((18, 18), pygame.SRCALPHA)
            pygame.draw.circle(bloom_surf, glow_col, (9, 9), 8)
            surface.blit(bloom_surf, (x - 9, y - 9))

        # Main LED bulb
        core_col = led_col if is_on else (40, 50, 40)
        pygame.draw.circle(surface, core_col, (x, y), 4)
        pygame.draw.circle(surface, (20, 20, 25), (x, y), 4, width=1)
        if is_on:
            surface.set_at((x - 1, y - 1), (255, 255, 255)) # Hot spot

        if label:
            txt = self.render_text(label, 7, PALETTE["text_gray"])
            surface.blit(txt, (x + 8, y - 4))

    def draw_scanlines(self, surface: pygame.Surface, intensity: int = 40):
        if intensity <= 0:
            return
        w, h = surface.get_size()
        if self._scanline_surface is None or self._last_screen_size != (w, h):
            self._last_screen_size = (w, h)
            self._scanline_surface = pygame.Surface((w, h), pygame.SRCALPHA)
            alpha = max(10, min(180, int(intensity * 1.4)))
            line_color = (0, 0, 0, alpha)
            for y in range(0, h, 3):
                pygame.draw.line(self._scanline_surface, line_color, (0, y), (w, y))

            # CRT Edge Vignette (Simulate curved Trinitron CRT shadow)
            vignette = pygame.Surface((w, h), pygame.SRCALPHA)
            corner_w = 40
            for i in range(corner_w):
                v_alpha = int((1.0 - (i / corner_w)) * 110)
                c_edge = (0, 0, 0, v_alpha)
                # Outer borders
                pygame.draw.rect(vignette, c_edge, (i, i, w - i * 2, h - i * 2), width=1)
            self._scanline_surface.blit(vignette, (0, 0))

        surface.blit(self._scanline_surface, (0, 0))

    def draw_cartridge(self, surface: pygame.Surface, rect: pygame.Rect, system_id: str, title: str = "", custom_image: pygame.Surface = None):
        """Draws realistic 3D rendered cartridge with sticker reflection and drop shadow."""
        if system_id == "neogeo":
            self._draw_neogeo_cartridge(surface, rect, title, custom_image)
        elif system_id == "megadrive":
            self._draw_megadrive_cartridge(surface, rect, title, custom_image)
        else:
            self._draw_snes_cartridge(surface, rect, title, custom_image)

    def _draw_snes_cartridge(self, surface: pygame.Surface, rect: pygame.Rect, title: str, custom_image: pygame.Surface):
        x, y, w, h = rect.x, rect.y, rect.width, rect.height

        # Drop shadow underneath cartridge
        shadow_rect = pygame.Rect(x + 6, y + h - 6, w - 12, 10)
        pygame.draw.ellipse(surface, (8, 6, 14, 180), shadow_rect)

        # Cartridge Body (SNES Classic Gray with realistic bevels)
        cart_color = PALETTE["snes_gray"]
        cart_dark = PALETTE["snes_dark_gray"]
        pygame.draw.rect(surface, cart_color, (x, y, w, h - 4), border_radius=8)
        
        # 3D Highlight & Shadow on plastic
        pygame.draw.line(surface, (230, 232, 240), (x + 2, y + 1), (x + w - 3, y + 1), 2)
        pygame.draw.line(surface, (60, 62, 72), (x + 2, y + h - 5), (x + w - 3, y + h - 5), 2)

        # Left & Right Grip Grooves
        groove_w = max(6, int(w * 0.08))
        pygame.draw.rect(surface, cart_dark, (x + 5, y + 10, groove_w, h - 22), border_radius=2)
        pygame.draw.rect(surface, cart_dark, (x + w - groove_w - 5, y + 10, groove_w, h - 22), border_radius=2)

        # Bottom connector notch
        pygame.draw.rect(surface, (20, 20, 24), (x + int(w * 0.28), y + h - 14, int(w * 0.44), 10))

        # Sticker Label Area
        label_rect = pygame.Rect(x + groove_w + 10, y + 14, w - (groove_w * 2) - 20, int(h * 0.68))
        pygame.draw.rect(surface, (18, 18, 22), label_rect, border_radius=3)

        if custom_image:
            scaled = pygame.transform.smoothscale(custom_image, (label_rect.width - 4, label_rect.height - 4))
            surface.blit(scaled, (label_rect.x + 2, label_rect.y + 2))
        else:
            # Authentic SNES Red Stripe and Label
            pygame.draw.rect(surface, (45, 42, 60), (label_rect.x + 2, label_rect.y + 2, label_rect.width - 4, label_rect.height - 4))
            snes_strip = pygame.Rect(label_rect.x + 4, label_rect.y + 4, label_rect.width - 8, 15)
            pygame.draw.rect(surface, (225, 40, 50), snes_strip)
            banner = self.render_text("SUPER NINTENDO", 7, PALETTE["text_white"])
            surface.blit(banner, (snes_strip.x + 4, snes_strip.y + 3))

            short_title = title[:16] if len(title) > 16 else title
            txt = self.render_text(short_title, 9, PALETTE["text_white"], PALETTE["border_dark"])
            txt_x = label_rect.x + (label_rect.width - txt.get_width()) // 2
            txt_y = label_rect.y + (label_rect.height - txt.get_height()) // 2 + 6
            surface.blit(txt, (txt_x, txt_y))

        # Glossy diagonal shine overlay across the cartridge label
        sheen_surf = pygame.Surface((label_rect.width - 4, label_rect.height - 4), pygame.SRCALPHA)
        pygame.draw.polygon(sheen_surf, (255, 255, 255, 38), [
            (0, 0), (int(label_rect.width * 0.35), 0),
            (0, int(label_rect.height * 0.70))
        ])
        surface.blit(sheen_surf, (label_rect.x + 2, label_rect.y + 2))

        # Molded "Nintendo" logo relief text at the bottom
        nintendo_txt = self.render_text("Nintendo", 6, (140, 142, 152))
        surface.blit(nintendo_txt, (x + (w - nintendo_txt.get_width()) // 2, y + h - 18))

    def _draw_megadrive_cartridge(self, surface: pygame.Surface, rect: pygame.Rect, title: str, custom_image: pygame.Surface):
        x, y, w, h = rect.x, rect.y, rect.width, rect.height

        # Drop shadow underneath cartridge
        shadow_rect = pygame.Rect(x + 6, y + h - 6, w - 12, 10)
        pygame.draw.ellipse(surface, (8, 6, 14, 180), shadow_rect)

        # Classic black Mega Drive rounded cartridge
        body_color = PALETTE["sega_black"]
        pygame.draw.rect(surface, body_color, (x, y, w, h - 4),
                         border_top_left_radius=16, border_top_right_radius=16,
                         border_bottom_left_radius=4, border_bottom_right_radius=4)
        
        # Subtle rim highlight
        pygame.draw.rect(surface, (55, 58, 70), (x, y, w, h - 4), width=2,
                         border_top_left_radius=16, border_top_right_radius=16)

        # Vertical top grip ridges
        for i in range(5):
            gx = x + int(w * 0.22) + (i * 12)
            pygame.draw.line(surface, (45, 45, 55), (gx, y + 6), (gx, y + 15), 2)

        # Label area
        label_rect = pygame.Rect(x + 12, y + 24, w - 24, int(h * 0.68))
        pygame.draw.rect(surface, (15, 15, 20), label_rect)

        if custom_image:
            scaled = pygame.transform.smoothscale(custom_image, (label_rect.width - 4, label_rect.height - 4))
            surface.blit(scaled, (label_rect.x + 2, label_rect.y + 2))
        else:
            # Classic red/blue grid pattern
            pygame.draw.rect(surface, PALETTE["sega_blue"], (label_rect.x + 2, label_rect.y + 2, label_rect.width - 4, label_rect.height - 4))
            grid_bar = pygame.Rect(label_rect.x + 4, label_rect.y + 4, label_rect.width - 8, 14)
            pygame.draw.rect(surface, PALETTE["sega_red"], grid_bar)
            sega_banner = self.render_text("SEGA MEGA DRIVE", 7, PALETTE["text_white"])
            surface.blit(sega_banner, (grid_bar.x + 4, grid_bar.y + 3))

            short_title = title[:16] if len(title) > 16 else title
            txt = self.render_text(short_title, 9, PALETTE["sonic_gold"], (0, 0, 0))
            txt_x = label_rect.x + (label_rect.width - txt.get_width()) // 2
            txt_y = label_rect.y + (label_rect.height - txt.get_height()) // 2 + 6
            surface.blit(txt, (txt_x, txt_y))

        # Glossy diagonal shine overlay across label
        sheen_surf = pygame.Surface((label_rect.width - 4, label_rect.height - 4), pygame.SRCALPHA)
        pygame.draw.polygon(sheen_surf, (255, 255, 255, 38), [
            (0, 0), (int(label_rect.width * 0.35), 0),
            (0, int(label_rect.height * 0.70))
        ])
        surface.blit(sheen_surf, (label_rect.x + 2, label_rect.y + 2))

        # Molded "SEGA" logo relief text at the bottom
        sega_txt = self.render_text("SEGA", 7, (75, 80, 95))
        surface.blit(sega_txt, (x + (w - sega_txt.get_width()) // 2, y + h - 18))

    def _draw_neogeo_cartridge(self, surface: pygame.Surface, rect: pygame.Rect, title: str, custom_image: pygame.Surface):
        x, y, w, h = rect.x, rect.y, rect.width, rect.height

        # Drop shadow underneath cartridge
        shadow_rect = pygame.Rect(x + 6, y + h - 6, w - 12, 10)
        pygame.draw.ellipse(surface, (8, 6, 14, 180), shadow_rect)

        # Huge MVS/AES textured matte black cartridge body
        body_color = (20, 18, 22)
        pygame.draw.rect(surface, body_color, (x, y, w, h - 4), border_radius=6)
        
        # Outer bezel highlight & shadow
        pygame.draw.rect(surface, (50, 48, 56), (x, y, w, h - 4), width=2, border_radius=6)
        pygame.draw.line(surface, (80, 78, 88), (x + 4, y + 2), (x + w - 5, y + 2), 1)

        # Prominent twin-cartridge handle grips on left & right
        grip_w = max(7, int(w * 0.08))
        pygame.draw.rect(surface, (32, 30, 38), (x + 4, y + 8, grip_w, h - 20), border_radius=3)
        pygame.draw.rect(surface, (32, 30, 38), (x + w - grip_w - 4, y + 8, grip_w, h - 20), border_radius=3)
        for i in range(4):
            gy = y + 16 + (i * 12)
            pygame.draw.line(surface, (15, 14, 18), (x + 6, gy), (x + 4 + grip_w - 2, gy), 2)
            pygame.draw.line(surface, (15, 14, 18), (x + w - grip_w - 2, gy), (x + w - 6, gy), 2)

        # Bottom connector notch
        pygame.draw.rect(surface, (12, 12, 16), (x + int(w * 0.25), y + h - 12, int(w * 0.50), 8))

        # Big arcade label area
        label_rect = pygame.Rect(x + grip_w + 8, y + 14, w - (grip_w * 2) - 16, int(h * 0.68))
        pygame.draw.rect(surface, (10, 10, 12), label_rect)

        if custom_image:
            scaled = pygame.transform.smoothscale(custom_image, (label_rect.width - 4, label_rect.height - 4))
            surface.blit(scaled, (label_rect.x + 2, label_rect.y + 2))
        else:
            # Iconic SNK Red & Gold Neo Geo arcade style banner
            pygame.draw.rect(surface, (35, 16, 22), (label_rect.x + 2, label_rect.y + 2, label_rect.width - 4, label_rect.height - 4))
            
            top_bar = pygame.Rect(label_rect.x + 4, label_rect.y + 4, label_rect.width - 8, 15)
            pygame.draw.rect(surface, PALETTE["neogeo_red"], top_bar)
            snk_banner = self.render_text("SNK NEO-GEO", 7, PALETTE["neogeo_gold"])
            surface.blit(snk_banner, (top_bar.x + 4, top_bar.y + 3))

            spec_bar = pygame.Rect(label_rect.x + 4, label_rect.y + 22, label_rect.width - 8, 12)
            pygame.draw.rect(surface, (18, 14, 20), spec_bar)
            spec_txt = self.render_text("MAX 330 MEGA", 6, PALETTE["gold_highlight"])
            surface.blit(spec_txt, (spec_bar.x + (spec_bar.width - spec_txt.get_width()) // 2, spec_bar.y + 2))

            short_title = title[:16] if len(title) > 16 else title
            txt = self.render_text(short_title, 9, PALETTE["text_white"], (0, 0, 0))
            txt_x = label_rect.x + (label_rect.width - txt.get_width()) // 2
            txt_y = label_rect.y + (label_rect.height - txt.get_height()) // 2 + 10
            surface.blit(txt, (txt_x, txt_y))

        # Glossy diagonal shine overlay across label
        sheen_surf = pygame.Surface((label_rect.width - 4, label_rect.height - 4), pygame.SRCALPHA)
        pygame.draw.polygon(sheen_surf, (255, 255, 255, 38), [
            (0, 0), (int(label_rect.width * 0.35), 0),
            (0, int(label_rect.height * 0.70))
        ])
        surface.blit(sheen_surf, (label_rect.x + 2, label_rect.y + 2))

        # Molded "SNK" logo relief text at the bottom
        snk_txt = self.render_text("SNK", 7, (90, 85, 100))
        surface.blit(snk_txt, (x + (w - snk_txt.get_width()) // 2, y + h - 18))

    def draw_snes_controller_preview(self, surface: pygame.Surface, center_x: int, center_y: int, highlight_btn: str = None):
        """Draws an authentic SNES controller diagram with button highlights."""
        w, h = 340, 140
        x = center_x - w // 2
        y = center_y - h // 2

        # Controller body (SNES gray with rounded dog-bone shape)
        body_color = PALETTE["snes_gray"]
        pygame.draw.rect(surface, body_color, (x + 20, y + 10, w - 40, h - 20), border_radius=30)
        pygame.draw.circle(surface, body_color, (x + 50, y + 70), 50)
        pygame.draw.circle(surface, body_color, (x + w - 50, y + 70), 50)
        pygame.draw.rect(surface, PALETTE["border_dark"], (x + 18, y + 8, w - 36, h - 16), width=3, border_radius=30)

        # L and R Shoulder Buttons
        l_color = PALETTE["gold_highlight"] if highlight_btn == "L" else PALETTE["snes_dark_gray"]
        r_color = PALETTE["gold_highlight"] if highlight_btn == "R" else PALETTE["snes_dark_gray"]
        pygame.draw.rect(surface, l_color, (x + 40, y - 2, 70, 10), border_radius=4)
        pygame.draw.rect(surface, r_color, (x + w - 110, y - 2, 70, 10), border_radius=4)
        surface.blit(self.render_text("L", 8, PALETTE["text_white"]), (x + 68, y - 1))
        surface.blit(self.render_text("R", 8, PALETTE["text_white"]), (x + w - 78, y - 1))

        # D-PAD (Left side)
        dpad_x, dpad_y = x + 50, y + 70
        d_color = PALETTE["snes_dark_gray"]
        arm_w, arm_h = 24, 70
        pygame.draw.rect(surface, d_color, (dpad_x - arm_w//2, dpad_y - arm_h//2, arm_w, arm_h), border_radius=3)
        pygame.draw.rect(surface, d_color, (dpad_x - arm_h//2, dpad_y - arm_w//2, arm_h, arm_w), border_radius=3)
        
        # Highlight specific dpad direction
        if highlight_btn == "UP":
            pygame.draw.rect(surface, PALETTE["gold_highlight"], (dpad_x - 10, dpad_y - 32, 20, 16))
        elif highlight_btn == "DOWN":
            pygame.draw.rect(surface, PALETTE["gold_highlight"], (dpad_x - 10, dpad_y + 16, 20, 16))
        elif highlight_btn == "LEFT":
            pygame.draw.rect(surface, PALETTE["gold_highlight"], (dpad_x - 32, dpad_y - 10, 16, 20))
        elif highlight_btn == "RIGHT":
            pygame.draw.rect(surface, PALETTE["gold_highlight"], (dpad_x + 16, dpad_y - 10, 16, 20))

        # Center: Select & Start buttons (Slanted pills)
        sel_color = PALETTE["gold_highlight"] if highlight_btn == "SELECT" else PALETTE["snes_dark_gray"]
        sta_color = PALETTE["gold_highlight"] if highlight_btn == "START" else PALETTE["snes_dark_gray"]
        
        pygame.draw.rect(surface, sel_color, (x + 125, y + 75, 26, 8), border_radius=4)
        pygame.draw.rect(surface, sta_color, (x + 165, y + 75, 26, 8), border_radius=4)
        surface.blit(self.render_text("SELECT", 7, PALETTE["text_dark"]), (x + 115, y + 90))
        surface.blit(self.render_text("START", 7, PALETTE["text_dark"]), (x + 163, y + 90))

        # Right side: 4 Action Buttons (Diamond layout: X top, Y left, B bottom, A right)
        ab_cx, ab_cy = x + w - 50, y + 70
        btn_radius = 12

        buttons = [
            ("X", ab_cx, ab_cy - 22, PALETTE["btn_x_blue"]),
            ("Y", ab_cx - 24, ab_cy, PALETTE["btn_y_green"]),
            ("B", ab_cx, ab_cy + 22, PALETTE["btn_b_yellow"]),
            ("A", ab_cx + 24, ab_cy, PALETTE["btn_a_red"]),
        ]

        for name, bx, by, col in buttons:
            fill_col = PALETTE["gold_highlight"] if highlight_btn == name else col
            pygame.draw.circle(surface, fill_col, (bx, by), btn_radius)
            pygame.draw.circle(surface, PALETTE["border_dark"], (bx, by), btn_radius, width=2)
            lbl = self.render_text(name, 8, PALETTE["text_white"])
            surface.blit(lbl, (bx - lbl.get_width()//2, by - lbl.get_height()//2))

    def draw_megadrive_controller_preview(self, surface: pygame.Surface, center_x: int, center_y: int, highlight_btn: str = None):
        """Draws an authentic Sega Mega Drive 6-button controller diagram with button highlights."""
        w, h = 340, 140
        x = center_x - w // 2
        y = center_y - h // 2

        # Controller body (Sleek matte charcoal/black with ergonomic curves)
        body_color = (28, 28, 34)
        border_col = (55, 58, 72)
        pygame.draw.rect(surface, body_color, (x + 16, y + 14, w - 32, h - 26), border_radius=36)
        pygame.draw.circle(surface, body_color, (x + 55, y + 70), 52)
        pygame.draw.circle(surface, body_color, (x + w - 55, y + 70), 52)
        pygame.draw.rect(surface, border_col, (x + 14, y + 12, w - 28, h - 22), width=3, border_radius=36)

        # Decorative Sega Red arc over button cluster
        pygame.draw.arc(surface, PALETTE["sega_red"], (x + w - 110, y + 26, 92, 34), 0.2, 2.9, width=3)

        # MODE button (Top right edge)
        mode_color = PALETTE["gold_highlight"] if highlight_btn == "MODE" else (48, 50, 62)
        pygame.draw.rect(surface, mode_color, (x + w - 85, y + 4, 34, 10), border_radius=4)
        surface.blit(self.render_text("MODE", 7, PALETTE["gold_highlight"] if highlight_btn == "MODE" else PALETTE["text_gray"]), (x + w - 82, y + 16))

        # D-PAD (Left side: circular dish + cross)
        dpad_x, dpad_y = x + 55, y + 70
        pygame.draw.circle(surface, (18, 18, 24), (dpad_x, dpad_y), 35)
        pygame.draw.circle(surface, (45, 48, 60), (dpad_x, dpad_y), 35, width=2)

        # 8-way cross
        cross_color = (40, 42, 52)
        arm_w, arm_h = 22, 60
        pygame.draw.rect(surface, cross_color, (dpad_x - arm_w//2, dpad_y - arm_h//2, arm_w, arm_h), border_radius=3)
        pygame.draw.rect(surface, cross_color, (dpad_x - arm_h//2, dpad_y - arm_w//2, arm_h, arm_w), border_radius=3)

        # Highlight D-pad directions
        if highlight_btn == "UP":
            pygame.draw.rect(surface, PALETTE["gold_highlight"], (dpad_x - 9, dpad_y - 28, 18, 16), border_radius=2)
        elif highlight_btn == "DOWN":
            pygame.draw.rect(surface, PALETTE["gold_highlight"], (dpad_x - 9, dpad_y + 12, 18, 16), border_radius=2)
        elif highlight_btn == "LEFT":
            pygame.draw.rect(surface, PALETTE["gold_highlight"], (dpad_x - 28, dpad_y - 9, 16, 18), border_radius=2)
        elif highlight_btn == "RIGHT":
            pygame.draw.rect(surface, PALETTE["gold_highlight"], (dpad_x + 12, dpad_y - 9, 16, 18), border_radius=2)

        # Center: START button (Red pill) & SEGA label
        sta_color = PALETTE["gold_highlight"] if highlight_btn == "START" else PALETTE["sega_red"]
        start_x, start_y = x + 135, y + 54
        pygame.draw.rect(surface, sta_color, (start_x, start_y, 28, 11), border_radius=5)
        sta_txt = self.render_text("START", 7, PALETTE["gold_highlight"] if highlight_btn == "START" else PALETTE["text_white"])
        surface.blit(sta_txt, (start_x + (28 - sta_txt.get_width()) // 2, start_y + 14))

        sega_txt = self.render_text("SEGA", 9, (80, 85, 105))
        surface.blit(sega_txt, (start_x + (28 - sega_txt.get_width()) // 2, start_y + 32))

        # Right side: 6 Action Buttons (Arc layout)
        # Top Row (X, Y, Z) - slightly smaller (r=10)
        top_buttons = [
            ("X", x + w - 92, y + 52),
            ("Y", x + w - 64, y + 48),
            ("Z", x + w - 36, y + 43),
        ]
        for name, bx, by in top_buttons:
            is_hl = (highlight_btn == name)
            f_col = PALETTE["gold_highlight"] if is_hl else (45, 48, 60)
            pygame.draw.circle(surface, f_col, (bx, by), 10)
            pygame.draw.circle(surface, PALETTE["border_dark"], (bx, by), 10, width=2)
            lbl = self.render_text(name, 7, (0, 0, 0) if is_hl else PALETTE["text_white"])
            surface.blit(lbl, (bx - lbl.get_width()//2, by - lbl.get_height()//2))

        # Bottom Row (A, B, C) - iconic primary buttons (r=12)
        bottom_buttons = [
            ("A", x + w - 94, y + 84, (40, 42, 55)),
            ("B", x + w - 64, y + 80, (40, 42, 55)),
            ("C", x + w - 34, y + 74, (40, 42, 55)),
        ]
        for name, bx, by, col in bottom_buttons:
            is_hl = (highlight_btn == name)
            f_col = PALETTE["gold_highlight"] if is_hl else col
            pygame.draw.circle(surface, f_col, (bx, by), 12)
            pygame.draw.circle(surface, (60, 64, 80), (bx, by), 12, width=2)
            lbl = self.render_text(name, 8, (0, 0, 0) if is_hl else PALETTE["text_white"])
            surface.blit(lbl, (bx - lbl.get_width()//2, by - lbl.get_height()//2))

    def draw_neogeo_controller_preview(self, surface: pygame.Surface, center_x: int, center_y: int, highlight_btn: str = None):
        """Draws an authentic SNK Neo Geo Arcade Stick diagram with 4-button curved layout."""
        w, h = 340, 140
        x = center_x - w // 2
        y = center_y - h // 2

        # Arcade Stick Heavy Chassis
        body_color = (22, 20, 26)
        border_col = (60, 58, 70)
        pygame.draw.rect(surface, body_color, (x + 10, y + 8, w - 20, h - 16), border_radius=12)
        pygame.draw.rect(surface, border_col, (x + 10, y + 8, w - 20, h - 16), width=2, border_radius=12)

        # Industrial chassis bolts at corners
        for bx, by in [(x + 18, y + 16), (x + w - 18, y + 16), (x + 18, y + h - 16), (x + w - 18, y + h - 16)]:
            pygame.draw.circle(surface, PALETTE["screw_slot"], (bx, by), 3)
            pygame.draw.circle(surface, PALETTE["screw_head"], (bx, by), 2)

        # Neo Geo Brand Header Bar in center-top
        logo_txt = self.render_text("NEO-GEO ARCADE STICK", 7, PALETTE["neogeo_gold"])
        surface.blit(logo_txt, (center_x - logo_txt.get_width() // 2, y + 14))

        # Left side: Classic Ball-top Arcade Joystick
        joy_cx, joy_cy = x + 65, y + 74
        # Dust cover / base ring
        pygame.draw.circle(surface, (14, 14, 18), (joy_cx, joy_cy + 8), 28)
        pygame.draw.circle(surface, (40, 42, 50), (joy_cx, joy_cy + 8), 28, width=2)
        # Metallic shaft
        pygame.draw.line(surface, (160, 165, 180), (joy_cx, joy_cy + 8), (joy_cx, joy_cy - 12), 5)
        # Red ball-top
        is_stick_hl = highlight_btn in ("UP", "DOWN", "LEFT", "RIGHT")
        ball_col = PALETTE["gold_highlight"] if is_stick_hl else PALETTE["neogeo_btn_a"]
        pygame.draw.circle(surface, ball_col, (joy_cx, joy_cy - 14), 16)
        pygame.draw.circle(surface, (30, 10, 10), (joy_cx, joy_cy - 14), 16, width=2)
        # Specular shine on ball
        surface.set_at((joy_cx - 4, joy_cy - 18), (255, 255, 255))
        surface.set_at((joy_cx - 5, joy_cy - 18), (255, 255, 255))
        surface.set_at((joy_cx - 4, joy_cy - 17), (255, 255, 255))

        # Directional arrows around joystick
        dpad_dirs = [
            ("UP", joy_cx, joy_cy - 36),
            ("DOWN", joy_cx, joy_cy + 34),
            ("LEFT", joy_cx - 36, joy_cy + 8),
            ("RIGHT", joy_cx + 36, joy_cy + 8),
        ]
        for dname, dx, dy in dpad_dirs:
            dcol = PALETTE["gold_highlight"] if highlight_btn == dname else PALETTE["text_gray"]
            dtxt = self.render_text(dname[0], 7, dcol)
            surface.blit(dtxt, (dx - dtxt.get_width() // 2, dy - dtxt.get_height() // 2))

        # Center: SELECT (COIN) and START buttons
        sel_color = PALETTE["gold_highlight"] if highlight_btn == "SELECT" else (48, 50, 62)
        sta_color = PALETTE["gold_highlight"] if highlight_btn == "START" else (48, 50, 62)

        sel_x, sel_y = x + 128, y + 68
        sta_x, sta_y = x + 172, y + 68

        pygame.draw.circle(surface, sel_color, (sel_x, sel_y), 8)
        pygame.draw.circle(surface, (15, 15, 20), (sel_x, sel_y), 8, width=2)
        sel_lbl = self.render_text("SEL", 6, PALETTE["gold_highlight"] if highlight_btn == "SELECT" else PALETTE["text_gray"])
        surface.blit(sel_lbl, (sel_x - sel_lbl.get_width() // 2, sel_y + 11))

        pygame.draw.circle(surface, sta_color, (sta_x, sta_y), 8)
        pygame.draw.circle(surface, (15, 15, 20), (sta_x, sta_y), 8, width=2)
        sta_lbl = self.render_text("START", 6, PALETTE["gold_highlight"] if highlight_btn == "START" else PALETTE["text_gray"])
        surface.blit(sta_lbl, (sta_x - sta_lbl.get_width() // 2, sta_y + 11))

        # Right side: 4 Iconic Curved Arcade Buttons (A=Red, B=Yellow, C=Green, D=Blue)
        buttons = [
            ("A", x + w - 108, y + 84, PALETTE["neogeo_btn_a"]),
            ("B", x + w - 82,  y + 72, PALETTE["neogeo_btn_b"]),
            ("C", x + w - 56,  y + 64, PALETTE["neogeo_btn_c"]),
            ("D", x + w - 30,  y + 60, PALETTE["neogeo_btn_d"]),
        ]
        btn_radius = 12

        for name, bx, by, col in buttons:
            is_hl = (highlight_btn == name)
            f_col = PALETTE["gold_highlight"] if is_hl else col
            # Rim ring
            pygame.draw.circle(surface, (16, 16, 20), (bx, by), btn_radius + 2)
            pygame.draw.circle(surface, (45, 48, 60), (bx, by), btn_radius + 2, width=1)
            # Button body
            pygame.draw.circle(surface, f_col, (bx, by), btn_radius)
            pygame.draw.circle(surface, (10, 10, 10), (bx, by), btn_radius, width=2)
            # Button letter
            lbl_col = (0, 0, 0) if is_hl or col == PALETTE["neogeo_btn_b"] else PALETTE["text_white"]
            lbl = self.render_text(name, 8, lbl_col)
            surface.blit(lbl, (bx - lbl.get_width() // 2, by - lbl.get_height() // 2))
