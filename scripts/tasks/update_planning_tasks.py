import os
import re

# Constants are relative to the repository root
PLANNING_TASKS_FILE = "Resources/planning/PLANNING_TASKS.md"
INDIVIDUAL_TASKS_DIR = "Resources/planning/tasks/"
TASK_STATUS_FILE = "Resources/planning/task-status.md" # For consistency, though not directly used for updating main file

# Regex to identify a task heading and extract its core ID (e.g., "1.1", "1.1b")
# Example: # Epic 1 -- Task 1.1: Create Script... -> "1.1"
# Example: # Epic 1 -- Task 1.1b: Verify and Document... -> "1.1b"
TASK_HEADING_PATTERN = re.compile(r"^#\s*Epic\s*\d+\s*--\s*Task\s*([\d\.]+[a-zA-Z]?):.*", re.MULTILINE)

# Regex to extract Epic number and Task ID from filename like epic_X_task_X_Y.md
FILENAME_PATTERN = re.compile(r"epic_(\d+)_task_(\d+_\d+[a-zA-Z]?)\.md")

def get_task_identifier_from_filename(filename):
    """
    Extracts a simplified task identifier (e.g., "1_1", "1_1b") from the filename.
    """
    match = FILENAME_PATTERN.match(os.path.basename(filename))
    if match:
        return f"{match.group(1)}_{match.group(2)}" # e.g. 1_1_1, 2_2_1b
    return None

def get_task_id_from_heading_match(match_obj):
    """
    Returns the task ID (e.g., "1.1", "1.1b") from a regex match object.
    """
    if match_obj:
        return match_obj.group(1)
    return None

def load_individual_tasks(tasks_dir):
    """
    Loads all tasks from individual .md files in the specified directory.
    Returns a dictionary where keys are task identifiers (e.g., "1.1", "1.1b" derived from filename pattern for now)
    and values are the content of the task files (excluding the 'Status:' line).
    """
    individual_tasks = {}
    if not os.path.isdir(tasks_dir):
        print(f"Error: Individual tasks directory not found at '{tasks_dir}'")
        return individual_tasks

    for filename in os.listdir(tasks_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(tasks_dir, filename)
            
            # Try to extract task ID from filename first as a key
            # This needs to be robust. Format: epic_1_task_1_1.md -> "1.1"
            fn_match = FILENAME_PATTERN.match(filename)
            if not fn_match:
                print(f"Warning: Could not parse task ID from filename: {filename}")
                continue
            
            epic_num_fn = fn_match.group(1)
            task_num_fn_part = fn_match.group(2).replace('_', '.') # e.g. 1_1 -> 1.1, 1_1b -> 1.1b
            task_key_from_filename = f"{task_num_fn_part}" # Simplifies to "1.1", "1.1b"

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                content_lines = []
                status_line_found = False
                for line in lines:
                    if line.lower().startswith("status:"):
                        status_line_found = True
                        continue
                    if status_line_found and line.strip() == "": # Skip blank line after status
                        status_line_found = False # only skip one blank line
                        continue
                    content_lines.append(line)
                
                task_content = "".join(content_lines).strip()
                if task_content: # Ensure there's actual content
                    individual_tasks[task_key_from_filename] = task_content
                else:
                    print(f"Warning: No content found (after status line) for task in {filename}")

            except Exception as e:
                print(f"Error reading or parsing individual task file {filename}: {e}")
    return individual_tasks

def update_main_planning_file(main_file_path, individual_tasks_content):
    """
    Updates the main planning file with content from individual tasks.
    This is a basic version that assumes tasks in PLANNING_TASKS.md are separated by "---"
    and tries to match them by task ID extracted from headings.
    """
    try:
        with open(main_file_path, 'r', encoding='utf-8') as f:
            main_content = f.read()
    except FileNotFoundError:
        print(f"Error: Main planning file not found at '{main_file_path}'")
        return
    except Exception as e:
        print(f"Error reading main planning file {main_file_path}: {e}")
        return

    # Split the main content by task separators "---"
    # We need to be careful as "---" can also be in mermaid diagrams.
    # For now, we'll assume "---" on its own line is a reliable task separator.
    # A more robust approach would be to find task headings and replace content between them.

    # Let's try finding task blocks by headings and replacing them.
    # The structure is:
    # ... content before tasks ...
    # ## Epic X ...
    # # Epic X -- Task X.Y: Title
    # ... task content ...
    # ---
    # # Epic X -- Task X.Z: Title
    # ... task content ...
    # ---
    # ... content after tasks (mermaid, timeline) ...

    # We'll iterate through matches of TASK_HEADING_PATTERN in the main content.
    # For each match, we identify the start of the task's text (the heading itself)
    # and the end (the "---" separator that follows it, or the start of the next task heading, or EOF).

    new_main_content_parts = []
    last_pos = 0
    tasks_updated_count = 0
    tasks_found_in_main = 0

    for match in TASK_HEADING_PATTERN.finditer(main_content):
        tasks_found_in_main += 1
        task_id_from_heading = get_task_id_from_heading_match(match) # e.g., "1.1", "1.1b"
        
        # Add content before this task
        new_main_content_parts.append(main_content[last_pos:match.start()])

        # Find the end of this task block
        # It ends either at the next "---" on its own line, or start of next task, or EOF
        
        # Search for "---" separator after the current task's heading
        separator_match = re.search(r"\n\s*---\s*\n", main_content[match.start():])
        
        next_task_heading_match = TASK_HEADING_PATTERN.search(main_content, pos=match.end())

        end_of_block = len(main_content) # Default to EOF

        if separator_match:
            # Separator found relative to match.start()
            end_of_current_task_content_before_separator = match.start() + separator_match.start()
        else: # Should not happen if format is consistent
            end_of_current_task_content_before_separator = -1 # Mark as not found

        if next_task_heading_match:
            end_of_block = next_task_heading_match.start()
        
        # Determine the actual end of the task content to be replaced.
        # It's from its heading to just before its "---"
        # Or, if no "---" is found before the next task, up to the next task.
        
        # The content of the task in the main file is from match.start() up to
        # the "---" that belongs to it.
        # Let's define the task block as starting with the heading and ending *after* its "---"
        # separator, if one exists before the next task heading or EOF.

        current_task_main_block_end = -1

        # Find the "---" that belongs to *this* task
        # It must appear before the next task's heading (if any)
        # and before the overall "end_of_block" determined by next task or EOF.
        
        search_end_for_separator = end_of_block
        # Regex for "\n---" possibly followed by newline or EOF
        # We want the one that's closest after match.end() but before next_task_heading_match.start()
        
        temp_separator_match = None
        # Search for "\n\s*---\s*(\n|$)" to find the separator line for the current task.
        # Start search from end of current task's heading.
        # End search at start of next task's heading or EOF.
        sep_iter = re.finditer(r"\n\s*---\s*(?:\n|$)", main_content[match.end():search_end_for_separator])
        
        # We take the first such separator found after the heading.
        try:
            first_sep_after_heading = next(sep_iter)
            # This separator's end is relative to match.end()
            current_task_main_block_end = match.end() + first_sep_after_heading.end()
            
            # The actual content of the task to be replaced is main_content[match.start() : match.end() + first_sep_after_heading.start()]
            # And then we need to add the individual task content + the separator itself.

        except StopIteration:
            # No "---" found for this task before the next task or EOF.
            # This implies this task is the last one in a section or the file without a separator,
            # or the structure is unexpected.
            # The block effectively ends where the next task begins or EOF.
            current_task_main_block_end = end_of_block
            print(f"Warning: No '---' separator found for task '{task_id_from_heading}' before next task or EOF. Assuming content runs until next element.")


        if task_id_from_heading in individual_tasks_content:
            # Replace this task's content (heading + body from individual file)
            # The individual_tasks_content already contains the heading and body.
            new_task_full_content = individual_tasks_content[task_id_from_heading]
            
            new_main_content_parts.append(new_task_full_content)
            tasks_updated_count += 1
            
            # Add the separator if one was originally there for this task block,
            # or if the individual content doesn't end with one (which it shouldn't per spec).
            # The individual task content *is* the heading + body. The "---" is a list separator.
            if current_task_main_block_end != -1 and main_content[match.end() + first_sep_after_heading.start() : current_task_main_block_end].strip() == "---":
                 new_main_content_parts.append("\n" + main_content[match.end() + first_sep_after_heading.start() : current_task_main_block_end].strip() + "\n") # Add the separator
            elif current_task_main_block_end == end_of_block and not new_task_full_content.endswith("\n---"):
                # If it was the last task and had no separator, but should have one, add it.
                # This logic needs to be careful not to add double separators.
                # The main loop structure should handle this better.
                # For now, let's assume individual_tasks_content *does not* include the "---"
                # and we add it after each task.
                pass # Separator handling will be refined.

        else:
            # Task not found in individual files, keep original block from main file
            new_main_content_parts.append(main_content[match.start():current_task_main_block_end])
            print(f"Warning: Task '{task_id_from_heading}' found in main file but not in individual tasks. Kept original.")

        last_pos = current_task_main_block_end
        if last_pos == -1: # Should not happen if logic is correct
            print(f"Error: last_pos became -1. This indicates a logic flaw for task {task_id_from_heading}")
            # Fallback: try to advance last_pos to avoid infinite loops or incorrect appends.
            # This part of the logic is tricky.
            # A simpler way: iterate tasks. For each task, append its content. Append "---".
            # The main file is a list of (intro, epic_heading, task_1, ---, task_2, ---, ..., diagram)
            # The current loop structure is trying to replace in place.

    # Add the remaining content of the main file (e.g., mermaid diagram, timeline)
    new_main_content_parts.append(main_content[last_pos:])

    # This reconstruction logic is flawed. Let's simplify.
    # We need to handle the introduction, then epics, then within epics, tasks.
    # The current regex finds all tasks. We need to preserve content *between* epics too.

    # A better strategy:
    # 1. Read main file.
    # 2. Split into header (everything before first "## Epic"), epics, and footer (Mermaid, etc.).
    # 3. For each epic:
    #    Split into epic header and tasks.
    #    For each task string:
    #        Parse its ID.
    #        If ID in individual_tasks_content, replace.
    #    Join tasks with "---".
    # 4. Join all parts.

    # Simpler strategy for Part 1:
    # Iterate through task matches in the main file.
    # For each task, if an update is available, substitute its content.
    # The main challenge is accurately defining the "block" of a task in the main file.
    # A task block is:
    #   `# Epic X -- Task X.Y: Title\n...content...\n---` (note the \n before ---)
    #   OR, if it's the last task in an epic or file, it might not have `---` if formatting is loose.

    output_content = []
    current_pos = 0
    actual_content_changed_in_any_task = False # New flag for true no-op
    
    local_tasks_found_in_main = 0
    local_tasks_with_content_change = 0 # Renamed from local_tasks_updated_count

    for match in TASK_HEADING_PATTERN.finditer(main_content):
        local_tasks_found_in_main += 1
        task_id = get_task_id_from_heading_match(match)
        task_start_char_index = match.start()

        # Append content before this task
        output_content.append(main_content[current_pos:task_start_char_index])

        # Determine the end of this task's content definition and the full block (including separator) in the main file.
        next_heading_match = TASK_HEADING_PATTERN.search(main_content, pos=match.end())
        limit_for_separator_search = next_heading_match.start() if next_heading_match else len(main_content)
        
        separator_regex = r"\n\s*---\s*(\n|$)"
        
        # Find the first separator that occurs *after* the task heading but *before* the next task heading.
        # Slice the search area from the start of the current task's heading
        search_area_for_separator = main_content[task_start_char_index : limit_for_separator_search]
        
        potential_separators = list(re.finditer(separator_regex, search_area_for_separator))

        original_task_definition_text_block = "" # The heading + body
        original_task_block_end_index_in_main = -1 # End of definition + separator in main_content coordinates
        original_separator_string = ""

        if potential_separators:
            # The first separator found belongs to this task
            sep_match_in_slice = potential_separators[0]
            
            # original_task_definition_text_block is from task heading up to the start of its separator
            original_task_definition_text_block = search_area_for_separator[:sep_match_in_slice.start()]
            
            # original_separator_string is the separator itself
            original_separator_string = sep_match_in_slice.group(0)
            
            # original_task_block_end_index_in_main is after this separator, in main_content coordinates
            original_task_block_end_index_in_main = task_start_char_index + sep_match_in_slice.end()
        else:
            # No "---" found before the next task or EOF. Task definition is the whole slice.
            original_task_definition_text_block = search_area_for_separator
            original_separator_string = "" # No separator
            original_task_block_end_index_in_main = limit_for_separator_search
            
        if task_id in individual_tasks_content:
            updated_task_content_from_individual = individual_tasks_content[task_id]
            
            # Compare stripped content of the task definition (heading + body)
            if original_task_definition_text_block.strip() != updated_task_content_from_individual.strip():
                output_content.append(updated_task_content_from_individual)
                actual_content_changed_in_any_task = True
                local_tasks_with_content_change += 1
                # print(f"DEBUG: Task '{task_id}' content CHANGED.")
            else:
                # Content is the same, append the original definition text block
                output_content.append(original_task_definition_text_block)
                # print(f"DEBUG: Task '{task_id}' content IDENTICAL.")

            # Append separator:
            # Add a standard separator if there's a next task.
            # If it's the last task, append its original separator string (which might be empty or the actual separator).
            if next_heading_match is not None:
                output_content.append("\n---\n") 
            else: # Last task in the sequence of tasks being processed
                output_content.append(original_separator_string) 
            
        else:
            # Task not found in individual files, so append its original block from main_content
            # This block is from task_start_char_index to original_task_block_end_index_in_main (which includes its separator)
            output_content.append(main_content[task_start_char_index:original_task_block_end_index_in_main])
            if task_id: 
                print(f"Warning: Task '{task_id}' found in main file but not in individual task files. Original content kept.")

        current_pos = original_task_block_end_index_in_main # Move current_pos past the processed block

    # Append any remaining content from the main file (e.g. mermaid diagram, timeline)
    output_content.append(main_content[current_pos:])
    
    final_content = "".join(output_content)
    final_content = re.sub(r'\n\n\n+', '\n\n', final_content) # Normalize multiple blank lines

    print(f"DEBUG: Total tasks processed in main file: {local_tasks_found_in_main}")
    print(f"DEBUG: Tasks with actual content changes: {local_tasks_with_content_change}")

    if actual_content_changed_in_any_task: # Write only if actual content difference was found
        try:
            with open(main_file_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            print(f"Successfully updated '{main_file_path}'. {local_tasks_with_content_change}/{local_tasks_found_in_main} tasks from the main file had their content modified.")
        except Exception as e:
            print(f"Error writing updated main planning file {main_file_path}: {e}")
    else:
        print(f"No actual content changes detected. '{main_file_path}' remains unchanged.")
        # Optional: print more details if needed, e.g. how many were processed.
        # print(f"{local_tasks_found_in_main} tasks processed in main file. No content differed from individuals.")


def main():
    print(f"Loading individual tasks from: {INDIVIDUAL_TASKS_DIR}")
    individual_tasks = load_individual_tasks(INDIVIDUAL_TASKS_DIR)
    
    if not individual_tasks:
        print("No individual tasks loaded. Exiting.")
        return

    print(f"Found {len(individual_tasks)} individual task files.")
    #for task_id, content in individual_tasks.items():
    #    print(f"  Task {task_id} loaded (first 50 chars): {content[:50].replace(os.linesep, ' ')}...")

    print(f"\nUpdating main planning file: {PLANNING_TASKS_FILE}")
    update_main_planning_file(PLANNING_TASKS_FILE, individual_tasks)

if __name__ == "__main__":
    main()
