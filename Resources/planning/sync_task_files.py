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
        # Ensure commands run from the git root if filepath is relative
        # However, git commands usually handle paths relative to CWD if CWD is in repo.
        # For safety, make filepaths absolute or relative to GIT_ROOT for -L commands.
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
    
    # Ensure filepath is relative to git root for the -L option
    abs_filepath = os.path.abspath(filepath)
    relative_filepath = os.path.relpath(abs_filepath, GIT_ROOT)

    if start_line == -1 or start_line > end_line : # No lines in range, invalid range, or content was empty
        # This can happen if a task content is empty after stripping metadata
        # print(f"Debug: Invalid line range for {relative_filepath}: L{start_line}-L{end_line}. Skipping git log.")
        return "NO_CONTENT_COMMIT", "1970-01-01T00:00:00Z" # Special values for empty content

    # Using format %H for commit hash, %aI for author date (ISO 8601 strict)
    # git log -1 --pretty="format:%H %aI" -L <start>,<end>:<file>
    cmd = [
        'git', 'log', '-1', 
        '--pretty=format:%H %aI', # Get hash and author date
        f'-L{start_line},{end_line}:{relative_filepath}'
    ]
    output = _run_git_command(cmd)
    if output:
        parts = output.split(' ', 1)
        if len(parts) == 2:
            commit_hash, commit_date_str = parts
            # Convert commit_date_str to datetime object then to consistent ISO format if needed
            # For now, assuming git outputs a usable ISO string.
            return commit_hash, commit_date_str 
    return None, None


def is_ancestor(commit1_hash, commit2_hash):
    """Checks if commit1 is an ancestor of commit2. Returns True, False, or None on error."""
    if commit1_hash == "NO_CONTENT_COMMIT" or commit2_hash == "NO_CONTENT_COMMIT":
        return False # Treat no-content as not an ancestor of actual content for simplicity
    if commit1_hash == commit2_hash: # A commit is an ancestor of itself
        return True 
        
    # `git merge-base --is-ancestor <commit1> <commit2>`
    # exits with 0 if true, 1 if false.
    cmd = ['git', 'merge-base', '--is-ancestor', commit1_hash, commit2_hash]
    try:
        subprocess.run(cmd, check=True, capture_output=True, cwd=GIT_ROOT)
        return True  # Exit code 0
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            return False # Exit code 1
        print(f"Error checking ancestry with git merge-base: {e.stderr.strip()}")
        return None # Other error
    except FileNotFoundError:
        print("Error: git command not found.")
        return None

def check_for_uncommitted_changes():
    """Checks if there are uncommitted changes in the Git working directory or staging area."""
    if not GIT_ROOT: return True # Assume changes if git is not working
    
    # Check for unstaged changes
    status_output_unstaged = _run_git_command(['git', 'status', '--porcelain'])
    if status_output_unstaged is None: return True # Error running git

    # Check for staged changes
    status_output_staged = _run_git_command(['git', 'diff', '--cached', '--quiet'])
    # For `git diff --cached --quiet`, exit code 0 means no staged changes, 1 means there are staged changes.
    # So, if _run_git_command returns something (meaning check=True didn't fail on non-zero),
    # it implies an error or unexpected success.
    # Let's refine this:
    try:
        subprocess.run(['git', 'diff', '--quiet'], check=True, cwd=GIT_ROOT) # Check working directory
        subprocess.run(['git', 'diff', '--cached', '--quiet'], check=True, cwd=GIT_ROOT) # Check staging area
        return False # No changes
    except subprocess.CalledProcessError:
        return True # Indicates changes
    except FileNotFoundError:
        return True # Git not found

# --- Content Parsing and Analysis ---

def get_task_id_from_filename(filename_basename):
    """ e.g. epic_1_task_1_1.md -> 1.1 """
    match = FILENAME_PATTERN.match(filename_basename)
    if match:
        return match.group(2).replace('_', '.')
    return None

def get_line_numbers_and_content(full_text_content, ignore_patterns=None, content_start_offset=0):
    """
    Calculates start and end line numbers of content after stripping ignored lines.
    `content_start_offset` is the 0-indexed line number where the relevant content block begins in `full_text_content`.
    Returns (content_str, start_line_num_1_indexed, end_line_num_1_indexed).
    Line numbers are relative to the start of `full_text_content`.
    """
    lines = full_text_content.splitlines(keepends=True)
    
    relevant_lines_info = [] # list of (line_text, original_line_index_0_based)
    
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
        return "", -1, -1 # No content

    # Content string is concatenation of relevant lines
    content_str = "".join([info[0] for info in relevant_lines_info])
    
    # Line numbers are 1-indexed from the original file's perspective
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
        # For Part 1, we can choose to proceed with this warning or exit.
        # Let's proceed for now, but this is important for accuracy.
        # return 

    # 1. Parse PLANNING_TASKS.md
    try:
        with open(PLANNING_TASKS_FILE, 'r', encoding='utf-8') as f:
            main_file_full_content = f.read()
    except FileNotFoundError:
        print(f"Error: Main planning file not found at '{PLANNING_TASKS_FILE}'")
        return
    
    main_tasks_data = {} # Keyed by task_id (e.g., "1.1")
    
    # Iterate through task headings in the main file
    main_file_lines = main_file_full_content.splitlines(keepends=True)
    
    for match in TASK_HEADING_PATTERN.finditer(main_file_full_content):
        task_id = match.group(1)
        task_title_rest = match.group(2) # Rest of the title line
        
        task_block_start_char_index = match.start()
        
        # Determine end of this task's block (before next task or specific footer)
        next_heading_match = TASK_HEADING_PATTERN.search(main_file_full_content, pos=match.end())
        limit_for_block_search = next_heading_match.start() if next_heading_match else len(main_file_full_content)
        
        # The task block in main file (from its heading to just before its "---" or next task)
        current_task_block_in_main_file = main_file_full_content[task_block_start_char_index : limit_for_block_search]
        
        # The definition part (heading + body, no trailing "---")
        # The separator "---" is outside the definition.
        separator_in_block_match = re.search(r"\n\s*---\s*(\n|$)", current_task_block_in_main_file)
        if separator_in_block_match:
            task_definition_in_block = current_task_block_in_main_file[:separator_in_block_match.start()]
        else:
            task_definition_in_block = current_task_block_in_main_file.rstrip() # Remove trailing newlines if no separator

        # Calculate line numbers for this definition block within the main file
        # First, find the 0-indexed start line of the task_definition_in_block within main_file_full_content
        block_start_line_0idx = main_file_full_content[:task_block_start_char_index].count('\n')

        content_main, start_line_main, end_line_main = get_line_numbers_and_content(
            task_definition_in_block, 
            ignore_patterns=[SYNC_STATUS_LINE_PATTERN], # Ignore sync status line within the block
            content_start_offset=block_start_line_0idx
        )
        
        commit_main, date_main = None, None
        if start_line_main != -1 : # If there was actual content
             commit_main, date_main = get_last_commit_for_lines(PLANNING_TASKS_FILE, start_line_main, end_line_main)

        main_tasks_data[task_id] = {
            "raw_content": content_main,
            "commit": commit_main,
            "date": date_main,
            "start_line": start_line_main, # For debugging or future use
            "end_line": end_line_main
        }

    # 2. Process individual task files
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
        if not task_id_from_file: continue # Should not happen due to pattern match above

        processed_individual_task_ids.add(task_id_from_file)
        filepath = os.path.join(INDIVIDUAL_TASKS_DIR, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                individual_file_full_content = f.read()
        except Exception as e:
            print(f"Error reading individual task file {filename}: {e}")
            report.append(f"Task {task_id_from_file} (File: {filename}): Error reading file.")
            continue

        # Get content and line numbers for individual file, ignoring Status and Sync Status lines
        content_individual, start_line_individual, end_line_individual = get_line_numbers_and_content(
            individual_file_full_content,
            ignore_patterns=[STATUS_LINE_PATTERN, SYNC_STATUS_LINE_PATTERN]
        )
        
        commit_individual, date_individual = None, None
        if start_line_individual != -1: # If actual content exists
            commit_individual, date_individual = get_last_commit_for_lines(filepath, start_line_individual, end_line_individual)

        # Compare with main task data
        main_data = main_tasks_data.get(task_id_from_file)

        if not main_data:
            report.append(f"Task {task_id_from_file} (File: {filename}): Exists in individual tasks dir, but not found in {PLANNING_TASKS_FILE}.")
            continue
        
        # Normalize content for comparison (strip whitespace)
        norm_content_main = main_data["raw_content"].strip()
        norm_content_individual = content_individual.strip() # content_individual is already stripped by get_line_numbers_and_content

        if norm_content_main == norm_content_individual:
            status_msg = "In Sync."
        else:
            # Content differs, analyze commits
            commit_m = main_data["commit"]
            date_m = main_data["date"]
            commit_i = commit_individual
            date_i = date_individual

            if not commit_m or not commit_i:
                status_msg = f"Conflict (Error fetching commit history. Main: {commit_m}, Ind: {commit_i}). Investigate."
            elif commit_m == commit_i and commit_m != "NO_CONTENT_COMMIT": # NO_CONTENT_COMMIT means empty content, so commits might be different
                status_msg = f"Conflict (Same commit {commit_m}, but content differs). Working tree changes or merge issue?"
            else:
                # Dates are strings like '2024-07-15T10:00:00-07:00' or '1970-01-01T00:00:00Z'
                # Convert to datetime for comparison if needed, but ancestry is primary
                is_main_ancestor_of_ind = is_ancestor(commit_m, commit_i)
                is_ind_ancestor_of_main = is_ancestor(commit_i, commit_m)

                if commit_m == "NO_CONTENT_COMMIT" and commit_i != "NO_CONTENT_COMMIT":
                    status_msg = f"Update main from individual (Main was empty. Individual commit: {commit_i} @ {date_i})."
                elif commit_i == "NO_CONTENT_COMMIT" and commit_m != "NO_CONTENT_COMMIT":
                     status_msg = f"Update individual from main (Individual was empty. Main commit: {commit_m} @ {date_m})."
                elif is_main_ancestor_of_ind: # main is older or same, individual is tip
                    status_msg = f"Update main from individual (Individual commit: {commit_i} @ {date_i} is newer than Main: {commit_m} @ {date_m})."
                elif is_ind_ancestor_of_main: # individual is older or same, main is tip
                    status_msg = f"Update individual from main (Main commit: {commit_m} @ {date_m} is newer than Individual: {commit_i} @ {date_i})."
                else: # Divergent or error in ancestry check
                    if is_main_ancestor_of_ind is None: # Error
                        status_msg = "Conflict (Error checking commit ancestry)."
                    else: # Divergent
                        status_msg = (f"Conflict (Divergent history. "
                                      f"Main: {commit_m} @ {date_m}, "
                                      f"Individual: {commit_i} @ {date_i}). Needs SYNC STATUS marker.")
        report.append(f"Task {task_id_from_file}: {status_msg}")

    # Check for tasks in main_tasks_data not found in individual files
    for task_id, data in main_tasks_data.items():
        if task_id not in processed_individual_task_ids:
            report.append(f"Task {task_id}: Exists in {PLANNING_TASKS_FILE}, but no corresponding individual file found in {INDIVIDUAL_TASKS_DIR}.")

    # Print report
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
