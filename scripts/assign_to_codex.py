#!/usr/bin/env python3
"""
Script to assign tasks to Codex (or any AI agent) by watching CODEX_TASKS.md for new tasks.
Marks tasks as 'in-progress by Codex' and can be run as a watcher or on demand.
"""
import time
import re
from pathlib import Path

TASK_FILE = Path(__file__).parent.parent / "CODEX_TASKS.md"
ASSIGNMENT_TAG = "[in-progress by Codex]"
CHECK_INTERVAL = 30  # seconds


def assign_new_tasks():
    """Assign unassigned high-priority tasks to Codex."""
    with TASK_FILE.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    changed = False
    for i, line in enumerate(lines):
        if (
            line.strip().startswith("-")
            and "High Priority" in "".join(lines[:i])
            and ASSIGNMENT_TAG not in line
            and not line.strip().startswith("- [")
        ):
            lines[i] = line.replace("- ", f"- {ASSIGNMENT_TAG} ", 1)
            changed = True
            print(f"Assigned to Codex: {line.strip()}")

    if changed:
        with TASK_FILE.open("w", encoding="utf-8") as f:
            f.writelines(lines)
        print("Updated CODEX_TASKS.md with new assignments.")
    else:
        print("No new tasks to assign.")


def watch_tasks():
    """Watch the task file and assign new tasks as they appear."""
    print("Watching for new Codex tasks...")
    last_mtime = TASK_FILE.stat().st_mtime
    while True:
        time.sleep(CHECK_INTERVAL)
        mtime = TASK_FILE.stat().st_mtime
        if mtime != last_mtime:
            print("Detected change in CODEX_TASKS.md. Checking for new tasks...")
            assign_new_tasks()
            last_mtime = mtime


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Assign tasks to Codex from CODEX_TASKS.md.")
    parser.add_argument("--watch", action="store_true", help="Watch for new tasks and assign automatically.")
    args = parser.parse_args()
    if args.watch:
        watch_tasks()
    else:
        assign_new_tasks()
