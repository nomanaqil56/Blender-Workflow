"""Test Suite: Phase 3 Essential Test - Natural Language to Tool Execution in Live Blender GUI."""

import unittest
from ai.brain.agent import agent
from blender.controller.blender_controller import blender_controller
from core.task_state import TaskStatus

class TestTaskExecution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        blender_controller.connect()
        insp = blender_controller.inspect_scene()
        for o in insp.get("objects", []):
            if "cylinder" in o["name"].lower():
                blender_controller.execute_tool("delete_object", {"object_name": o["name"], "confirm": True})

    def test_01_primitive_cylinder_workflow(self):
        """Execute natural language instruction: 'Create a blue cylinder, move it two units up, and add a bevel modifier.'"""
        instruction = "Create a blue cylinder, move it two units up, and add a bevel modifier."
        task = agent.process_instruction(instruction)

        # 1. Verify Task Status
        self.assertEqual(task.status, TaskStatus.COMPLETED)

        # 2. Verify Plan Steps
        self.assertIsNotNone(task.plan)
        step_tools = [s.tool_name for s in task.plan.steps]
        self.assertIn("create_object", step_tools)
        self.assertIn("create_material", step_tools)
        self.assertIn("assign_material", step_tools)
        self.assertIn("transform_object", step_tools)
        self.assertIn("add_modifier", step_tools)

        # 3. Verify in Blender Scene Data
        created_obj_name = task.history[0].data.get("object_name", "Object_Cylinder")
        obj_res = blender_controller.inspect_object(created_obj_name)
        self.assertEqual(obj_res.get("status"), "SUCCESS")
        data = obj_res.get("data", {})
        self.assertEqual(data.get("name"), created_obj_name)
        self.assertTrue(any(abs(coord - 2.0) < 0.1 for coord in data.get("location", [])))

        # 4. Verify Bevel Modifier exists
        mod_types = [m.get("type") for m in data.get("modifiers", [])]
        mod_names = [m.get("name", "").lower() for m in data.get("modifiers", [])]
        self.assertTrue("BEVEL" in mod_types or any("bevel" in n for n in mod_names))

if __name__ == "__main__":
    unittest.main()
