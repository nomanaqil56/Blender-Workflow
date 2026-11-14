"""Blender Environment Configuration and Communication Settings."""

import os
from pathlib import Path
from typing import Optional

BLENDER_HOST = "127.0.0.1"
BLENDER_PORT = 9855
SOCKET_TIMEOUT = 10.0
COMMAND_TIMEOUT = 60.0

# Blender Paths
LOCAL_APPDATA = os.environ.get("LOCALAPPDATA", "")
APPDATA = os.environ.get("APPDATA", "")

CANDIDATE_EXECUTABLES = [
    Path(LOCAL_APPDATA) / "Microsoft" / "WindowsApps" / "blender-launcher.exe",
    Path(r"C:\Program Files\WindowsApps\BlenderFoundation.Blender_5.3.0.0_x64__ppwjx1n5r4v9t\Blender\blender.exe"),
    Path(r"C:\Program Files\Blender Foundation\Blender 5.3\blender.exe"),
    Path(r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"),
]

BLENDER_ADDON_DIR = Path(APPDATA) / "Blender Foundation" / "Blender" / "5.3" / "scripts" / "addons" / "blender_ai_studio"

def get_blender_executable() -> Optional[Path]:
    """Find the valid Blender executable on the system."""
    for exe in CANDIDATE_EXECUTABLES:
        if exe.exists():
            return exe
    return None
