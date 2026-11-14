"""Lifecycle and state coordinator for autonomous agent tasks."""

import time
import uuid
from typing import Dict, Optional, List
from core.task_state import Task, TaskPlan, TaskStep, TaskStatus, ToolCall, ToolResult
from core.tool_executor import tool_executor
from core.checkpoint_manager import CheckpointManager
from core.event_bus import event_bus
from core.logger import logger

class TaskManager:
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._active_task_id: Optional[str] = None
        self.checkpoint_mgr = CheckpointManager()

    def create_task(self, prompt: str) -> Task:
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task = Task(task_id=task_id, prompt=prompt, status=TaskStatus.PENDING)
        self._tasks[task_id] = task
        self._active_task_id = task_id
        event_bus.publish("task_created", {"task_id": task_id, "prompt": prompt})
        logger.info(f"Task created: {task_id} ('{prompt}')")
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def get_active_task(self) -> Optional[Task]:
        if self._active_task_id:
            return self._tasks.get(self._active_task_id)
        return None

    def set_plan(self, task_id: str, plan: TaskPlan):
        task = self.get_task(task_id)
        if task:
            task.plan = plan
            task.status = TaskStatus.RUNNING
            task.updated_at = time.time()
            event_bus.publish("task_planned", {"task_id": task_id, "step_count": len(plan.steps)})

    def execute_step(self, task_id: str, step: TaskStep) -> ToolResult:
        task = self.get_task(task_id)
        if not task:
            return ToolResult(call_id="", tool_name=step.tool_name, status="ERROR", error_message="Task not found")

        step.status = TaskStatus.RUNNING
        call = ToolCall(tool_name=step.tool_name, parameters=step.parameters)
        res = tool_executor.execute(call)

        step.result = res
        step.status = TaskStatus.COMPLETED if res.status == "SUCCESS" else TaskStatus.FAILED
        task.history.append(res)
        task.updated_at = time.time()

        return res

    def complete_task(self, task_id: str, artifacts: Dict[str, str] = None):
        task = self.get_task(task_id)
        if task:
            task.status = TaskStatus.COMPLETED
            if artifacts:
                task.artifacts.update(artifacts)
            task.updated_at = time.time()
            event_bus.publish("task_completed", {"task_id": task_id, "artifacts": task.artifacts})
            logger.info(f"Task {task_id} completed successfully.")

    def fail_task(self, task_id: str, error_message: str):
        task = self.get_task(task_id)
        if task:
            task.status = TaskStatus.FAILED
            task.error_message = error_message
            task.updated_at = time.time()
            event_bus.publish("task_failed", {"task_id": task_id, "error": error_message})
            logger.error(f"Task {task_id} failed: {error_message}")

    def cancel_task(self, task_id: str):
        task = self.get_task(task_id)
        if task:
            task.status = TaskStatus.CANCELLED
            task.updated_at = time.time()
            event_bus.publish("task_cancelled", {"task_id": task_id})
            logger.info(f"Task {task_id} cancelled.")

task_manager = TaskManager()
