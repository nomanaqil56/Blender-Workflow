"""
Blender AI Studio - Blender Engine & Socket Server
Runs directly inside Blender Python (bpy).
Provides full scene inspection, procedural modeling, geometry nodes,
material synthesis, Cycles/EEVEE rendering, and asset I/O.
"""

import sys
import os
import json
import socket
import threading
import math
import traceback
from pathlib import Path

try:
    import bpy
    import mathutils
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False
    print("Warning: blender_server.py imported outside Blender environment.")

HOST = "127.0.0.1"
PORT = 9855


class BlenderEngine:
    """Core Blender operations handler executing inside bpy."""

    @staticmethod
    def inspect_scene() -> dict:
        """Inspects all objects, lights, cameras, materials, and render settings."""
        scene = bpy.context.scene
        objects_data = []

        for obj in scene.objects:
            obj_info = {
                "name": obj.name,
                "type": obj.type,
                "location": list(obj.location),
                "rotation_euler": [math.degrees(r) for r in obj.rotation_euler],
                "scale": list(obj.scale),
                "dimensions": list(obj.dimensions),
                "visible": obj.visible_get(),
                "materials": [m.name for m in obj.data.materials if m] if hasattr(obj.data, "materials") else [],
            }
            if obj.type == "MESH" and obj.data:
                obj_info["vertices_count"] = len(obj.data.vertices)
                obj_info["polygons_count"] = len(obj.data.polygons)
                obj_info["edges_count"] = len(obj.data.edges)
            objects_data.append(obj_info)

        camera_info = None
        if scene.camera:
            camera_info = {
                "name": scene.camera.name,
                "location": list(scene.camera.location),
                "rotation_euler": [math.degrees(r) for r in scene.camera.rotation_euler],
                "focal_length": scene.camera.data.lens if hasattr(scene.camera.data, "lens") else None
            }

        return {
            "scene_name": scene.name,
            "render_engine": scene.render.engine,
            "resolution": [scene.render.resolution_x, scene.render.resolution_y],
            "camera": camera_info,
            "objects_count": len(objects_data),
            "objects": objects_data
        }

    @staticmethod
    def create_object(obj_type: str = "cube", name: str = None, location=(0, 0, 0),
                      rotation=(0, 0, 0), scale=(1, 1, 1), size: float = 2.0, **kwargs) -> dict:
        """Creates a primitive mesh or empty object in the scene."""
        loc = tuple(location)
        rot = tuple(math.radians(r) for r in rotation)
        obj_type = obj_type.lower()

        if obj_type == "cube":
            bpy.ops.mesh.primitive_cube_add(size=size, location=loc, rotation=rot)
        elif obj_type == "sphere" or obj_type == "uv_sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(radius=size / 2.0, location=loc, rotation=rot)
        elif obj_type == "ico_sphere":
            bpy.ops.mesh.primitive_ico_sphere_add(radius=size / 2.0, location=loc, rotation=rot)
        elif obj_type == "cylinder":
            bpy.ops.mesh.primitive_cylinder_add(radius=size / 2.0, depth=size, location=loc, rotation=rot)
        elif obj_type == "cone":
            bpy.ops.mesh.primitive_cone_add(radius1=size / 2.0, depth=size, location=loc, rotation=rot)
        elif obj_type == "plane":
            bpy.ops.mesh.primitive_plane_add(size=size, location=loc, rotation=rot)
        elif obj_type == "torus":
            bpy.ops.mesh.primitive_torus_add(major_radius=size / 2.0, minor_radius=size / 6.0, location=loc, rotation=rot)
        elif obj_type == "monkey" or obj_type == "suzanne":
            bpy.ops.mesh.primitive_monkey_add(size=size, location=loc, rotation=rot)
        elif obj_type == "empty":
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=loc, rotation=rot)
        else:
            raise ValueError(f"Unsupported primitive type: '{obj_type}'")

        obj = bpy.context.active_object
        if name:
            obj.name = name
        obj.scale = tuple(scale)

        return {
            "status": "success",
            "name": obj.name,
            "type": obj.type,
            "location": list(obj.location),
            "scale": list(obj.scale)
        }

    @staticmethod
    def modify_object(name: str, location=None, rotation=None, scale=None,
                      visible: bool = None, select: bool = None, apply_transforms: bool = False) -> dict:
        """Modifies transformations or visibility of an existing object."""
        if name not in bpy.data.objects:
            raise KeyError(f"Object '{name}' not found in scene.")
        obj = bpy.data.objects[name]

        if location is not None:
            obj.location = tuple(location)
        if rotation is not None:
            obj.rotation_euler = tuple(math.radians(r) for r in rotation)
        if scale is not None:
            obj.scale = tuple(scale)
        if visible is not None:
            obj.hide_viewport = not visible
            obj.hide_render = not visible

        if select:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

        if apply_transforms and obj.type == 'MESH':
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        return {
            "status": "success",
            "name": obj.name,
            "location": list(obj.location),
            "rotation_euler": [math.degrees(r) for r in obj.rotation_euler],
            "scale": list(obj.scale)
        }

    @staticmethod
    def mesh_operations(name: str, action: str, params: dict = None) -> dict:
        """Applies mesh operations (subdivide, boolean, remesh, normals, cleanup)."""
        if name not in bpy.data.objects:
            raise KeyError(f"Object '{name}' not found.")
        obj = bpy.data.objects[name]
        if obj.type != 'MESH':
            raise TypeError(f"Object '{name}' is not a mesh.")

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        params = params or {}
        action = action.lower()

        if action == "subdivide":
            cuts = params.get("cuts", 1)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.subdivide(number_cuts=cuts)
            bpy.ops.object.mode_set(mode='OBJECT')

        elif action == "recalculate_normals":
            inside = params.get("inside", False)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=inside)
            bpy.ops.object.mode_set(mode='OBJECT')

        elif action == "merge_by_distance" or action == "remove_doubles":
            distance = params.get("distance", 0.0001)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=distance)
            bpy.ops.object.mode_set(mode='OBJECT')

        elif action == "shade_smooth":
            bpy.ops.object.shade_smooth()

        elif action == "shade_flat":
            bpy.ops.object.shade_flat()

        elif action == "remesh":
            mode = params.get("mode", "VOXEL")
            voxel_size = params.get("voxel_size", 0.05)
            mod = obj.modifiers.new(name="AutoRemesh", type='REMESH')
            mod.mode = mode
            if mode == 'VOXEL':
                mod.voxel_size = voxel_size
            bpy.ops.object.modifier_apply(modifier=mod.name)

        elif action == "boolean":
            target_name = params.get("target")
            operation = params.get("operation", "DIFFERENCE")  # DIFFERENCE, UNION, INTERSECT
            if target_name not in bpy.data.objects:
                raise KeyError(f"Boolean target '{target_name}' not found.")
            target_obj = bpy.data.objects[target_name]
            mod = obj.modifiers.new(name="AutoBoolean", type='BOOLEAN')
            mod.operation = operation
            mod.object = target_obj
            bpy.ops.object.modifier_apply(modifier=mod.name)

        elif action == "decimate":
            ratio = params.get("ratio", 0.5)
            mod = obj.modifiers.new(name="AutoDecimate", type='DECIMATE')
            mod.ratio = ratio
            bpy.ops.object.modifier_apply(modifier=mod.name)

        else:
            raise ValueError(f"Unknown mesh operation: '{action}'")

        return {
            "status": "success",
            "name": obj.name,
            "action": action,
            "vertices_count": len(obj.data.vertices),
            "polygons_count": len(obj.data.polygons)
        }

    @staticmethod
    def create_material(name: str, pbr_properties: dict = None, assign_to: str = None) -> dict:
        """Creates a complete PBR Principled BSDF material."""
        pbr = pbr_properties or {}
        mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        bsdf = None
        for n in nodes:
            if n.type == 'BSDF_PRINCIPLED':
                bsdf = n
                break
        if not bsdf:
            bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')

        # Set standard Principled BSDF inputs (compatible with Blender 4.x / 5.x)
        if "base_color" in pbr:
            c = pbr["base_color"]
            if len(c) == 3:
                c = (c[0], c[1], c[2], 1.0)
            bsdf.inputs['Base Color'].default_value = c

        if "metallic" in pbr and 'Metallic' in bsdf.inputs:
            bsdf.inputs['Metallic'].default_value = float(pbr["metallic"])
        if "roughness" in pbr and 'Roughness' in bsdf.inputs:
            bsdf.inputs['Roughness'].default_value = float(pbr["roughness"])
        if "ior" in pbr and 'IOR' in bsdf.inputs:
            bsdf.inputs['IOR'].default_value = float(pbr["ior"])
        if "emission_color" in pbr and 'Emission Color' in bsdf.inputs:
            ec = pbr["emission_color"]
            if len(ec) == 3:
                ec = (ec[0], ec[1], ec[2], 1.0)
            bsdf.inputs['Emission Color'].default_value = ec
        if "emission_strength" in pbr and 'Emission Strength' in bsdf.inputs:
            bsdf.inputs['Emission Strength'].default_value = float(pbr["emission_strength"])

        # Assign to object if requested
        if assign_to and assign_to in bpy.data.objects:
            obj = bpy.data.objects[assign_to]
            if obj.type == 'MESH':
                if not obj.data.materials:
                    obj.data.materials.append(mat)
                else:
                    obj.data.materials[0] = mat

        return {
            "status": "success",
            "material_name": mat.name,
            "assigned_to": assign_to
        }

    @staticmethod
    def assign_texture(material_name: str, texture_type: str, image_path: str) -> dict:
        """Assigns an image texture map to a material's PBR shader graph."""
        if material_name not in bpy.data.materials:
            raise KeyError(f"Material '{material_name}' not found.")
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Texture file '{image_path}' does not exist.")

        mat = bpy.data.materials[material_name]
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        bsdf = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if not bsdf:
            raise ValueError(f"Principled BSDF node missing in material '{material_name}'.")

        image = bpy.data.images.load(image_path, check_existing=True)
        tex_node = nodes.new(type='ShaderNodeTexImage')
        tex_node.image = image
        tex_node.location = (bsdf.location.x - 350, bsdf.location.y)

        texture_type = texture_type.lower()
        if texture_type in ["diffuse", "base_color", "albedo"]:
            links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
        elif texture_type == "roughness":
            image.colorspace_settings.name = 'Non-Color'
            links.new(tex_node.outputs['Color'], bsdf.inputs['Roughness'])
        elif texture_type == "metallic":
            image.colorspace_settings.name = 'Non-Color'
            links.new(tex_node.outputs['Color'], bsdf.inputs['Metallic'])
        elif texture_type == "normal":
            image.colorspace_settings.name = 'Non-Color'
            normal_map = nodes.new(type='ShaderNodeNormalMap')
            normal_map.location = (bsdf.location.x - 180, bsdf.location.y - 150)
            links.new(tex_node.outputs['Color'], normal_map.inputs['Color'])
            links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])
        else:
            raise ValueError(f"Unsupported texture type: '{texture_type}'")

        return {
            "status": "success",
            "material": material_name,
            "texture_type": texture_type,
            "image": image.name
        }

    @staticmethod
    def setup_lighting(light_type: str = "SUN", energy: float = 3.0,
                       color=(1.0, 1.0, 1.0), location=(5.0, -5.0, 8.0),
                       rotation=(45.0, 0.0, 45.0), name: str = "StudioLight") -> dict:
        """Creates or configures a scene lamp."""
        light_type = light_type.upper()
        if light_type not in ['POINT', 'SUN', 'SPOT', 'AREA']:
            light_type = 'SUN'

        light_data = bpy.data.lights.get(name) or bpy.data.lights.new(name=name, type=light_type)
        light_data.energy = energy
        light_data.color = tuple(color[:3])
        light_data.type = light_type

        obj = bpy.data.objects.get(name)
        if not obj:
            obj = bpy.data.objects.new(name=name, object_data=light_data)
            bpy.context.collection.objects.link(obj)

        obj.location = tuple(location)
        obj.rotation_euler = tuple(math.radians(r) for r in rotation)

        return {
            "status": "success",
            "name": obj.name,
            "type": light_type,
            "energy": energy,
            "location": list(obj.location)
        }

    @staticmethod
    def setup_camera(location=(7.0, -7.0, 5.0), rotation=(60.0, 0.0, 45.0),
                     focal_length: float = 50.0, look_at: tuple = None, name: str = "Camera") -> dict:
        """Sets up the active scene camera and optionally points it at a target location."""
        cam_data = bpy.data.cameras.get(name) or bpy.data.cameras.new(name=name)
        cam_data.lens = focal_length

        cam_obj = bpy.data.objects.get(name)
        if not cam_obj:
            cam_obj = bpy.data.objects.new(name=name, object_data=cam_data)
            bpy.context.collection.objects.link(cam_obj)

        cam_obj.location = tuple(location)
        bpy.context.scene.camera = cam_obj

        if look_at is not None:
            # Calculate rotation to point at look_at coordinate
            loc = mathutils.Vector(location)
            target = mathutils.Vector(look_at)
            direction = target - loc
            rot_quat = direction.to_track_quat('-Z', 'Y')
            cam_obj.rotation_euler = rot_quat.to_euler()
        else:
            cam_obj.rotation_euler = tuple(math.radians(r) for r in rotation)

        return {
            "status": "success",
            "name": cam_obj.name,
            "location": list(cam_obj.location),
            "rotation_euler": [math.degrees(r) for r in cam_obj.rotation_euler],
            "focal_length": focal_length
        }

    @staticmethod
    def apply_geometry_nodes(object_name: str, node_graph_type: str = "wireframe", params: dict = None) -> dict:
        """Applies a procedural Geometry Nodes modifier tree."""
        if object_name not in bpy.data.objects:
            raise KeyError(f"Object '{object_name}' not found.")
        obj = bpy.data.objects[object_name]
        params = params or {}

        mod = obj.modifiers.new(name=f"GN_{node_graph_type}", type='NODES')
        tree = bpy.data.node_groups.new(name=f"GNTree_{node_graph_type}", type='GeometryNodeTree')
        mod.node_group = tree

        # Define input & output sockets
        tree.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
        tree.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

        input_node = tree.nodes.new(type='NodeGroupInput')
        output_node = tree.nodes.new(type='NodeGroupOutput')
        input_node.location = (-300, 0)
        output_node.location = (400, 0)

        node_graph_type = node_graph_type.lower()
        if node_graph_type == "wireframe" or node_graph_type == "mesh_to_curve":
            m2c = tree.nodes.new(type='GeometryNodeMeshToCurve')
            c2m = tree.nodes.new(type='GeometryNodeCurveToMesh')
            circle = tree.nodes.new(type='GeometryNodeCurvePrimitiveCircle')
            circle.inputs['Radius'].default_value = params.get("radius", 0.02)
            
            tree.links.new(input_node.outputs['Geometry'], m2c.inputs['Mesh'])
            tree.links.new(m2c.outputs['Curve'], c2m.inputs['Curve'])
            tree.links.new(circle.outputs['Curve'], c2m.inputs['Profile Curve'])
            tree.links.new(c2m.outputs['Mesh'], output_node.inputs['Geometry'])

        elif node_graph_type == "subdivision":
            sub = tree.nodes.new(type='GeometryNodeSubdivideMesh')
            sub.inputs['Level'].default_value = params.get("level", 2)
            tree.links.new(input_node.outputs['Geometry'], sub.inputs['Mesh'])
            tree.links.new(sub.outputs['Mesh'], output_node.inputs['Geometry'])

        else:
            # Passthrough
            tree.links.new(input_node.outputs['Geometry'], output_node.inputs['Geometry'])

        return {
            "status": "success",
            "object": obj.name,
            "modifier": mod.name,
            "type": node_graph_type
        }

    @staticmethod
    def render(output_path: str, engine: str = "CYCLES", resolution_x: int = 1280,
               resolution_y: int = 720, samples: int = 64, device: str = "GPU") -> dict:
        """Renders current scene using Cycles (OptiX/CUDA) or EEVEE Next."""
        scene = bpy.context.scene
        scene.render.resolution_x = resolution_x
        scene.render.resolution_y = resolution_y
        scene.render.resolution_percentage = 100
        scene.render.filepath = os.path.abspath(output_path)
        scene.render.image_settings.file_format = 'PNG'

        engine = engine.upper()
        if engine == "CYCLES":
            scene.render.engine = 'CYCLES'
            scene.cycles.samples = samples
            if device.upper() == "GPU":
                scene.cycles.device = 'GPU'
                # Configure OptiX / CUDA preferences
                prefs = bpy.context.preferences
                cprefs = prefs.addons['cycles'].preferences
                cprefs.compute_device_type = 'OPTIX'
                cprefs.get_devices()
                for d in cprefs.devices:
                    d.use = True
            else:
                scene.cycles.device = 'CPU'
        else:
            # Blender 4.2+ / 5.x uses BLENDER_EEVEE_NEXT or BLENDER_EEVEE
            if hasattr(bpy.types, "RenderSettings") and 'BLENDER_EEVEE_NEXT' in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items:
                scene.render.engine = 'BLENDER_EEVEE_NEXT'
            else:
                scene.render.engine = 'BLENDER_EEVEE'

        # Trigger Render
        bpy.ops.render.render(write_still=True)

        if not os.path.isfile(scene.render.filepath):
            # Check with extension
            if os.path.isfile(f"{scene.render.filepath}.png"):
                output_path = f"{scene.render.filepath}.png"

        return {
            "status": "success",
            "filepath": output_path,
            "engine": scene.render.engine,
            "resolution": [resolution_x, resolution_y],
            "samples": samples
        }

    @staticmethod
    def inspect_render(image_path: str) -> dict:
        """Inspects rendered image file for existence, size, and dimensions."""
        if not os.path.isfile(image_path):
            if os.path.isfile(f"{image_path}.png"):
                image_path = f"{image_path}.png"
            else:
                raise FileNotFoundError(f"Render output file '{image_path}' not found.")

        stat = os.stat(image_path)
        img = bpy.data.images.load(image_path, check_existing=True)
        res = [img.size[0], img.size[1]]

        return {
            "status": "success",
            "filepath": image_path,
            "size_bytes": stat.st_size,
            "resolution": res,
            "channels": img.channels
        }

    @staticmethod
    def save_project(filepath: str) -> dict:
        """Saves current scene to .blend file."""
        p = Path(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(p.resolve()))
        return {"status": "success", "filepath": str(p.resolve())}

    @staticmethod
    def import_asset(filepath: str, format: str = None) -> dict:
        """Imports 3D asset file (GLB, OBJ, FBX, STL, PLY)."""
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"Asset file '{filepath}' does not exist.")

        p = Path(filepath)
        fmt = (format or p.suffix.lstrip(".")).lower()
        before_objs = set(bpy.data.objects.keys())

        if fmt in ["glb", "gltf"]:
            bpy.ops.import_scene.gltf(filepath=str(p.resolve()))
        elif fmt == "obj":
            if hasattr(bpy.ops.wm, "obj_import"):
                bpy.ops.wm.obj_import(filepath=str(p.resolve()))
            else:
                bpy.ops.import_scene.obj(filepath=str(p.resolve()))
        elif fmt == "fbx":
            bpy.ops.import_scene.fbx(filepath=str(p.resolve()))
        elif fmt == "stl":
            if hasattr(bpy.ops.wm, "stl_import"):
                bpy.ops.wm.stl_import(filepath=str(p.resolve()))
            else:
                bpy.ops.import_mesh.stl(filepath=str(p.resolve()))
        elif fmt == "ply":
            if hasattr(bpy.ops.wm, "ply_import"):
                bpy.ops.wm.ply_import(filepath=str(p.resolve()))
            else:
                bpy.ops.import_mesh.ply(filepath=str(p.resolve()))
        else:
            raise ValueError(f"Unsupported 3D asset format: '{fmt}'")

        after_objs = set(bpy.data.objects.keys())
        new_objs = list(after_objs - before_objs)

        return {
            "status": "success",
            "filepath": str(p.resolve()),
            "format": fmt,
            "imported_objects": new_objs
        }

    @staticmethod
    def export_asset(filepath: str, format: str = None, selected_only: bool = False) -> dict:
        """Exports scene or selected objects to 3D format (GLB, OBJ, FBX, STL, USDC)."""
        p = Path(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        fmt = (format or p.suffix.lstrip(".")).lower()

        if fmt in ["glb", "gltf"]:
            export_fmt = 'GLB' if fmt == 'glb' else 'GLTF_SEPARATE'
            bpy.ops.export_scene.gltf(
                filepath=str(p.resolve()),
                export_format=export_fmt,
                use_selection=selected_only
            )
        elif fmt == "obj":
            if hasattr(bpy.ops.wm, "obj_export"):
                bpy.ops.wm.obj_export(filepath=str(p.resolve()), export_selected_objects=selected_only)
            else:
                bpy.ops.export_scene.obj(filepath=str(p.resolve()), use_selection=selected_only)
        elif fmt == "fbx":
            bpy.ops.export_scene.fbx(filepath=str(p.resolve()), use_selection=selected_only)
        elif fmt == "stl":
            if hasattr(bpy.ops.wm, "stl_export"):
                bpy.ops.wm.stl_export(filepath=str(p.resolve()), export_selected_objects=selected_only)
            else:
                bpy.ops.export_mesh.stl(filepath=str(p.resolve()), use_selection=selected_only)
        elif fmt in ["usdc", "usd", "usda"]:
            bpy.ops.wm.usd_export(filepath=str(p.resolve()), selected_objects_only=selected_only)
        else:
            raise ValueError(f"Unsupported export format: '{fmt}'")

        return {
            "status": "success",
            "filepath": str(p.resolve()),
            "format": fmt,
            "size_bytes": os.path.getsize(str(p.resolve())) if p.exists() else 0
        }

    @staticmethod
    def execute_script(code: str) -> dict:
        """Safely executes an arbitrary procedural bpy script."""
        exec_globals = {
            "bpy": bpy,
            "mathutils": mathutils,
            "math": math,
            "os": os,
            "sys": sys
        }
        exec_locals = {}
        exec(code, exec_globals, exec_locals)
        result = exec_locals.get("result")
        if result is None:
            result = exec_globals.get("result", "Script executed successfully.")
        return {"status": "success", "result": result}


def handle_request(req_data: dict) -> dict:
    """Dispatches a JSON-RPC method to the BlenderEngine."""
    method = req_data.get("method")
    params = req_data.get("params", {})

    dispatch_table = {
        "inspect_scene": BlenderEngine.inspect_scene,
        "create_object": lambda: BlenderEngine.create_object(**params),
        "modify_object": lambda: BlenderEngine.modify_object(**params),
        "mesh_operations": lambda: BlenderEngine.mesh_operations(**params),
        "create_material": lambda: BlenderEngine.create_material(**params),
        "assign_texture": lambda: BlenderEngine.assign_texture(**params),
        "setup_lighting": lambda: BlenderEngine.setup_lighting(**params),
        "setup_camera": lambda: BlenderEngine.setup_camera(**params),
        "apply_geometry_nodes": lambda: BlenderEngine.apply_geometry_nodes(**params),
        "render": lambda: BlenderEngine.render(**params),
        "inspect_render": lambda: BlenderEngine.inspect_render(**params),
        "save_project": lambda: BlenderEngine.save_project(**params),
        "import_asset": lambda: BlenderEngine.import_asset(**params),
        "export_asset": lambda: BlenderEngine.export_asset(**params),
        "execute_script": lambda: BlenderEngine.execute_script(**params),
    }

    if method not in dispatch_table:
        return {"status": "error", "message": f"Method '{method}' not recognized."}

    try:
        fn = dispatch_table[method]
        result = fn() if callable(fn) else None
        return {"status": "success", "data": result}
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }


def run_socket_server(host=HOST, port=PORT):
    """Starts persistent localhost TCP server inside Blender."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"[Blender AI Studio] Socket bridge listening on {host}:{port}")

    while True:
        try:
            client, addr = server.accept()
            data = b""
            while True:
                chunk = client.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b"\n" in chunk:
                    break

            if data:
                try:
                    req = json.loads(data.decode("utf-8").strip())
                    resp = handle_request(req)
                except Exception as err:
                    resp = {"status": "error", "message": str(err)}
                client.sendall((json.dumps(resp) + "\n").encode("utf-8"))
            client.close()
        except Exception as e:
            print(f"[Blender AI Studio] Server error: {e}")
            break


# CLI one-shot execution support
if __name__ == "__main__" and IN_BLENDER:
    args = sys.argv
    if "--exec-json" in args:
        idx = args.index("--exec-json")
        req_file = args[idx + 1]
        resp_file = args[idx + 2]
        with open(req_file, "r") as f:
            req = json.load(f)
        resp = handle_request(req)
        
        # Auto-save session if requested and successful
        if "--save-session" in args and resp.get("status") == "success":
            save_idx = args.index("--save-session")
            save_target = args[save_idx + 1]
            try:
                os.makedirs(os.path.dirname(os.path.abspath(save_target)), exist_ok=True)
                bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(save_target))
            except Exception as se:
                print(f"[Blender AI Studio] Auto-save session error: {se}")

        with open(resp_file, "w") as f:
            json.dump(resp, f, indent=2)
        print(f"[Blender AI Studio] Processed one-shot request from {req_file}")
    elif "--run-server" in args:
        run_socket_server()
