import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai.brain.planner import planner

tests = [
    "Make the black panels slightly less glossy and give the white panels a more realistic leather appearance.",
    "Make the seams between the panels more visible, but keep the football's overall spherical shape.",
    "Improve the studio lighting so that the football looks more professional and the panel details are easier to see.",
    "Inspect the football and tell me how many pentagonal and hexagonal panels it has.",
    "Make the football slightly smaller and rotate it to show more of the black pentagonal panels."
]

for idx, prompt in enumerate(tests, 1):
    print(f"\n--- Follow-up Test {idx} ---")
    print(f"Prompt: {prompt}")
    plan = planner.create_plan(f"followup_{idx}", prompt, {"active_object": "Realistic_Football", "total_objects": 3})
    print(f"Generated {len(plan.steps)} steps:")
    for s in plan.steps:
        print(f"  [{s.tool_name}] -> {s.parameters}")
