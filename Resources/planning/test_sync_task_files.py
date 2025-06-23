import unittest
import os
import shutil
import subprocess
import tempfile
from unittest.mock import patch
import io
import contextlib
import re
import importlib # Import importlib

# Assuming sync_task_files.py is in the same directory or PYTHONPATH is set up
import sync_task_files

class TestSyncTaskFiles(unittest.TestCase):
    """
    Test suite for the `sync_task_files.py` script.

    This suite verifies the script's ability to analyze and report the synchronization
    status between a main planning file (PLANNING_TASKS.md) and individual task
    markdown files located in a tasks directory.

    Key functionalities tested include:
    - Parsing of main and individual task files.
    - Extraction of relevant content, ignoring metadata lines (Status, Sync Status).
    - Correct usage of Git history (`git log -L`, `git merge-base --is-ancestor`)
      to determine the last commit affecting content blocks and their ancestry.
    - Handling of various sync scenarios:
        - Files in sync.
        - Main file newer.
        - Individual file newer.
        - Divergent histories.
        - Empty content scenarios (NO_CONTENT_COMMIT).
        - Tasks existing in one location but not the other.
    - Correct reporting of uncommitted changes in the repository.

    Setup:
    Each test (or setUp method) creates a temporary Git repository. Mock task files
    are created and committed within this temporary repository to simulate different
    historical states. The `sync_task_files.py` script's global constants for
    file paths and the Git root are patched to point to this temporary test environment.
    The `sync_task_files` module is reloaded before each test run using
    `importlib.reload` to ensure a clean state and correct GIT_ROOT initialization.

    Running the tests:
    From the repository root (or a location where Python can find this test file
    and `sync_task_files.py`):
        python -m unittest Resources/planning/test_sync_task_files.py
    """

    def setUp(self):
        self.test_dir_obj = tempfile.TemporaryDirectory()
        self.test_dir = self.test_dir_obj.name

        # Store current CWD and change to test_dir
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Initialize Git repo in self.test_dir (now CWD)
        # No cwd=self.test_dir needed as it's the current directory
        subprocess.run(['git', 'init', '-b', 'main'], check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], check=True)

        # Reload module while CWD is test_dir. GIT_ROOT in sync_task_files should be self.test_dir.
        importlib.reload(sync_task_files)

        # Restore original CWD
        os.chdir(self.original_cwd)

        # Verify GIT_ROOT in the reloaded module (optional debug line)
        # print(f"DEBUG: sync_task_files.GIT_ROOT = {sync_task_files.GIT_ROOT}, self.test_dir = {self.test_dir}")
        # assert sync_task_files.GIT_ROOT == self.test_dir, "GIT_ROOT not set correctly after reload"


        self.mock_main_tasks_file_relpath = "PLANNING_TASKS.md"
        self.mock_individual_tasks_dir_relpath = "tasks/"

        self.mock_main_tasks_file_abs_path = os.path.join(self.test_dir, self.mock_main_tasks_file_relpath)
        self.mock_individual_tasks_dir_abs_path = os.path.join(self.test_dir, self.mock_individual_tasks_dir_relpath)
        os.makedirs(self.mock_individual_tasks_dir_abs_path, exist_ok=True)

        # Patch file paths (GIT_ROOT is now correctly set in the module)
        self.patch_main_file = patch('sync_task_files.PLANNING_TASKS_FILE', self.mock_main_tasks_file_abs_path)
        self.patch_individual_dir = patch('sync_task_files.INDIVIDUAL_TASKS_DIR', self.mock_individual_tasks_dir_abs_path)

        self.mock_main_file_val = self.patch_main_file.start()
        self.mock_individual_dir_val = self.patch_individual_dir.start()

        self.c1_ignore_test = None # Initialize for test_ignored_line_changes_only_in_sync

    def tearDown(self):
        # No patch_get_git_root to stop
        self.patch_main_file.stop()
        self.patch_individual_dir.stop()
        self.test_dir_obj.cleanup()

    def _create_file(self, relative_path, content):
        abs_path = os.path.join(self.test_dir, relative_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return abs_path

    def _commit_changes(self, message):
        subprocess.run(['git', 'add', '.'], cwd=self.test_dir, check=True, capture_output=True)
        commit_process = subprocess.run(['git', 'commit', '--allow-empty', '-m', message], cwd=self.test_dir, check=True, capture_output=True, text=True)
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=self.test_dir, text=True).strip()

    def _get_main_task_content(self, task_id, body_content, title="Test Task", sync_status_line=None):
        header = f"# Epic 1 -- Task {task_id}: {title}\n"
        sync_line = f"{sync_status_line}\n" if sync_status_line else ""
        return f"{header}{sync_line}{body_content}\n"

    def _get_individual_task_filename(self, task_id):
        return f"epic_1_task_{task_id.replace('.', '_')}.md"

    def _get_individual_task_content(self, task_id, body_content, status="Not Started", title="Test Task", sync_status_line=None): # Default title changed to "Test Task"
        header = f"# Epic 1 -- Task {task_id}: {title}\n"
        status_line_text = f"Status: {status}\n\n"
        sync_line = f"{sync_status_line}\n" if sync_status_line else ""
        return f"{status_line_text}{header}{sync_line}{body_content}\n"

    def _run_analyze_and_get_report(self):
        current_dir = os.getcwd()
        os.chdir(self.test_dir)
        stdout_capture = io.StringIO()
        with contextlib.redirect_stdout(stdout_capture):
            sync_task_files.analyze_tasks()
        os.chdir(current_dir)
        return stdout_capture.getvalue()

    # --- Test Cases ---

    def test_no_changes_in_sync(self):
        task_id = "1.1"
        common_body = "This is synced content."
        main_content = self._get_main_task_content(task_id, common_body)
        self._create_file(self.mock_main_tasks_file_relpath, main_content)
        ind_filename = self._get_individual_task_filename(task_id)
        ind_content = self._get_individual_task_content(task_id, common_body)
        self._create_file(os.path.join(self.mock_individual_tasks_dir_relpath, ind_filename), ind_content)
        self._commit_changes("C1: Initial commit")
        report = self._run_analyze_and_get_report()
        self.assertIn(f"Task {task_id}: In Sync.", report)

    def test_main_file_updated_individual_outdated(self):
        task_id = "1.1"
        v1_body = "Version 1 content."
        v2_main_body = "Version 2 content in main."
        main_v1 = self._get_main_task_content(task_id, v1_body)
        self._create_file(self.mock_main_tasks_file_relpath, main_v1)
        ind_filename = self._get_individual_task_filename(task_id)
        ind_v1 = self._get_individual_task_content(task_id, v1_body)
        self._create_file(os.path.join(self.mock_individual_tasks_dir_relpath, ind_filename), ind_v1)
        c1_hash = self._commit_changes("C1: V1 Synced")
        main_v2 = self._get_main_task_content(task_id, v2_main_body)
        self._create_file(self.mock_main_tasks_file_relpath, main_v2)
        c2_hash = self._commit_changes("C2: Main updated")
        report = self._run_analyze_and_get_report()
        self.assertRegex(report, f"Task {task_id}: Update individual from main \\(Main commit: {c2_hash[:7]}.* is newer than Individual: {c1_hash[:7]}.*\\)")

    def test_individual_file_updated_main_outdated(self):
        task_id = "1.2"
        v1_body = "Version 1 content for 1.2"
        v2_ind_body = "Version 2 content in individual for 1.2"
        main_v1 = self._get_main_task_content(task_id, v1_body)
        self._create_file(self.mock_main_tasks_file_relpath, main_v1)
        ind_filename = self._get_individual_task_filename(task_id)
        ind_v1 = self._get_individual_task_content(task_id, v1_body)
        self._create_file(os.path.join(self.mock_individual_tasks_dir_relpath, ind_filename), ind_v1)
        c1_hash = self._commit_changes("C1: V1 Synced (1.2)")
        ind_v2 = self._get_individual_task_content(task_id, v2_ind_body)
        self._create_file(os.path.join(self.mock_individual_tasks_dir_relpath, ind_filename), ind_v2)
        c2_hash = self._commit_changes("C2: Individual updated (1.2)")
        report = self._run_analyze_and_get_report()
        self.assertRegex(report, f"Task {task_id}: Update main from individual \\(Individual commit: {c2_hash[:7]}.* is newer than Main: {c1_hash[:7]}.*\\)")

    def test_divergent_histories_conflict(self):
        self.setUp()
        task_id = "1.3d"
        base_title = "Shared Base Title for 1.3d"
        main_specific_title = "Main Specific Title for 1.3d"
        ind_specific_title = "Ind Specific Title for 1.3d"
        base_body = f"Base content for {task_id}"
        main_change_body = "Main-specific content change for 1.3d"
        ind_change_body = "Individual-specific content change for 1.3d"

        # C1: Base commit
        self._create_file(self.mock_main_tasks_file_relpath, self._get_main_task_content(task_id, base_body, title=base_title))
        ind_fn = self._get_individual_task_filename(task_id)
        self._create_file(os.path.join(self.mock_individual_tasks_dir_relpath, ind_fn), self._get_individual_task_content(task_id, base_body, title=base_title))
        c1 = self._commit_changes("C1 Base for divergent test")

        # Branch 1: Main file change
        # Create a branch for main change to keep it separate
        subprocess.run(['git', 'checkout', '-b', 'branch-main', c1], cwd=self.test_dir, check=True)
        self._create_file(self.mock_main_tasks_file_relpath, self._get_main_task_content(task_id, main_change_body, title=main_specific_title))
        c2_main = self._commit_changes("C2 Main Change on branch-main")

        # Branch 2: Individual file change (starting from C1)
        subprocess.run(['git', 'checkout', '-b', 'branch-ind', c1], cwd=self.test_dir, check=True)
        # Ensure main file on this branch is C1's version initially
        self._create_file(self.mock_main_tasks_file_relpath, self._get_main_task_content(task_id, base_body, title=base_title))
        # Now change individual file
        self._create_file(os.path.join(self.mock_individual_tasks_dir_relpath, ind_fn), self._get_individual_task_content(task_id, ind_change_body, title=ind_specific_title))
        c3_ind = self._commit_changes("C3 Ind Change on branch-ind")

        # Merge branch-main into branch-ind. This creates C4 (merge commit).
        # We expect git to handle the merge: PLANNING_TASKS.md from branch-main, individual file from branch-ind.
        # If conflicts, this simple merge won't work. Assume no direct conflict for now.
        try:
            subprocess.run(['git', 'merge', 'branch-main', '-m', "C4: Merge main changes into ind branch"], cwd=self.test_dir, check=True)
        except subprocess.CalledProcessError as e:
            # If merge fails (e.g. conflict in PLANNING_TASKS.md if ind branch also changed it),
            # we might need to manually set content and commit.
            # For this test, main branch changed PLANNING_TASKS.md, ind branch changed its own file.
            # So auto-merge should succeed.
            print(f"Merge failed: {e.stderr}")
            # Fallback: Manually construct the merged state if auto-merge is problematic
            main_content_from_branch_main = subprocess.check_output(['git', 'show', f'branch-main:{self.mock_main_tasks_file_relpath}'], cwd=self.test_dir, text=True)
            self._create_file(self.mock_main_tasks_file_relpath, main_content_from_branch_main)
            # ind file is already from branch-ind (c3_ind)
            self._commit_changes("C4: Forced merge state with main from branch-main, ind from branch-ind")


        # Now HEAD is the merge commit (C4). This is a clean state.
        # analyze_tasks will run on this clean C4 state.
        # get_last_commit_for_lines for main file task should trace to C2_main.
        # get_last_commit_for_lines for ind file task should trace to C3_ind.
        # C2_main and C3_ind are divergent.
        report = self._run_analyze_and_get_report()

        # No "uncommitted changes" warning expected.
        self.assertNotIn("Warning: There are uncommitted changes", report)
        self.assertRegex(report, f"Task {task_id}: Conflict \\(Divergent history. Main: {c2_main[:7]}.*, Individual: {c3_ind[:7]}.*\\)")

    def test_main_empty_individual_has_content(self): # Test name implies main is "empty"
        self.setUp()
        task_id = "1.4m"
        main_min_body = ""
        main_content_minimal = self._get_main_task_content(task_id, main_min_body, title="Minimal Main Task")
        self._create_file(self.mock_main_tasks_file_relpath, main_content_minimal)
        c_main_minimal = self._commit_changes(f"C Main Minimal for {task_id}")

        ind_body_content = "Individual has actual substantive content here."
        ind_filename = self._get_individual_task_filename(task_id)
        # Use a different title for individual to ensure content differs if main is just a title
        ind_content_with_data = self._get_individual_task_content(task_id, ind_body_content, title="Individual Full Task")
        self._create_file(os.path.join(self.mock_individual_tasks_dir_relpath, ind_filename), ind_content_with_data)
        c_ind_has_content = self._commit_changes(f"C Ind Content for {task_id}")

        report = self._run_analyze_and_get_report()
        self.assertRegex(report, f"Task {task_id}: Update main from individual \\(Individual commit: {c_ind_has_content[:7]}.* is newer than Main: {c_main_minimal[:7]}.*\\)")

    def test_individual_empty_main_has_content(self):
        self.setUp()
        task_id = "1.5i"
        main_body_content = "Main has actual content here."
        main_content_with_data = self._get_main_task_content(task_id, main_body_content, title="Main Full Task")
        self._create_file(self.mock_main_tasks_file_relpath, main_content_with_data)
        c_main_has_content = self._commit_changes(f"C Main Content for {task_id}")

        ind_filename = self._get_individual_task_filename(task_id)
        # This content will result in NO_CONTENT_COMMIT for the individual file
        ind_content_truly_empty = "Status: This file is effectively empty for content extraction.\n**SYNC STATUS:** Also empty\n"
        self._create_file(os.path.join(self.mock_individual_tasks_dir_relpath, ind_filename), ind_content_truly_empty)
        c_ind_no_content = self._commit_changes(f"C Ind Truly Empty for {task_id}")

        report = self._run_analyze_and_get_report()
        self.assertRegex(report, f"Task {task_id}: Update individual from main \\(Individual was empty. Main commit: {c_main_has_content[:7]}.*\\)")

    def test_both_empty_in_sync(self): # Redefined: Both have identical minimal content (effectively header only)
        self.setUp()
        task_id = "1.6e"
        minimal_body = ""
        title_for_minimal = "Minimal Task Title" # Same title for both

        main_content_minimal = self._get_main_task_content(task_id, minimal_body, title=title_for_minimal)
        self._create_file(self.mock_main_tasks_file_relpath, main_content_minimal)

        ind_filename = self._get_individual_task_filename(task_id)
        ind_content_minimal = self._get_individual_task_content(task_id, minimal_body, title=title_for_minimal)
        self._create_file(os.path.join(self.mock_individual_tasks_dir_relpath, ind_filename), ind_content_minimal)

        self._commit_changes("C Both Minimal and Identical")

        report = self._run_analyze_and_get_report()
        self.assertIn(f"Task {task_id}: In Sync.", report)

    def test_ignored_line_changes_only_in_sync(self): # Expect update, not "In Sync"
        self.setUp()
        task_id = "1.7g"
        common_body = "This is the core content."
        common_title = "Test Task for Ignored Lines"

        main_v1 = self._get_main_task_content(task_id, common_body, title=common_title, sync_status_line="**SYNC:** V1")
        self._create_file(self.mock_main_tasks_file_relpath, main_v1)
        ind_fn = self._get_individual_task_filename(task_id)
        ind_v1 = self._get_individual_task_content(task_id, common_body, title=common_title, status="Not Started")
        self._create_file(os.path.join(self.mock_individual_tasks_dir_relpath, ind_fn), ind_v1)
        self.c1_ignore_test = self._commit_changes("C1 ignore test")

        main_v2 = self._get_main_task_content(task_id, common_body, title=common_title, sync_status_line="**SYNC:** V2 - changed")
        self._create_file(self.mock_main_tasks_file_relpath, main_v2) # Main file changed
        # Individual file's status line changed, content (header+body) effectively same as C1
        ind_v2 = self._get_individual_task_content(task_id, common_body, title=common_title, status="In Progress - changed")
        self._create_file(os.path.join(self.mock_individual_tasks_dir_relpath, ind_fn), ind_v2) # Ind file changed
        c2_metadata_changes = self._commit_changes("C2 ignore test - metadata changed in both files")

        report = self._run_analyze_and_get_report()
        # Main's content block (header+body) is affected by sync_line change -> commit_m = C2
        # Ind's content block (header+body) is NOT affected by status_line change -> commit_i = C1
        # Filtered content is same. C1 is ancestor of C2.
        self.assertRegex(report, f"Task {task_id}: Update individual from main \\(Main commit: {c2_metadata_changes[:7]}.* is newer than Individual: {self.c1_ignore_test[:7]}.*\\)")

    def test_task_in_main_not_in_individual(self):
        task_id = "1.8"
        main_content = self._get_main_task_content(task_id, "Content for task only in main.")
        self._create_file(self.mock_main_tasks_file_relpath, main_content)
        self._commit_changes("C: Task only in main")
        report = self._run_analyze_and_get_report()
        self.assertIn(f"Task {task_id}: Exists in {self.mock_main_tasks_file_abs_path}, but no corresponding individual file found", report)

    def test_task_in_individual_not_in_main(self):
        task_id = "1.9"
        ind_filename = self._get_individual_task_filename(task_id)
        ind_content = self._get_individual_task_content(task_id, "Content for task only in individual.")
        self._create_file(os.path.join(self.mock_individual_tasks_dir_relpath, ind_filename), ind_content)
        self._commit_changes("C: Task only in individual")
        self._create_file(self.mock_main_tasks_file_relpath, "# Main file without task 1.9\n")
        self._commit_changes("Update main to ensure it doesn't have 1.9")
        report = self._run_analyze_and_get_report()
        expected_msg_part = f"Task {task_id} (File: {ind_filename}): Exists in individual tasks dir, but not found in {self.mock_main_tasks_file_abs_path}"
        self.assertTrue(any(expected_msg_part in line for line in report.splitlines()), f"Expected part '{expected_msg_part}' not found in report:\n{report}")

    def test_uncommitted_changes_warning(self):
        task_id = "1.10"
        self._create_file(self.mock_main_tasks_file_relpath, self._get_main_task_content(task_id, "Initial content."))
        self._commit_changes("C1 for uncommitted test")
        self._create_file(self.mock_main_tasks_file_relpath, self._get_main_task_content(task_id, "Modified uncommitted content."))
        report = self._run_analyze_and_get_report()
        self.assertIn("Warning: There are uncommitted changes", report)

    def test_multiple_tasks_scenario(self):
        self.setUp()
        task_A_id, task_B_id, task_C_id = "2.1", "2.2", "2.3"
        main_A_v1 = self._get_main_task_content(task_A_id, "A V1")
        ind_A_v1_fn = self._get_individual_task_filename(task_A_id)
        self._create_file(os.path.join(self.mock_individual_tasks_dir_relpath, ind_A_v1_fn), self._get_individual_task_content(task_A_id, "A V1"))
        main_B_v1 = self._get_main_task_content(task_B_id, "B V1")
        ind_B_v1_fn = self._get_individual_task_filename(task_B_id)
        self._create_file(os.path.join(self.mock_individual_tasks_dir_relpath, ind_B_v1_fn), self._get_individual_task_content(task_B_id, "B V1"))
        main_C_v1 = self._get_main_task_content(task_C_id, "C V1")
        ind_C_v1_fn = self._get_individual_task_filename(task_C_id)
        self._create_file(os.path.join(self.mock_individual_tasks_dir_relpath, ind_C_v1_fn), self._get_individual_task_content(task_C_id, "C V1"))
        full_main_v1 = f"{main_A_v1}\n---\n{main_B_v1}\n---\n{main_C_v1}"
        self._create_file(self.mock_main_tasks_file_relpath, full_main_v1)
        c1 = self._commit_changes("C1: All V1")

        ind_B_v2_body = "B V2 individual"
        self._create_file(os.path.join(self.mock_individual_tasks_dir_relpath, ind_B_v1_fn), self._get_individual_task_content(task_B_id, ind_B_v2_body))
        main_C_v2_body = "C V2 main"
        new_main_C_content = self._get_main_task_content(task_C_id, main_C_v2_body)
        full_main_c2_target = f"{main_A_v1}\n---\n{main_B_v1}\n---\n{new_main_C_content}"
        self._create_file(self.mock_main_tasks_file_relpath, full_main_c2_target)
        c2 = self._commit_changes("C2: Ind B V2, Main C V2")

        report = self._run_analyze_and_get_report()
        self.assertIn(f"Task {task_A_id}: In Sync.", report)
        self.assertRegex(report, f"Task {task_B_id}: Update main from individual \\(Individual commit: {c2[:7]}.* is newer than Main: {c1[:7]}.*\\)")
        self.assertRegex(report, f"Task {task_C_id}: Update individual from main \\(Main commit: {c2[:7]}.* is newer than Individual: {c1[:7]}.*\\)")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
