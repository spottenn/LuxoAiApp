Status: Not Started

# Epic 1 -- Task 1.2: Unified Script for Android SDK & Emulator Management (Space, Logging, Detachment Aware)

**Type:** `chore`

**Background:**
Automated tests for `LuxoAI` require a functional Android emulator. The execution environment (`jules.md`, `docs/jules/environment_summary_report.md`) is space-constrained (approx. 9.8GB total disk) and can be unstable, necessitating robust logging for debugging and recovery. This task focuses on creating a **single, unified shell script** (e.g., `avd_manager.sh`) for advanced Android Virtual Device (AVD) management. This script will consolidate functionalities previously envisioned as separate and will build upon the basic SDK setup potentially handled by `scripts/setup_jules_env.sh` (Task 1.1). This script is critical for CI/CD and development workflows.

**Key Considerations:**
*   **Single Script with Subcommands:** The script should operate via subcommands (e.g., `avd_manager.sh start_avd`, `avd_manager.sh stop_avd`, `avd_manager.sh delete_avd`).
*   **Space Efficiency:** The script must be extremely mindful of disk usage.
    *   When creating AVDs, it should default to or allow specification of minimal system images (e.g., `system-images;android-35;default;x86_64` or `system-images;android-35;aosp_atd;x86_64`). `aosp_atd` is preferred if available and functional for basic app testing, as it's typically smaller.
    *   The `delete_avd` command should ensure all associated AVD files are removed to reclaim maximum disk space.
    *   Disk space (e.g., using `df -h`) should be logged before and after significant operations like system image installation (if applicable during AVD creation), AVD creation, and AVD deletion.
*   **Detailed Progress Logging:** The script must implement comprehensive logging for all its operations. This includes:
    *   Commands being executed.
    *   Status updates at each significant step.
    *   Error messages in full.
    *   Timings for long operations (e.g., emulator boot, image download).
    *   This logging is crucial for diagnosing issues in potentially unstable CI environments.
*   **Idempotency & Error Handling:** The script should be runnable multiple times without adverse effects (e.g., trying to start an AVD that's already running should be handled gracefully or inform the user). It should handle common errors robustly (e.g., AVD not found, emulator failing to start, SDK components missing).
*   **Process Detachment:** When starting an emulator, the script must ensure the emulator process runs in the background, detached from the script's execution, allowing the script to exit while the emulator continues running (e.g., using `nohup ... &`).

**Acceptance Criteria:**
A single shell script (e.g., `scripts/avd_manager.sh`) is created with the following subcommands and characteristics:

*   **`start_avd [avd_name]` Subcommand:**
    *   Takes an optional AVD name (defaults to a predefined name like `luxo_avd`).
    *   Checks if the specified AVD exists.
    *   If the AVD does not exist:
        *   Checks if the required system image (e.g., `system-images;android-35;default;x86_64` or `system-images;android-35;aosp_atd;x86_64`) is installed. If not, attempts to install it using `sdkmanager`.
        *   Creates the AVD using `avdmanager create avd` with specified characteristics (name, the chosen space-efficient system image, a generic phone device definition, e.g., `pixel_6`).
    *   Starts the specified AVD in headless mode using `emulator @<avd_name>` with flags like `-no-window -no-audio -no-boot-anim -gpu swiftshader_indirect -read-only -no-snapshot-load -no-snapshot-save`. (Adding read-only and no-snapshot flags for better space management and faster starts).
    *   The emulator process must be detached (e.g., `nohup ... > /tmp/emulator.log 2>&1 &`).
    *   Reliably detects when the emulator has fully booted and is ready for `adb` commands (e.g., by polling `adb -s <emulator_id> shell getprop sys.boot_completed` until it returns `1`). The script should output the emulator ID (e.g., `emulator-5554`) once ready.
    *   Logs all steps, including disk space checks.
*   **`stop_avd [avd_name|emulator_id]` Subcommand:**
    *   Takes an optional AVD name or emulator ID (e.g., `emulator-5554`). If AVD name is given, it might need to determine the emulator ID. Defaults to stopping the AVD associated with the predefined name.
    *   Stops the running emulator instance (e.g., using `adb -s <emulator_id> emu kill`).
    *   Provides clear logging of the action.
*   **`delete_avd [avd_name]` Subcommand:**
    *   Takes an optional AVD name (defaults to the predefined name `luxo_avd`).
    *   Ensures the AVD is stopped if running.
    *   Deletes the AVD using `avdmanager delete avd -n <avd_name>`.
    *   Logs disk space before and after deletion to confirm space reclamation.
*   **General Script Characteristics:**
    *   All script operations are logged with sufficient detail (timestamps, command executed, output, errors) to trace execution flow and diagnose errors.
    *   The script is idempotent where applicable (e.g., attempting to create an AVD that already exists should not error out but inform the user).
    *   Handles common errors gracefully with informative messages.
    *   Includes checks for necessary tools (`sdkmanager`, `avdmanager`, `emulator`, `adb`) and `ANDROID_HOME` being set.

**Dependencies:**
*   Task 1.1 (`scripts/setup_jules_env.sh`): Base Android SDK command-line tools, platform tools, and build tools must be installed and available in `PATH`. The `avd_manager.sh` script will rely on `sdkmanager`, `avdmanager`, `emulator`, and `adb` being correctly configured and accessible.

**Parallelizable?:** `yes`

**Suggested Labels:** `ci`, `android`, `emulator`, `linux`, `scripting`, `automation`, `single-script`

**Effort Estimate:** L (Remains L due to the complexity of robust scripting, error handling, and process management in a single file)

**Definition of Done:**
1.  A new, well-documented shell script, named `avd_manager.sh` (or a similar clear name), is created in the `scripts/` directory that implements all specified subcommands and fulfills all acceptance criteria.
2.  The script is executable and rigorously tested for functionality, robustness, error handling, and idempotency.
3.  This task file (`epic_1_task_1_2.md`) is confirmed to accurately reflect these detailed requirements for the single script.
4.  Relevant project documentation, specifically a new or updated `docs/emulator_management.md`, is created/updated to explain the usage of this new unified script, including its subcommands and any important considerations (like `ANDROID_HOME` setup).
5.  The task status is updated to `Done` in `docs/planning/task-status.md`.
