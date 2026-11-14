"""Image capture interface for viewport and production renders."""

from pathlib import Path
from typing import Optional
from blender.controller.blender_controller import blender_controller
from config.settings import RENDERS_DIR

class ImageCapture:
    def capture_viewport(self, filename: str = "agent_viewport.png") -> Optional[Path]:
        res = blender_controller.execute_tool("capture_viewport", {"output_filename": filename})
        if res.status == "SUCCESS":
            return Path(res.data.get("output_path", ""))
        return None

    def capture_render(self, filename: str = "agent_render.png", samples: int = 32) -> Optional[Path]:
        res = blender_controller.execute_tool("render_preview", {"output_filename": filename, "samples": samples})
        if res.status == "SUCCESS":
            return Path(res.data.get("output_path", ""))
        return None

image_capture = ImageCapture()
