import os
import re

# Constants are relative to the repository root,
# as the script is likely executed from there by tools/users.
PLANNING_TASKS_FILE = "Resources/planning/PLANNING_TASKS.md"
OUTPUT_DIR = "Resources/planning/tasks/"
STATUS_FILE = "Resources/planning/task-status.md"


def load_task_statuses(status_file_path):
    """
    Loads task statuses from the given status file.
    Returns a dictionary mapping filenames to their statuses.
    Example: {"epic_1_task_1_1.md": "Not Started"}
    """
    statuses = {}
    try:
        with open(status_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith("- ") and ": " in line:
                    parts = line[2:].split(": ", 1)
                    if len(parts) == 2:
                        filename = parts[0].strip()
                        status = parts[1].strip()
                        statuses[filename] = status
    except FileNotFoundError:
        print(f"Warning: Status file not found at '{status_file_path}'. No statuses will be loaded.")
    except Exception as e:
        print(f"Error reading status file {status_file_path}: {e}")
    return statuses


def parse_and_save_tasks():
    try:
        # Ensure the script can find the PLANNING_TASKS_FILE relative to the repo root
        # This assumes the current working directory is the repo root when the script is run.
        with open(PLANNING_TASKS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found at '{PLANNING_TASKS_FILE}'. Make sure the script is run from the repository root or adjust paths.")
        return
    except Exception as e:
        print(f"Error reading file {PLANNING_TASKS_FILE}: {e}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    task_statuses = load_task_statuses(STATUS_FILE)

    # Regex to find task headings (e.g., "# Epic 1 -- Task 1.1: Title" or "# Epic 1 -- Task 1.1a: Title")
    task_pattern = r"^# Epic \d+ -- Task (\d+\.\d+[a-zA-Z]?):.*"

    tasks_data = []
    for match in re.finditer(task_pattern, content, flags=re.MULTILINE):
        tasks_data.append({
            "id": match.group(1),
            "start_pos": match.start(),
            "heading": match.group(0)  # The full heading line
        })

    if not tasks_data:
        print("No tasks found in the input file.")
        return

    for i, task_data in enumerate(tasks_data):
        task_id = task_data["id"]
        start_pos = task_data["start_pos"]

        # Determine the end position of the current task's content
        # It's the start of the next task, or EOF if this is the last task
        end_pos = tasks_data[i+1]["start_pos"] if i + 1 < len(tasks_data) else len(content)

        # Determine the end position of the current task's content block
        # This block extends from the current task's heading to the start of the next task's heading, or EOF.
        next_task_start_pos = tasks_data[i+1]["start_pos"] if i + 1 < len(tasks_data) else len(content)
        task_block_content = content[start_pos : next_task_start_pos]

        # The actual content for the task file is everything within this block *before* its own "---" separator.
        # The "---" separator is expected to be preceded by a newline.
        # We find the last occurrence of "\n---" in the block. The content before it is the task's content.
        # This handles cases where the last task's block might include extra data after its separator.

        # Find the last occurrence of a line starting with "---" (possibly with leading whitespace on the line, after the newline)
        # within the task_block_content.
        last_separator_match = None
        # Regex: newline, optional whitespace, then ---
        for match_iter in re.finditer(r"\n\s*---", task_block_content):
            last_separator_match = match_iter

        idx = -1 # Default if no separator found (for debug)
        if last_separator_match:
            idx = last_separator_match.start() # This is the start of "\n\s*---"
            current_task_content = task_block_content[:idx]
        else:
            # No separator line found
            current_task_content = task_block_content.rstrip()

        # Removed debug prints for task 10.2 that were here.


        # Construct filename (e.g., epic_1_task_1_1.md)
        epic_num = task_id.split('.')[0]
        task_filename_id = task_id.replace('.', '_')
        filename = os.path.join(OUTPUT_DIR, f"epic_{epic_num}_task_{task_filename_id}.md")

        try:
            # Write the (potentially modified) task content to its file
            # .strip() removes leading/trailing whitespace from the slice, then add one newline.
            with open(filename, 'w', encoding='utf-8') as f:
                # Get base filename for status lookup, e.g., "epic_1_task_1_1.md"
                base_filename = os.path.basename(filename)
                status = task_statuses.get(base_filename, "Not Started") # Default if not found

                f.write(f"Status: {status}\n\n")
                f.write(current_task_content.strip() + "\n")
            print(f"Successfully wrote task {task_id} to {filename} with status '{status}'")
        except IOError as e:
            print(f"Error writing file {filename}: {e}")

if __name__ == "__main__":
    parse_and_save_tasks()
