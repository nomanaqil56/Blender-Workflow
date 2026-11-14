"""N-Panel Sidebar Interface for Blender AI Studio in 3D Viewport."""

import bpy
from blender.addon.connection_manager import connection_manager
from blender.addon.scene_inspector import get_quick_status

class BAIS_PT_AgentPanel(bpy.types.Panel):
    bl_label = "Blender AI Studio Agent"
    bl_idname = "BAIS_PT_agent_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AI Studio'

    def draw(self, context):
        layout = self.layout

        # 1. Connection Status Box
        box = layout.box()
        box.label(text="Agent Bridge", icon='RADIOBUT_ON' if connection_manager.is_running else 'RADIOBUT_OFF')
        row = box.row(align=True)
        if connection_manager.is_running:
            row.label(text=f"Listening: {connection_manager.host}:{connection_manager.port}", icon='CHECKMARK')
            row.operator("bais.stop_server", text="Disconnect", icon='PAUSE')
        else:
            row.label(text="Bridge Inactive", icon='ERROR')
            row.operator("bais.start_server", text="Connect", icon='PLAY')

        # 2. Scene Quick Status
        box2 = layout.box()
        box2.label(text="Live Scene State", icon='SCENE_DATA')
        status = get_quick_status()
        box2.label(text=f"Objects in Scene: {status.get('object_count')}")
        box2.label(text=f"Active Object: {status.get('active_object')}")
        box2.label(text=f"Render Engine: {status.get('engine')}")

        row2 = box2.row(align=True)
        row2.operator("bais.inspect_scene_ui", text="Inspect Scene", icon='VIEWZOOM')

        # 3. Model & Hardware Profile
        box3 = layout.box()
        box3.label(text="Local AI Stack", icon='DESKTOP')
        box3.label(text="GPU: RTX 5060 8GB VRAM")
        box3.label(text="Model: Qwen2.5-Coder-7B (LM Studio)")

classes = (
    BAIS_PT_AgentPanel,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
