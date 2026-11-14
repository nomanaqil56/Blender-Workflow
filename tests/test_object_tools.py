"""Test Suite: Object Tools against live Blender session."""

import unittest
import time
from blender.controller.blender_controller import blender_controller

class TestObjectTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        blender_controller.connect()

    def test_01_create_primitives(self):
        """Create UV Sphere, Cylinder, and Plane."""
        for ptype in ["uv_sphere", "cylinder", "plane"]:
            name = f"Test_{ptype}_{int(time.time()*1000)%10000}"
            res = blender_controller.execute_tool("create_object", {
                "primitive_type": ptype,
                "name": name,
                "location": [0.0, 0.0, 0.0]
            })
            self.assertEqual(res.status, "SUCCESS")
            self.assertEqual(res.data.get("object_name"), name)

    def test_02_duplicate_and_transform(self):
        """Duplicate an object and transform it."""
        base_name = f"BaseObj_{int(time.time()*1000)%10000}"
        blender_controller.execute_tool("create_object", {"primitive_type": "cube", "name": base_name})

        dup_name = base_name + "_copy"
        res_dup = blender_controller.execute_tool("duplicate_object", {
            "source_name": base_name,
            "new_name": dup_name,
            "location_offset": [2.0, 0.0, 0.0]
        })
        self.assertEqual(res_dup.status, "SUCCESS")

        res_tf = blender_controller.execute_tool("transform_object", {
            "object_name": dup_name,
            "scale": [2.0, 2.0, 2.0]
        })
        self.assertEqual(res_tf.status, "SUCCESS")

    def test_03_delete_object_safety(self):
        """Verify delete_object fails without confirm=True and succeeds with confirm=True."""
        del_target = f"DelTarget_{int(time.time()*1000)%10000}"
        blender_controller.execute_tool("create_object", {"primitive_type": "cube", "name": del_target})

        # Attempt delete without confirm
        res_fail = blender_controller.execute_tool("delete_object", {"object_name": del_target, "confirm": False})
        self.assertEqual(res_fail.status, "ERROR")
        self.assertIn("confirm=True", res_fail.error_message)

        # Delete with confirm
        res_ok = blender_controller.execute_tool("delete_object", {"object_name": del_target, "confirm": True})
        self.assertEqual(res_ok.status, "SUCCESS")
        self.assertEqual(res_ok.data.get("deleted"), del_target)

if __name__ == "__main__":
    unittest.main()
