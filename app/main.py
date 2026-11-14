"""Blender AI Studio Entrypoint CLI."""

import sys
import argparse
from app.lifecycle import app_lifecycle
from app.application import application
from interface.status_view import status_view
from interface.task_view import task_view
from interface.plan_view import plan_view
from blender.controller.blender_controller import blender_controller

def main():
    parser = argparse.ArgumentParser(description="Blender AI Studio - Autonomous 3D AI Agent")
    parser.add_argument("--prompt", "-p", type=str, help="Instruction to execute autonomously in Blender")
    parser.add_argument("--status", "-s", action="store_true", help="Print system status banner")
    parser.add_argument("--inspect", "-i", action="store_true", help="Inspect current Blender scene")
    args = parser.parse_args()

    app_lifecycle.initialize()

    if args.status:
        print(status_view.format_system_banner())
        return

    if args.inspect:
        res = blender_controller.inspect_scene(detailed=True)
        print("Scene Objects Count:", res.get("total_objects", 0))
        print("Active Object:", res.get("active_object"))
        for o in res.get("objects", []):
            print(f"  * {o['name']} ({o['type']}) at {o['location']}")
        return

    if args.prompt:
        print(status_view.format_system_banner())
        print(f"\n[Prompt]: {args.prompt}\n")
        task = application.execute_prompt(args.prompt)
        if task.plan:
            print(plan_view.format_plan_text(task.plan))
        print(task_view.format_task_summary(task))
        return

    # Interactive Loop
    print(status_view.format_system_banner())
    print("\nType your instruction below (or 'exit', 'status', 'inspect'):\n")
    try:
        while True:
            cmd = input("BlenderAIStudio > ").strip()
            if not cmd:
                continue
            if cmd.lower() in ["exit", "quit", "q"]:
                break
            elif cmd.lower() == "status":
                print(status_view.format_system_banner())
            elif cmd.lower() == "inspect":
                res = blender_controller.inspect_scene()
                print(f"Active object: {res.get('active_object')}, Total objects: {res.get('total_objects')}")
            else:
                task = application.execute_prompt(cmd)
                print(task_view.format_task_summary(task))
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        app_lifecycle.shutdown()

if __name__ == "__main__":
    main()
