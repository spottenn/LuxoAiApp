#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.
# set -x # Print commands and their arguments as they are executed.

# --- Configuration ---
DEFAULT_AVD_NAME="luxo_avd"
# Preferred system image: AOSP Automated Test Device (ATD) - typically smaller
PREFERRED_SYSTEM_IMAGE="system-images;android-35;aosp_atd;x86_64"
# Fallback system image: Standard AOSP image
FALLBACK_SYSTEM_IMAGE="system-images;android-35;default;x86_64" # Fallback if ATD fails
# Device definition to use for the AVD
AVD_DEVICE_DEFINITION="Nexus S" # Using Nexus S due to space issues with pixel_6
# Log file for emulator output
EMULATOR_LOG_DIR="/tmp"

# --- Logging Functions ---
log_info() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1"
}

log_error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1" >&2
}

log_command() {
    log_info "Executing command: $@"
    "$@"
}

log_space() {
    log_info "Current disk space usage:"
    df -h
}

# --- Helper Functions ---

# Function to find an available emulator port (e.g., 5554, 5556, etc.)
# Note: This is a simple approach. A more robust solution might involve
# checking if the port is truly free or letting the emulator pick one.
# For now, we'll rely on the standard behavior and typical single-emulator scenarios.
get_emulator_id_from_avd_name() {
    local avd_name_to_check="$1"
    # List devices and try to find one that might match the AVD name pattern.
    # This is heuristic as 'adb devices' doesn't directly link to AVD names before boot.
    # A common pattern is emulator-XXXX. We'll assume the first one for now if only one is booting/running.
    # A more reliable method post-boot is to query properties, but we need an ID to query.
    # For now, we'll assume the standard port `emulator-5554` if trying to connect to a newly started AVD.
    # This part might need refinement if multiple emulators are managed by this script simultaneously.
    # A simple approach: if an AVD named 'luxo_avd' is started, it often gets 'emulator-5554'.
    # This is not guaranteed, especially with multiple AVDs or concurrent emulator instances.
    # For now, we'll hardcode a common default, as detection is complex pre-connection.
    # A better approach for future improvement:
    # 1. After `emulator` command, try to list devices.
    # 2. If a new `emulator-XXXX` appears, assume that's the one.
    # This requires careful state management if other emulators are already running.

    # For now, let's assume the default port for the default AVD name,
    # and require explicit emulator_id for others if this heuristic fails.
    if [ "$avd_name_to_check" == "$DEFAULT_AVD_NAME" ]; then
        echo "emulator-5554"
    else
        # For non-default AVD names, this heuristic is weaker.
        # We might need to rely on the user providing the emulator_id if stop/delete needs it before it's known.
        # However, for start_avd, the boot check will find the correct one.
        echo "emulator-5554" # Default guess, will be verified by boot check
    fi
}

get_running_emulator_id_for_avd() {
    local target_avd_name="$1"
    local_emulator_id=""
    # Try to get the path of the running AVD, which includes its name.
    # This is a more robust way to link an emulator ID to an AVD name if it's already running.
    # We need to iterate through `adb devices` and then query each device.
    # `adb -s <emulator-id> emu avd path` can give the path, which contains the AVD name.
    # However, `emu avd path` is not a standard adb shell command.
    # A common approach is to query `ro.kernel.qemu.avd_name` or similar, but this might not always be available or accurate.

    # Simpler approach for now: use `telnet localhost <port> avd name`
    # This requires knowing the console port, which is usually the number in emulator-XXXX.
    # Example: emulator-5554 -> console port 5554
    # This is still complex. The most straightforward way for *this script's managed AVD*
    # is to rely on the fact that we are starting it and will discover its ID.
    # If we need to find an ID for an AVD started *outside* this script, it's harder.

    # Given the task's focus on this script managing the AVD,
    # the `start_avd` will find the ID. `stop_avd` and `delete_avd`
    # can use a known ID (if passed) or the default `emulator-5554` for the default AVD.

    # Let's refine `get_emulator_id_from_avd_name` to be more of a placeholder
    # and improve the boot detection in `start_avd` to find the actual ID.
    # For now, returning a default, assuming `start_avd` will confirm/find the correct one.
    echo "emulator-5554" # Placeholder, actual detection logic is more complex for already running emulators.
}


check_env_vars() {
    log_info "Checking required environment variables..."
    if [ -z "$ANDROID_HOME" ] && [ -z "$ANDROID_SDK_ROOT" ]; then
        log_error "ANDROID_HOME or ANDROID_SDK_ROOT environment variable is not set. Please set it to your Android SDK path."
        exit 1
    fi
    # Prefer ANDROID_HOME if both are set, otherwise use ANDROID_SDK_ROOT
    # This aligns with Android Gradle Plugin behavior.
    if [ -z "$ANDROID_HOME" ]; then
      ANDROID_HOME="$ANDROID_SDK_ROOT"
    fi
    log_info "ANDROID_HOME is set to: $ANDROID_HOME"

    # Ensure SDK manager, AVD manager, emulator, and ADB are in PATH or accessible via ANDROID_HOME
    # Adding them to PATH for the script's session if not already there and ANDROID_HOME is set.
    export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"
    # Also ensure USER is set, as some Android tools might need it.
    export USER=$(whoami)
}

install_emulator_if_missing() {
    log_info "Checking for Android Emulator package..."
    if [ -d "$ANDROID_HOME/emulator" ] && [ -x "$ANDROID_HOME/emulator/emulator" ]; then
        log_info "Android Emulator directory and executable found."
        # Ensure emulator is on PATH for command -v check if it wasn't already
        if ! command -v emulator &> /dev/null; then
             export PATH="$ANDROID_HOME/emulator:$PATH" # Add it if somehow missed
        fi
        if command -v emulator &> /dev/null; then
            log_info "Emulator command is available in PATH: $(command -v emulator)"
            return 0
        fi
    fi

    log_info "Android Emulator not found or not executable at $ANDROID_HOME/emulator/emulator, or not in PATH correctly."
    log_info "Attempting to install Android Emulator package using sdkmanager..."
    # It's important that sdkmanager itself is found by this point.
    if ! command -v sdkmanager &> /dev/null; then
        log_error "sdkmanager not found. Cannot install emulator. Please ensure ANDROID_HOME is set and cmdline-tools are installed."
        exit 1
    fi

    log_command sdkmanager --install "emulator" || {
        log_error "Failed to install Android Emulator package using sdkmanager. Please check sdkmanager output."
        # Check available packages to see if "emulator" is listed
        log_info "Listing available packages via sdkmanager --list:"
        sdkmanager --list || true # List packages for debugging, don't fail script if list fails
        exit 1
    }

    # After installation, re-check
    if [ -d "$ANDROID_HOME/emulator" ] && [ -x "$ANDROID_HOME/emulator/emulator" ]; then
        log_info "Android Emulator package installed successfully."
        # Ensure it's on PATH for subsequent checks/use
        export PATH="$ANDROID_HOME/emulator:$PATH"
        if command -v emulator &> /dev/null; then
             log_info "Emulator command is now available in PATH: $(command -v emulator)"
             return 0
        else
            log_error "Emulator installed, but still not found in PATH correctly. Path issue."
            exit 1
        fi
    else
        log_error "Android Emulator package installation command ran, but emulator still not found at $ANDROID_HOME/emulator/emulator or not executable."
        exit 1
    fi
}

check_tools() {
    log_info "Checking for required tools..."
    # First, ensure emulator package is present, as it might affect PATH for the 'emulator' command check
    install_emulator_if_missing

    local missing_tools=0
    for tool in sdkmanager avdmanager emulator adb; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool could not be found. Please ensure it's installed and in your PATH."
            log_error "Current PATH: $PATH"
            # Specific check for emulator if it fails
            if [ "$tool" == "emulator" ]; then
                if [ ! -d "$ANDROID_HOME/emulator" ]; then
                    log_error "Directory $ANDROID_HOME/emulator does not exist."
                elif [ ! -x "$ANDROID_HOME/emulator/emulator" ]; then
                    log_error "File $ANDROID_HOME/emulator/emulator exists but is not executable."
                    ls -l "$ANDROID_HOME/emulator/emulator"
                else
                    log_error "File $ANDROID_HOME/emulator/emulator exists and is executable, but 'command -v emulator' failed."
                fi
            fi
            missing_tools=1
        else
            log_info "$tool found at: $(command -v $tool)"
        fi
    done
    if [ "$missing_tools" -eq 1 ]; then
        exit 1
    fi
    log_info "All required tools are available."
}

# --- Main Script Logic ---
main() {
    check_env_vars # Sets ANDROID_HOME and initial PATH modifications
    check_tools    # Installs emulator if needed, then checks all tools

    if [ $# -eq 0 ]; then
        log_error "No subcommand provided. Usage: $0 {start_avd|stop_avd|delete_avd} [avd_name|emulator_id]"
        exit 1
    fi

    SUBCOMMAND=$1
    AVD_ARG_NAME="${2:-$DEFAULT_AVD_NAME}" # Use provided name or default for AVD specific commands

    case "$SUBCOMMAND" in
        start_avd)
            start_avd "$AVD_ARG_NAME"
            ;;
        stop_avd)
            # Argument for stop_avd can be AVD name or emulator_id
            local target_identifier="${2:-$DEFAULT_AVD_NAME}"
            stop_avd "$target_identifier"
            ;;
        delete_avd)
            delete_avd "$AVD_ARG_NAME"
            ;;
        *)
            log_error "Invalid subcommand: $SUBCOMMAND. Usage: $0 {start_avd|stop_avd|delete_avd} [avd_name | emulator_id]"
            exit 1
            ;;
    esac
}

# --- Subcommand Implementations ---

start_avd() {
    local avd_name="$1"
    log_info "Starting AVD: $avd_name"
    log_space

    # Check if AVD exists
    if avdmanager list avd | grep -q "Name: $avd_name"; then
        log_info "AVD '$avd_name' already exists."
    else
        log_info "AVD '$avd_name' does not exist. Attempting to create it."
        local system_image_to_use=""
        local image_installed=false

        # Check for preferred system image
        log_info "Checking for preferred system image: $PREFERRED_SYSTEM_IMAGE"
        if sdkmanager --list_installed | grep -q "$PREFERRED_SYSTEM_IMAGE"; then
            log_info "Preferred system image '$PREFERRED_SYSTEM_IMAGE' is already installed."
            system_image_to_use="$PREFERRED_SYSTEM_IMAGE"
            image_installed=true
        else
            log_info "Preferred system image '$PREFERRED_SYSTEM_IMAGE' not found. Attempting to install..."
            log_command sdkmanager --install "$PREFERRED_SYSTEM_IMAGE" || {
                log_error "Failed to install preferred system image '$PREFERRED_SYSTEM_IMAGE'. Trying fallback."
            }
            if sdkmanager --list_installed | grep -q "$PREFERRED_SYSTEM_IMAGE"; then
                log_info "Successfully installed preferred system image '$PREFERRED_SYSTEM_IMAGE'."
                system_image_to_use="$PREFERRED_SYSTEM_IMAGE"
                image_installed=true
                log_space
            fi
        fi

        # If preferred image failed or wasn't chosen, try fallback
        if [ "$image_installed" = false ]; then
            log_info "Checking for fallback system image: $FALLBACK_SYSTEM_IMAGE"
            if sdkmanager --list_installed | grep -q "$FALLBACK_SYSTEM_IMAGE"; then
                log_info "Fallback system image '$FALLBACK_SYSTEM_IMAGE' is already installed."
                system_image_to_use="$FALLBACK_SYSTEM_IMAGE"
                image_installed=true
            else
                log_info "Fallback system image '$FALLBACK_SYSTEM_IMAGE' not found. Attempting to install..."
                log_command sdkmanager --install "$FALLBACK_SYSTEM_IMAGE" || {
                    log_error "Failed to install fallback system image '$FALLBACK_SYSTEM_IMAGE'. Cannot create AVD."
                    exit 1
                }
                if sdkmanager --list_installed | grep -q "$FALLBACK_SYSTEM_IMAGE"; then
                    log_info "Successfully installed fallback system image '$FALLBACK_SYSTEM_IMAGE'."
                    system_image_to_use="$FALLBACK_SYSTEM_IMAGE"
                    image_installed=true
                    log_space
                else
                    log_error "Failed to install any suitable system image. Cannot create AVD."
                    exit 1
                fi
            fi
        fi

        if [ -z "$system_image_to_use" ]; then
            log_error "Could not determine a system image to use. Cannot create AVD."
            exit 1
        fi

        log_info "Creating AVD '$avd_name' with system image '$system_image_to_use', device '$AVD_DEVICE_DEFINITION', and SD card size 100M."
        # Use "echo no" to automatically answer prompt if AVD skin is not found, preventing script from hanging.
        # Adding -c 100M for a small SD card.
        echo "no" | log_command avdmanager create avd -n "$avd_name" -k "$system_image_to_use" -d "$AVD_DEVICE_DEFINITION" -c 100M --force || {
             log_error "Failed to create AVD '$avd_name'. Please check avdmanager output."
             # Attempt to provide more specific feedback if possible
             if ! sdkmanager --list_installed | grep -q "$system_image_to_use"; then
                log_error "The system image '$system_image_to_use' may not have been installed correctly or is not available for the AVD manager."
             fi
             if ! avdmanager list device | grep -q "name: $AVD_DEVICE_DEFINITION"; then
                log_error "The device definition '$AVD_DEVICE_DEFINITION' might not be available. Check 'avdmanager list device'."
             fi
             exit 1
        }
        log_info "AVD '$avd_name' created successfully."
        log_space

        # Attempt to reduce disk.dataPartition.size to save space
        local avd_config_ini_path="$HOME/.android/avd/${avd_name}.avd/config.ini"
        if [ -f "$avd_config_ini_path" ]; then
            log_info "Modifying $avd_config_ini_path to reduce disk.dataPartition.size..."
            local original_data_size=$(grep "disk.dataPartition.size" "$avd_config_ini_path" | cut -d'=' -f2)
            log_info "Original disk.dataPartition.size = $original_data_size"
            # Set to 2G, which seems to be a common default for smaller devices.
            if grep -q "disk.dataPartition.size" "$avd_config_ini_path"; then
                sed -i 's/disk.dataPartition.size.*/disk.dataPartition.size = 2048M/' "$avd_config_ini_path"
            else
                echo "disk.dataPartition.size = 2048M" >> "$avd_config_ini_path"
            fi
            local new_data_size=$(grep "disk.dataPartition.size" "$avd_config_ini_path" | cut -d'=' -f2)
            log_info "New disk.dataPartition.size = $new_data_size"
        else
            log_warn "Could not find AVD config.ini at $avd_config_ini_path to modify data partition size. Proceeding with default."
        fi
    fi

    # Check if an emulator for this AVD might already be running
    # This is tricky. `adb devices` shows device IDs (emulator-XXXX) not AVD names.
    # A simple check could be to see if the default port is busy, but this is not robust.
    # For now, we proceed to start, and if it fails due to port conflict, `emulator` command should indicate this.
    # More advanced check: `adb devices | grep emulator-` and then try to kill existing ones if they match a known pattern or if a general cleanup is desired.
    # However, the task asks to handle "AVD already running" gracefully. `emulator` usually handles this if it's the *same* AVD.

    log_info "Starting emulator for AVD '$avd_name'..."
    local emulator_logfile="${EMULATOR_LOG_DIR}/emulator_${avd_name}.log"
    log_info "Emulator logs will be at: $emulator_logfile"

    # Ensure emulator log directory exists
    mkdir -p "$EMULATOR_LOG_DIR"

    # Start the emulator in the background
    # Using -read-only as per task spec for potentially faster starts and space management.
    # -no-snapshot-load and -no-snapshot-save are also for faster starts and consistent state.
    # Adding -no-cache as a test.
    nohup "$ANDROID_HOME/emulator/emulator" -avd "$avd_name" -no-window -no-audio -no-boot-anim -gpu swiftshader_indirect -read-only -no-snapshot-load -no-snapshot-save -no-cache > "$emulator_logfile" 2>&1 &
    EMULATOR_PID=$!
    log_info "Emulator process started with PID $EMULATOR_PID. Waiting for boot..."

    # Wait for the emulator to boot and obtain its ID
    local boot_completed=0
    local max_wait_time=300 # 5 minutes
    local wait_interval=5 # seconds
    local elapsed_time=0
    local emulator_id=""

    # Give the emulator a few seconds to register itself before polling `adb devices`
    sleep 10

    while [ $elapsed_time -lt $max_wait_time ]; do
        # Try to find the emulator ID. This is the most complex part.
        # `adb devices` lists devices like "emulator-5554 device".
        # We need to find the one corresponding to the AVD we just started.
        # If multiple emulators are running, this can be ambiguous without more sophisticated checks.
        # A common strategy: find the newest "emulator-XXXX" device that is not yet fully booted.

        # Get list of all emulators
        emulator_ids_found=$(adb devices | grep "emulator-" | awk '{print $1}')

        if [ -z "$emulator_ids_found" ]; then
            log_info "No emulators found yet by 'adb devices'. Waiting..."
            sleep "$wait_interval"
            elapsed_time=$((elapsed_time + wait_interval + 10)) # Account for initial sleep
            continue
        fi

        for id in $emulator_ids_found; do
            # Check if this emulator is the one we are trying to start.
            # One way is to check its AVD name if possible, but that's hard before full boot.
            # Another is to check boot status. If multiple are booting, this could pick the wrong one.
            # For now, we assume if an emulator is found and not yet booted, it's likely ours.
            # If an emulator is already booted, we also check it.

            log_info "Checking status of emulator: $id"
            current_boot_status=$(adb -s "$id" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r\n')

            if [ "$current_boot_status" = "1" ]; then
                # If it's booted, we need to ensure it's the *correct* AVD.
                # This is difficult without a reliable command to get AVD name from emulator ID.
                # For now, if an emulator is booted and we haven't found ours,
                # and if only one emulator is expected, this might be it.
                # A temporary workaround: assume the first booted one we find is ours if $emulator_id is not set.
                # This is not robust for multiple emulators.
                log_info "Emulator '$id' has sys.boot_completed=1."

                # Attempt to get AVD name from emulator. This is not standard/reliable.
                # Trying a common property, but it might not exist.
                # adb -s $id shell getprop ro.kernel.qemu.avd_name
                # adb -s $id emu avd name (not a standard adb command)

                # For now, we'll assume if we find a booted device and $avd_name matches a common pattern (like the default)
                # and $id is the default port, it's probably the one. This needs improvement.
                # A better way would be to parse the emulator log file for the port it's using.

                # If we started an AVD named $avd_name, and an emulator $id is booted,
                # we'll assume it's the one we started for now.
                # This is the most problematic part of the script in a multi-emulator environment.
                emulator_id="$id"
                boot_completed=1
                break # Exit the inner loop (checking IDs)
            elif [[ "$current_boot_status" =~ ^[0-9]+$ ]]; then # If it's a number but not 1, it's booting
                log_info "Emulator '$id' is booting (sys.boot_completed=$current_boot_status)."
                # We can tentatively assign this ID, and keep checking it.
                # If multiple are booting, this picks the first one from `adb devices`.
                emulator_id="$id"
            else
                log_info "Emulator '$id' not responsive or status unknown ('$current_boot_status'). Might be shutting down or starting up."
            fi
        done

        if [ "$boot_completed" -eq 1 ] && [ -n "$emulator_id" ]; then
            break # Exit the outer while loop (waiting for boot)
        fi

        if [ -n "$emulator_id" ]; then
            log_info "Emulator ID tentatively identified as '$emulator_id'. Waiting for full boot (sys.boot_completed=1)... ($elapsed_time/$max_wait_time s)"
        else
            log_info "No emulator fully booted or identified yet. Waiting... ($elapsed_time/$max_wait_time s)"
        fi

        sleep "$wait_interval"
        elapsed_time=$((elapsed_time + wait_interval))

        # Check if the nohup process is still alive
        if ! ps -p $EMULATOR_PID > /dev/null; then
            log_error "Emulator process with PID $EMULATOR_PID is no longer running. Check logs at $emulator_logfile."
            # Try to get last few lines of emulator log
            if [ -f "$emulator_logfile" ]; then
                log_error "Last 10 lines of emulator log ($emulator_logfile):"
                tail -n 10 "$emulator_logfile" >&2
            fi
            exit 1
        fi
    done

    if [ "$boot_completed" -eq 1 ] && [ -n "$emulator_id" ]; then
        log_info "Emulator '$emulator_id' for AVD '$avd_name' successfully booted."
        echo "Emulator ready: $emulator_id"
        log_space
    else
        log_error "Emulator for AVD '$avd_name' did not boot within $max_wait_time seconds or could not be identified."
        log_error "Final list of devices from 'adb devices':"
        adb devices >&2
        if [ -f "$emulator_logfile" ]; then
            log_error "Last 20 lines of emulator log ($emulator_logfile):"
            tail -n 20 "$emulator_logfile" >&2
        fi
        # Attempt to kill the emulator process if it's still running to prevent zombies
        if ps -p $EMULATOR_PID > /dev/null; then
            log_info "Attempting to kill lingering emulator process PID $EMULATOR_PID..."
            kill $EMULATOR_PID
            sleep 2
            if ps -p $EMULATOR_PID > /dev/null; then
                log_info "Emulator process $EMULATOR_PID still alive, trying kill -9..."
                kill -9 $EMULATOR_PID
            fi
        fi
        exit 1
    fi
}

stop_avd() {
    local target="$1" # Can be AVD name or emulator_id
    log_info "Attempting to stop AVD/emulator: $target"

    local emulator_id_to_stop=""

    if [[ "$target" == emulator-* ]]; then
        emulator_id_to_stop="$target"
        log_info "Provided target is an emulator ID: $emulator_id_to_stop"
    else
        # Target is an AVD name, try to find its emulator_id
        # This is complex if multiple emulators are running.
        # For a single managed emulator, we can assume the default or try to find it.
        log_info "Provided target is an AVD name: $target. Attempting to find corresponding emulator ID."
        # This helper function is a placeholder and might not be robust enough.
        emulator_id_to_stop=$(get_running_emulator_id_for_avd "$target")

        if [ -z "$emulator_id_to_stop" ]; then
            log_error "Could not determine emulator ID for AVD name '$target'. If it's running, try providing the emulator ID directly (e.g., emulator-5554)."
            # Check if any emulators are running at all
            if ! adb devices | grep -q "emulator-"; then
                log_info "No emulators appear to be running according to 'adb devices'."
                # If the AVD name is the default, it's possible it was never started or already stopped.
                if [ "$target" == "$DEFAULT_AVD_NAME" ]; then
                    log_info "AVD '$target' (default) might not be running or was already stopped."
                    return 0 # Consider this a success if the goal is to stop it and it's not running
                fi
            fi
            # return 1 # Disabled to allow delete_avd to proceed even if stop fails to find ID
        fi
        log_info "Determined emulator ID for AVD '$target' as '$emulator_id_to_stop'. This is a best guess."
    fi

    # Check if the determined emulator_id is actually in the list of devices
    if ! adb devices | grep -q "^$emulator_id_to_stop"; then
        log_info "Emulator '$emulator_id_to_stop' not found in 'adb devices' list. It might already be stopped or the ID is incorrect."
        # If the AVD name was the default, assume it's okay if not found.
        if [[ "$target" == "$DEFAULT_AVD_NAME" ]] && [[ "$emulator_id_to_stop" == "emulator-5554" ]]; then
            log_info "Assuming default AVD '$target' is already stopped as '$emulator_id_to_stop' is not active."
            return 0
        fi
        log_error "Cannot stop '$emulator_id_to_stop' as it's not listed by 'adb devices'."
        # return 1 # Allow delete_avd to proceed
    fi

    log_info "Sending 'emu kill' command to $emulator_id_to_stop."
    log_command adb -s "$emulator_id_to_stop" emu kill || {
        log_error "Failed to stop emulator '$emulator_id_to_stop' using 'adb emu kill'. It might have already been stopped or encountered an issue."
        # Check if it's still in adb devices
        if adb devices | grep -q "^$emulator_id_to_stop"; then
            log_info "Emulator '$emulator_id_to_stop' is still listed by 'adb devices'. The 'emu kill' command might have failed."
            # return 1 # Allow delete_avd to proceed
        else
            log_info "Emulator '$emulator_id_to_stop' is no longer listed by 'adb devices'. Assuming it was stopped."
        fi
    }
    log_info "Emulator '$emulator_id_to_stop' (for AVD/target '$target') stop command issued. It may take a moment to fully shut down."
    # Add a small delay to allow the emulator to shut down
    sleep 5
    if adb devices | grep -q "^$emulator_id_to_stop"; then
        log_info "Emulator '$emulator_id_to_stop' still listed after 'emu kill'. It might be unresponsive or taking longer to shut down."
    else
        log_info "Emulator '$emulator_id_to_stop' is no longer listed by 'adb devices'. Successfully stopped."
    fi
}

delete_avd() {
    local avd_name="$1"
    log_info "Deleting AVD: $avd_name"
    log_space

    # Ensure AVD is stopped first.
    # This is best effort; if emulator ID cannot be found, deletion will still be attempted.
    log_info "Ensuring AVD '$avd_name' is stopped before deletion..."
    stop_avd "$avd_name" # Pass AVD name to stop_avd

    if ! avdmanager list avd | grep -q "Name: $avd_name"; then
        log_info "AVD '$avd_name' does not exist or was already deleted."
    else
        log_info "Attempting to delete AVD '$avd_name' using avdmanager..."
        log_command avdmanager delete avd -n "$avd_name" || {
            log_error "Failed to delete AVD '$avd_name' using avdmanager. It might be in use or there was an error."
            # Check if it's still listed
            if avdmanager list avd | grep -q "Name: $avd_name"; then
                log_error "AVD '$avd_name' is still listed by 'avdmanager list avd'."
            else
                log_info "AVD '$avd_name' is no longer listed. Deletion might have partially succeeded or completed despite error message."
            fi
            # exit 1 # Don't exit, just log, maybe it was already gone.
        }
        if avdmanager list avd | grep -q "Name: $avd_name"; then
             log_error "AVD '$avd_name' still exists after deletion attempt."
        else
             log_info "AVD '$avd_name' successfully deleted (or was not found after attempt)."
        fi
    fi
    log_space
}


# Call main function with all script arguments
main "$@"
