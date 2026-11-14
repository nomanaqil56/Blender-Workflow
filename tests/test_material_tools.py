"""Test Suite: Material, Modifier, Lighting, and Export Tools."""

import unittest
import time
from pathlib import Path
from blender.controller.blender_controller import blender_controller
from config.settings import PROJECTS_DIR, EXPORTS_DIR

class TestMaterialTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        blender_controller.connect()

    def test_01_material_creation_and_assignment(self):
        """Create a custom PBR material and assign it to an object."""
        obj_name = f"MatCube_{int(time.time()*1000)%10000}"
        mat_name = f"PBR_Gold_{int(time.time()*1000)%10000}"

        blender_controller.execute_tool("create_object", {"primitive_type": "cube", "name": obj_name})

        # Create material
        res_mat = blender_controller.execute_tool("create_material", {
            "material_name": mat_name,
            "base_color": [1.0, 0.766, 0.336, 1.0],
            "metallic": 0.95,
            "roughness": 0.2
        })
        self.assertEqual(res_mat.status, "SUCCESS")

        # Assign material
        res_assign = blender_controller.execute_tool("assign_material", {
            "object_name": obj_name,
            "material_name": mat_name
        })
        self.assertEqual(res_assign.status, "SUCCESS")

    def test_02_modifier_stack_operations(self):
        """Add, configure, and apply a Subsurf modifier."""
        obj_name = f"ModCube_{int(time.time()*1000)%10000}"
        blender_controller.execute_tool("create_object", {"primitive_type": "cube", "name": obj_name})

        # Add subsurf
        res_add = blender_controller.execute_tool("add_modifier", {
            "object_name": obj_name,
            "modifier_type": "SUBSURF",
            "modifier_name": "Subdivision",
            "properties": {"levels": 1, "render_levels": 2}
        })
        self.assertEqual(res_add.status, "SUCCESS")

        # Configure
        res_conf = blender_controller.execute_tool("configure_modifier", {
            "object_name": obj_name,
            "modifier_name": "Subdivision",
            "properties": {"levels": 2}
        })
        self.assertEqual(res_conf.status, "SUCCESS")

        # Apply
        res_apply = blender_controller.execute_tool("apply_modifier", {
            "object_name": obj_name,
            "modifier_name": "Subdivision"
        })
        self.assertEqual(res_apply.status, "SUCCESS")

    def test_03_lighting_camera_and_export(self):
        """Setup studio light, camera, and export GLB."""
        # Light
        res_light = blender_controller.execute_tool("setup_light", {
            "light_name": "StudioKeyLight",
            "light_type": "AREA",
            "energy": 600.0,
            "location": [4.0, -4.0, 5.0]
        })
        self.assertEqual(res_light.status, "SUCCESS")

        # Camera
        res_cam = blender_controller.execute_tool("setup_camera", {
            "camera_name": "StudioMainCam",
            "location": [5.0, -5.0, 3.0],
            "focal_length": 50.0
        })
        self.assertEqual(res_cam.status, "SUCCESS")

        # Export GLB
        glb_path = EXPORTS_DIR / "phase2_toolkit_test.glb"
        res_exp = blender_controller.execute_tool("export_asset", {
            "filepath": str(glb_path),
            "format": "glb"
        })
        self.assertEqual(res_exp.status, "SUCCESS")
        self.assertTrue(glb_path.exists())

if __name__ == "__main__":
    unittest.main()
