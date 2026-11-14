"""Error recovery planner for self-healing tool failures."""

from typing import Optional, Dict, Any
from core.task_state import TaskStep, TaskStatus

class ErrorRecovery:
    def plan_recovery_step(self, failed_step: TaskStep, error_info: Dict[str, Any]) -> Optional[TaskStep]:
        """Generate a corrective action step if recoverable."""
        reason = error_info.get("reason", "").lower()

        # If confirmation was missing for deletion, inject confirmed retry if permitted
        if "confirm=true" in reason and failed_step.tool_name == "delete_object":
            new_params = dict(failed_step.parameters)
            new_params["confirm"] = True
            return TaskStep(
                step_index=failed_step.step_index + 100,
                description=f"Auto-recovery: re-try {failed_step.tool_name} with confirmation",
                tool_name=failed_step.tool_name,
                parameters=new_params
            )

        return None

error_recovery = ErrorRecovery()
