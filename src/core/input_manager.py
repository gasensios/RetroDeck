"""
Input Manager for RetroDeck.
Handles multi-system keyboard and joystick inputs, hotplugging, and per-system remapping.
"""

import pygame
from typing import Dict, List, Optional, Tuple, Callable

# SNES Virtual Button layout
SNES_BUTTONS: List[Tuple[str, str]] = [
    ("UP", "D-Pad Arriba"),
    ("DOWN", "D-Pad Abajo"),
    ("LEFT", "D-Pad Izquierda"),
    ("RIGHT", "D-Pad Derecha"),
    ("B", "Botón B (Inferior)"),
    ("A", "Botón A (Derecha)"),
    ("Y", "Botón Y (Izquierda)"),
    ("X", "Botón X (Superior)"),
    ("L", "Gatillo L"),
    ("R", "Gatillo R"),
    ("SELECT", "Select"),
    ("START", "Start"),
]

# Sega Mega Drive Virtual Button layout (6-Button Pad)
MEGADRIVE_BUTTONS: List[Tuple[str, str]] = [
    ("UP", "D-Pad Arriba"),
    ("DOWN", "D-Pad Abajo"),
    ("LEFT", "D-Pad Izquierda"),
    ("RIGHT", "D-Pad Derecha"),
    ("A", "Botón A (Fila Inf. Izq)"),
    ("B", "Botón B (Fila Inf. Cen)"),
    ("C", "Botón C (Fila Inf. Der)"),
    ("X", "Botón X (Fila Sup. Izq)"),
    ("Y", "Botón Y (Fila Sup. Cen)"),
    ("Z", "Botón Z (Fila Sup. Der)"),
    ("START", "Start"),
    ("MODE", "Mode"),
]

def get_system_buttons(system_id: str) -> List[Tuple[str, str]]:
    """Returns the button definition list for the requested system."""
    if system_id == "megadrive":
        return MEGADRIVE_BUTTONS
    return SNES_BUTTONS


class InputManager:
    def __init__(self, config_manager):
        self.config = config_manager
        self.joysticks = []
        self.active_joystick = None
        self.mapping_callback: Optional[Callable[[str, str], None]] = None
        self.is_remapping = False
        self.remap_system_id = "snes"
        self.remap_target_type = "keyboard"  # 'keyboard' or 'gamepad'
        self.remap_target_button = None
        
        self.refresh_joysticks()

    def refresh_joysticks(self):
        self.joysticks.clear()
        count = pygame.joystick.get_count()
        for i in range(count):
            try:
                j = pygame.joystick.Joystick(i)
                j.init()
                self.joysticks.append(j)
            except Exception:
                pass
        self.active_joystick = self.joysticks[0] if self.joysticks else None

    def get_controller_name(self) -> str:
        if self.active_joystick:
            return self.active_joystick.get_name()
        return "Teclado (Sin mando detectado)"

    def start_remap(self, system_id: str, input_type: str, button_name: str, callback: Callable[[str, str], None]):
        self.is_remapping = True
        self.remap_system_id = system_id
        self.remap_target_type = input_type
        self.remap_target_button = button_name
        self.mapping_callback = callback

    def cancel_remap(self):
        self.is_remapping = False
        self.remap_target_button = None
        self.mapping_callback = None

    def process_event(self, event, system_id: str = "snes") -> Optional[str]:
        """
        Translates raw pygame event to virtual action ('UP', 'DOWN', 'A', 'B', etc.).
        If in remapping mode, captures the input and invokes the callback.
        """
        # Handle joystick hotplug
        if event.type == pygame.JOYDEVICEADDED or event.type == pygame.JOYDEVICEREMOVED:
            self.refresh_joysticks()
            return None

        # REMAPPING MODE
        if self.is_remapping:
            return self._handle_remap_event(event)

        # NORMAL MODE: Check keyboard
        if event.type == pygame.KEYDOWN:
            # Direct universal navigation shortcuts
            if event.key == pygame.K_UP: return "UP"
            if event.key == pygame.K_DOWN: return "DOWN"
            if event.key == pygame.K_LEFT: return "LEFT"
            if event.key == pygame.K_RIGHT: return "RIGHT"
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE): return "A"
            if event.key == pygame.K_ESCAPE: return "MENU"
            if event.key == pygame.K_BACKSPACE: return "B"

            # Custom mapped keys for active system
            kb_map = self.config.get_input_map(system_id, "keyboard")
            key_name = pygame.key.name(event.key).upper()
            for btn_key, mapped_k in kb_map.items():
                if key_name == str(mapped_k).upper():
                    return btn_key

        # NORMAL MODE: Check Gamepad
        elif event.type == pygame.JOYBUTTONDOWN:
            gp_map = self.config.get_input_map(system_id, "gamepad")
            btn_idx = event.button
            for btn_key, mapped_idx in gp_map.items():
                if isinstance(mapped_idx, int) and mapped_idx == btn_idx:
                    return btn_key

        elif event.type == pygame.JOYHATMOTION:
            # Hat / D-pad
            hat_x, hat_y = event.value
            if hat_y == 1: return "UP"
            elif hat_y == -1: return "DOWN"
            if hat_x == -1: return "LEFT"
            elif hat_x == 1: return "RIGHT"

        elif event.type == pygame.JOYAXISMOTION:
            # Analog stick threshold
            if event.axis == 1: # Vertical axis
                if event.value < -0.5: return "UP"
                elif event.value > 0.5: return "DOWN"
            elif event.axis == 0: # Horizontal axis
                if event.value < -0.5: return "LEFT"
                elif event.value > 0.5: return "RIGHT"

        return None

    def _handle_remap_event(self, event) -> Optional[str]:
        if self.remap_target_type == "keyboard" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.cancel_remap()
                return "CANCEL"
            key_str = pygame.key.name(event.key).upper()
            self.config.set("input", self.remap_system_id, "keyboard", self.remap_target_button, key_str)
            if self.mapping_callback:
                self.mapping_callback(self.remap_target_button, key_str)
            self.cancel_remap()
            return "MAPPED"

        elif self.remap_target_type == "gamepad" and event.type == pygame.JOYBUTTONDOWN:
            btn_id = event.button
            self.config.set("input", self.remap_system_id, "gamepad", self.remap_target_button, btn_id)
            if self.mapping_callback:
                self.mapping_callback(self.remap_target_button, f"Button {btn_id}")
            self.cancel_remap()
            return "MAPPED"

        return None

    def get_button_label(self, system_id: str, input_type: str, button_name: str) -> str:
        inp_map = self.config.get_input_map(system_id, input_type)
        val = inp_map.get(button_name, "")
        if input_type == "keyboard":
            return str(val).upper() if val != "" else "NONE"
        else:
            return f"Btn {val}" if val != "" else "None"
