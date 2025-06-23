import os
import re
import subprocess
from datetime import datetime

# Constants
PLANNING_TASKS_FILE = "Resources/planning/PLANNING_TASKS.md"
INDIVIDUAL_TASKS_DIR = "Resources/planning/tasks/"
# STATUS_FILE = "Resources/planning/task-status.md" # Not directly used for sync logic

# Regexes (can be imported or redefined if this script becomes standalone)
TASK_HEADING_PATTERN = re.compile(r"^#\s*Epic\s*\d+\s*--\s*Task\s*([\d\.]+[a-zA-Z]?):(.*)", re.MULTILINE)
FILENAME_PATTERN = re.compile(r"epic_(\d+)_task_(\d+_\d+[a-zA-Z]?)\.md")
STATUS_LINE_PATTERN = re.compile(r"Status:.*\n?", re.IGNORECASE)
SYNC_STATUS_LINE_PATTERN = re.compile(r"\*\*SYNC STATUS:\*\*.*\n?", re.IGNORECASE)

# --- Git Interaction ---
def get_git_root():
    """Returns the root directory of the git repository."""
    try:
        return subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip()
    except subprocess.CalledProcessError:
        print("Error: Not a git repository or git command not found.")
        return None

GIT_ROOT = get_git_root()

def _run_git_command(command):
    """Helper to run a git command and return its output."""
    try:
        process = subprocess.run(command, capture_output=True, text=True, check=True, cwd=GIT_ROOT)
        return process.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running git command '{' '.join(command)}': {e.stderr.strip()}")
        return None
    except FileNotFoundError:
        print("Error: git command not found. Is git installed and in PATH?")
        return None


def get_last_commit_for_lines(filepath, start_line, end_line):
    """
    Gets the last commit hash and author date that modified the given line range in a file.
    Line numbers are 1-indexed.
    Returns (commit_hash, commit_date_iso) or (None, None) if error.
    """
    if not GIT_ROOT: return None, None
    
    abs_filepath = os.path.abspath(filepath)
    relative_filepath = os.path.relpath(abs_filepath, GIT_ROOT)

    # If start_line or end_line is -1 (from get_line_numbers_and_content meaning no relevant content found)
    # or if the range is otherwise invalid.
    if start_line == -1 or end_line == -1 or start_line > end_line :
        return "NO_CONTENT_COMMIT", "1970-01-01T00:00:00Z" # Special values for empty content

    # Using format %H for commit hash, %aI for author date (ISO 8601 strict)
    # Added --no-patch to prevent implicit patch display with -L
    cmd = [
        'git', 'log', '-1', '--no-patch',
        '--pretty=format:%H %aI', # Get hash and author date
        f'-L{start_line},{end_line}:{relative_filepath}'
    ]
    output = _run_git_command(cmd)
    if output:
        parts = output.split(' ', 1)
        if len(parts) == 2:
            commit_hash, commit_date_str = parts
            return commit_hash, commit_date_str 
    return None, None


def is_ancestor(commit1_hash, commit2_hash):
    """Checks if commit1 is an ancestor of commit2. Returns True, False, or None on error."""
    if commit1_hash == "NO_CONTENT_COMMIT" or commit2_hash == "NO_CONTENT_COMMIT":
        return False
    if commit1_hash == commit2_hash:
        return True 
        
    cmd = ['git', 'merge-base', '--is-ancestor', commit1_hash, commit2_hash]
    try:
        subprocess.run(cmd, check=True, capture_output=True, cwd=GIT_ROOT)
        return True
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            return False
        print(f"Error checking ancestry with git merge-base: {e.stderr.strip()}")
        return None
    except FileNotFoundError:
        print("Error: git command not found.")
        return None

def check_for_uncommitted_changes():
    """Checks if there are uncommitted changes in the Git working directory or staging area."""
    if not GIT_ROOT: return True
    
    try:
        subprocess.run(['git', 'diff', '--quiet'], check=True, cwd=GIT_ROOT)
        subprocess.run(['git', 'diff', '--cached', '--quiet'], check=True, cwd=GIT_ROOT)
        return False
    except subprocess.CalledProcessError:
        return True
    except FileNotFoundError:
        return True

# --- Content Parsing and Analysis ---

def get_task_id_from_filename(filename_basename):
    match = FILENAME_PATTERN.match(filename_basename)
    if match:
        return match.group(2).replace('_', '.')
    return None

def get_line_numbers_and_content(full_text_content, ignore_patterns=None, content_start_offset=0):
    lines = full_text_content.splitlines(keepends=True)
    relevant_lines_info = []
    for i, line_text in enumerate(lines):
        original_line_idx = content_start_offset + i
        skip_line = False
        if ignore_patterns:
            for pattern in ignore_patterns:
                if pattern.match(line_text):
                    skip_line = True
                    break
        if not skip_line:
            relevant_lines_info.append((line_text, original_line_idx))

    if not relevant_lines_info:
        return "", -1, -1

    content_str = "".join([info[0] for info in relevant_lines_info])
    start_line_num = relevant_lines_info[0][1] + 1
    end_line_num = relevant_lines_info[-1][1] + 1
    
    return content_str.strip(), start_line_num, end_line_num


def analyze_tasks():
    if not GIT_ROOT:
        print("Cannot proceed without git.")
        return

    if check_for_uncommitted_changes():
        print("Warning: There are uncommitted changes in your repository.")
        print("Please commit or stash them before running the sync script, as Git history is used for comparison.")

    try:
        with open(PLANNING_TASKS_FILE, 'r', encoding='utf-8') as f:
            main_file_full_content = f.read()
    except FileNotFoundError:
        print(f"Error: Main planning file not found at '{PLANNING_TASKS_FILE}'")
        return
    
    main_tasks_data = {}
    main_file_lines = main_file_full_content.splitlines(keepends=True)
    
    for match in TASK_HEADING_PATTERN.finditer(main_file_full_content):
        task_id = match.group(1)
        task_block_start_char_index = match.start()
        next_heading_match = TASK_HEADING_PATTERN.search(main_file_full_content, pos=match.end())
        limit_for_block_search = next_heading_match.start() if next_heading_match else len(main_file_full_content)
        current_task_block_in_main_file = main_file_full_content[task_block_start_char_index : limit_for_block_search]
        
        separator_in_block_match = re.search(r"\n\s*---\s*(\n|$)", current_task_block_in_main_file)
        if separator_in_block_match:
            task_definition_in_block = current_task_block_in_main_file[:separator_in_block_match.start()]
        else:
            task_definition_in_block = current_task_block_in_main_file.rstrip()

        block_start_line_0idx = main_file_full_content[:task_block_start_char_index].count('\n')
        content_main, start_line_main, end_line_main = get_line_numbers_and_content(
            task_definition_in_block, 
            ignore_patterns=[SYNC_STATUS_LINE_PATTERN],
            content_start_offset=block_start_line_0idx
        )
        
        commit_main, date_main = None, None
        if start_line_main != -1 :
             commit_main, date_main = get_last_commit_for_lines(PLANNING_TASKS_FILE, start_line_main, end_line_main)

        main_tasks_data[task_id] = {
            "raw_content": content_main,
            "commit": commit_main,
            "date": date_main,
            "start_line": start_line_main,
            "end_line": end_line_main
        }

    if not os.path.isdir(INDIVIDUAL_TASKS_DIR):
        print(f"Error: Individual tasks directory not found: {INDIVIDUAL_TASKS_DIR}")
        return

    report = []
    processed_individual_task_ids = set()

    for filename in sorted(os.listdir(INDIVIDUAL_TASKS_DIR)):
        if not FILENAME_PATTERN.match(filename):
            if filename.endswith(".md"):
                print(f"Info: Skipped file with non-standard name: {filename}")
            continue

        task_id_from_file = get_task_id_from_filename(filename)
        if not task_id_from_file: continue

        processed_individual_task_ids.add(task_id_from_file)
        filepath = os.path.join(INDIVIDUAL_TASKS_DIR, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                individual_file_full_content = f.read()
        except Exception as e:
            print(f"Error reading individual task file {filename}: {e}")
            report.append(f"Task {task_id_from_file} (File: {filename}): Error reading file.")
            continue

        content_individual, start_line_individual, end_line_individual = get_line_numbers_and_content(
            individual_file_full_content,
            ignore_patterns=[STATUS_LINE_PATTERN, SYNC_STATUS_LINE_PATTERN]
        )
        
        commit_individual, date_individual = None, None
        if start_line_individual == -1: # No actual content found after filtering
            commit_individual = "NO_CONTENT_COMMIT"
            date_individual = "1970-01-01T00:00:00Z"
        else: # Content found, get commit from git history
            commit_individual, date_individual = get_last_commit_for_lines(filepath, start_line_individual, end_line_individual)

        main_data = main_tasks_data.get(task_id_from_file)

        if not main_data:
            report.append(f"Task {task_id_from_file} (File: {filename}): Exists in individual tasks dir, but not found in {PLANNING_TASKS_FILE}.")
            continue
        
        norm_content_main = main_data["raw_content"].strip()
        norm_content_individual = content_individual.strip()

        if norm_content_main == norm_content_individual:
            status_msg = "In Sync."
        else:
            commit_m = main_data["commit"]
            date_m = main_data["date"]
            commit_i = commit_individual
            date_i = date_individual

            if not commit_m or not commit_i: # This includes case where one/both are None from git error
                status_msg = f"Conflict (Error fetching commit history. Main: {commit_m}, Ind: {commit_i}). Investigate."
            elif commit_m == "NO_CONTENT_COMMIT" and commit_i == "NO_CONTENT_COMMIT": # Both intentionally empty
                 status_msg = "In Sync." # Content should be "" vs ""
            elif commit_m == commit_i and commit_m != "NO_CONTENT_COMMIT":
                status_msg = f"Conflict (Same commit {commit_m}, but content differs). Working tree changes or merge issue?"
            else:
                is_main_ancestor_of_ind = is_ancestor(commit_m, commit_i)
                is_ind_ancestor_of_main = is_ancestor(commit_i, commit_m)

                if commit_m == "NO_CONTENT_COMMIT" and commit_i != "NO_CONTENT_COMMIT":
                    status_msg = f"Update main from individual (Main was empty. Individual commit: {commit_i} @ {date_i})."
                elif commit_i == "NO_CONTENT_COMMIT" and commit_m != "NO_CONTENT_COMMIT":
                     status_msg = f"Update individual from main (Individual was empty. Main commit: {commit_m} @ {date_m})."
                elif is_main_ancestor_of_ind:
                    status_msg = f"Update main from individual (Individual commit: {commit_i} @ {date_i} is newer than Main: {commit_m} @ {date_m})."
                elif is_ind_ancestor_of_main:
                    status_msg = f"Update individual from main (Main commit: {commit_m} @ {date_m} is newer than Individual: {commit_i} @ {date_i})."
                else:
                    if is_main_ancestor_of_ind is None:
                        status_msg = "Conflict (Error checking commit ancestry)."
                    else:
                        status_msg = (f"Conflict (Divergent history. "
                                      f"Main: {commit_m} @ {date_m}, "
                                      f"Individual: {commit_i} @ {date_i}). Needs SYNC STATUS marker.")
        report.append(f"Task {task_id_from_file}: {status_msg}")

    for task_id, data in main_tasks_data.items():
        if task_id not in processed_individual_task_ids:
            report.append(f"Task {task_id}: Exists in {PLANNING_TASKS_FILE}, but no corresponding individual file found in {INDIVIDUAL_TASKS_DIR}.")

    print("\n--- Task Sync Status Report (Dry Run) ---")
    if not report:
        print("No tasks found to analyze.")
    else:
        for line in report:
            print(line)
    print("--- End of Report ---")
    print("\nNo files have been changed. This is a dry run.")

if __name__ == "__main__":
    analyze_tasks()
