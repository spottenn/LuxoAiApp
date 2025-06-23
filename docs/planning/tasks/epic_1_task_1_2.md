Status: Not Started

# Epic 1 -- Task 1.2: Advanced Scripting for Android SDK & Emulator Management (Space & Logging Aware)

**Type:** `chore`

**Background:**
Automated tests for `LuxoAI` require a functional Android emulator. The execution environment (`jules.md`, `docs/jules/environment_summary_report.md`) is space-constrained (approx. 9.8GB total disk) and can be unstable, necessitating robust logging for debugging and recovery. This task focuses on creating new, dedicated scripts for advanced Android Virtual Device (AVD) management, building upon the basic SDK setup potentially handled by `scripts/setup_jules_env.sh` (Task 1.1). These scripts are critical for CI/CD and development workflows.

**Key Considerations:**
*   **Space Efficiency:** Scripts must be mindful of disk usage. This includes selecting minimal AVD system images (e.g., `aosp_atd` or `default` profiles, `x86_64` architecture), and providing options to clean up unused AVDs and system images. Disk space should be logged before/after significant operations.
*   **Detailed Progress Logging:** All scripts must implement comprehensive logging of their operations (e.g., commands executed, status updates, errors, timings for long operations like emulator boot). This is crucial for diagnosing issues in potentially unstable environments.
*   **Idempotency & Error Handling:** Scripts should be runnable multiple times without adverse effects and should handle common errors gracefully (e.g., AVD already exists, emulator fails to start).
*   **Modularity:** Separate scripts for AVD management (create, delete, list, manage system images) and emulator control (start, stop, status) are preferred.

**Acceptance Criteria:**
*   **SDK System Image Management:**
    *   Script can list available Android SDK system images (e.g., for API 35).
    *   Script can download and install a specified, space-efficient system image (e.g., `system-images;android-35;aosp_atd;x86_64` or `system-images;android-35;default;x86_64`).
    *   Script can uninstall a specified system image to reclaim disk space.
*   **AVD Management (`manage_avd.sh` or similar):**
    *   Script can create a new AVD with specified characteristics (name, system image, device definition like a generic phone, API level).
    *   Script can delete an existing AVD by name.
    *   Script can list all created AVDs and their configurations/status.
*   **Emulator Control (`control_emulator.sh` or similar):**
    *   Script can start a specified AVD in headless mode (e.g., using flags like `-no-window -no-audio -no-boot-anim -gpu swiftshader_indirect`).
    *   Script can reliably detect when the emulator has fully booted and is ready for `adb` commands (e.g., by checking `getprop sys.boot_completed`).
    *   Script can stop a running emulator instance (e.g., using `adb emu kill`).
    *   Script can report the status of the emulator (e.g., running, not running, which AVD).
*   **Logging & Stability:**
    *   All script operations are logged with sufficient detail to trace execution flow and diagnose errors.
    *   Emulator runs stably once started.
    *   Disk space usage is logged at critical points (install/uninstall images, create/delete AVDs).

**Dependencies:**
*   Task 1.1 (`scripts/setup_jules_env.sh`): Base Android SDK command-line tools, platform tools, and build tools must be installed and available in `PATH`. The new scripts will rely on `sdkmanager`, `avdmanager`, `emulator`, and `adb`.

**Parallelizable?:** `yes` (script development can be parallel to other non-dependent tasks)

**Suggested Labels:** `ci`, `android`, `emulator`, `linux`, `scripting`, `automation`

**Effort Estimate:** L (Increased from M due to enhanced requirements for logging, space management, and robustness)

**Definition of Done:**
1.  New, well-documented shell scripts (`manage_avd.sh`, `control_emulator.sh` or similarly named) are created in `scripts/` that fulfill all acceptance criteria.
2.  These scripts are executable and tested for functionality and robustness.
3.  Task `epic_1_task_1_2.md` (this file) is updated to reflect these detailed requirements.
4.  Relevant project documentation (`jules.md` if impacted, and a new `resources/docs/emulator_management.md`) is updated or created to explain the usage of these new scripts.
5.  Task status updated in `docs/planning/task-status.md`.

**Debugging Notes / Known Issues (from previous attempts):**
When developing scripts that interact with the Android SDK tools (`sdkmanager`, `avdmanager`, `emulator`, `adb`), be mindful of the shell environment. Previous attempts to run such scripts encountered errors like:
*   `sdkmanager command not found. Please ensure Android SDK command-line tools are installed and in PATH.` (and similar for `avdmanager`, `emulator`, `adb`)
*   Suggestions from error messages included:
    *   `You might need to run 'source /home/jules/.bashrc' or re-login if they were just installed.`
    *   `Alternatively, ensure ANDROID_HOME/cmdline-tools/latest/bin and ANDROID_HOME/platform-tools are in PATH.`
        This indicates that even if `setup_jules_env.sh` correctly installs tools and sets `ANDROID_HOME`/`PATH` for its own execution context, subsequent scripts or shell sessions might not inherit this environment correctly without explicit action (e.g., sourcing a profile script, or ensuring the calling environment for the scripts correctly sets up `ANDROID_HOME` and `PATH`). The enhanced logging for `setup_jules_env.sh` aims to help diagnose if it's setting these variables as expected.
        The scripts themselves (`manage_avd.sh`, `control_emulator.sh`) should also be robust in checking for `ANDROID_HOME` and the presence of necessary SDK binaries in `PATH`.
Logs have been created for the startup script in /logs/startup.log. This log file is to show the commands that the environment runs by itself and the output of those commands, the startup script and the setup script.