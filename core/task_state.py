"""Data models and state representations for tasks, steps, tool calls, and results."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional
import time
import uuid

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    PLANNING = "PLANNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass
class ToolCall:
    tool_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    call_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

@dataclass
class ToolResult:
    call_id: str
    tool_name: str
    status: str  # "SUCCESS" or "ERROR"
    data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    execution_time_sec: float = 0.0

@dataclass
class TaskStep:
    step_index: int
    description: str
    tool_name: str
    parameters: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[ToolResult] = None
    visual_feedback_requested: bool = False

@dataclass
class TaskPlan:
    task_id: str
    prompt: str
    objective: str
    steps: List[TaskStep] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

@dataclass
class Task:
    task_id: str
    prompt: str
    status: TaskStatus = TaskStatus.PENDING
    plan: Optional[TaskPlan] = None
    current_step_index: int = 0
    history: List[ToolResult] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    error_message: Optional[str] = None
    artifacts: Dict[str, str] = field(default_factory=dict)
