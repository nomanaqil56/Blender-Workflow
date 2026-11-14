"""Task Plan visualizer and step list formatter."""

from core.task_state import TaskPlan

class PlanView:
    def format_plan_text(self, plan: TaskPlan) -> str:
        lines = [
            f"=== TASK PLAN: {plan.task_id} ===",
            f"Objective: {plan.objective}",
            f"Total Steps: {len(plan.steps)}",
            "-" * 50
        ]
        for s in plan.steps:
            vis = " [Visual Check]" if s.visual_feedback_requested else ""
            lines.append(f"  [{s.step_index}] {s.description} ({s.tool_name}){vis}")
        lines.append("-" * 50)
        return "\n".join(lines)

plan_view = PlanView()
