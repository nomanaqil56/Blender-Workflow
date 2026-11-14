"""Unified High-Level Blender Controller for AI Studio."""

import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional

from blender.controller.command_client import CommandClient
from blender.controller.session_manager import session_manager
from config.blender_config import get_blender_executable, BLENDER_HOST, BLENDER_PORT
from core.logger import logger
from core.task_state import ToolResult

class BlenderController:
    def __init__(self, host: str = BLENDER_HOST, port: int = BLENDER_PORT):
        self.client = CommandClient(host=host, port=port)

    def connect(self) -> bool:
        return self.client.connect()

    def disconnect(self):
        self.client.disconnect()

    def is_connected(self) -> bool:
        return self.client.is_connected()

    def ping(self) -> Dict[str, Any]:
        return self.client.send_command("ping", {})

    def inspect_scene(self, detailed: bool = True) -> Dict[str, Any]:
        res = self.client.send_command("inspect_scene", {"detailed": detailed})
        if res.get("status") == "SUCCESS":
            session_manager.update_from_inspection(res)
        return res

    def inspect_object(self, object_name: str = "") -> Dict[str, Any]:
        return self.client.send_command("inspect_object", {"object_name": object_name})

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> ToolResult:
        """Execute a registered tool and return structured ToolResult."""
        start_time = time.time()
        res = self.client.send_command(tool_name, parameters)
        elapsed = round(time.time() - start_time, 3)

        status = res.get("status", "ERROR")
        error_msg = res.get("message") if status == "ERROR" else None
        call_id = res.get("call_id", "")

        return ToolResult(
            call_id=call_id,
            tool_name=tool_name,
            status=status,
            data=res,
            error_message=error_msg,
            execution_time_sec=elapsed
        )

    def launch_blender_gui(self, blend_file: Optional[Path] = None) -> bool:
        """Launch desktop Blender GUI with the AI Studio addon enabled."""
        exe = get_blender_executable()
        if not exe:
            logger.error("No valid Blender executable found.")
            return False

        cmd = [str(exe)]
        if blend_file and Path(blend_file).exists():
            cmd.append(str(blend_file))

        # Pass python command to ensure addon is active
        cmd.extend(["--python-expr", "import bpy; bpy.ops.preferences.addon_enable(module='blender_ai_studio') if 'blender_ai_studio' not in bpy.context.preferences.addons else None; print('[Blender AI Studio] GUI Ready.')"])

        logger.info(f"Launching desktop Blender GUI: {' '.join(cmd)}")
        try:
            subprocess.Popen(cmd)
            # Wait up to 15s for socket server to become available
            for _ in range(30):
                time.sleep(0.5)
                if self.is_connected():
                    logger.info("Successfully connected to live Blender GUI!")
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to launch Blender: {e}")
            return False

blender_controller = BlenderController()
