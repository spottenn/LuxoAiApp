# Android Emulator Management using avd_manager.sh

This document describes the usage of the `scripts/avd_manager.sh` script, a unified tool for managing Android Virtual Devices (AVDs) and emulators, primarily for CI/CD and development workflows within the LuxoAI project.

## Prerequisites

Before using `avd_manager.sh`, ensure the following:

1.  **Android SDK Command-line Tools**: Must be installed. The `setup_jules_env.sh` script (Task 1.1) should handle the base installation.
2.  **Environment Variable**: `ANDROID_HOME` (or `ANDROID_SDK_ROOT`) must be set and point to your Android SDK installation directory. The script will add necessary SDK tool paths (`cmdline-tools/latest/bin`, `platform-tools`, `emulator`) to its `PATH` if they are not already present.
3.  **Required SDK Components**: The script relies on `sdkmanager`, `avdmanager`, `emulator`, and `adb`. These should be accessible once `ANDROID_HOME` is correctly set up.
4.  **System Image**: The script will attempt to download necessary system images if they are not found. By default, it prefers `system-images;android-35;aosp_atd;x86_64` (AOSP Automated Test Device) for its smaller footprint and falls back to `system-images;android-35;default;x86_64`.

## Script Location

The script is located at `scripts/avd_manager.sh`.

## Usage

The script operates via subcommands.

```bash
./scripts/avd_manager.sh <subcommand> [arguments]
```

### Subcommands

#### 1. `start_avd [avd_name]`

Starts an Android emulator.

*   **`avd_name`** (optional): The name of the AVD to start.
    *   If not provided, defaults to `luxo_avd`.
*   **Functionality**:
    *   Checks if the specified AVD exists.
    *   If the AVD does not exist:
        *   It checks if the required system image (`system-images;android-35;aosp_atd;x86_64` or fallback `system-images;android-35;default;x86_64`) is installed. If not, it attempts to install it using `sdkmanager`.
        *   Creates the AVD using `avdmanager create avd` with the name, the chosen system image, and a device definition (default: `pixel_6`).
    *   Starts the AVD in headless mode (`-no-window -no-audio -no-boot-anim`) with specific performance and stability flags (`-gpu swiftshader_indirect -read-only -no-snapshot-load -no-snapshot-save`).
    *   The emulator process is detached and runs in the background. Emulator logs are saved to `/tmp/emulator_<avd_name>.log`.
    *   The script waits for the emulator to fully boot (by checking `sys.boot_completed` via ADB) and then outputs its emulator ID (e.g., `emulator-5554`).
    *   Logs disk space usage before and after significant operations (image installation, AVD creation, successful boot).

*   **Example**:
    ```bash
    ./scripts/avd_manager.sh start_avd
    ./scripts/avd_manager.sh start_avd my_custom_avd
    ```

#### 2. `stop_avd [avd_name|emulator_id]`

Stops a running Android emulator.

*   **`avd_name|emulator_id`** (optional):
    *   Can be the AVD name (e.g., `luxo_avd`). The script will attempt to determine the corresponding emulator ID (this is a best-effort for the default AVD, `emulator-5554`).
    *   Can be the direct emulator ID (e.g., `emulator-5554`).
    *   If not provided, defaults to stopping the AVD associated with the name `luxo_avd`.
*   **Functionality**:
    *   Stops the specified emulator instance using `adb -s <emulator_id> emu kill`.
    *   Provides logging of the action.

*   **Example**:
    ```bash
    ./scripts/avd_manager.sh stop_avd
    ./scripts/avd_manager.sh stop_avd luxo_avd
    ./scripts/avd_manager.sh stop_avd emulator-5554
    ```

#### 3. `delete_avd [avd_name]`

Deletes an Android Virtual Device.

*   **`avd_name`** (optional): The name of the AVD to delete.
    *   If not provided, defaults to `luxo_avd`.
*   **Functionality**:
    *   Ensures the AVD is stopped (calls `stop_avd` logic internally).
    *   Deletes the AVD using `avdmanager delete avd -n <avd_name>`.
    *   Logs disk space before and after deletion to confirm space reclamation.

*   **Example**:
    ```bash
    ./scripts/avd_manager.sh delete_avd
    ./scripts/avd_manager.sh delete_avd my_custom_avd
    ```

## Logging

*   All script operations are logged to standard output with timestamps.
*   Emulator-specific logs (from the `emulator` command itself) are saved to `/tmp/emulator_<avd_name>.log`. This is crucial for debugging emulator startup issues.
*   Disk space (`df -h`) is logged at key points to monitor usage, especially during AVD creation and deletion.

## Error Handling and Idempotency

*   The script checks for necessary tools (`sdkmanager`, `avdmanager`, `emulator`, `adb`) and the `ANDROID_HOME` variable at startup.
*   It attempts to handle common errors gracefully (e.g., AVD not found, emulator failing to start).
*   Operations are designed to be idempotent:
    *   Starting an AVD that already exists will not recreate it but will attempt to start the emulator.
    *   Stopping an already stopped emulator or deleting a non-existent AVD will be logged appropriately without causing script failure.

## Important Considerations

*   **Disk Space**: The script is designed for space-constrained environments. It uses space-efficient system images (`aosp_atd`) by default and logs disk usage. Monitor these logs if space issues arise.
*   **Emulator ID Detection**: The `start_avd` command actively waits for and identifies the emulator ID of the AVD it starts. For `stop_avd` when an AVD name is provided, the script makes a best guess for the emulator ID (typically `emulator-5554` for the default AVD). If multiple emulators are running, providing the specific `emulator_id` to `stop_avd` is more reliable.
*   **Headless Operation**: Emulators are started in headless mode, suitable for CI environments.
*   **Root/Sudo**: The script does not require `sudo` privileges for standard operations, assuming the user has permissions to manage the Android SDK and create files in `/tmp`.
```
