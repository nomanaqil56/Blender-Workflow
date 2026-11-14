"""Active task execution and artifact view."""

from core.task_state import Task

class TaskView:
    def format_task_summary(self, task: Task) -> str:
        lines = [
            f"--- Task Status: {task.status.value} [{task.task_id}] ---",
            f"Prompt: {task.prompt}",
            f"History: {len(task.history)} tool executions performed."
        ]
        if task.error_message:
            lines.append(f"Error: {task.error_message}")
        if task.artifacts:
            lines.append("Generated Artifacts:")
            for k, v in task.artifacts.items():
                lines.append(f"  * {k}: {v}")
        return "\n".join(lines)

task_view = TaskView()
