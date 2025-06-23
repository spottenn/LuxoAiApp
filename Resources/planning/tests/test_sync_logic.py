import os
import shutil
import subprocess
import pytest
from pathlib import Path

# Adjust the import path to reach sync_task_files.py from the tests directory
# This assumes the test script is run from the repository root, or pytest handles paths correctly.
# For robustness, it's often better to make the project installable or manipulate sys.path.
# Assuming pytest is run from the repository root.
from Resources.planning import sync_task_files

# --- Constants for Test Data ---
TEST_REPO_DIR = Path("temp_test_repo_sync_logic")
MAIN_FILE_NAME = "PLANNING_TASKS.md"
TASKS_DIR_NAME = "tasks"
INDIVIDUAL_TASK_DIR_REL_PATH = f"Resources/planning/{TASKS_DIR_NAME}" # Relative to repo root for script

# --- Helper Functions for Git and File Manipulation ---

def run_git_command(repo_path, command_args):
    """Runs a git command in the specified repository path."""
    try:
        subprocess.run(["git"] + command_args, cwd=repo_path, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {' '.join(command_args)}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        raise

def setup_git_repo(repo_path):
    """Initializes a new Git repository."""
    if repo_path.exists():
        shutil.rmtree(repo_path)
    repo_path.mkdir(parents=True)
    run_git_command(repo_path, ["init"])
    # Basic git config for commits to work
    run_git_command(repo_path, ["config", "user.name", "Test User"])
    run_git_command(repo_path, ["config", "user.email", "test@example.com"])

def create_file(repo_path, file_rel_path, content, commit_message=None):
    """Creates a file and optionally commits it."""
    full_file_path = repo_path / file_rel_path
    full_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_file_path, "w", encoding="utf-8") as f:
        f.write(content)
    if commit_message:
        run_git_command(repo_path, ["add", str(file_rel_path)])
        run_git_command(repo_path, ["commit", "-m", commit_message])

# --- Pytest Fixture for Temporary Git Repository ---

@pytest.fixture
def temp_git_repo(tmp_path):
    """
    Creates a temporary Git repository for testing, populates it,
    and configures sync_task_files to use it.
    Cleans up after the test.
    """
    original_cwd = Path.cwd()
    repo_root = tmp_path / "test_repo"
    setup_git_repo(repo_root)

    # Create the directory structure expected by the sync script
    # (Resources/planning/tasks)
    (repo_root / "Resources" / "planning" / "tasks").mkdir(parents=True, exist_ok=True)

    # Override constants in sync_task_files to point to the temp repo
    original_main_file = sync_task_files.PLANNING_TASKS_FILE
    original_tasks_dir = sync_task_files.INDIVIDUAL_TASKS_DIR
    original_git_root = sync_task_files.GIT_ROOT

    sync_task_files.PLANNING_TASKS_FILE = str(repo_root / "Resources" / "planning" / MAIN_FILE_NAME)
    sync_task_files.INDIVIDUAL_TASKS_DIR = str(repo_root / "Resources" / "planning" / TASKS_DIR_NAME)
    sync_task_files.GIT_ROOT = str(repo_root)

    # Use monkeypatch for changing CWD and setting module attributes for better isolation and teardown
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.chdir(repo_root)

    monkeypatch.setattr(sync_task_files, 'PLANNING_TASKS_FILE', str(repo_root / "Resources" / "planning" / MAIN_FILE_NAME))
    monkeypatch.setattr(sync_task_files, 'INDIVIDUAL_TASKS_DIR', str(repo_root / "Resources" / "planning" / TASKS_DIR_NAME))
    monkeypatch.setattr(sync_task_files, 'GIT_ROOT', str(repo_root))

    yield repo_root # Provide the repo path to the test

    # monkeypatch automatically handles teardown (undoing chdir and setattr)
    # shutil.rmtree(repo_root) # tmp_path fixture handles cleanup of repo_root

# --- Test Cases ---

def test_initial_sync_no_changes(temp_git_repo):
    """
    Scenario: Main file and individual file exist and are identical.
    Expected: Script reports "In Sync" and makes no changes.
    """
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
    create_file(temp_git_repo, Path("Resources/planning") / MAIN_FILE_NAME, main_content, "Initial commit main")
    create_file(temp_git_repo, Path("Resources/planning/tasks") / "epic_1_task_1_1.md", task1_content, "Initial commit task 1.1")

    # Run the sync script (dry_run=False to test file non-modification)
    sync_task_files.analyze_tasks(dry_run=False)

    # Assertions
    with open(temp_git_repo / "Resources/planning" / MAIN_FILE_NAME, "r") as f:
        assert f.read().strip() == main_content.strip()
    with open(temp_git_repo / "Resources/planning/tasks" / "epic_1_task_1_1.md", "r") as f:
        assert f.read().strip() == task1_content.strip()

    # Check git status for no changes
    status_output = subprocess.check_output(["git", "status", "--porcelain"], cwd=temp_git_repo, text=True)
    assert status_output == "", "Git status should be clean after sync with no changes."


def test_update_main_from_individual(temp_git_repo):
    """
    Scenario: Individual file is newer than the main file.
    Expected: Main file is updated with content from the individual file.
    """
    main_initial_content = """\
# Epic 1 -- Task 1.1: Task Title
Original content in main.
---
"""
    individual_initial_content = """\
Status: In Progress

# Epic 1 -- Task 1.1: Task Title
Original content in individual.
"""
    # Create main file and commit
    main_file_path = Path("Resources/planning") / MAIN_FILE_NAME
    ind_file_rel_path = Path("Resources/planning/tasks") / "epic_1_task_1_1.md"

    create_file(temp_git_repo, main_file_path, main_initial_content, "Commit main file v1")
    create_file(temp_git_repo, ind_file_rel_path, individual_initial_content, "Commit individual file v1") # Same content initially for simplicity of setup

    # Modify individual file to be "newer"
    individual_updated_content = """\
Status: In Progress

# Epic 1 -- Task 1.1: Task Title
Updated content from individual. This is newer.
"""
    create_file(temp_git_repo, ind_file_rel_path, individual_updated_content, "Update individual file v2 (newer)")

    sync_task_files.analyze_tasks(dry_run=False)

    # Assert main file content is updated
    expected_main_content_after_sync = """\
# Epic 1 -- Task 1.1: Task Title
Updated content from individual. This is newer.
---
"""
    with open(temp_git_repo / main_file_path, "r") as f:
        actual_main_content = f.read()
        print("Actual main content after sync:\n", actual_main_content) # Debug print
        assert actual_main_content.strip() == expected_main_content_after_sync.strip()

    # Assert individual file remains unchanged
    with open(temp_git_repo / ind_file_rel_path, "r") as f:
        assert f.read().strip() == individual_updated_content.strip()

    # Check git status - main file should be modified
    status_output = subprocess.check_output(["git", "status", "--porcelain"], cwd=temp_git_repo, text=True)
    # Normalize path for comparison, especially on Windows
    normalized_main_file_path = str(main_file_path).replace("\\", "/")
    assert f"M  {normalized_main_file_path}" in status_output.replace("\\", "/"), "Main file should be modified."


def test_update_individual_from_main(temp_git_repo):
    """
    Scenario: Main file is newer than the individual file.
    Expected: Individual file is updated with content from the main file, preserving Status line.
    """
    main_initial_content = """\
# Epic 1 -- Task 1.1: Task Title
Original content in main.
"""
    individual_initial_content = """\
Status: To Do

# Epic 1 -- Task 1.1: Task Title
Original content in individual.
"""
    main_file_path = Path("Resources/planning") / MAIN_FILE_NAME
    ind_file_rel_path = Path("Resources/planning/tasks") / "epic_1_task_1_1.md"

    create_file(temp_git_repo, main_file_path, main_initial_content, "Commit main file v1")
    create_file(temp_git_repo, ind_file_rel_path, individual_initial_content, "Commit individual file v1")

    # Modify main file to be "newer"
    main_updated_content = """\
# Epic 1 -- Task 1.1: Task Title
Updated content from main. This is newer.
"""
    create_file(temp_git_repo, main_file_path, main_updated_content, "Update main file v2 (newer)")

    sync_task_files.analyze_tasks(dry_run=False)

    # Assert individual file content is updated
    expected_individual_content_after_sync = """\
Status: To Do

# Epic 1 -- Task 1.1: Task Title
Updated content from main. This is newer.
"""
    with open(temp_git_repo / ind_file_rel_path, "r") as f:
        actual_individual_content = f.read()
        print("Actual individual content after sync:\n", actual_individual_content) # Debug
        assert actual_individual_content.strip() == expected_individual_content_after_sync.strip()

    # Assert main file remains unchanged by this operation
    with open(temp_git_repo / main_file_path, "r") as f:
        assert f.read().strip() == main_updated_content.strip()

    status_output = subprocess.check_output(["git", "status", "--porcelain"], cwd=temp_git_repo, text=True)
    normalized_ind_file_path = str(ind_file_rel_path).replace("\\", "/")
    assert f"M  {normalized_ind_file_path}" in status_output.replace("\\", "/"), "Individual file should be modified."


def test_conflict_divergent_changes(temp_git_repo):
    """
    Scenario: Both main and individual files have new, different commits since a common ancestor.
    Expected: Both files are marked with SYNC STATUS conflict messages.
    """
    base_main_content = """\
# Epic 1 -- Task 1.1: Base Task
Base content.
---
"""
    base_individual_content = """\
Status: Base Status

# Epic 1 -- Task 1.1: Base Task
Base content.
"""
    main_file_path = Path("Resources/planning") / MAIN_FILE_NAME
    ind_file_rel_path = Path("Resources/planning/tasks") / "epic_1_task_1_1.md"

    create_file(temp_git_repo, main_file_path, base_main_content, "Commit base main")
    create_file(temp_git_repo, ind_file_rel_path, base_individual_content, "Commit base individual")

    # Create divergent changes
    main_change_content = """\
# Epic 1 -- Task 1.1: Base Task
Main has new changes.
---
"""
    create_file(temp_git_repo, main_file_path, main_change_content, "Divergent change in main")

    # Before changing individual, "checkout" the base commit for main to simulate parallel branch
    # This is tricky. Simpler: just ensure commits are not ancestors.
    # For this test, ensure individual's change is *after* base, but *not after* main's change in terms of ancestry.
    # The current setup already ensures this if we just commit another change to individual.
    # The script uses `is_ancestor`. If neither is an ancestor of the other, it's divergent.

    individual_change_content = """\
Status: Updated Status

# Epic 1 -- Task 1.1: Base Task
Individual also has new changes.
"""
    create_file(temp_git_repo, ind_file_rel_path, individual_change_content, "Divergent change in individual")

    sync_task_files.analyze_tasks(dry_run=False)

    # Assertions for SYNC STATUS markers
    with open(temp_git_repo / main_file_path, "r") as f:
        content = f.read()
        assert "# Epic 1 -- Task 1.1: Base Task" in content
        assert "**SYNC STATUS:** Conflict detected" in content
        assert "Divergent." in content # From the conflict_detail message

    with open(temp_git_repo / ind_file_rel_path, "r") as f:
        content = f.read()
        assert "Status: Updated Status" in content # Original status line
        assert "# Epic 1 -- Task 1.1: Base Task" in content
        assert "**SYNC STATUS:** Conflict detected" in content
        assert "Divergent." in content

    status_output = subprocess.check_output(["git", "status", "--porcelain"], cwd=temp_git_repo, text=True)
    normalized_main_file_path = str(main_file_path).replace("\\", "/")
    normalized_ind_file_path = str(ind_file_rel_path).replace("\\", "/")
    assert f"M  {normalized_main_file_path}" in status_output.replace("\\", "/"), "Main file should be modified with sync marker."
    assert f"M  {normalized_ind_file_path}" in status_output.replace("\\", "/"), "Individual file should be modified with sync marker."


def test_empty_content_sync_main_was_empty(temp_git_repo):
    """
    Scenario: Main task content was empty (NO_CONTENT_COMMIT), individual has content.
    Expected: Main file is updated from individual.
    """
    main_empty_task_content = """\
# Epic 1 -- Task 1.1: Empty Task
---
""" # Effectively empty content for the task
    individual_with_content = """\
Status: Ready

# Epic 1 -- Task 1.1: Empty Task
Individual has some content.
"""
    main_file_path = Path("Resources/planning") / MAIN_FILE_NAME
    ind_file_rel_path = Path("Resources/planning/tasks") / "epic_1_task_1_1.md"

    create_file(temp_git_repo, main_file_path, main_empty_task_content, "Commit main with empty task")
    create_file(temp_git_repo, ind_file_rel_path, individual_with_content, "Commit individual with content")

    sync_task_files.analyze_tasks(dry_run=False)

    expected_main_content_after_sync = """\
# Epic 1 -- Task 1.1: Empty Task
Individual has some content.
---
"""
    with open(temp_git_repo / main_file_path, "r") as f:
        assert f.read().strip() == expected_main_content_after_sync.strip()

    status_output = subprocess.check_output(["git", "status", "--porcelain"], cwd=temp_git_repo, text=True)
    normalized_main_file_path = str(main_file_path).replace("\\", "/")
    assert f"M  {normalized_main_file_path}" in status_output.replace("\\", "/"), "Main file should be modified."


def test_empty_content_sync_individual_was_empty(temp_git_repo):
    """
    Scenario: Individual task content was empty (NO_CONTENT_COMMIT), main has content.
    Expected: Individual file is updated from main.
    """
    main_with_content = """\
# Epic 1 -- Task 1.1: Task With Content
Main has this content.
---
"""
    individual_empty_content = """\
Status: Not Started

# Epic 1 -- Task 1.1: Task With Content
""" # Effectively empty content
    main_file_path = Path("Resources/planning") / MAIN_FILE_NAME
    ind_file_rel_path = Path("Resources/planning/tasks") / "epic_1_task_1_1.md"

    create_file(temp_git_repo, main_file_path, main_with_content, "Commit main with content")
    create_file(temp_git_repo, ind_file_rel_path, individual_empty_content, "Commit individual with empty content")

    sync_task_files.analyze_tasks(dry_run=False)

    expected_individual_content_after_sync = """\
Status: Not Started

# Epic 1 -- Task 1.1: Task With Content
Main has this content.
"""
    with open(temp_git_repo / ind_file_rel_path, "r") as f:
        assert f.read().strip() == expected_individual_content_after_sync.strip()

    status_output = subprocess.check_output(["git", "status", "--porcelain"], cwd=temp_git_repo, text=True)
    normalized_ind_file_path = str(ind_file_rel_path).replace("\\", "/")
    assert f"M  {normalized_ind_file_path}" in status_output.replace("\\", "/"), "Individual file should be modified."


def test_sync_status_marker_idempotency(temp_git_repo):
    """
    Scenario: Files have divergent changes, sync runs marking conflict. Run sync again.
    Expected: Conflict markers are not duplicated; they are effectively replaced or stay the same.
    """
    base_main_content = "# Epic 1 -- Task 1.1: Base\nBase content.\n---\n"
    base_individual_content = "Status: Base\n\n# Epic 1 -- Task 1.1: Base\nBase content."
    main_file_path = Path("Resources/planning") / MAIN_FILE_NAME
    ind_file_rel_path = Path("Resources/planning/tasks") / "epic_1_task_1_1.md"

    create_file(temp_git_repo, main_file_path, base_main_content, "Base main")
    create_file(temp_git_repo, ind_file_rel_path, base_individual_content, "Base individual")

    create_file(temp_git_repo, main_file_path, base_main_content.replace("Base content", "Main change"), "Main divergent")
    create_file(temp_git_repo, ind_file_rel_path, base_individual_content.replace("Base content", "Individual change"), "Individual divergent")

    # First run: creates markers
    sync_task_files.analyze_tasks(dry_run=False)

    with open(temp_git_repo / main_file_path, "r") as f:
        content_after_first_run = f.read()
        assert content_after_first_run.count("**SYNC STATUS:** Conflict detected") == 1
    with open(temp_git_repo / ind_file_rel_path, "r") as f:
        content_after_first_run_ind = f.read()
        assert content_after_first_run_ind.count("**SYNC STATUS:** Conflict detected") == 1

    # Commit the files with markers (simulating user saving them)
    # This is important: the script's SYNC_STATUS_LINE_PATTERN is used to ignore these lines
    # when comparing content. So, if content is otherwise same, it would be "In Sync".
    # However, the conflict is based on Git history. If history is still divergent, it will re-mark.
    # The _remove_sync_status_lines should handle cleaning before adding a new one.
    create_file(temp_git_repo, main_file_path, content_after_first_run, "Commit main with conflict marker")
    create_file(temp_git_repo, ind_file_rel_path, content_after_first_run_ind, "Commit individual with conflict marker")

    # Second run: should not add more markers because the _remove_sync_status_lines handles it.
    # The script will still see a git history conflict and re-apply the (same) conflict markers.
    sync_task_files.analyze_tasks(dry_run=False)

    with open(temp_git_repo / main_file_path, "r") as f:
        content_after_second_run = f.read()
        print("Main after 2nd run:\n", content_after_second_run)
        assert content_after_second_run.count("**SYNC STATUS:** Conflict detected") == 1, "Marker should not be duplicated in main file."
    with open(temp_git_repo / ind_file_rel_path, "r") as f:
        content_after_second_run_ind = f.read()
        print("Ind after 2nd run:\n", content_after_second_run_ind)
        assert content_after_second_run_ind.count("**SYNC STATUS:** Conflict detected") == 1, "Marker should not be duplicated in individual file."


def test_multiple_tasks_sync(temp_git_repo):
    """
    Scenario: Multiple tasks with different sync states.
    Task 1.1: In sync.
    Task 1.2: Main is newer.
    Task 1.3: Individual is newer.
    Task 1.4: Conflict.
    Expected: Each task is handled correctly.
    """
    main_file_path = Path("Resources/planning") / MAIN_FILE_NAME
    task1_path = Path("Resources/planning/tasks") / "epic_1_task_1_1.md"
    task2_path = Path("Resources/planning/tasks") / "epic_1_task_1_2.md"
    task3_path = Path("Resources/planning/tasks") / "epic_1_task_1_3.md"
    task4_path = Path("Resources/planning/tasks") / "epic_1_task_1_4.md"

    # Initial state (all in sync for setup simplicity)
    main_content_v1 = """\
# Epic 1 -- Task 1.1: Sync Task
Content for 1.1
---
# Epic 1 -- Task 1.2: Main Newer Task
Content for 1.2
---
# Epic 1 -- Task 1.3: Individual Newer Task
Content for 1.3
---
# Epic 1 -- Task 1.4: Conflict Task
Content for 1.4
---
"""
    task1_v1 = "Status: Done\n\n# Epic 1 -- Task 1.1: Sync Task\nContent for 1.1"
    task2_v1 = "Status: ToDo\n\n# Epic 1 -- Task 1.2: Main Newer Task\nContent for 1.2"
    task3_v1 = "Status: In Progress\n\n# Epic 1 -- Task 1.3: Individual Newer Task\nContent for 1.3"
    task4_v1 = "Status: Blocked\n\n# Epic 1 -- Task 1.4: Conflict Task\nContent for 1.4"

    create_file(temp_git_repo, main_file_path, main_content_v1, "Commit v1 main")
    create_file(temp_git_repo, task1_path, task1_v1, "Commit v1 task 1.1")
    create_file(temp_git_repo, task2_path, task2_v1, "Commit v1 task 1.2")
    create_file(temp_git_repo, task3_path, task3_v1, "Commit v1 task 1.3")
    create_file(temp_git_repo, task4_path, task4_v1, "Commit v1 task 1.4")

    # Create divergent states
    # Task 1.1: No change from v1 for both files.

    # Task 1.2: Main updated (v2 for main), individual task2_v1 is older.
    main_content_v2_task2_updated = main_content_v1.replace("Content for 1.2", "Main's new content for 1.2")
    create_file(temp_git_repo, main_file_path, main_content_v2_task2_updated, "Commit v2 main (1.2 updated)")

    # Task 1.3: Individual updated (v2 for task3), main_content_v2_task2_updated is older for this task.
    task3_v2_updated = task3_v1.replace("Content for 1.3", "Individual's new content for 1.3")
    create_file(temp_git_repo, task3_path, task3_v2_updated, "Commit v2 task 1.3 (updated)")

    # Task 1.4: Conflict
    # Main file's task 1.4 was last updated in "Commit v2 main (1.2 updated)" (content is "Content for 1.4")
    # Individual task4_v1 is "Content for 1.4"
    # Now, make conflicting changes:
    main_content_v3_task4_conflict = main_content_v2_task2_updated.replace("Content for 1.4", "Main's conflict change for 1.4")
    create_file(temp_git_repo, main_file_path, main_content_v3_task4_conflict, "Commit v3 main (1.4 conflict)")

    task4_v2_conflict = task4_v1.replace("Content for 1.4", "Individual's conflict change for 1.4")
    create_file(temp_git_repo, task4_path, task4_v2_conflict, "Commit v2 task 1.4 (conflict)")

    # Run sync
    sync_task_files.analyze_tasks(dry_run=False)

    # Assertions
    with open(temp_git_repo / main_file_path, "r") as f:
        main_final_content = f.read()
        print("Main final content for multi-task:\n", main_final_content)

    # Task 1.1 (In Sync)
    with open(temp_git_repo / task1_path, "r") as f:
        task1_final_content = f.read()
        assert "Content for 1.1" in task1_final_content
        assert "**SYNC STATUS:**" not in task1_final_content
    assert "# Epic 1 -- Task 1.1: Sync Task\nContent for 1.1" in main_final_content
    # Check that no sync status was added under task 1.1 heading in main file
    task1_1_main_block_match = re.search(r"(# Epic 1 -- Task 1.1: Sync Task.*?)(?:# Epic|\Z)", main_final_content, re.DOTALL)
    assert task1_1_main_block_match is not None
    assert "**SYNC STATUS:**" not in task1_1_main_block_match.group(1)


    # Task 1.2 (Main was newer -> individual updated)
    with open(temp_git_repo / task2_path, "r") as f:
        task2_final_content = f.read()
        assert "Status: ToDo" in task2_final_content
        assert "Main's new content for 1.2" in task2_final_content
    assert "# Epic 1 -- Task 1.2: Main Newer Task\nMain's new content for 1.2" in main_final_content

    # Task 1.3 (Individual was newer -> main updated)
    assert "# Epic 1 -- Task 1.3: Individual Newer Task\nIndividual's new content for 1.3" in main_final_content
    with open(temp_git_repo / task3_path, "r") as f: # Check individual file is untouched
        assert task3_v2_updated in f.read()


    # Task 1.4 (Conflict)
    assert "# Epic 1 -- Task 1.4: Conflict Task\n**SYNC STATUS:** Conflict detected" in main_final_content
    with open(temp_git_repo / task4_path, "r") as f:
        task4_final_content = f.read()
        assert "Status: Blocked" in task4_final_content
        # The original conflicting content should be there, followed by the marker
        assert "Individual's conflict change for 1.4" in task4_final_content
        assert "**SYNC STATUS:** Conflict detected" in task4_final_content

    # Check git status (main, task2, task4 should be modified by the script)
    status_output = subprocess.check_output(["git", "status", "--porcelain"], cwd=temp_git_repo, text=True).replace("\\", "/")
    print("Git status after multi-task sync:\n", status_output)

    # Normalize paths for assertion
    norm_main_path = str(main_file_path).replace("\\","/")
    norm_task1_path = str(task1_path).replace("\\","/")
    norm_task2_path = str(task2_path).replace("\\","/")
    norm_task3_path = str(task3_path).replace("\\","/")
    norm_task4_path = str(task4_path).replace("\\","/")

    assert f"M  {norm_main_path}" in status_output # Modified by task 1.3 update and task 1.4 marker
    assert f"M  {norm_task2_path}" in status_output # Modified by update from main
    assert f"M  {norm_task4_path}" in status_output # Modified by conflict marker

    assert f"M  {norm_task1_path}" not in status_output # Task 1.1 should not be modified
    # Task 1.3 individual file was the source, so it wasn't modified by the script.
    assert f"M  {norm_task3_path}" not in status_output


# TODO:
# - test_uncommitted_changes_handling (script should refuse live run, warn on dry run)
# - test files with no trailing "---" for the last task in PLANNING_TASKS.md
# - test removal of sync status marker when files become "In Sync" again (ADVANCED).


def test_uncommitted_changes_live_run(temp_git_repo, capsys):
    """
    Scenario: Uncommitted changes exist in the repo.
    Expected: Script refuses to run in live mode (dry_run=False) and prints an error.
    """
    main_content = "# Epic 1 -- Task 1.1: Test\nContent"
    main_file_path = Path("Resources/planning") / MAIN_FILE_NAME
    create_file(temp_git_repo, main_file_path, main_content, "Initial commit")

    # Introduce uncommitted change
    with open(temp_git_repo / main_file_path, "a") as f:
        f.write("\nUncommitted change.")

    sync_task_files.analyze_tasks(dry_run=False)

    captured = capsys.readouterr()
    assert "Error: There are uncommitted changes" in captured.out
    # Check that file was not modified by sync script (beyond the uncommitted change)
    with open(temp_git_repo / main_file_path, "r") as f:
        content = f.read()
        assert content.strip() == (main_content + "\nUncommitted change.").strip()
        assert "**SYNC STATUS:**" not in content # Ensure no sync markers were added

def test_uncommitted_changes_dry_run(temp_git_repo, capsys):
    """
    Scenario: Uncommitted changes exist in the repo.
    Expected: Script runs in dry mode but prints a warning.
    """
    main_content = "# Epic 1 -- Task 1.1: Test\nContent"
    main_file_path = Path("Resources/planning") / MAIN_FILE_NAME
    create_file(temp_git_repo, main_file_path, main_content, "Initial commit")

    # Introduce uncommitted change
    with open(temp_git_repo / main_file_path, "a") as f:
        f.write("\nUncommitted change.")

    sync_task_files.analyze_tasks(dry_run=True) # Dry run

    captured = capsys.readouterr()
    assert "Warning: There are uncommitted changes. For accurate results, commit or stash them." in captured.out
    # Ensure original file content (plus uncommitted change) is intact
    with open(temp_git_repo / main_file_path, "r") as f:
        assert f.read().strip() == (main_content + "\nUncommitted change.").strip()


def test_last_task_no_trailing_separator_update_main(temp_git_repo):
    """
    Scenario: PLANNING_TASKS.md has a task that is last and has no '---' separator.
              Individual file for this task is newer.
    Expected: Main file is updated correctly, and a '---' is NOT erroneously added if not needed.
              (Or, if the policy is to always add '---' except for very last, test that)
              Current policy of update_task_in_main_file is to add separator if it's not the very last element.
              If it is the last task, original separator (or lack thereof) is respected.
    """
    main_initial_content = """\
# Epic 1 -- Task 1.1: First Task
Content for 1.1
---
# Epic 1 -- Task 1.2: Last Task No Sep
Original content in main for 1.2
""" # No "---" after Task 1.2

    task1_content = "Status: Done\n\n# Epic 1 -- Task 1.1: First Task\nContent for 1.1"
    task2_individual_initial = "Status: ToDo\n\n# Epic 1 -- Task 1.2: Last Task No Sep\nOriginal content in main for 1.2"

    main_file_path = Path("Resources/planning") / MAIN_FILE_NAME
    task1_path = Path("Resources/planning/tasks") / "epic_1_task_1_1.md"
    task2_path = Path("Resources/planning/tasks") / "epic_1_task_1_2.md"

    create_file(temp_git_repo, main_file_path, main_initial_content, "Commit main v1")
    create_file(temp_git_repo, task1_path, task1_content, "Commit task1 v1")
    create_file(temp_git_repo, task2_path, task2_individual_initial, "Commit task2 v1")

    # Update individual file for task 1.2 to make it newer
    task2_individual_updated = """\
Status: In Progress

# Epic 1 -- Task 1.2: Last Task No Sep
Updated content for 1.2 from individual.
"""
    create_file(temp_git_repo, task2_path, task2_individual_updated, "Update task2 v2 (newer)")

    sync_task_files.analyze_tasks(dry_run=False)

    expected_main_content_after_sync = """\
# Epic 1 -- Task 1.1: First Task
Content for 1.1
---
# Epic 1 -- Task 1.2: Last Task No Sep
Updated content for 1.2 from individual.
""" # Should still have no "---" at the very end of the file
    with open(temp_git_repo / main_file_path, "r") as f:
        actual_main = f.read()
        print("Main after last task no sep update:\n", actual_main)
        assert actual_main.strip() == expected_main_content_after_sync.strip()
        assert not actual_main.rstrip().endswith("---") # Ensure no extra separator added at EOF

# TODO:
# - test removal of sync status marker when files become "In Sync" again (ADVANCED).

"""
To run these tests:
1. Ensure pytest is installed (`pip install pytest`).
2. Navigate to the repository root in your terminal.
3. Run `pytest Resources/planning/tests/test_sync_logic.py`
"""
