"""Test Suite: Mesh Operations against live Blender session."""

import unittest
import time
from blender.controller.blender_controller import blender_controller

class TestMeshTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        blender_controller.connect()

    def test_01_create_custom_mesh(self):
        """Create custom mesh from explicit vertices and faces."""
        name = f"CustomPyramid_{int(time.time()*1000)%10000}"
        verts = [
            [-1.0, -1.0, 0.0],
            [1.0, -1.0, 0.0],
            [1.0, 1.0, 0.0],
            [-1.0, 1.0, 0.0],
            [0.0, 0.0, 1.5]
        ]
        faces = [
            [0, 1, 2, 3],
            [0, 1, 4],
            [1, 2, 4],
            [2, 3, 4],
            [3, 0, 4]
        ]
        res = blender_controller.execute_tool("create_mesh", {
            "name": name,
            "vertices": verts,
            "faces": faces
        })
        self.assertEqual(res.status, "SUCCESS")
        self.assertEqual(res.data.get("vertices_count"), 5)
        self.assertEqual(res.data.get("faces_count"), 5)

    def test_02_mesh_editing_operations(self):
        """Test subdivide, bevel, and smooth on a cube."""
        obj_name = f"MeshOpsCube_{int(time.time()*1000)%10000}"
        blender_controller.execute_tool("create_object", {"primitive_type": "cube", "name": obj_name})

        # Subdivide
        res_sub = blender_controller.execute_tool("subdivide", {"object_name": obj_name, "cuts": 1})
        self.assertEqual(res_sub.status, "SUCCESS")

        # Bevel
        res_bev = blender_controller.execute_tool("bevel", {"object_name": obj_name, "offset": 0.05, "segments": 2})
        self.assertEqual(res_bev.status, "SUCCESS")

        # Edit mesh: recalculate normals and shade smooth
        res_norm = blender_controller.execute_tool("edit_mesh", {"object_name": obj_name, "operation": "recalculate_normals"})
        self.assertEqual(res_norm.status, "SUCCESS")

        res_smooth = blender_controller.execute_tool("edit_mesh", {"object_name": obj_name, "operation": "shade_smooth"})
        self.assertEqual(res_smooth.status, "SUCCESS")

if __name__ == "__main__":
    unittest.main()
