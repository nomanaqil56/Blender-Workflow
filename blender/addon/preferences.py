"""Addon Preferences for Blender AI Studio."""

import bpy

class BlenderAIStudioPreferences(bpy.types.AddonPreferences):
    bl_idname = "blender_ai_studio"

    host: bpy.props.StringProperty(
        name="Host Address",
        description="Localhost binding address",
        default="127.0.0.1"
    )

    port: bpy.props.IntProperty(
        name="Port",
        description="TCP socket port for agent communication",
        default=9855,
        min=1024,
        max=65535
    )

    auth_token: bpy.props.StringProperty(
        name="Auth Token",
        description="Secret key to authorize incoming commands",
        default="blender_ai_studio_local_token_9855",
        subtype='PASSWORD'
    )

    auto_start_server: bpy.props.BoolProperty(
        name="Auto-start Server",
        description="Automatically start the socket server on Blender launch",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Agent Connection Settings", icon='NETWORK_DRIVE')
        box.prop(self, "host")
        box.prop(self, "port")
        box.prop(self, "auth_token")
        box.prop(self, "auto_start_server")
