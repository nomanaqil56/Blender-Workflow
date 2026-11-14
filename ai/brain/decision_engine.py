"""Decision engine evaluating tool execution results."""

from typing import Dict, Any, Tuple
from core.task_state import ToolResult

class DecisionEngine:
    def evaluate_step_result(self, result: ToolResult) -> Tuple[bool, str, Dict[str, Any]]:
        """Evaluate if step succeeded and determine next action."""
        if result.status == "SUCCESS":
            return True, "CONTINUE", {}

        # Error analysis
        msg = result.error_message or "Unknown error"
        if "not found" in msg.lower():
            return False, "RECOVERY_OBJECT_MISSING", {"reason": msg}
        if "confirm=true" in msg.lower():
            return False, "RECOVERY_CONFIRMATION_REQUIRED", {"reason": msg}

        return False, "ABORT", {"reason": msg}

decision_engine = DecisionEngine()
