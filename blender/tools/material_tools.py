"""Material creation, shader node editing, and slot assignment tools."""

import bpy
from typing import Dict, Any, List, Optional

def create_material(material_name: str, base_color: Optional[List[float]] = None,
                    metallic: float = 0.0, roughness: float = 0.4, specular: float = 0.5,
                    transmission: float = 0.0, emission_color: Optional[List[float]] = None,
                    emission_strength: float = 0.0, **kwargs) -> Dict[str, Any]:
    """Create a high-quality PBR material using Principled BSDF."""
    mat = bpy.data.materials.get(material_name)
    if not mat:
        mat = bpy.data.materials.new(name=material_name)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    principled = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)

    if not principled:
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        output = nodes.get('Material Output') or nodes.new(type='ShaderNodeOutputMaterial')
        mat.node_tree.links.new(principled.outputs['BSDF'], output.inputs['Surface'])

    # Set base color
    if base_color is not None:
        rgba = list(base_color)
        if len(rgba) == 3:
            rgba.append(1.0)
        principled.inputs['Base Color'].default_value = rgba

    # Set PBR inputs with Blender version compatibility
    if 'Metallic' in principled.inputs:
        principled.inputs['Metallic'].default_value = float(metallic)
    if 'Roughness' in principled.inputs:
        principled.inputs['Roughness'].default_value = float(roughness)
    if 'Specular IOR Level' in principled.inputs:
        principled.inputs['Specular IOR Level'].default_value = float(specular)
    elif 'Specular' in principled.inputs:
        principled.inputs['Specular'].default_value = float(specular)
    if 'Transmission Weight' in principled.inputs:
        principled.inputs['Transmission Weight'].default_value = float(transmission)
    elif 'Transmission' in principled.inputs:
        principled.inputs['Transmission'].default_value = float(transmission)

    if emission_strength > 0:
        if 'Emission Strength' in principled.inputs:
            principled.inputs['Emission Strength'].default_value = float(emission_strength)
        if emission_color and 'Emission Color' in principled.inputs:
            ec = list(emission_color)
            if len(ec) == 3:
                ec.append(1.0)
            principled.inputs['Emission Color'].default_value = ec

    return {
        "status": "SUCCESS",
        "material_name": mat.name,
        "metallic": metallic,
        "roughness": roughness
    }

def assign_material(object_name: str, material_name: str, slot_index: int = 0, **kwargs) -> Dict[str, Any]:
    """Assign an existing material to an object slot."""
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {"status": "ERROR", "message": f"Object '{object_name}' not found."}

    mat = bpy.data.materials.get(material_name)
    if not mat:
        return {"status": "ERROR", "message": f"Material '{material_name}' not found."}

    # Ensure enough slots
    while len(obj.data.materials) <= slot_index:
        obj.data.materials.append(None)

    obj.data.materials[slot_index] = mat
    return {"status": "SUCCESS", "object_name": obj.name, "material_name": mat.name, "slot_index": slot_index}
