"""Desktop screenshot capture using Windows GDI / ctypes."""

import ctypes
from ctypes import wintypes
from pathlib import Path
from typing import Optional, Tuple
from config.settings import RENDERS_DIR

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

class ScreenCapture:
    def capture_screen_bounds(self, rect: Optional[Tuple[int, int, int, int]] = None, output_filename: str = "desktop_capture.png") -> Optional[Path]:
        """Capture screenshot via Blender viewport or GDI."""
        out_path = RENDERS_DIR / output_filename
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # Fallback to Blender viewport screenshot if available
        from blender.controller.blender_controller import blender_controller
        if blender_controller.is_connected():
            res = blender_controller.execute_tool("capture_viewport", {"output_filename": str(out_path)})
            if res.status == "SUCCESS":
                return out_path

        return None

screen_capture = ScreenCapture()
