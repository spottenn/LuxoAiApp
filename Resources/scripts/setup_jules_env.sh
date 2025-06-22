set -eux
cd /app
# export PIP_BREAK_SYSTEM_PACKAGES=1
# files=$(find . -maxdepth 2 -type f -wholename "*requirements*.txt") && python -m pip install $(echo "$files" | xargs -I {{}} echo -r {{}}) || true

#!/bin/bash
set -euxo pipefail

# --- Configuration ---
CMDLINE_TOOLS_VERSION="13114758"
CMDLINE_TOOLS_URL="https://dl.google.com/android/repository/commandlinetools-linux-${CMDLINE_TOOLS_VERSION}_latest.zip"
ANDROID_HOME_DIR="$HOME/android_sdk"
JAVA_HOME_DIR="" # Will be determined based on pre-installed Java

# Android SDK components
PLATFORM_VERSION="android-35"
BUILD_TOOLS_VERSION="35.0.0"

# Command line options
VALIDATE_BUILD=true

# --- Set Python ---
set_python() {
  echo "--- Setting Python   3.10 globally ---"
  pyenv global 3.10.18
  echo "Python version set globally to:"
  python --version
  pip --version
}
# --- Parse Command Line Arguments ---
parse_arguments() {
  while [[ $# -gt 0 ]]; do
    case $1 in
      --validate)
        VALIDATE_BUILD=true
        shift
        ;;
      -h|--help)
        echo "Usage: $0 [--validate] [--help]"
        echo ""
        echo "Options:"
        echo "  --validate    Run the actual build and tests (default: setup environment only)"
        echo "  --help        Show this help message"
        exit 0
        ;;
      *)
        echo "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
    esac
  done
}


# --- Helper Functions ---
ensure_dir_exists() {
  if [ ! -d "$1" ]; then
    mkdir -p "$1"
    echo "Created directory: $1"
  else
    echo "Directory already exists: $1"
  fi
}

check_command_exists() {
  if command -v "$1" &> /dev/null; then
    echo "$1 is available in PATH."
    return 0
  else
    echo "$1 is NOT available in PATH."
    return 1
  fi
}

# --- Main Functions ---

setup_java() {
  echo "--- Setting up Java ---"
  # Try to find pre-installed Java
  # Common locations for system Java or asdf/sdkman installations
  if [ -n "$JAVA_HOME" ] && [ -x "$JAVA_HOME/bin/java" ]; then
    JAVA_HOME_DIR="$JAVA_HOME"
  elif [ -L /usr/bin/java ] && readlink -f /usr/bin/java | grep -q "jdk"; then # RedHat alternatives
      JAVA_HOME_DIR=$(dirname $(dirname $(readlink -f /usr/bin/java)))
  elif [ -x "/usr/lib/jvm/java-21-openjdk-amd64/bin/java" ]; then # Common path for OpenJDK 21
      JAVA_HOME_DIR="/usr/lib/jvm/java-21-openjdk-amd64"
  elif [ -x "/opt/java/openjdk/bin/java" ]; then # Another common path
      JAVA_HOME_DIR="/opt/java/openjdk"
  else
      echo "ERROR: Could not automatically find a suitable pre-installed JDK 21. JAVA_HOME was '$JAVA_HOME'."
      echo "Please ensure JDK 21 is installed and JAVA_HOME is set, or modify this script."
      # As per environment report, OpenJDK 21 is pre-installed. This is a fallback.
      # If this script were to install Java, it would go here.
      # For now, we rely on the pre-installed version as per task and environment report.
      # If 'java' command works, try to infer JAVA_HOME more generically
      local java_path=$(command -v java)
      if [ -n "$java_path" ]; then
          # Resolve symlinks and go up two levels (bin -> parent_dir -> JAVA_HOME)
          java_path=$(readlink -f "$java_path")
          JAVA_HOME_DIR=$(dirname $(dirname "$java_path"))
          echo "Inferred JAVA_HOME_DIR as $JAVA_HOME_DIR from 'which java'"
      else
          echo "ERROR: 'java' command not found. Cannot infer JAVA_HOME."
          return 1
      fi
  fi

  if [ ! -d "$JAVA_HOME_DIR" ] || [ ! -x "$JAVA_HOME_DIR/bin/java" ]; then
    echo "ERROR: JAVA_HOME_DIR ('$JAVA_HOME_DIR') is not a valid JDK installation."
    return 1
  fi

  export JAVA_HOME="$JAVA_HOME_DIR"
  export PATH="$JAVA_HOME/bin:$PATH"
  echo "Using JAVA_HOME: $JAVA_HOME"
  java -version
  echo "Java setup complete."
}

setup_android_sdk() {
  echo "--- Setting up Android SDK ---"
  ensure_dir_exists "$ANDROID_HOME_DIR"

  # Check if cmdline-tools are already installed to a degree
  if [ -d "$ANDROID_HOME_DIR/cmdline-tools/latest/bin" ] && [ -x "$ANDROID_HOME_DIR/cmdline-tools/latest/bin/sdkmanager" ]; then
    echo "Android SDK command-line tools already appear to be in place."
    # This doesn't check the version, but for idempotency, we assume if 'latest' exists, it's good enough or managed externally.
    # A more robust check would verify the version of the tools or specific installed packages.
  else
    echo "Downloading Android SDK command-line tools..."
    local temp_zip_path="/tmp/cmdline-tools.zip"
    curl -Lo "$temp_zip_path" "$CMDLINE_TOOLS_URL"

    # Expected structure: cmdline-tools/LICENSE cmdline-tools/bin/ etc.
    # We want to extract it so that $ANDROID_HOME_DIR/cmdline-tools/latest exists
    local temp_extract_dir="/tmp/cmdline-tools-extract"
    ensure_dir_exists "$temp_extract_dir"
    unzip -q "$temp_zip_path" -d "$temp_extract_dir"

    # The zip extracts to a directory named 'cmdline-tools'. We need to move this
    # into $ANDROID_HOME_DIR/cmdline-tools and then rename to 'latest'
    ensure_dir_exists "$ANDROID_HOME_DIR/cmdline-tools"
    if [ -d "$ANDROID_HOME_DIR/cmdline-tools/latest" ]; then
        echo "Backing up existing $ANDROID_HOME_DIR/cmdline-tools/latest"
        mv "$ANDROID_HOME_DIR/cmdline-tools/latest" "$ANDROID_HOME_DIR/cmdline-tools/latest_$(date +%s)"
    fi
    mv "$temp_extract_dir/cmdline-tools" "$ANDROID_HOME_DIR/cmdline-tools/latest"

    rm "$temp_zip_path"
    rm -rf "$temp_extract_dir"
    echo "Android SDK command-line tools downloaded and extracted."
  fi

  export ANDROID_HOME="$ANDROID_HOME_DIR"
  # Newer tools prefer ANDROID_SDK_ROOT, but ANDROID_HOME is often still used/needed.
  export ANDROID_SDK_ROOT="$ANDROID_HOME_DIR"
  export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"

  echo "Updating/Installing SDK components..."
  # Accept licenses. This needs to be done before listing or installing packages if licenses haven't been accepted.
  # Note: `yes` might not work on all systems/sdkmanager versions if it expects specific phrases.
  # Add --sdk_root to be explicit, though ANDROID_HOME should be picked up.
  echo "Accepting Android SDK licenses..."
  yes | sdkmanager --licenses --sdk_root="$ANDROID_HOME" > /dev/null 2>&1 || echo "License acceptance may have had issues, continuing..."
  echo "Installing: platform-tools, $PLATFORM_VERSION, build-tools;$BUILD_TOOLS_VERSION"
  sdkmanager --install "platform-tools" "platforms;$PLATFORM_VERSION" "build-tools;$BUILD_TOOLS_VERSION" --sdk_root="$ANDROID_HOME"

  # Verify sdkmanager can list installed packages
  sdkmanager --list_installed --sdk_root="$ANDROID_HOME"
  echo "Android SDK setup complete."
}

setup_gradle() {
  echo "--- Setting up Gradle ---"
  # Gradle is pre-installed as per environment report (version 8.8)
  # This function will just verify it's available.
  if check_command_exists "gradle"; then
    echo "Gradle version:"
    gradle -v
  else
    echo "ERROR: Gradle command not found, but was expected to be pre-installed."
    # If this script were to install Gradle, it would go here.
    return 1
  fi
  echo "Gradle setup complete (using pre-installed)."
}

verify_environment() {
  echo "--- Verifying Environment ---"
  echo "JAVA_HOME: $JAVA_HOME"
  java -version

  echo "ANDROID_HOME: $ANDROID_HOME"
  echo "ANDROID_SDK_ROOT: $ANDROID_SDK_ROOT"
  sdkmanager --version || echo "sdkmanager not found or version check failed"

  echo "Gradle version:"
  gradle -v

  echo "PATH: $PATH"
  echo "Disk space:"
  df -h
  echo "Environment verification complete."
}

build_luxoai_app() {
  echo "--- Building LuxoAI App ---"
  if [ ! -d "LuxoAI" ]; then
    echo "ERROR: LuxoAI directory not found. Script must be run from the repository root."
    return 1
  fi
  cd LuxoAI

  # Ensure gradlew is executable
  if [ -f "./gradlew" ]; then
    chmod +x ./gradlew
    echo "Attempting build with ./gradlew"
    ./gradlew clean build -Dorg.gradle.jvmargs="-Xmx2048m -Dfile.encoding=UTF-8"
  elif check_command_exists "gradle"; then
    echo "Attempting build with system gradle"
    gradle clean build -Dorg.gradle.jvmargs="-Xmx2048m -Dfile.encoding=UTF-8"
  else
    echo "ERROR: Neither ./gradlew nor system gradle found."
    return 1
  fi

  echo "LuxoAI App build attempt finished."
  cd .. # Return to root
}

run_luxoai_tests() {
  echo "--- Running LuxoAI Unit Tests ---"
  if [ ! -d "LuxoAI" ]; then
    echo "ERROR: LuxoAI directory not found. Script must be run from the repository root."
    return 1
  fi
  cd LuxoAI

  # Placeholder for actual test execution
  # Check if placeholder test exists, if not, create one (as per task requirements)
  local test_file_path="app/src/test/java/com/spottenn/luxoai/PlaceholderUnitTest.kt"
  if [ ! -f "$test_file_path" ]; then
    echo "Placeholder unit test not found. Creating one..."
    mkdir -p "$(dirname "$test_file_path")"
    cat > "$test_file_path" << EOF
package com.spottenn.luxoai

import org.junit.Test
import org.junit.Assert.*

class PlaceholderUnitTest {
    @Test
    fun addition_isCorrect() {
        assertEquals(4, 2 + 2)
    }
}
EOF
    echo "Placeholder unit test created at $test_file_path"
  fi

  if [ -f "./gradlew" ]; then
    echo "Attempting tests with ./gradlew"
    ./gradlew test -Dorg.gradle.jvmargs="-Xmx1024m -Dfile.encoding=UTF-8"
  elif check_command_exists "gradle"; then
    echo "Attempting tests with system gradle"
    gradle test -Dorg.gradle.jvmargs="-Xmx1024m -Dfile.encoding=UTF-8"
  else
    echo "ERROR: Neither ./gradlew nor system gradle found for testing."
    return 1
  fi

  echo "LuxoAI App unit test execution attempt finished."
  cd .. # Return to root
}



main() {
  parse_arguments "$@"


  echo "Starting Android Build Environment Setup Script"
  if [ "$VALIDATE_BUILD" = true ]; then
    echo "Build validation enabled - will run actual build and tests"
  else
    echo "Build validation disabled - will only setup environment (use --validate to run build)"
  fi

  df -h

  set_python
  setup_java
  df -h

  setup_gradle
  df -h

  setup_android_sdk
  df -h

  verify_environment

  if [ "$VALIDATE_BUILD" = true ]; then
    build_luxoai_app
    run_luxoai_tests
    echo "Android Build Environment Setup Script finished successfully!"
  else
    echo "--- Skipping Build and Tests ---"
    echo "Environment setup complete. Use --validate option to run actual build and tests."
  fi

  echo "Final disk space:"
  df -h

}

# Run main function
main "$@"

