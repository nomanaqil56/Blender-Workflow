"""Execution driver running plan steps through the tool executor."""

import time
from typing import Dict, Any, List
from core.task_state import Task, TaskStep, TaskStatus, ToolResult
from core.task_manager import task_manager
from ai.brain.decision_engine import decision_engine
from ai.brain.error_recovery import error_recovery
from core.logger import logger

class Executor:
    def execute_plan(self, task: Task) -> bool:
        if not task.plan:
            logger.error("No plan attached to task.")
            return False

        logger.info(f"Starting plan execution for task {task.task_id} ({len(task.plan.steps)} steps)")
        for idx, step in enumerate(task.plan.steps):
            task.current_step_index = idx + 1
            logger.info(f"Step {idx+1}/{len(task.plan.steps)}: {step.description} [{step.tool_name}]")

            result: ToolResult = task_manager.execute_step(task.task_id, step)

            success, decision, info = decision_engine.evaluate_step_result(result)
            if not success:
                logger.warning(f"Step {idx+1} failed ({result.error_message}). Decision: {decision}")
                recovery_step = error_recovery.plan_recovery_step(step, info)
                if recovery_step:
                    logger.info(f"Attempting recovery: {recovery_step.description}")
                    rec_result = task_manager.execute_step(task.task_id, recovery_step)
                    if rec_result.status != "SUCCESS":
                        task_manager.fail_task(task.task_id, f"Step {idx+1} and recovery failed: {result.error_message}")
                        return False
                else:
                    task_manager.fail_task(task.task_id, f"Step {idx+1} failed: {result.error_message}")
                    return False

        task_manager.complete_task(task.task_id)
        return True

executor = Executor()
