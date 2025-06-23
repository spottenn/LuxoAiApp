import os
import re
import subprocess
from datetime import datetime

# Constants
PLANNING_TASKS_FILE = "Resources/planning/PLANNING_TASKS.md"
INDIVIDUAL_TASKS_DIR = "Resources/planning/tasks/"
# STATUS_FILE = "Resources/planning/task-status.md" # Not directly used for sync logic

# Regexes
TASK_HEADING_PATTERN = re.compile(r"^#\s*Epic\s*\d+\s*--\s*Task\s*([\d\.]+[a-zA-Z]?):(.*)", re.MULTILINE)
# Regex to capture the entire task heading line, to preserve it when updating individual files
FULL_TASK_HEADING_PATTERN = re.compile(r"^(#\s*Epic\s*\d+\s*--\s*Task\s*[\d\.]+[a-zA-Z]?):(.*)", re.MULTILINE)
FILENAME_PATTERN = re.compile(r"epic_(\d+)_task_(\d+_\d+[a-zA-Z]?)\.md")
STATUS_LINE_PATTERN = re.compile(r"^(Status:.*)\n?", re.IGNORECASE | re.MULTILINE) # Ensure it captures the line
SYNC_STATUS_LINE_PATTERN = re.compile(r"^(\*\*SYNC STATUS:\*\*\s*.*\S)\s*\n?", re.IGNORECASE | re.MULTILINE) # Ensure it captures the line and trailing spaces


# --- File Modification Functions ---

def _remove_sync_status_lines(text_content):
    """Removes all occurrences of SYNC STATUS lines from the text."""
    return SYNC_STATUS_LINE_PATTERN.sub("", text_content)

def _get_status_line(file_content):
    """Extracts the 'Status: ...' line from file content, if present."""
    match = STATUS_LINE_PATTERN.search(file_content)
    if match:
        return match.group(1) # The whole status line
    return None

def update_task_in_main_file(task_id, individual_task_content_with_heading, dry_run=True):
    """
    Updates a specific task block in PLANNING_TASKS.md with new content.
    `individual_task_content_with_heading` is the full definition from the individual file,
    already including its own heading.
    """
    if dry_run:
        print(f"[Dry Run] Would update task {task_id} in {PLANNING_TASKS_FILE} with new content.")
        return

    try:
        with open(PLANNING_TASKS_FILE, 'r', encoding='utf-8') as f:
            main_content = f.read()
    except Exception as e:
        print(f"Error reading {PLANNING_TASKS_FILE} for update: {e}")
        return

    new_main_content_parts = []
    last_pos = 0
    task_found_and_updated = False

    for match in TASK_HEADING_PATTERN.finditer(main_content):
        current_task_id = match.group(1)
        block_start_char_index = match.start()

        # Content before the current task block
        new_main_content_parts.append(main_content[last_pos:block_start_char_index])

        # Determine the end of this task's definition (before its separator)
        # and the end of its full block (including its separator)
        next_heading_match = TASK_HEADING_PATTERN.search(main_content, pos=match.end())
        limit_for_separator_search = next_heading_match.start() if next_heading_match else len(main_content)

        current_task_block_in_main = main_content[block_start_char_index : limit_for_separator_search]

        task_definition_in_block = ""
        separator_string = "\n---\n" # Default separator to add if task is updated

        # Find separator for current task, if any
        # Regex for "\n\s*---\s*(\n|$)"
        separator_match = re.search(r"(\n\s*---\s*(?:\n|$))", current_task_block_in_main)

        if separator_match:
            task_definition_in_block = current_task_block_in_main[:separator_match.start()]
            # Preserve original separator if task is not the one being updated, or if it's the last task
            # For updated task, we'll add a standard one unless it's the last overall.
            original_separator_for_this_task = separator_match.group(1)
        else:
            task_definition_in_block = current_task_block_in_main.rstrip()
            original_separator_for_this_task = "" # No separator found for this task

        if current_task_id == task_id:
            # This is the task to update.
            # Remove any existing SYNC STATUS from the individual content before inserting.
            clean_individual_content = _remove_sync_status_lines(individual_task_content_with_heading)
            new_main_content_parts.append(clean_individual_content.strip())

            # Add separator unless this is the last task in the file (no next_heading_match and no original separator for the whole section)
            if next_heading_match or (separator_match and limit_for_separator_search != len(main_content)): # Add separator if it's not the very last element
                 new_main_content_parts.append(separator_string)
            elif original_separator_for_this_task: # If it was the last task but had a separator
                 new_main_content_parts.append(original_separator_for_this_task)

            task_found_and_updated = True
        else:
            # Not the task to update, append its original definition and separator
            new_main_content_parts.append(task_definition_in_block)
            new_main_content_parts.append(original_separator_for_this_task)

        last_pos = block_start_char_index + len(task_definition_in_block) + len(original_separator_for_this_task)


    new_main_content_parts.append(main_content[last_pos:]) # Append content after the last task

    if task_found_and_updated:
        try:
            with open(PLANNING_TASKS_FILE, 'w', encoding='utf-8') as f:
                f.write("".join(new_main_content_parts))
            print(f"Successfully updated task {task_id} in {PLANNING_TASKS_FILE}.")
        except Exception as e:
            print(f"Error writing updated {PLANNING_TASKS_FILE}: {e}")
    elif not task_found_and_updated and current_task_id == task_id : # special case: last task updated
         pass # Handled if last_pos was updated correctly
    elif not task_found_and_updated:
        print(f"Error: Task {task_id} not found in {PLANNING_TASKS_FILE} during update attempt.")


def update_individual_task_file(filepath, main_task_content_definition, dry_run=True):
    """
    Updates an individual task file with content from the main planning file.
    `main_task_content_definition` is the task's definition (heading + body) from PLANNING_TASKS.md.
    The Status: line from the original individual file should be preserved.
    """
    if dry_run:
        print(f"[Dry Run] Would update individual task file {filepath}.")
        return

    original_status_line = ""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
        status_match = STATUS_LINE_PATTERN.search(original_content)
        if status_match:
            original_status_line = status_match.group(1) + "\n\n" # Status line + blank line
    except Exception as e:
        print(f"Warning: Could not read original status from {filepath}: {e}. Will proceed without it.")

    # Remove any existing SYNC STATUS from the main content before writing to individual file.
    clean_main_task_content = _remove_sync_status_lines(main_task_content_definition)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(original_status_line) # Write preserved status line (or empty if not found)
            f.write(clean_main_task_content.strip() + "\n") # Write new content
        print(f"Successfully updated individual task file {filepath}.")
    except Exception as e:
        print(f"Error writing to individual task file {filepath}: {e}")


def add_sync_conflict_marker(filepath, task_id_or_filename, conflict_detail_msg, is_main_file, dry_run=True):
    """
    Adds or updates a SYNC STATUS marker in the specified file.
    `task_id_or_filename` is the task_id for main file, or filename for individual file.
    `conflict_detail_msg` is the specific message like "Main: hash1, Individual: hash2".
    """
    sync_marker_text = f"**SYNC STATUS:** Conflict detected - {conflict_detail_msg}"

    if dry_run:
        print(f"[Dry Run] Would add/update sync conflict marker in {filepath} for {task_id_or_filename}: '{sync_marker_text}'")
        return

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {filepath} to add sync marker: {e}")
        return

    # Remove any existing sync status line(s) first
    content_no_old_marker = _remove_sync_status_lines(content)

    # Reconstruct content with the new marker
    # For main file, marker goes after task heading.
    # For individual file, marker goes after Status: line (and its blank line) AND after task heading.

    new_content = ""
    if is_main_file:
        # Find the specific task heading for task_id_or_filename (which is task_id)
        # This requires finding the heading and inserting after it.
        # Simplified: Assume it's for a task, re-parse to insert.
        # This is complex; for now, let's make a placeholder for precise insertion.
        # A better way would be to pass the full task heading line.

        # A more robust way for main file:
        # Find the task heading. Insert marker on the next line.
        # This means splitting content at the end of the heading line.

        # For each task heading:
        found = False
        temp_output = []
        last_slice_end = 0
        for match in TASK_HEADING_PATTERN.finditer(content_no_old_marker):
            current_task_id = match.group(1)
            heading_line = match.group(0) # Full heading line

            temp_output.append(content_no_old_marker[last_slice_end : match.start()]) # Content before heading

            if current_task_id == task_id_or_filename:
                temp_output.append(heading_line + "\n" + sync_marker_text + "\n")
                found = True
            else:
                temp_output.append(heading_line) # Keep original heading

            last_slice_end = match.end()
        temp_output.append(content_no_old_marker[last_slice_end:])

        if found:
            new_content = "".join(temp_output)
        else:
            print(f"Error: Task heading for {task_id_or_filename} not found in {filepath} to add sync marker.")
            return # Don't write if task not found

    else: # Individual file
        # Marker goes after Status: line (if any) and its blank line, then after task heading.
        status_line_obj = STATUS_LINE_PATTERN.search(content_no_old_marker)

        # Find the first task heading in the individual file
        # (should typically be only one, but use finditer for safety)
        task_heading_match = FULL_TASK_HEADING_PATTERN.search(content_no_old_marker)

        if not task_heading_match:
            print(f"Error: No task heading found in individual file {filepath} to add sync marker.")
            # Fallback: add at top after status, if any
            if status_line_obj:
                new_content = status_line_obj.group(0) + "\n" + sync_marker_text + "\n\n" + content_no_old_marker[status_line_obj.end():]
            else:
                new_content = sync_marker_text + "\n\n" + content_no_old_marker
        else:
            # Insert after heading
            heading_end_pos = task_heading_match.end()
            # Check if there's a status line before the heading
            prefix = content_no_old_marker[:heading_end_pos]
            suffix = content_no_old_marker[heading_end_pos:]
            new_content = prefix + "\n" + sync_marker_text + suffix


    if new_content: # Ensure new_content was formed
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Successfully added/updated sync marker in {filepath} for {task_id_or_filename}.")
        except Exception as e:
            print(f"Error writing sync marker to {filepath}: {e}")
    else:
        # This case might occur if the task_id was not found in main file.
        # The error message for that is printed above.
        pass


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

    if start_line > end_line : # No lines in range or invalid range
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


def analyze_tasks(dry_run=True): # Added dry_run parameter
    if not GIT_ROOT:
        print("Cannot proceed without git.")
        return

    if not dry_run and check_for_uncommitted_changes():
        print("Error: There are uncommitted changes in your repository.")
        print("Please commit or stash them before running the sync script with `dry_run=False`.")
        print("Git history is used for comparison, and uncommitted changes can lead to incorrect sync operations.")
        return
    elif dry_run and check_for_uncommitted_changes():
        print("Warning: There are uncommitted changes. For accurate results, commit or stash them.")


    # 1. Parse PLANNING_TASKS.md
    try:
        with open(PLANNING_TASKS_FILE, 'r', encoding='utf-8') as f:
            main_file_full_content = f.read()
    except FileNotFoundError:
        print(f"Error: Main planning file not found at '{PLANNING_TASKS_FILE}'")
        return
    
    main_tasks_data = {} # Keyed by task_id (e.g., "1.1")
    
    # Store full task definitions from main file (including heading) for potential updates to individual files
    main_task_definitions_for_ind_update = {}

    for match in TASK_HEADING_PATTERN.finditer(main_file_full_content):
        task_id = match.group(1)
        # task_title_rest = match.group(2) # Rest of the title line
        
        task_block_start_char_index = match.start()
        
        next_heading_match = TASK_HEADING_PATTERN.search(main_file_full_content, pos=match.end())
        limit_for_block_search = next_heading_match.start() if next_heading_match else len(main_file_full_content)
        
        current_task_block_in_main_file = main_file_full_content[task_block_start_char_index : limit_for_block_search]
        
        separator_in_block_match = re.search(r"\n\s*---\s*(\n|$)", current_task_block_in_main_file)
        if separator_in_block_match:
            task_definition_in_block = current_task_block_in_main_file[:separator_in_block_match.start()]
        else:
            task_definition_in_block = current_task_block_in_main_file.rstrip()

        main_task_definitions_for_ind_update[task_id] = task_definition_in_block # Store for later use

        block_start_line_0idx = main_file_full_content[:task_block_start_char_index].count('\n')

        # Get content for comparison (stripping sync status)
        content_main_for_compare, start_line_main, end_line_main = get_line_numbers_and_content(
            task_definition_in_block, 
            ignore_patterns=[SYNC_STATUS_LINE_PATTERN],
            content_start_offset=block_start_line_0idx
        )
        
        commit_main, date_main = None, None
        if start_line_main != -1 :
             commit_main, date_main = get_last_commit_for_lines(PLANNING_TASKS_FILE, start_line_main, end_line_main)

        main_tasks_data[task_id] = {
            "raw_content_for_compare": content_main_for_compare, # Content used for comparison
            "commit": commit_main,
            "date": date_main,
            "start_line": start_line_main,
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
        if not task_id_from_file: continue

        processed_individual_task_ids.add(task_id_from_file)
        filepath = os.path.join(INDIVIDUAL_TASKS_DIR, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                individual_file_full_content = f.read()
        except Exception as e:
            report.append(f"Task {task_id_from_file} (File: {filename}): Error reading file: {e}")
            continue

        # Get the full content of the individual file (including its heading) for potential update to main file
        # but strip status and sync status for comparison content.
        content_individual_for_compare, start_line_individual, end_line_individual = get_line_numbers_and_content(
            individual_file_full_content,
            ignore_patterns=[STATUS_LINE_PATTERN, SYNC_STATUS_LINE_PATTERN]
        )
        
        commit_individual, date_individual = None, None
        if start_line_individual != -1:
            commit_individual, date_individual = get_last_commit_for_lines(filepath, start_line_individual, end_line_individual)

        main_data = main_tasks_data.get(task_id_from_file)

        if not main_data:
            report.append(f"Task {task_id_from_file} (File: {filename}): Exists in individual dir, but not in {PLANNING_TASKS_FILE}.")
            continue
        
        norm_content_main = main_data["raw_content_for_compare"].strip()
        norm_content_individual = content_individual_for_compare.strip() # Already stripped by get_line_numbers_and_content

        action_taken = False
        if norm_content_main == norm_content_individual:
            status_msg = "In Sync."
            # If in sync, ensure no old conflict markers exist
            if not dry_run:
                # This requires reading the file and removing markers if present.
                # For simplicity in this step, we'll assume markers are handled by explicit conflict marking only.
                # TODO: Add cleanup of old markers if files become "In Sync".
                pass
        else:
            commit_m = main_data["commit"]
            date_m = main_data["date"]
            commit_i = commit_individual
            date_i = date_individual

            decision = "" # To store what action to take

            if not commit_m or not commit_i:
                decision = "conflict_history_error"
            elif commit_m == commit_i and commit_m != "NO_CONTENT_COMMIT":
                decision = "conflict_same_commit_diff_content"
            else:
                is_main_ancestor_of_ind = is_ancestor(commit_m, commit_i)
                is_ind_ancestor_of_main = is_ancestor(commit_i, commit_m)

                if commit_m == "NO_CONTENT_COMMIT" and commit_i != "NO_CONTENT_COMMIT":
                    decision = "update_main"
                elif commit_i == "NO_CONTENT_COMMIT" and commit_m != "NO_CONTENT_COMMIT":
                    decision = "update_individual"
                elif is_main_ancestor_of_ind:
                    decision = "update_main"
                elif is_ind_ancestor_of_main:
                    decision = "update_individual"
                else: # Divergent or error in ancestry check
                    if is_main_ancestor_of_ind is None: # Error
                        decision = "conflict_ancestry_error"
                    else: # Divergent
                        decision = "conflict_divergent"

            # Perform actions based on decision
            if decision == "update_main":
                status_msg = f"Update main from individual (Ind: {commit_i} @ {date_i} vs Main: {commit_m} @ {date_m})."
                # The content to write to main is the *full* individual file content,
                # but with its 'Status:' line removed, and any sync status line removed.
                content_from_individual_for_main = SYNC_STATUS_LINE_PATTERN.sub("", STATUS_LINE_PATTERN.sub("", individual_file_full_content)).strip()
                update_task_in_main_file(task_id_from_file, content_from_individual_for_main, dry_run)
                action_taken = True
            elif decision == "update_individual":
                status_msg = f"Update individual from main (Main: {commit_m} @ {date_m} vs Ind: {commit_i} @ {date_i})."
                # The content to write to individual is the task definition from main.
                main_task_def = main_task_definitions_for_ind_update.get(task_id_from_file, "")
                update_individual_task_file(filepath, main_task_def, dry_run)
                action_taken = True
            elif decision.startswith("conflict"):
                conflict_detail = ""
                if decision == "conflict_history_error":
                    status_msg = f"Conflict (Error fetching commit history. Main: {commit_m}, Ind: {commit_i})."
                    conflict_detail = f"Error fetching history. Main: {commit_m}, Ind: {commit_i}"
                elif decision == "conflict_same_commit_diff_content":
                     status_msg = f"Conflict (Same commit {commit_m}, but content differs). Working tree changes or merge issue?"
                     conflict_detail = f"Content differs on same commit {commit_m}. Possible working tree changes."
                elif decision == "conflict_ancestry_error":
                    status_msg = "Conflict (Error checking commit ancestry)."
                    conflict_detail = "Error checking commit ancestry."
                elif decision == "conflict_divergent":
                    status_msg = (f"Conflict (Divergent history. Main: {commit_m} @ {date_m}, Individual: {commit_i} @ {date_i}).")
                    conflict_detail = f"Divergent. Main: {commit_m} ({date_m}), Individual: {commit_i} ({date_i})"

                add_sync_conflict_marker(PLANNING_TASKS_FILE, task_id_from_file, conflict_detail, is_main_file=True, dry_run=dry_run)
                add_sync_conflict_marker(filepath, filename, conflict_detail, is_main_file=False, dry_run=dry_run)
                action_taken = True
            else: # Should not happen
                status_msg = "Error: Unknown decision state."

        report_msg_prefix = "[Dry Run] " if dry_run and action_taken else ""
        report.append(f"Task {task_id_from_file}: {report_msg_prefix}{status_msg}")


    # Check for tasks in main_tasks_data not found in individual files
    for task_id, data in main_tasks_data.items():
        if task_id not in processed_individual_task_ids:
            report.append(f"Task {task_id}: Exists in {PLANNING_TASKS_FILE}, but no corresponding individual file found in {INDIVIDUAL_TASKS_DIR}. (No action taken by sync script)")

    # Print report
    run_type = "Dry Run" if dry_run else "Live Run"
    print(f"\n--- Task Sync Status Report ({run_type}) ---")
    if not report:
        print("No tasks found to analyze or sync.")
    else:
        for line in report:
            print(line)
    print("--- End of Report ---")
    if dry_run:
        print("\nNo files have been changed. This was a dry run.")
    else:
        print("\nSync process complete. Files may have been changed.")


if __name__ == "__main__":
    # Example: run with dry_run=False by providing an argument
    import sys
    # Basic argument parsing: if any argument is given, it could mean non-dry run.
    # A more robust CLI arg parsing (e.g. argparse) would be better for a real tool.
    # For now, let's default to dry_run=True unless specifically told otherwise.
    # We can make it False for testing.

    # Default to dry run, but can be overridden by test suite or direct call.
    # For command line execution:
    # `python sync_task_files.py` -> dry_run = True
    # `python sync_task_files.py live` -> dry_run = False (example)

    perform_dry_run = True
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'live':
        print("Executing LIVE run as per command line argument.")
        perform_dry_run = False

    analyze_tasks(dry_run=perform_dry_run)
