"""Unified Desktop Automation Controller with Process and Window Integration."""

from typing import Optional, Dict, Any, Tuple
from desktop.window_manager import window_manager
from desktop.mouse_controller import mouse_controller
from desktop.keyboard_controller import keyboard_controller
from desktop.screen_capture import screen_capture
from core.logger import logger

class DesktopController:
    def __init__(self):
        self.window = window_manager
        self.mouse = mouse_controller
        self.keyboard = keyboard_controller
        self.screen = screen_capture

    def get_blender_window_info(self) -> Dict[str, Any]:
        proc = self.window.find_blender_process()
        hwnd = self.window.find_blender_window()
        rect = self.window.get_window_rect(hwnd) if hwnd else None

        return {
            "found": proc is not None or hwnd is not None,
            "pid": proc.pid if proc else None,
            "process_name": proc.name() if proc else None,
            "hwnd": hwnd,
            "rect": rect,
            "width": rect[2] - rect[0] if rect else 0,
            "height": rect[3] - rect[1] if rect else 0
        }

    def focus_blender(self) -> bool:
        info = self.get_blender_window_info()
        if info.get("hwnd"):
            return self.window.bring_to_front(info["hwnd"])
        return info.get("found", False)

desktop_controller = DesktopController()
