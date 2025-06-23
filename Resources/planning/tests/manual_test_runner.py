import os
import shutil
import subprocess
import sys
from pathlib import Path

# Ensure the script can find sync_task_files
# Assuming this manual_test_runner.py is in Resources/planning/tests/
# and sync_task_files.py is in Resources/planning/
# We need to go up two levels from 'tests' to 'Resources/planning' then access the module.
# Or, more simply, add repo root to path and import from Resources.planning
sys.path.append(str(Path(__file__).resolve().parent.parent.parent)) # Adds repo root /app
from Resources.planning import sync_task_files

# --- Constants for Test Data (mirroring pytest test) ---
BASE_TEST_DIR = Path("temp_manual_test_sync_logic") # Create in CWD (which should be /app)
MAIN_FILE_NAME = "PLANNING_TASKS.md"
TASKS_DIR_NAME = "tasks"

# --- Helper Functions (simplified from pytest test) ---

def run_git_command(repo_path, command_args):
    try:
        subprocess.run(["git"] + command_args, cwd=repo_path, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {' '.join(command_args)}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        raise

def setup_git_repo(repo_path):
    if repo_path.exists():
        shutil.rmtree(repo_path)
    repo_path.mkdir(parents=True)
    run_git_command(repo_path, ["init"])
    run_git_command(repo_path, ["config", "user.name", "Manual Test User"])
    run_git_command(repo_path, ["config", "user.email", "manual_test@example.com"])
    print(f"Git repo initialized at {repo_path}")

def create_file_and_commit(repo_path, file_rel_path, content, commit_message):
    full_file_path = repo_path / file_rel_path
    full_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_file_path, "w", encoding="utf-8") as f:
        f.write(content)
    run_git_command(repo_path, ["add", str(file_rel_path)])
    run_git_command(repo_path, ["commit", "-m", commit_message])
    print(f"Created and committed {file_rel_path}")

def manual_test_initial_sync_no_changes():
    print("\n--- Running Test: manual_test_initial_sync_no_changes ---")
    repo_root = BASE_TEST_DIR / "test_initial_sync_no_changes_repo"
    setup_git_repo(repo_root)

    # Paths for the sync script to use
    main_file_abs_path = repo_root / "Resources" / "planning" / MAIN_FILE_NAME
    tasks_dir_abs_path = repo_root / "Resources" / "planning" / TASKS_DIR_NAME

    (repo_root / "Resources" / "planning" / "tasks").mkdir(parents=True, exist_ok=True)

    # Override constants in sync_task_files
    original_main_file = sync_task_files.PLANNING_TASKS_FILE
    original_tasks_dir = sync_task_files.INDIVIDUAL_TASKS_DIR
    original_git_root = sync_task_files.GIT_ROOT

    sync_task_files.PLANNING_TASKS_FILE = str(main_file_abs_path)
    sync_task_files.INDIVIDUAL_TASKS_DIR = str(tasks_dir_abs_path)
    sync_task_files.GIT_ROOT = str(repo_root)

    original_cwd = Path.cwd()
    os.chdir(repo_root) # The script expects to run from repo root for some git commands

    try:
        main_content = """\
# Epic 1 -- Task 1.1: First Task
This is the first task.
---
# Epic 1 -- Task 1.2: Second Task
This is the second task.
"""
        task1_content = """\
Status: Not Started

# Epic 1 -- Task 1.1: First Task
This is the first task.
"""
        # Relative paths for create_file_and_commit
        main_file_rel = Path("Resources/planning") / MAIN_FILE_NAME
        task1_rel = Path("Resources/planning/tasks") / "epic_1_task_1_1.md"

        create_file_and_commit(repo_root, main_file_rel, main_content, "Initial commit main")
        create_file_and_commit(repo_root, task1_rel, task1_content, "Initial commit task 1.1")

        print("Running sync_task_files.analyze_tasks(dry_run=False)...")
        sync_task_files.analyze_tasks(dry_run=False)

        # Assertions
        with open(main_file_abs_path, "r") as f:
            assert f.read().strip() == main_content.strip(), "Main content changed!"
        with open(tasks_dir_abs_path / "epic_1_task_1_1.md", "r") as f:
            assert f.read().strip() == task1_content.strip(), "Task 1.1 content changed!"

        status_output = subprocess.check_output(["git", "status", "--porcelain"], cwd=repo_root, text=True)
        assert status_output == "", f"Git status not clean: {status_output}"

        print("Test manual_test_initial_sync_no_changes: PASSED")

    except Exception as e:
        print(f"Test manual_test_initial_sync_no_changes: FAILED - {e}")
        import traceback
        traceback.print_exc()
    finally:
        os.chdir(original_cwd)
        sync_task_files.PLANNING_TASKS_FILE = original_main_file
        sync_task_files.INDIVIDUAL_TASKS_DIR = original_tasks_dir
        sync_task_files.GIT_ROOT = original_git_root
        if repo_root.exists():
            shutil.rmtree(repo_root)
        print(f"Cleaned up {repo_root}")

if __name__ == "__main__":
    if BASE_TEST_DIR.exists(): # Cleanup from previous partial runs if any
        print(f"Warning: Base test directory {BASE_TEST_DIR} exists. Removing it.")
        shutil.rmtree(BASE_TEST_DIR)
    BASE_TEST_DIR.mkdir(parents=True)

    manual_test_initial_sync_no_changes()

    # TODO: Add calls to other manual test functions here

    # Final cleanup of the base directory for all tests
    if BASE_TEST_DIR.exists():
        shutil.rmtree(BASE_TEST_DIR)
        print(f"Cleaned up base test directory {BASE_TEST_DIR}")
    print("\nAll manual tests complete.")
