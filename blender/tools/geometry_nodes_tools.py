"""Geometry Nodes modifier creation and parameter exposure tools."""

import bpy
from typing import Dict, Any

def add_geometry_nodes(object_name: str, modifier_name: str = "GeometryNodes", **kwargs) -> Dict[str, Any]:
    """Add a Geometry Nodes modifier and initialize node group."""
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {"status": "ERROR", "message": f"Object '{object_name}' not found."}

    mod = obj.modifiers.new(name=modifier_name, type='NODES')
    group = bpy.data.node_groups.new(name=f"{object_name}_GN", type='GeometryNodeTree')
    mod.node_group = group

    # Create input and output nodes
    in_node = group.nodes.new('NodeGroupInput')
    out_node = group.nodes.new('NodeGroupOutput')
    in_node.location = (-200, 0)
    out_node.location = (200, 0)

    return {
        "status": "SUCCESS",
        "object_name": obj.name,
        "modifier_name": mod.name,
        "node_group": group.name
    }
