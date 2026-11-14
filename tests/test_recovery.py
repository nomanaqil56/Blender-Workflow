"""Test Suite: Iterative Agent, Follow-up Modifying, Recovery, and Cancellation."""

import unittest
from ai.brain.agent import agent
from blender.controller.blender_controller import blender_controller
from core.task_manager import task_manager
from core.task_state import TaskStatus

class TestRecoveryAndIteration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        blender_controller.connect()

    def test_01_multi_turn_follow_up_modification(self):
        """Verify follow-up instruction edits the existing object instead of duplicating."""
        # Initial task
        t1 = agent.process_instruction("Create a cylinder primitive")
        self.assertEqual(t1.status, TaskStatus.COMPLETED)

        initial_scene = blender_controller.inspect_scene()
        initial_count = initial_scene.get("total_objects", 0)

        # Follow-up task referencing the cylinder
        t2 = agent.process_instruction("Improve this model with a bevel modifier")
        self.assertEqual(t2.status, TaskStatus.COMPLETED)

        updated_scene = blender_controller.inspect_scene()
        updated_count = updated_scene.get("total_objects", 0)

        # Object count should not have increased by a duplicate cylinder
        self.assertEqual(initial_count, updated_count, "Follow-up command should modify existing object, not duplicate it.")

    def test_02_task_cancellation(self):
        """Verify task cancellation sets task status to CANCELLED."""
        task = task_manager.create_task("Long running task to cancel")
        task_manager.cancel_task(task.task_id)
        self.assertEqual(task.status, TaskStatus.CANCELLED)

if __name__ == "__main__":
    unittest.main()
