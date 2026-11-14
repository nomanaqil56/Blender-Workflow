"""Main application controller tying UI, agent, and storage together."""

from typing import Dict, Any
from ai.brain.agent import agent
from blender.controller.blender_controller import blender_controller
from storage.task_store import task_store
from core.task_state import Task
from core.logger import logger

class Application:
    def __init__(self):
        self.agent = agent
        self.controller = blender_controller

    def execute_prompt(self, prompt: str) -> Task:
        logger.info(f"Application executing prompt: '{prompt}'")
        task = self.agent.process_instruction(prompt)
        # Persist task record
        task_store.save_task({
            "task_id": task.task_id,
            "prompt": task.prompt,
            "status": task.status.value,
            "step_count": len(task.plan.steps) if task.plan else 0,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "artifacts": task.artifacts
        })
        return task

application = Application()
