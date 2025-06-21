import os
import threading
import multiprocessing
import time
import sys

def basic_thread_func():
    time.sleep(60) # Keep thread alive for a bit

def basic_process_func():
    time.sleep(60) # Keep process alive for a bit

def test_thread_limits():
    print("Starting thread limit test...")
    threads = []
    count = 0
    try:
        while True:
            thread = threading.Thread(target=basic_thread_func)
            thread.daemon = True # Allow main program to exit even if threads are running
            thread.start()
            threads.append(thread)
            count += 1
            if count % 100 == 0:
                print(f"Successfully started {count} threads...")
    except RuntimeError as e:
        print(f"Failed to start thread number {count + 1}: {e}")
        print(f"Maximum number of threads created: {count}")
    except Exception as e:
        print(f"An unexpected error occurred at thread {count + 1}: {e}")
        print(f"Maximum number of threads created: {count}")
    finally:
        print(f"Total threads attempted: {count}")
        # No need to explicitly join daemon threads for this test's purpose

def test_process_limits():
    print("\nStarting process limit test...")
    processes = []
    count = 0
    # Set start method for multiprocessing if not default (spawn is often safer)
    # Python 3.8+ on macOS defaults to 'spawn', Linux often 'fork'
    # Forcing 'spawn' can avoid some issues with fork if resources aren't inherited cleanly
    if sys.platform == "darwin": # Though this environment is Linux, good practice
         multiprocessing.set_start_method('spawn', force=True)

    try:
        while True:
            process = multiprocessing.Process(target=basic_process_func)
            process.daemon = True # Allow main program to exit
            process.start()
            processes.append(process)
            count += 1
            if count % 50 == 0: # Processes are heavier, log more frequently
                print(f"Successfully started {count} processes...")
    except Exception as e: # Catching a broad exception as different OS errors can occur
        print(f"Failed to start process number {count + 1}: {e}")
        print(f"Maximum number of processes created: {count}")
    finally:
        print(f"Total processes attempted: {count}")
        # Terminate all spawned processes
        for p in processes:
            if p.is_alive():
                p.terminate()
                p.join(timeout=1) # Wait a bit for termination
        print("Process cleanup attempted.")


if __name__ == "__main__":
    # It's often better to test these separately, as one can affect the other.
    # However, the original report didn't specify, so running sequentially.
    # Note: High number of processes might make thread test less reliable if run after.
    # For a clean test, these should ideally be run in fresh environments or with reboots.

    # Let's test threads first as they are lighter weight.
    test_thread_limits()

    # Brief pause to let system stabilize, though with daemon threads it's less critical
    time.sleep(5)

    test_process_limits()
