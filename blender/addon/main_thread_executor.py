"""Main thread executor running via bpy.app.timers to safely dispatch bpy commands."""

import bpy
import traceback
import sys
from pathlib import Path
from typing import Dict, Any

from blender.addon.task_queue import task_queue

# Map of action names to tool functions
TOOL_MAP = {}

def init_tool_map():
    global TOOL_MAP
    try:
        from blender.tools import (
            scene_tools, object_tools, mesh_tools,
            modifier_tools, material_tools, camera_tools,
            lighting_tools, render_tools, file_tools,
            uv_tools, geometry_nodes_tools
        )

        TOOL_MAP = {
            "inspect_scene": scene_tools.inspect_scene,
            "inspect_object": scene_tools.inspect_object,
            "create_object": object_tools.create_object,
            "delete_object": object_tools.delete_object,
            "select_object": object_tools.select_object,
            "transform_object": object_tools.transform_object,
            "duplicate_object": object_tools.duplicate_object,
            "create_mesh": mesh_tools.create_mesh,
            "create_truncated_icosahedron": mesh_tools.create_truncated_icosahedron,
            "edit_mesh": mesh_tools.edit_mesh,
            "extrude": mesh_tools.extrude,
            "inset": mesh_tools.inset,
            "bevel": mesh_tools.bevel,
            "subdivide": mesh_tools.subdivide,
            "add_modifier": modifier_tools.add_modifier,
            "configure_modifier": modifier_tools.configure_modifier,
            "apply_modifier": modifier_tools.apply_modifier,
            "create_material": material_tools.create_material,
            "assign_material": material_tools.assign_material,
            "setup_camera": camera_tools.setup_camera,
            "setup_light": lighting_tools.setup_light,
            "render_preview": render_tools.render_preview,
            "capture_viewport": render_tools.capture_viewport,
            "save_project": file_tools.save_project,
            "export_asset": file_tools.export_asset,
            "uv_unwrap": uv_tools.uv_unwrap,
            "add_geometry_nodes": geometry_nodes_tools.add_geometry_nodes,
        }
    except Exception as e:
        print(f"[Blender AI Studio] Error importing tools in executor: {e}")

def main_thread_timer_tick() -> float:
    """Timer callback invoked by Blender's main loop."""
    if not TOOL_MAP:
        init_tool_map()

    cmd = task_queue.get_next()
    if cmd:
        action = cmd.action
        params = cmd.params or {}
        try:
            if action in TOOL_MAP:
                handler = TOOL_MAP[action]
                result = handler(**params)
                cmd.result = result
            elif action == "undo":
                bpy.ops.ed.undo()
                cmd.result = {"status": "SUCCESS", "action": "undo"}
            elif action == "redo":
                bpy.ops.ed.redo()
                cmd.result = {"status": "SUCCESS", "action": "redo"}
            else:
                cmd.result = {"status": "ERROR", "message": f"Unknown tool action: '{action}'"}
        except Exception as e:
            trace = traceback.format_exc()
            print(f"[MainThreadExecutor Error on {action}]:\n{trace}")
            cmd.result = {"status": "ERROR", "message": str(e), "traceback": trace}
        finally:
            cmd.done_event.set()

    return 0.02  # Run every 20ms

_is_timer_registered = False

def start_main_thread_timer():
    global _is_timer_registered
    if not _is_timer_registered:
        bpy.app.timers.register(main_thread_timer_tick, persistent=True)
        _is_timer_registered = True
        print("[Blender AI Studio] Main thread executor timer registered.")

def stop_main_thread_timer():
    global _is_timer_registered
    if _is_timer_registered:
        try:
            bpy.app.timers.unregister(main_thread_timer_tick)
        except Exception:
            pass
        _is_timer_registered = False
        print("[Blender AI Studio] Main thread executor timer unregistered.")
