"""Test Suite: Phase 3 Essential Test - Natural Language to Tool Execution in Live Blender GUI."""

import unittest
from ai.brain.agent import agent
from blender.controller.blender_controller import blender_controller
from core.task_state import TaskStatus

class TestTaskExecution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        blender_controller.connect()

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
        obj_res = blender_controller.inspect_object("Object_Cylinder")
        self.assertEqual(obj_res.get("status"), "SUCCESS")
        data = obj_res.get("data", {})
        self.assertEqual(data.get("name"), "Object_Cylinder")
        self.assertAlmostEqual(data.get("location")[2], 2.0, places=2)

        # 4. Verify Bevel Modifier exists
        mod_names = [m["name"] for m in data.get("modifiers", [])]
        self.assertIn("Bevel", mod_names)

if __name__ == "__main__":
    unittest.main()
