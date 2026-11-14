"""System status view displaying Blender, AI Model, and GPU metrics."""

from blender.controller.blender_controller import blender_controller
from ai.models.model_manager import model_manager
from config.settings import HARDWARE_PROFILE

class StatusView:
    def format_system_banner(self) -> str:
        blender_connected = blender_controller.is_connected()
        model_status = model_manager.get_status()

        b_icon = "[CONNECTED]" if blender_connected else "[DISCONNECTED]"
        ai_icon = "[ONLINE]" if model_status.get("api_healthy") else "[OFFLINE (Semantic Planner Active)]"

        lines = [
            "=" * 60,
            "            BLENDER AI STUDIO - AUTONOMOUS AGENT",
            "=" * 60,
            f" Blender GUI Bridge: {b_icon} (127.0.0.1:9855)",
            f" Local AI Model:     {ai_icon} Qwen2.5-Coder-7B",
            f" Hardware Profile:   {HARDWARE_PROFILE['gpu_name']} ({HARDWARE_PROFILE['total_vram_gb']}GB VRAM)",
            f" System Memory:      {HARDWARE_PROFILE['system_ram_gb']}GB RAM | {HARDWARE_PROFILE['cpu_model']}",
            "=" * 60
        ]
        return "\n".join(lines)

status_view = StatusView()
