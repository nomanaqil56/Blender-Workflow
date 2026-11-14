"""Test Suite: Live Blender GUI Control and Tool Execution."""

import unittest
import time
from pathlib import Path
from blender.controller.blender_controller import blender_controller

class TestLiveGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        connected = blender_controller.connect()
        assert connected, "Blender GUI must be running and connected."
        cls.obj_name = f"LiveCube_{int(time.time())}"

    @classmethod
    def tearDownClass(cls):
        blender_controller.disconnect()

    def test_01_create_cube_in_gui(self):
        """Create a cube in the open GUI session."""
        res = blender_controller.execute_tool("create_object", {
            "primitive_type": "cube",
            "name": self.obj_name,
            "location": [1.0, 2.0, 0.5]
        })
        self.assertEqual(res.status, "SUCCESS")
        self.assertEqual(res.data.get("object_name"), self.obj_name)

    def test_02_inspect_created_cube(self):
        """Inspect the cube created in the GUI."""
        res = blender_controller.inspect_object(self.obj_name)
        self.assertEqual(res.get("status"), "SUCCESS")
        data = res.get("data", {})
        self.assertEqual(data.get("name"), self.obj_name)
        self.assertEqual(data.get("vertices_count"), 8)
        self.assertEqual(data.get("polygons_count"), 6)

    def test_03_transform_cube(self):
        """Transform the cube in the GUI."""
        res = blender_controller.execute_tool("transform_object", {
            "object_name": self.obj_name,
            "location": [2.0, 3.0, 1.0],
            "scale": [1.5, 1.5, 1.5]
        })
        self.assertEqual(res.status, "SUCCESS")

    def test_04_capture_viewport(self):
        """Capture viewport screenshot from GUI."""
        filename = "test_live_gui_capture.png"
        res = blender_controller.execute_tool("capture_viewport", {
            "output_filename": filename
        })
        self.assertEqual(res.status, "SUCCESS")
        saved_path = Path(res.data.get("output_path", ""))
        self.assertTrue(saved_path.exists())

if __name__ == "__main__":
    unittest.main()
