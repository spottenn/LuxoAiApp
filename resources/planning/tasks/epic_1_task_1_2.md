Status: Started

# Epic 1 -- Task 1.2: Script Android SDK & Emulator Installation and Management (with Enhanced Logging and Debug Info)

**Type:** `chore`

**Background:** Automated tests require an Android emulator. This task focuses on scripting the installation of the Android SDK (if not fully covered by 1.1) and, crucially, the setup and management of an Android Virtual Device (AVD).

**Acceptance Criteria:**
*   Script can download and install specific Android SDK platform versions and build tools.
*   Script can create a new AVD with specified characteristics (e.g., API level, screen size, hardware profile), ideally with space-saving considerations.
*   Script can start and stop the created AVD in headless mode.
*   Emulator runs stably.
*   **Enhanced Logging for `setup_jules_env.sh`**: The main environment setup script (`resources/scripts/setup_jules_env.sh`) must be modified to ensure its full execution log (including stdout and stderr of all operations, and `set -x` style tracing if enabled by default in the script) is saved to a persistent file within the repository.
    *   Log file location: `tmp/startup_logs/setup_jules_env.log`.
    *   The `tmp/startup_logs/` directory should be created at the root of the repository if it doesn't exist.
    *   This log is crucial for diagnosing environment setup issues.

**Dependencies:** Task 1.1 (or its core components like `resources/scripts/setup_jules_env.sh`)

**Parallelizable?:** `yes`

**Suggested Labels:** `ci`, `android`, `emulator`, `linux`, `logging`, `debugging`

**Effort Estimate:** M (may increase to L depending on complexity of `setup_jules_env.sh` modification)

**Definition of Done:**
1.  Scripts to install SDK components and create/manage a headless AVD are developed and tested (pending environment stability).
2.  The `resources/scripts/setup_jules_env.sh` script is modified to output detailed logs to `tmp/startup_logs/setup_jules_env.log`.
3.  This task definition (`epic_1_task_1_2.md`) is updated to reflect these requirements.

**Debugging Notes / Known Issues (from previous attempts):**
When developing scripts that interact with the Android SDK tools (`sdkmanager`, `avdmanager`, `emulator`, `adb`), be mindful of the shell environment. Previous attempts to run such scripts encountered errors like:
*   `sdkmanager command not found. Please ensure Android SDK command-line tools are installed and in PATH.` (and similar for `avdmanager`, `emulator`, `adb`)
*   Suggestions from error messages included:
    *   `You might need to run 'source /home/jules/.bashrc' or re-login if they were just installed.`
    *   `Alternatively, ensure ANDROID_HOME/cmdline-tools/latest/bin and ANDROID_HOME/platform-tools are in PATH.`
This indicates that even if `setup_jules_env.sh` correctly installs tools and sets `ANDROID_HOME`/`PATH` for its own execution context, subsequent scripts or shell sessions might not inherit this environment correctly without explicit action (e.g., sourcing a profile script, or ensuring the calling environment for the scripts correctly sets up `ANDROID_HOME` and `PATH`). The enhanced logging for `setup_jules_env.sh` aims to help diagnose if it's setting these variables as expected.
The scripts themselves (`manage_avd.sh`, `control_emulator.sh`) should also be robust in checking for `ANDROID_HOME` and the presence of necessary SDK binaries in `PATH`.
