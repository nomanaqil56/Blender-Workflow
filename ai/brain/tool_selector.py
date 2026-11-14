"""Tool selection and argument validation helper."""

from typing import Dict, Any, Optional
from core.tool_registry import tool_registry, ToolDefinition

class ToolSelector:
    def __init__(self):
        self.registry = tool_registry

    def find_tool(self, tool_name: str) -> Optional[ToolDefinition]:
        return self.registry.get(tool_name)

    def validate_call_arguments(self, tool_name: str, args: Dict[str, Any]) -> Tuple[bool, str]:
        t = self.find_tool(tool_name)
        if not t:
            return False, f"Unknown tool: '{tool_name}'"

        required = t.parameters_schema.get("required", [])
        for r in required:
            if r not in args:
                return False, f"Missing required parameter '{r}' for tool '{tool_name}'"

        return True, "Valid"

from typing import Tuple
tool_selector = ToolSelector()
