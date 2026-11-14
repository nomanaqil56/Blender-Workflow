"""Windows native window detection and process monitor using ctypes and psutil."""

import ctypes
from ctypes import wintypes
import psutil
from typing import Optional, Tuple, Dict, Any

user32 = ctypes.windll.user32

class WindowManager:
    def __init__(self):
        self.user32 = user32

    def find_blender_process(self) -> Optional[psutil.Process]:
        for p in psutil.process_iter(['name', 'pid']):
            if "blender" in p.info['name'].lower():
                try:
                    return p
                except Exception:
                    pass
        return None

    def find_blender_window(self) -> Optional[int]:
        blender_hwnd = None

        def enum_windows_proc(hwnd, lParam):
            nonlocal blender_hwnd
            if self.user32.IsWindowVisible(hwnd):
                length = self.user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    self.user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value
                    if "blender" in title.lower():
                        blender_hwnd = hwnd
                        return False
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        self.user32.EnumWindows(WNDENUMPROC(enum_windows_proc), 0)
        return blender_hwnd

    def get_window_rect(self, hwnd: int) -> Optional[Tuple[int, int, int, int]]:
        rect = wintypes.RECT()
        if self.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return (rect.left, rect.top, rect.right, rect.bottom)
        return None

    def bring_to_front(self, hwnd: int) -> bool:
        if not hwnd:
            return False
        self.user32.ShowWindow(hwnd, 9)
        return bool(self.user32.SetForegroundWindow(hwnd))

window_manager = WindowManager()
