import os
import sys

def test_file_creation_limit(test_dir="test_dir_file_limits"):
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    file_count = 0
    try:
        while True:
            file_path = os.path.join(test_dir, f"test_file_{file_count}.tmp")
            with open(file_path, "w") as f:
                f.write("test")
            file_count += 1
            if file_count % 1000 == 0:
                print(f"Created {file_count} files...")
    except OSError as e:
        print(f"Failed to create file number {file_count + 1}: {e}")
        print(f"Maximum number of files created in '{test_dir}': {file_count}")
    except Exception as e:
        print(f"An unexpected error occurred at file {file_count + 1}: {e}")
        print(f"Maximum number of files created in '{test_dir}': {file_count}")
    finally:
        print("Cleaning up created files...")
        for i in range(file_count):
            try:
                os.remove(os.path.join(test_dir, f"test_file_{i}.tmp"))
            except OSError:
                pass # Ignore if already deleted or other error
        if os.path.exists(test_dir):
            try:
                os.rmdir(test_dir)
            except OSError as e:
                print(f"Could not remove test directory {test_dir}: {e}")
        print("Cleanup complete.")

if __name__ == "__main__":
    test_file_creation_limit()
