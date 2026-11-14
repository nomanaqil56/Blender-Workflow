"""Master Test Runner executing all unit test suites and generating reports."""

import unittest
import time
import json
import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import REPORTS_DIR

def run_all():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_modules = [
        "tests.test_blender_connection",
        "tests.test_live_gui",
        "tests.test_scene_inspection",
        "tests.test_object_tools",
        "tests.test_mesh_tools",
        "tests.test_material_tools",
        "tests.test_ai_connection",
        "tests.test_task_execution",
        "tests.test_visual_feedback",
        "tests.test_recovery",
        "tests.test_security",
    ]

    for mod in test_modules:
        try:
            suite.addTests(loader.loadTestsFromName(mod))
        except Exception as e:
            print(f"Error loading {mod}: {e}")

    runner = unittest.TextTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    elapsed = round(time.time() - start_time, 2)

    data = {
        "timestamp": time.time(),
        "total_tests": result.testsRun,
        "passed": result.testsRun - len(result.failures) - len(result.errors),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "elapsed_sec": elapsed,
        "status": "PASS" if result.wasSuccessful() else "FAIL"
    }

    out_file = REPORTS_DIR / "test_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("\n" + "=" * 60)
    print(f"MASTER TEST SUITE FINISHED: {data['passed']}/{data['total_tests']} PASSED ({elapsed}s)")
    print(f"Summary written to {out_file}")
    print("=" * 60)
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all()
    exit(0 if success else 1)
