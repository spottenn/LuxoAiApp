import unittest
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone

# Add the parent directory of 'planning' to sys.path to allow direct import of sync_task_files
import sys
# Assuming the script is run from the root of the repository or a similar context
# where 'Resources' is a top-level directory.
# Adjust if the execution context for tests is different.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from Resources.planning.sync_task_files import analyze_tasks, get_git_root, PLANNING_TASKS_FILE, INDIVIDUAL_TASKS_DIR

class TestSyncTaskFiles(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # This is to ensure that the global GIT_ROOT in sync_task_files is set correctly
        # if it's determined at import time. We might need to re-import or mock.
        # For now, assume we run tests from a context where GIT_ROOT is the main repo.
        # The test-specific git repos will be handled within each test or setUp.
        cls.original_cwd = os.getcwd()
        cls.project_root = get_git_root()
        if not cls.project_root:
            raise Exception("Failed to get project root. Ensure tests are run within the git repo.")

    def setUp(self):
        # Create a temporary directory for each test
        self.test_dir = tempfile.mkdtemp(prefix="test_sync_")
        os.chdir(self.test_dir)

        # Initialize a Git repository in the test directory
        self._run_command(['git', 'init', '-b', 'main'])
        self._run_command(['git', 'config', 'user.email', 'test@example.com'])
        self._run_command(['git', 'config', 'user.name', 'Test User'])

        # Create necessary directory structure
        self.planning_dir = os.path.join(self.test_dir, "Resources", "planning")
        self.tasks_dir = os.path.join(self.planning_dir, "tasks")
        os.makedirs(self.tasks_dir, exist_ok=True)

        # Crucial: Override the global constants in the imported module for the duration of the test
        self.original_planning_tasks_file = PLANNING_TASKS_FILE
        self.original_individual_tasks_dir = INDIVIDUAL_TASKS_DIR

        # Point the script's constants to our temporary test locations
        # Note: This is a common way to handle module-level constants in tests,
        # but can be tricky if modules are reloaded or if constants are used in decorators/defaults.
        # An alternative is to pass them as arguments to functions if the script design allows.
        sys.modules['Resources.planning.sync_task_files'].PLANNING_TASKS_FILE = os.path.join(self.planning_dir, "PLANNING_TASKS.md")
        sys.modules['Resources.planning.sync_task_files'].INDIVIDUAL_TASKS_DIR = self.tasks_dir
        sys.modules['Resources.planning.sync_task_files'].GIT_ROOT = self.test_dir # Critical for git commands in script

        # Need to ensure the `sync_task_files` module uses this temp git root.
        # The `GIT_ROOT` in `sync_task_files` is set at its import time based on its location.
        # We must override it for test functions. This is done above.

    def tearDown(self):
        # Restore original constants
        sys.modules['Resources.planning.sync_task_files'].PLANNING_TASKS_FILE = self.original_planning_tasks_file
        sys.modules['Resources.planning.sync_task_files'].INDIVIDUAL_TASKS_DIR = self.original_individual_tasks_dir
        sys.modules['Resources.planning.sync_task_files'].GIT_ROOT = self.project_root # Restore to original project root

        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def _run_command(self, command, check=True):
        """Helper to run shell commands."""
        return subprocess.run(command, capture_output=True, text=True, check=check, cwd=self.test_dir)

    def _create_file(self, filepath, content):
        """Helper to create a file with content in the test directory."""
        abs_filepath = os.path.join(self.test_dir, filepath)
        os.makedirs(os.path.dirname(abs_filepath), exist_ok=True)
        with open(abs_filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return abs_filepath

    def _commit_changes(self, message):
        """Commits all current changes in the test repo."""
        self._run_command(['git', 'add', '.'])
        self._run_command(['git', 'commit', '-m', message])
        # Get commit hash
        return self._run_command(['git', 'rev-parse', 'HEAD']).stdout.strip()

    def test_initial_structure(self):
        """A simple test to ensure setUp and tearDown are working."""
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertTrue(os.path.exists(self.tasks_dir))
        # Create a dummy main planning file
        main_file_path_in_script = sys.modules['Resources.planning.sync_task_files'].PLANNING_TASKS_FILE
        self._create_file(main_file_path_in_script, "# Test Planning File\n")
        self._commit_changes("Initial commit for structure test")

        # Example: Check if analyze_tasks can run without erroring (though it won't do much)
        # We need to capture stdout to check its output.
        # For now, just a basic run.
        try:
            # Redirect stdout to check script's print statements
            from io import StringIO
            captured_output = StringIO()
            sys.stdout = captured_output
            analyze_tasks() # This will use the overridden GIT_ROOT
            sys.stdout = sys.__stdout__ # Reset redirect
            output = captured_output.getvalue()
            self.assertIn("--- Task Sync Status Report (Dry Run) ---", output)
        except Exception as e:
            self.fail(f"analyze_tasks() raised an exception: {e}")

    def _capture_analyze_tasks_output(self):
        from io import StringIO
        captured_output = StringIO()
        original_stdout = sys.stdout
        try:
            sys.stdout = captured_output
            analyze_tasks()
        finally:
            sys.stdout = original_stdout
        return captured_output.getvalue()

    def test_scenario_in_sync(self):
        """Scenario 1: Main and individual files are identical and from the same commit."""
        main_file_script_path = sys.modules['Resources.planning.sync_task_files'].PLANNING_TASKS_FILE
        individual_tasks_script_dir = sys.modules['Resources.planning.sync_task_files'].INDIVIDUAL_TASKS_DIR

        task_content_body = "This is the content of task 1.1.\nIt has multiple lines."
        task_heading = "# Epic 1 -- Task 1.1: Test Task In Sync"
        full_task_content = f"{task_heading}\n{task_content_body}"

        # Create main planning file
        self._create_file(main_file_script_path, f"{full_task_content}\n---\n")

        # Create individual task file
        individual_file_path = os.path.join(individual_tasks_script_dir, "epic_1_task_1_1.md")
        self._create_file(individual_file_path, f"{full_task_content}\nStatus: Open\n")

        self._commit_changes("Feat: Add task 1.1, in sync")

        output = self._capture_analyze_tasks_output()

        self.assertIn("Task 1.1: In Sync.", output)
        self.assertNotIn("Conflict", output)
        self.assertNotIn("Update main", output)
        self.assertNotIn("Update individual", output)

    def test_scenario_main_newer(self):
        """Scenario 2: Main File Newer."""
        main_file_script_path = sys.modules['Resources.planning.sync_task_files'].PLANNING_TASKS_FILE
        individual_tasks_script_dir = sys.modules['Resources.planning.sync_task_files'].INDIVIDUAL_TASKS_DIR
        individual_file_rel_path = os.path.join(os.path.basename(individual_tasks_script_dir), "epic_1_task_1_1.md") # relative for create_file

        task_heading = "# Epic 1 -- Task 1.1: Test Task Main Newer"
        original_body = "Original content."
        updated_body_main = "Main file has updated content."

        # Initial commit: individual file has original content
        self._create_file(os.path.join(self.tasks_dir, "epic_1_task_1_1.md"), f"{task_heading}\n{original_body}\nStatus: Open")
        self._commit_changes("Add task 1.1 - individual version")
        commit_individual = self._run_command(['git', 'rev-parse', 'HEAD']).stdout.strip()


        # Second commit: main file has updated content
        self._create_file(main_file_script_path, f"{task_heading}\n{updated_body_main}\n---\n")
        self._commit_changes("Update task 1.1 in main file")
        commit_main = self._run_command(['git', 'rev-parse', 'HEAD']).stdout.strip()

        output = self._capture_analyze_tasks_output()

        # Make assertion less brittle: check for key components
        self.assertIn("Task 1.1: Update individual from main", output)
        self.assertIn(f"Main commit: {commit_main}", output)
        self.assertIn(f"is newer than Individual: {commit_individual}", output)
        self.assertNotIn("In Sync.", output)
        self.assertNotIn("Update main from individual", output)

    def test_scenario_individual_newer(self):
        """Scenario 3: Individual File Newer."""
        main_file_script_path = sys.modules['Resources.planning.sync_task_files'].PLANNING_TASKS_FILE
        individual_tasks_script_dir = sys.modules['Resources.planning.sync_task_files'].INDIVIDUAL_TASKS_DIR

        task_heading = "# Epic 1 -- Task 1.1: Test Task Individual Newer"
        original_body = "Original content for task."
        updated_body_individual = "Individual file has updated content."

        # Initial commit: main file has original content
        self._create_file(main_file_script_path, f"{task_heading}\n{original_body}\n---\n")
        self._commit_changes("Add task 1.1 - main file version")
        commit_main = self._run_command(['git', 'rev-parse', 'HEAD']).stdout.strip()

        # Second commit: individual file has updated content
        individual_file_path = os.path.join(individual_tasks_script_dir, "epic_1_task_1_1.md")
        self._create_file(individual_file_path, f"{task_heading}\n{updated_body_individual}\nStatus: In Progress")
        self._commit_changes("Update task 1.1 in individual file")
        commit_individual = self._run_command(['git', 'rev-parse', 'HEAD']).stdout.strip()

        output = self._capture_analyze_tasks_output()

        self.assertIn("Task 1.1: Update main from individual", output)
        self.assertIn(f"Individual commit: {commit_individual}", output)
        self.assertIn(f"is newer than Main: {commit_main}", output)
        self.assertNotIn("In Sync.", output)
        self.assertNotIn("Update individual from main", output)


    def test_scenario_divergent_history(self):
        """Scenario 4: Divergent History.
        This test checks if the script correctly identifies divergent histories
        based on the commit hashes of the content blocks.
        """
        main_file_script_path = sys.modules['Resources.planning.sync_task_files'].PLANNING_TASKS_FILE
        individual_tasks_script_dir = sys.modules['Resources.planning.sync_task_files'].INDIVIDUAL_TASKS_DIR
        individual_file_path = os.path.join(individual_tasks_script_dir, "epic_1_task_1_1.md") # Actual path for creation
        relative_individual_file_path = "Resources/planning/tasks/epic_1_task_1_1.md" # Path for git checkout

        task_heading = "# Epic 1 -- Task 1.1: Test Task Divergent"
        base_body = "Base content."
        main_specific_update = "Main file has a unique update for task 1.1."
        individual_specific_update = "Individual file has its own unique update for task 1.1."

        # 1. Base commit: Both files have base_body for task 1.1
        self._create_file(main_file_script_path, f"{task_heading}\n{base_body}\n---\n")
        self._create_file(individual_file_path, f"{task_heading}\n{base_body}\nStatus: Base")
        base_commit_hash = self._commit_changes("Base for divergence test")

        # 2. Commit M1 (on current branch, say 'main'): Update main_file_script_path with main_specific_update.
        #    Individual file (individual_file_path) still contains base_body from base_commit_hash.
        self._create_file(main_file_script_path, f"{task_heading}\n{main_specific_update}\n---\n")
        m1_commit_hash = self._commit_changes("Commit M1: Main file updated") # m1 is child of base

        # 3. Create divergence: Go back to base_commit_hash, create a new branch 'indiv_branch'.
        #    On 'indiv_branch', commit I1: Update individual_file_path with individual_specific_update.
        #    For this commit I1, main_file_script_path should contain base_body.
        self._run_command(['git', 'checkout', '-b', 'indiv_branch', base_commit_hash]) # New branch from base
        self._create_file(individual_file_path, f"{task_heading}\n{individual_specific_update}\nStatus: Indiv Update")
        self._create_file(main_file_script_path, f"{task_heading}\n{base_body}\n---\n") # Ensure main is base on this branch
        self._run_command(['git', 'add', main_file_script_path])
        i1_commit_hash = self._commit_changes("Commit I1: Individual file updated on indiv_branch, main is base") # i1 is child of base

        # M1 and I1 are now divergent commits from base.

        # 4. Prepare the state for analysis: Go back to 'main' branch (which is at M1).
        #    Then, bring the content of the individual file from 'indiv_branch' (commit I1) into the working directory.
        #    This simulates a state where divergent contents are present (e.g., post-merge attempt or manual copy).
        self._run_command(['git', 'checkout', 'main']) # Now at M1. Main file has M1 content, Indiv file has base content.

        # Get the individual file content from I1 commit on indiv_branch
        self._run_command(['git', 'checkout', 'indiv_branch', '--', individual_file_path])
        # After this, working directory on 'main' branch has:
        # - Main file: M1 content (from M1 commit)
        # - Individual file: I1 content (copied from I1 commit on indiv_branch)

        # Commit this mixed state. This is the state analyze_tasks will see.
        final_commit = self._commit_changes("Commit mixed content state for divergent analysis")

        # analyze_tasks will be run on this `final_commit` state.
        # - It parses main_file_script_path (containing main_specific_update).
        #   `get_last_commit_for_lines` for these lines should trace back to m1_commit_hash.
        # - It parses individual_file_path (containing individual_specific_update).
        #   `get_last_commit_for_lines` for these lines should trace back to i1_commit_hash.
        # Then, it compares m1_commit_hash and i1_commit_hash for ancestry.
        output = self._capture_analyze_tasks_output()

        self.assertIn("Task 1.1: Conflict (Divergent history.", output, f"Output was: {output}")
        self.assertIn(f"Main: {m1_commit_hash}", output)
        self.assertIn(f"Individual: {i1_commit_hash}", output)
        self.assertIn("Needs SYNC STATUS marker.", output)
        self.assertNotIn("Warning: There are uncommitted changes", output) # Should be clean before analysis

    def test_scenario_content_diff_same_commit(self):
        """Scenario 5: Content Difference, Same Commit (e.g. uncommitted changes)."""
        main_file_script_path = sys.modules['Resources.planning.sync_task_files'].PLANNING_TASKS_FILE
        individual_tasks_script_dir = sys.modules['Resources.planning.sync_task_files'].INDIVIDUAL_TASKS_DIR
        individual_file_path = os.path.join(individual_tasks_script_dir, "epic_1_task_1_1.md")

        task_heading = "# Epic 1 -- Task 1.1: Test Content Diff Same Commit"
        committed_body = "This is the committed content."
        main_file_uncommitted_change = "This is uncommitted content in main."

        # Commit identical content for both
        self._create_file(main_file_script_path, f"{task_heading}\n{committed_body}\n---\n")
        self._create_file(individual_file_path, f"{task_heading}\n{committed_body}\nStatus: Committed")
        commit_hash = self._commit_changes("Commit base for same_commit_diff test")

        # Now, modify main file in working directory without committing
        self._create_file(main_file_script_path, f"{task_heading}\n{main_file_uncommitted_change}\n---\n")

        output = self._capture_analyze_tasks_output()

        # The script's `get_last_commit_for_lines` for the modified main file section
        # should still point to `commit_hash` because the *lines themselves* (if completely new)
        # won't have a commit history yet, or if partially changed, it might pick up the old commit.
        # The content comparison happens on working directory content.
        # If `get_last_commit_for_lines` for the *new* lines in main returns `commit_hash` (or similar),
        # and for individual it's `commit_hash`, then the "Same commit, but content differs" should trigger.

        # The `check_for_uncommitted_changes()` should print a warning.
        self.assertIn("Warning: There are uncommitted changes", output)

        expected_message = f"Task 1.1: Conflict (Same commit {commit_hash}, but content differs). Working tree changes or merge issue?"
        self.assertIn(expected_message, output)

    def test_scenario_task_in_main_not_individual(self):
        """Scenario 6: Task in Main, Not Individual."""
        main_file_script_path = sys.modules['Resources.planning.sync_task_files'].PLANNING_TASKS_FILE

        task_heading = "# Epic 1 -- Task 1.1: Main Only Task"
        self._create_file(main_file_script_path, f"{task_heading}\nContent for main only task.\n---\n")
        self._commit_changes("Add task 1.1 to main file only")

        output = self._capture_analyze_tasks_output()

        # Use the actual path the script would use (which is absolute in this test setup)
        script_main_file_path_used_in_output = sys.modules['Resources.planning.sync_task_files'].PLANNING_TASKS_FILE
        script_individual_dir_used_in_output = sys.modules['Resources.planning.sync_task_files'].INDIVIDUAL_TASKS_DIR
        expected_message = f"Task 1.1: Exists in {script_main_file_path_used_in_output}, but no corresponding individual file found in {script_individual_dir_used_in_output}."
        self.assertIn(expected_message, output)

    def test_scenario_task_in_individual_not_main(self):
        """Scenario 7: Task in Individual, Not Main."""
        main_file_script_path = sys.modules['Resources.planning.sync_task_files'].PLANNING_TASKS_FILE
        individual_tasks_script_dir = sys.modules['Resources.planning.sync_task_files'].INDIVIDUAL_TASKS_DIR
        individual_file_name = "epic_1_task_1_1.md"
        individual_file_path = os.path.join(individual_tasks_script_dir, individual_file_name)

        task_heading = "# Epic 1 -- Task 1.1: Individual Only Task"
        self._create_file(individual_file_path, f"{task_heading}\nContent for individual only task.\nStatus: Orphaned")
        self._commit_changes("Add task 1.1 to individual file only")

        # Main file is empty or has no tasks
        self._create_file(main_file_script_path, "# Main Planning File - No Tasks\n")
        self._commit_changes("Update main file to be empty of tasks") # Make sure it's part of a commit

        output = self._capture_analyze_tasks_output()

        script_main_file_path_used_in_output = sys.modules['Resources.planning.sync_task_files'].PLANNING_TASKS_FILE
        expected_message = f"Task 1.1 (File: {individual_file_name}): Exists in individual tasks dir, but not found in {script_main_file_path_used_in_output}."
        self.assertIn(expected_message, output)

    def test_scenario_empty_content_main_vs_individual_has_content(self):
        """Scenario 8a: Empty Content in Main, Individual has content."""
        main_file_script_path = sys.modules['Resources.planning.sync_task_files'].PLANNING_TASKS_FILE
        individual_tasks_script_dir = sys.modules['Resources.planning.sync_task_files'].INDIVIDUAL_TASKS_DIR
        individual_file_path = os.path.join(individual_tasks_script_dir, "epic_1_task_1_1.md")

        task_heading = "# Epic 1 -- Task 1.1: Test Empty Main"

        # Main file has task heading but no content (or only ignored lines)
        # The script's `get_line_numbers_and_content` for main should yield empty content.
        # This means `commit_main` will be "NO_CONTENT_COMMIT".
        self._create_file(main_file_script_path, f"{task_heading}\n**SYNC STATUS:** Some Status\n---\n") # Only ignored line
        self._commit_changes("Commit main file with effectively empty task 1.1")

        # Individual file has content
        self._create_file(individual_file_path, f"{task_heading}\nThis is real content in individual.\nStatus: Has Content")
        commit_individual = self._commit_changes("Commit individual file with content for 1.1")

        output = self._capture_analyze_tasks_output()
        self.assertIn("Task 1.1: Update main from individual (Main was empty.", output)
        self.assertIn(f"Individual commit: {commit_individual}", output)

    def test_scenario_empty_content_individual_vs_main_has_content(self):
        """Scenario 8b: Empty Content in Individual, Main has content."""
        main_file_script_path = sys.modules['Resources.planning.sync_task_files'].PLANNING_TASKS_FILE
        individual_tasks_script_dir = sys.modules['Resources.planning.sync_task_files'].INDIVIDUAL_TASKS_DIR
        individual_file_path = os.path.join(individual_tasks_script_dir, "epic_1_task_1_1.md")

        task_heading = "# Epic 1 -- Task 1.1: Test Empty Individual"

        # Main file has content
        self._create_file(main_file_script_path, f"{task_heading}\nThis is real content in main.\n---\n")
        commit_main = self._commit_changes("Commit main file with content for 1.1")

        # Individual file has task heading but effectively no content
        self._create_file(individual_file_path, f"{task_heading}\nStatus: Effectively Empty\n**SYNC STATUS:** Some status\n")
        self._commit_changes("Commit individual file with effectively empty task 1.1") # commit_individual will be "NO_CONTENT_COMMIT"

        output = self._capture_analyze_tasks_output()
        self.assertIn("Task 1.1: Update individual from main (Individual was empty.", output)
        self.assertIn(f"Main commit: {commit_main}", output)

    def test_scenario_both_empty_content(self):
        """Scenario 8c: Both Main and Individual have empty content for a task."""
        main_file_script_path = sys.modules['Resources.planning.sync_task_files'].PLANNING_TASKS_FILE
        individual_tasks_script_dir = sys.modules['Resources.planning.sync_task_files'].INDIVIDUAL_TASKS_DIR
        individual_file_path = os.path.join(individual_tasks_script_dir, "epic_1_task_1_1.md")

        task_heading = "# Epic 1 -- Task 1.1: Both Empty"

        self._create_file(main_file_script_path, f"{task_heading}\n---\n") # Empty
        self._create_file(individual_file_path, f"{task_heading}\nStatus: Empty") # Empty
        self._commit_changes("Commit both main and individual as empty for task 1.1")

        output = self._capture_analyze_tasks_output()
        # If both are "NO_CONTENT_COMMIT", they should be considered in sync.
        self.assertIn("Task 1.1: In Sync.", output)


    def test_scenario_multiple_tasks_varied_status(self):
        """Scenario 10: Multiple Tasks with varied statuses."""
        main_file_script_path = sys.modules['Resources.planning.sync_task_files'].PLANNING_TASKS_FILE
        tasks_dir = sys.modules['Resources.planning.sync_task_files'].INDIVIDUAL_TASKS_DIR

        # Task 1.1: In Sync
        task1_heading = "# Epic 1 -- Task 1.1: Multi-Test In Sync"
        task1_body = "Content for task 1.1"
        self._create_file(main_file_script_path, f"{task1_heading}\n{task1_body}\n---\n")
        self._create_file(os.path.join(tasks_dir, "epic_1_task_1_1.md"), f"{task1_heading}\n{task1_body}\nStatus: Sync")
        self._commit_changes("Task 1.1 for multi-test")

        # Task 1.2: Main Newer
        task2_heading = "# Epic 1 -- Task 1.2: Multi-Test Main Newer"
        task2_body_orig = "Original for 1.2"
        task2_body_main_new = "Main updated 1.2"
        self._create_file(os.path.join(tasks_dir, "epic_1_task_1_2.md"), f"{task2_heading}\n{task2_body_orig}\nStatus: Old Indiv")
        self._commit_changes("Task 1.2 individual (older)")
        commit_task2_indiv = self._run_command(['git', 'rev-parse', 'HEAD']).stdout.strip()

        # Append task 2 to main file (which has task 1)
        with open(main_file_script_path, 'a', encoding='utf-8') as f:
            f.write(f"{task2_heading}\n{task2_body_main_new}\n---\n")
        self._commit_changes("Task 1.2 main (newer)")
        commit_task2_main = self._run_command(['git', 'rev-parse', 'HEAD']).stdout.strip()

        # Task 1.3: Individual Newer
        task3_heading = "# Epic 1 -- Task 1.3: Multi-Test Individual Newer"
        task3_body_orig = "Original for 1.3"
        task3_body_indiv_new = "Individual updated 1.3"
        # Append task 3 to main file with original content
        with open(main_file_script_path, 'a', encoding='utf-8') as f:
            f.write(f"{task3_heading}\n{task3_body_orig}\n---\n")
        self._commit_changes("Task 1.3 main (older)")
        commit_task3_main = self._run_command(['git', 'rev-parse', 'HEAD']).stdout.strip()

        self._create_file(os.path.join(tasks_dir, "epic_1_task_1_3.md"), f"{task3_heading}\n{task3_body_indiv_new}\nStatus: New Indiv")
        self._commit_changes("Task 1.3 individual (newer)")
        commit_task3_indiv = self._run_command(['git', 'rev-parse', 'HEAD']).stdout.strip()

        output = self._capture_analyze_tasks_output()

        self.assertIn("Task 1.1: In Sync.", output)
        self.assertIn(f"Task 1.2: Update individual from main (Main commit: {commit_task2_main}", output)
        self.assertIn(f"Task 1.3: Update main from individual (Individual commit: {commit_task3_indiv}", output)


if __name__ == '__main__':
    unittest.main()
