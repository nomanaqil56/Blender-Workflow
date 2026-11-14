"""Operators for Blender AI Studio addon UI."""

import bpy
from blender.addon.connection_manager import connection_manager
from blender.addon.main_thread_executor import start_main_thread_timer, stop_main_thread_timer
from blender.tools.scene_tools import inspect_scene

class BAIS_OT_StartServer(bpy.types.Operator):
    bl_idname = "bais.start_server"
    bl_label = "Start Agent Bridge"
    bl_description = "Start the background socket server for AI Studio communication"

    def execute(self, context):
        start_main_thread_timer()
        connection_manager.start()
        self.report({'INFO'}, f"Blender AI Studio server active on {connection_manager.host}:{connection_manager.port}")
        return {'FINISHED'}

class BAIS_OT_StopServer(bpy.types.Operator):
    bl_idname = "bais.stop_server"
    bl_label = "Stop Agent Bridge"
    bl_description = "Stop the background socket server"

    def execute(self, context):
        connection_manager.stop()
        stop_main_thread_timer()
        self.report({'INFO'}, "Blender AI Studio server stopped.")
        return {'FINISHED'}

class BAIS_OT_InspectScene(bpy.types.Operator):
    bl_idname = "bais.inspect_scene_ui"
    bl_label = "Inspect Scene"
    bl_description = "Query active scene elements"

    def execute(self, context):
        res = inspect_scene(detailed=True)
        self.report({'INFO'}, f"Objects: {res.get('total_objects', 0)}, Active: {res.get('active_object')}")
        return {'FINISHED'}

classes = (
    BAIS_OT_StartServer,
    BAIS_OT_StopServer,
    BAIS_OT_InspectScene,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
