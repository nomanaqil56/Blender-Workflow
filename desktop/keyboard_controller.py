"""Windows native keyboard input automation using ctypes SendInput."""

import ctypes
import time
from typing import List

user32 = ctypes.windll.user32

KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004

class KeyboardController:
    def send_key(self, vk_code: int):
        user32.keybd_event(vk_code, 0, 0, 0)
        time.sleep(0.02)
        user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)

    def type_text(self, text: str):
        for ch in text:
            user32.keybd_event(0, ord(ch), KEYEVENTF_UNICODE, 0)
            time.sleep(0.01)
            user32.keybd_event(0, ord(ch), KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0)

    def send_hotkey(self, modifier_vks: List[int], key_vk: int):
        for mod in modifier_vks:
            user32.keybd_event(mod, 0, 0, 0)
        user32.keybd_event(key_vk, 0, 0, 0)
        time.sleep(0.02)
        user32.keybd_event(key_vk, 0, KEYEVENTF_KEYUP, 0)
        for mod in reversed(modifier_vks):
            user32.keybd_event(mod, 0, KEYEVENTF_KEYUP, 0)

keyboard_controller = KeyboardController()
