#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define pinned versions
# Using OpenJDK 17 as required by the current Android Gradle Plugin version in the project.
# For SDK tools, see https://developer.android.com/studio#command-tools
# For Gradle, see https://gradle.org/releases/
JAVA_VERSION="17"
SDK_TOOLS_VERSION="10406996" # Example version for commandlinetools-linux-10406996_latest.zip
GRADLE_VERSION="8.4" # Example version, ensure compatibility with AGP

# Directories
INSTALL_DIR="/opt"
ANDROID_HOME_DIR="${INSTALL_DIR}/android-sdk"
JAVA_HOME_DIR="" # Will be set after Java installation
GRADLE_HOME_DIR="${INSTALL_DIR}/gradle-${GRADLE_VERSION}"

# --- Helper Functions ---
is_command_available() {
    command -v "$1" >/dev/null 2>&1
}

is_java_installed() {
    if is_command_available java; then
        local current_java_version_output
        current_java_version_output=$(java -version 2>&1)
        # Check if the output contains "openjdk version "17." (or the currently set JAVA_VERSION)
        if [[ "$current_java_version_output" == *"openjdk version \"${JAVA_VERSION}."* ]]; then
            echo "Java ${JAVA_VERSION} is already installed."
            local java_path_from_alternatives
            # Use grep "java-${JAVA_VERSION}-openjdk" to be generic
            java_path_from_alternatives=$(update-alternatives --list java | grep "java-${JAVA_VERSION}-openjdk" || true)

            if [ -n "$java_path_from_alternatives" ] && [ -x "$java_path_from_alternatives" ]; then
                JAVA_HOME_DIR=$(dirname "$(dirname "$java_path_from_alternatives")")
                echo "Found JAVA_HOME for existing OpenJDK ${JAVA_VERSION} at ${JAVA_HOME_DIR}"
                return 0 # True
            elif [ -d "/usr/lib/jvm/java-${JAVA_VERSION}-openjdk-amd64" ]; then # Fallback
                JAVA_HOME_DIR="/usr/lib/jvm/java-${JAVA_VERSION}-openjdk-amd64"
                echo "Found JAVA_HOME for existing OpenJDK ${JAVA_VERSION} (fallback) at ${JAVA_HOME_DIR}"
                return 0 # True
            else
                echo "Java ${JAVA_VERSION} is installed, but could not determine JAVA_HOME automatically."
                return 1 # Consider it not fully configured
            fi
        else
            echo "A Java version is installed, but it's not OpenJDK ${JAVA_VERSION}."
            echo "Detected version: $current_java_version_output"
            return 1 # False
        fi
    else
        echo "Java command not found."
        return 1 # False
    fi
}

is_sdk_installed() {
    if [ -d "${ANDROID_HOME_DIR}/cmdline-tools/latest" ] && [ -x "${ANDROID_HOME_DIR}/cmdline-tools/latest/bin/sdkmanager" ]; then
        echo "Android SDK command-line tools seem to be installed at ${ANDROID_HOME_DIR}."
        return 0 # True
    else
        echo "Android SDK command-line tools not found at ${ANDROID_HOME_DIR}."
        return 1 # False
    fi
}

is_gradle_installed() {
    if [ -d "${GRADLE_HOME_DIR}" ] && [ -x "${GRADLE_HOME_DIR}/bin/gradle" ]; then
        echo "Gradle ${GRADLE_VERSION} seems to be installed at ${GRADLE_HOME_DIR}."
        return 0 # True
    else
        echo "Gradle ${GRADLE_VERSION} not found at ${GRADLE_HOME_DIR}."
        return 1 # False
    fi
}

# --- Installation Functions ---

install_java() {
    echo "Installing Java (OpenJDK ${JAVA_VERSION})..."
    sudo apt-get update -y
    # Use the JAVA_VERSION variable for the package name
    sudo apt-get install -y "openjdk-${JAVA_VERSION}-jdk"

    # Find and set JAVA_HOME
    local java_path_from_alternatives
    java_path_from_alternatives=$(update-alternatives --list java | grep "java-${JAVA_VERSION}-openjdk" || true)

    if [ -n "$java_path_from_alternatives" ] && [ -x "$java_path_from_alternatives" ]; then
        JAVA_HOME_DIR=$(dirname "$(dirname "$java_path_from_alternatives")")
        echo "Found OpenJDK ${JAVA_VERSION} at ${java_path_from_alternatives}"
        echo "JAVA_HOME set to ${JAVA_HOME_DIR}"
    elif [ -d "/usr/lib/jvm/java-${JAVA_VERSION}-openjdk-amd64" ]; then # Fallback
        JAVA_HOME_DIR="/usr/lib/jvm/java-${JAVA_VERSION}-openjdk-amd64"
        echo "JAVA_HOME set to fallback /usr/lib/jvm/java-${JAVA_VERSION}-openjdk-amd64"
    else
        echo "ERROR: Could not determine JAVA_HOME for OpenJDK ${JAVA_VERSION} after installation."
        echo "Output of 'update-alternatives --list java':"
        update-alternatives --list java || true
        echo "Please set JAVA_HOME manually or check installation."
        exit 1
    fi

    export JAVA_HOME="${JAVA_HOME_DIR}"
    # Prepend to PATH to ensure our Java version is used
    export PATH="${JAVA_HOME_DIR}/bin:${PATH}"
    echo "Java installation process complete. Verifying version..."
    java -version || echo "Java version command failed but continuing."
    echo "Java version check done."
}

install_android_sdk_tools() {
    echo "Installing Android SDK command-line tools version ${SDK_TOOLS_VERSION}..."
    if [ -z "$JAVA_HOME" ] || ! is_command_available java; then
        echo "Error: JAVA_HOME is not set or Java is not installed. Please install Java first."
        exit 1
    fi

    sudo mkdir -p "${ANDROID_HOME_DIR}"
    cd /tmp # Use /tmp for downloads to save space on the main filesystem

    # Download SDK tools
    # The URL format is generally: https://dl.google.com/android/repository/commandlinetools-linux-${VERSION}_latest.zip
    SDK_TOOLS_URL="https://dl.google.com/android/repository/commandlinetools-linux-${SDK_TOOLS_VERSION}_latest.zip"
    echo "Downloading SDK tools from ${SDK_TOOLS_URL}..."
    wget -q "${SDK_TOOLS_URL}" -O sdk-tools.zip

    # Extract to a temporary location first, then move to the final cmdline-tools/latest path
    # This is the structure required by Android SDK: $ANDROID_HOME/cmdline-tools/latest/
    # The zip file typically extracts to a directory like `cmdline-tools`
    unzip -q sdk-tools.zip -d sdk-temp

    # The unzipped folder might be just 'cmdline-tools'. We need to place its contents into $ANDROID_HOME_DIR/cmdline-tools/latest
    # Create the target directory structure
    sudo mkdir -p "${ANDROID_HOME_DIR}/cmdline-tools/latest"
    # Move the contents of the unzipped 'cmdline-tools' (or similar) directory
    # to the 'latest' directory.
    # Example: if sdk-temp/cmdline-tools contains bin/, lib/, etc.
    # we move them to $ANDROID_HOME_DIR/cmdline-tools/latest/
    sudo mv sdk-temp/cmdline-tools/* "${ANDROID_HOME_DIR}/cmdline-tools/latest/"

    # Clean up
    rm sdk-tools.zip
    rm -rf sdk-temp

    export ANDROID_HOME="${ANDROID_HOME_DIR}"
    # Add SDK tools to PATH (both platform-tools and cmdline-tools/latest/bin)
    export PATH="${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools:${PATH}"

    echo "Android SDK command-line tools installation complete."
    echo "ANDROID_HOME set to ${ANDROID_HOME}"

    # Accept licenses - this is crucial for CI environments
    # Use yes to automatically accept all licenses
    echo "Accepting SDK licenses..."
    # Need to ensure sdkmanager is executable and JAVA_HOME is correctly picked up
    # Sometimes sdkmanager needs specific Java version.
    # The `yes` command might not work if sdkmanager prompts in a more complex way.
    # Ensure JAVA_HOME is explicitly passed if sdkmanager doesn't find it.
    yes | sudo JAVA_HOME="${JAVA_HOME_DIR}" "${ANDROID_HOME}/cmdline-tools/latest/bin/sdkmanager" --licenses > /dev/null || echo "License acceptance may have had issues, check logs if build fails."

    # Install platform-tools, and a recent platform and build-tools version that the project might need.
    # The build log indicated a need for build-tools;35.0.0 and platforms;android-35.
    echo "Installing core SDK components: platform-tools, build-tools;35.0.0, platforms;android-35..."
    sudo JAVA_HOME="${JAVA_HOME_DIR}" "${ANDROID_HOME}/cmdline-tools/latest/bin/sdkmanager" \
        "platform-tools" \
        "build-tools;35.0.0" \
        "platforms;android-35" > /dev/null || echo "Core SDK component installation may have had issues. Check build logs if problems persist."

    # Ownership will be handled after the main SDK setup block
    echo "Android SDK setup finished."
}

install_gradle() {
    echo "Installing Gradle version ${GRADLE_VERSION}..."
    cd /tmp
    GRADLE_URL="https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip"
    echo "Downloading Gradle from ${GRADLE_URL}..."
    wget -q "${GRADLE_URL}" -O gradle.zip

    sudo mkdir -p "${INSTALL_DIR}" # Ensure /opt exists
    # Use sudo for unzipping to /opt
    sudo unzip -q gradle.zip -d "${INSTALL_DIR}" # Extracts to /opt/gradle-X.Y
    # The extracted folder is gradle-${GRADLE_VERSION}

    # No need to move, it's already extracted to the correct GRADLE_HOME_DIR path
    # sudo mv "/opt/gradle-${GRADLE_VERSION}" "${GRADLE_HOME_DIR}"

    rm gradle.zip

    export GRADLE_HOME="${GRADLE_HOME_DIR}"
    export PATH="${GRADLE_HOME}/bin:${PATH}"

    echo "Gradle ${GRADLE_VERSION} installation complete."
    echo "GRADLE_HOME set to ${GRADLE_HOME}"
    gradle -v
}

# --- Main Script ---

echo "Starting Android Build Environment Setup..."
echo "Disk space before installation:"
df -h /


# 1. Install Java
if ! is_java_installed; then
    install_java
else
    # Ensure JAVA_HOME and PATH are set if already installed
    export JAVA_HOME="${JAVA_HOME_DIR}" # Relies on is_java_installed setting it
    if [ -z "${JAVA_HOME_DIR}" ]; then # If it wasn't set by is_java_installed
        echo "Warning: Java is installed but JAVA_HOME_DIR could not be determined. Trying common paths."
        # Attempt to find JAVA_HOME again or use a default
        if [ -d "/usr/lib/jvm/java-11-openjdk-amd64" ]; then
            JAVA_HOME_DIR="/usr/lib/jvm/java-11-openjdk-amd64"
        elif [ -d "/usr/lib/jvm/java-11-openjdk" ]; then # For other distros
             JAVA_HOME_DIR="/usr/lib/jvm/java-11-openjdk"
        else
            echo "Cannot find a suitable Java 11 installation. Please check."
            # Fallback to hoping 'java' in PATH is sufficient
        fi
        export JAVA_HOME="${JAVA_HOME_DIR}"
    fi
    export PATH="${JAVA_HOME_DIR}/bin:${PATH}"
    echo "Using existing Java installation from ${JAVA_HOME_DIR}"
    java -version
fi

# 2. Install Android SDK command-line tools
if ! is_sdk_installed; then
    install_android_sdk_tools
else
    export ANDROID_HOME="${ANDROID_HOME_DIR}"
    export PATH="${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools:${PATH}"
    echo "Using existing Android SDK tools from ${ANDROID_HOME}"
    # Even if SDK is existing, ensure critical components are attempted to be installed by root first
    # (in case they are missing from a partial previous setup but base dir exists)
    echo "Verifying/Installing core SDK components with sudo for existing SDK directory..."
    sudo JAVA_HOME="${JAVA_HOME_DIR}" "${ANDROID_HOME}/cmdline-tools/latest/bin/sdkmanager" \
        "platform-tools" \
        "build-tools;35.0.0" \
        "platforms;android-35" > /dev/null || echo "Sudo SDK component installation for existing SDK had issues or components already present."
fi

# Ensure ANDROID_HOME is writable by the current user
if [ -d "${ANDROID_HOME_DIR}" ]; then
    echo "Ensuring ${ANDROID_HOME_DIR} is writable by $(whoami)..."
    sudo chown -R "$(whoami)" "${ANDROID_HOME_DIR}"

    # Now, try to install/update required packages as the current user.
    # This ensures Gradle can also manage these if needed later.
    echo "Verifying/Installing core SDK components as $(whoami)..."
    # Ensure sdkmanager is in PATH for the current user session
    PATH="${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools:${PATH}" \
    "${ANDROID_HOME}/cmdline-tools/latest/bin/sdkmanager" \
        "platform-tools" \
        "build-tools;35.0.0" \
        "platforms;android-35" > /dev/null || echo "User-level SDK component installation had issues or components already present."
else
    echo "Warning: ANDROID_HOME (${ANDROID_HOME_DIR}) does not exist, skipping chown and user-level sdkmanager calls."
fi


# 3. Install Gradle (Optional, as gradlew will be used, but good for consistency)
# The project's gradlew should ideally be used, but installing a system Gradle can be a fallback
# or used for other Gradle tasks if needed.
# For this script, we'll ensure it's available if we decide to use it over ./gradlew directly for some reason.
# However, for building the Android app, ./gradlew is preferred.
# We can skip this if we strictly use ./gradlew to save space.
# For now, let's install it for completeness of the "environment setup" task.
if ! is_gradle_installed; then
    install_gradle
else
    export GRADLE_HOME="${GRADLE_HOME_DIR}"
    export PATH="${GRADLE_HOME}/bin:${PATH}"
    echo "Using existing Gradle installation from ${GRADLE_HOME}"
    # gradle -v # Verify version if needed
fi


echo "--- Environment Variables ---"
echo "JAVA_HOME=${JAVA_HOME}"
echo "ANDROID_HOME=${ANDROID_HOME}"
echo "GRADLE_HOME=${GRADLE_HOME}"
echo "PATH=${PATH}"
echo "-----------------------------"

echo "Setup script finished. Environment should be ready for Android builds."
echo "Disk space after installation:"
df -h /

echo "--- Starting LuxoAI Build and Test ---"

# Navigate to the project root relative to this script's location or assume a known path
# This script is in LuxoAI/scripts/, so project root is one level up.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="${SCRIPT_DIR}/.."

cd "${PROJECT_ROOT}"
echo "Changed directory to $(pwd)"

# Ensure gradlew is executable
if [ -f "./gradlew" ]; then
    chmod +x ./gradlew
else
    echo "ERROR: gradlew not found in ${PROJECT_ROOT}. Cannot proceed with build."
    exit 1
fi

# Perform a clean build
echo "Running './gradlew clean build'..."
# Pass JAVA_HOME explicitly to gradlew if it might not pick it up from the environment
# This is good practice in CI scripts.
if ./gradlew clean build -Dorg.gradle.java.home="${JAVA_HOME_DIR}"; then
    echo "Build successful."
else
    echo "ERROR: Build failed."
    exit 1
fi

# Execute unit tests
echo "Running './gradlew test'..."
if ./gradlew test -Dorg.gradle.java.home="${JAVA_HOME_DIR}"; then
    echo "Tests executed successfully."
else
    echo "ERROR: Tests failed or could not be executed."
    # Depending on policy, this might not be a fatal error for the script itself,
    # but it indicates a problem with the project's tests.
    # For this task, failing tests should be reported.
    exit 1
fi

echo "--- LuxoAI Build and Test Complete ---"
