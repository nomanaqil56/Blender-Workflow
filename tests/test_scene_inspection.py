"""Test Suite: Scene and Object Inspection Tools."""

import unittest
from blender.controller.blender_controller import blender_controller

class TestSceneInspection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        blender_controller.connect()

    def test_01_scene_overview(self):
        """Query general scene overview."""
        res = blender_controller.inspect_scene(detailed=True)
        self.assertEqual(res.get("status"), "SUCCESS")
        self.assertGreater(res.get("total_objects", 0), 0)
        self.assertIn("objects", res)

    def test_02_manifold_and_mesh_stats(self):
        """Verify non-manifold check and vertex count on an active mesh."""
        # Create a clean cube
        blender_controller.execute_tool("create_object", {"primitive_type": "cube", "name": "ManifoldCheckCube"})
        inspect_res = blender_controller.inspect_object("ManifoldCheckCube")
        self.assertEqual(inspect_res.get("status"), "SUCCESS")
        data = inspect_res.get("data", {})
        self.assertEqual(data.get("non_manifold_edges"), 0)
        self.assertEqual(data.get("vertices_count"), 8)

if __name__ == "__main__":
    unittest.main()
