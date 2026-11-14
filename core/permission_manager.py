"""Permission and confirmation control for tool execution."""

from typing import Dict, Any, Tuple
from config.security_config import DESTRUCTIVE_TOOLS, PERMITTED_TOOLS

class PermissionManager:
    def __init__(self, auto_approve_safe: bool = True, require_destructive_approval: bool = True):
        self.auto_approve_safe = auto_approve_safe
        self.require_destructive_approval = require_destructive_approval
        self._approved_tasks = set()

    def check_tool_permission(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """Verify whether tool execution is permitted."""
        if tool_name not in PERMITTED_TOOLS:
            return False, f"Tool '{tool_name}' is not in the allowed tools whitelist."

        if tool_name in DESTRUCTIVE_TOOLS:
            confirmed = parameters.get("confirm", False)
            if self.require_destructive_approval and not confirmed:
                return False, f"Tool '{tool_name}' is a destructive action and requires 'confirm=True'."

        return True, "Permitted"

    def approve_task(self, task_id: str):
        self._approved_tasks.add(task_id)

    def is_task_approved(self, task_id: str) -> bool:
        return task_id in self._approved_tasks
