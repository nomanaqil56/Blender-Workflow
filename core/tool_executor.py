"""Execution engine for registered tools, validating permissions and dispatching to Blender."""

from typing import Dict, Any
from core.tool_registry import tool_registry
from core.permission_manager import PermissionManager
from core.task_state import ToolCall, ToolResult
from blender.controller.blender_controller import blender_controller
from core.event_bus import event_bus
from core.logger import logger

class ToolExecutor:
    def __init__(self, permission_mgr: PermissionManager = None):
        self.permission_mgr = permission_mgr or PermissionManager()

    def execute(self, tool_call: ToolCall) -> ToolResult:
        tool_name = tool_call.tool_name
        params = tool_call.parameters

        tool_def = tool_registry.get(tool_name)
        if not tool_def:
            err = f"Tool '{tool_name}' is not registered."
            logger.error(err)
            return ToolResult(call_id=tool_call.call_id, tool_name=tool_name, status="ERROR", error_message=err)

        # Check permissions
        permitted, reason = self.permission_mgr.check_tool_permission(tool_name, params)
        if not permitted:
            logger.warning(f"Permission denied for '{tool_name}': {reason}")
            return ToolResult(call_id=tool_call.call_id, tool_name=tool_name, status="ERROR", error_message=reason)

        event_bus.publish("tool_execution_started", {"tool": tool_name, "params": params})

        # Dispatch via blender_controller
        result = blender_controller.execute_tool(tool_name, params)
        result.call_id = tool_call.call_id

        if result.status == "SUCCESS":
            event_bus.publish("tool_execution_success", {"tool": tool_name, "data": result.data})
        else:
            event_bus.publish("tool_execution_failed", {"tool": tool_name, "error": result.error_message})

        return result

tool_executor = ToolExecutor()
