bl_info = {
    "name": "Blender AI Studio",
    "author": "Antigravity Engineering",
    "version": (2, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > AI Studio",
    "description": "Autonomous AI Agent for live desktop Blender control with main-thread safety",
    "category": "3D View",
}

import sys
from pathlib import Path
import bpy

# Ensure Studio Root is on sys.path
STUDIO_ROOT = Path(r"D:\AI Local\Blender AI Studio")
if str(STUDIO_ROOT) not in sys.path:
    sys.path.insert(0, str(STUDIO_ROOT))

from blender.addon import preferences, operators, panels
from blender.addon.connection_manager import connection_manager
from blender.addon.main_thread_executor import start_main_thread_timer, stop_main_thread_timer

def register():
    bpy.utils.register_class(preferences.BlenderAIStudioPreferences)
    operators.register()
    panels.register()

    # Start timer and socket listener automatically
    try:
        start_main_thread_timer()
        connection_manager.start()
        print("[Blender AI Studio] Autonomous Agent Addon registered and live.")
    except Exception as e:
        print(f"[Blender AI Studio] Error starting bridge during register: {e}")

def unregister():
    try:
        connection_manager.stop()
        stop_main_thread_timer()
    except Exception as e:
        print(f"[Blender AI Studio] Error stopping bridge: {e}")

    panels.unregister()
    operators.unregister()
    bpy.utils.unregister_class(preferences.BlenderAIStudioPreferences)
    print("[Blender AI Studio] Addon unregistered.")

if __name__ == "__main__":
    register()
