"""Autonomous Agent loop coordinating planning, execution, and observation."""

import time
from typing import Dict, Any, Optional
from core.task_state import Task, TaskStatus
from core.task_manager import task_manager
from ai.brain.planner import planner
from ai.brain.executor import executor
from ai.brain.context_manager import context_manager
from blender.controller.blender_controller import blender_controller
from core.logger import logger

class Agent:
    def __init__(self):
        self.context_mgr = context_manager
        self.planner = planner
        self.executor = executor

    def process_instruction(self, instruction: str) -> Task:
        """Main entry point: execute an instruction from start to finish."""
        logger.info(f"Agent received instruction: '{instruction}'")

        # Ensure Blender connection
        if not blender_controller.is_connected():
            logger.info("Blender not connected, attempting to connect...")
            if not blender_controller.connect():
                logger.info("Attempting to launch Blender GUI...")
                blender_controller.launch_blender_gui()

        # Step 1: Create Task
        task = task_manager.create_task(instruction)

        # Step 2: Observe Scene Context
        scene_ctx = self.context_mgr.refresh_scene_context()

        # Step 3: Plan
        plan = self.planner.create_plan(task.task_id, instruction, scene_ctx)
        task_manager.set_plan(task.task_id, plan)

        # Step 4: Execute
        success = self.executor.execute_plan(task)

        # Step 5: Post-Execution Observation
        self.context_mgr.refresh_scene_context()
        logger.info(f"Task {task.task_id} completed with status: {task.status}")

        return task

agent = Agent()
