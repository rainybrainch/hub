#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows Task Scheduler setup for habit-cycle.py
毎分実行するタスクをWindows Task Schedulerに登録
"""

import subprocess
import sys
import os
from pathlib import Path

def create_task():
    """Create scheduled task for habit improvement cycle"""

    script_dir = Path(__file__).parent
    python_exe = sys.executable
    habit_cycle_script = script_dir / "habit-cycle.py"

    if not habit_cycle_script.exists():
        print(f"ERROR: {habit_cycle_script} not found")
        sys.exit(1)

    task_name = "HabitAppImprovementCycle"

    # Check if task already exists
    try:
        check_cmd = f'tasklist /FI "TASKNAME eq {task_name}"'
        result = subprocess.run(check_cmd, capture_output=True, text=True, shell=True)
        if task_name in result.stdout:
            print(f"Task '{task_name}' already exists. Deleting...")
            delete_cmd = f'taskkill /F /IM "Task Scheduler.exe" 2>nul; schtasks /delete /tn {task_name} /f'
            subprocess.run(delete_cmd, shell=True)
    except:
        pass

    # Create task - run every 1 minute
    create_cmd = f'''schtasks /create /tn "{task_name}" /tr "python.exe "{habit_cycle_script}"" /sc minute /mo 1 /f'''

    print("Creating Windows Task Scheduler task...")
    print(f"  Task Name: {task_name}")
    print(f"  Script: {habit_cycle_script}")
    print(f"  Frequency: Every 1 minute")
    print("")

    try:
        result = subprocess.run(create_cmd, capture_output=True, text=True, shell=True, encoding='utf-8')

        if result.returncode == 0:
            print("[OK] Task created successfully!")
            print("")
            print("Next steps:")
            print(f"  1. Open 'Task Scheduler' (Windows key + 'Task Scheduler')")
            print(f"  2. Look for task named '{task_name}'")
            print(f"  3. Right-click > Run (to start immediately)")
            print("")
            print("Verification:")
            print(f"  - Task Scheduler: Control Panel > Administrative Tools > Task Scheduler")
            print(f"  - Logs: {script_dir / 'logs' / 'habit-cycle.log'}")
            print("")
            return True
        else:
            print(f"ERROR creating task: {result.stderr}")
            print(f"STDOUT: {result.stdout}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    success = create_task()
    sys.exit(0 if success else 1)
