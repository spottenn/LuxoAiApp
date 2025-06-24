# Jules VM Startup Script Configuration

This document provides a template for a startup script to be used in Jules Virtual Machines. This script sets up necessary environment variables for API keys and then runs the main environment setup script for the LuxoAI project.

**Instructions:**

1.  Copy the bash script block below.
2.  Paste it into the "Initial Setup" section of your Jules repo configuration UI.
3.  **IMPORTANT:** Replace the placeholder values (e.g., `YOUR_OPENAI_KEY_HERE`, `YOUR_REPLICATE_TOKEN_HERE`) with your actual secret API keys.
4.  Save the VM configuration. On the next VM startup, this script will execute.

```bash
#!/bin/bash
set -euxo pipefail

echo "--- Starting Custom Jules VM Startup Script ---"

# --- BEGIN User-configurable secrets ---
# !! IMPORTANT !!
# Replace the placeholder values below with your actual secret keys.

export OPENAI_API_KEY="YOUR_OPENAI_KEY_HERE"
export REPLICATE_API_TOKEN="YOUR_REPLICATE_TOKEN_HERE"
# Add other environment variables for secrets as needed:
# export ANOTHER_API_KEY="YOUR_OTHER_KEY_HERE"

# --- BEGIN Google Cloud Credentials for Gradle Cache ---
# !! IMPORTANT !!
# Replace the placeholder JSON below with the actual content of your Google Cloud service account key file.
# This key is used by Gradle to authenticate with Google Cloud Storage for build caching.
# Ensure the JSON is correctly formatted and pasted within the single quotes.
export GRADLE_SERVICE_ACCOUNT_JSON='{
  "type": "service_account",
  "project_id": "YOUR_PROJECT_ID",
  "private_key_id": "YOUR_PRIVATE_KEY_ID",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nYOUR_PRIVATE_KEY\\n-----END PRIVATE KEY-----\\n",
  "client_email": "YOUR_CLIENT_EMAIL",
  "client_id": "YOUR_CLIENT_ID",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "YOUR_CLIENT_X509_CERT_URL",
  "universe_domain": "googleapis.com"
}'

# Create a temporary directory for the credentials file and write the JSON to it.
# This directory and file will be created at runtime within the Jules VM.
GCP_CREDS_DIR="/tmp/gcp_creds"
GOOGLE_APPLICATION_CREDENTIALS_FILE="${GCP_CREDS_DIR}/gradle_service_account.json"

mkdir -p "$GCP_CREDS_DIR"

# Temporarily disable command printing to avoid logging secret content
set +x
echo "$GRADLE_SERVICE_ACCOUNT_JSON" > "$GOOGLE_APPLICATION_CREDENTIALS_FILE"
# Re-enable command printing
set -x

export GOOGLE_APPLICATION_CREDENTIALS="$GOOGLE_APPLICATION_CREDENTIALS_FILE"

echo "Google Cloud credentials for Gradle Cache have been configured."
# For security, avoid printing the actual keys to logs if possible in a production/shared environment.
# --- END Google Cloud Credentials for Gradle Cache ---

echo "Environment variables for secrets have been set."
# For security, avoid printing the actual keys to logs if possible in a production/shared environment.

# --- END User-configurable secrets ---

# --- Run the main project setup script ---
# This assumes the script is in the standard location within the cloned repository.
# Adjust the path if your project structure is different.
PROJECT_ROOT="/app" # Standard root for Jules
SETUP_SCRIPT_PATH="${PROJECT_ROOT}/scripts/setup_jules_env.sh"

if [ -f "$SETUP_SCRIPT_PATH" ]; then
  echo "Found setup script at $SETUP_SCRIPT_PATH. Executing..."
  # Ensure the script is executable, then run it
  chmod +x "$SETUP_SCRIPT_PATH"
  # You might want to pass arguments to the setup script if needed, e.g., --validate
  # For now, running without arguments.
  "$SETUP_SCRIPT_PATH"
  echo "Main setup script finished."
else
  echo "ERROR: Main setup script not found at $SETUP_SCRIPT_PATH."
  echo "Please ensure the repository is cloned correctly and the path is valid."
  # Optionally, exit with an error code if the setup script is critical
  # exit 1
fi

echo "--- Custom Jules VM Startup Script Finished ---"

```

**Explanation:**

*   `set -euxo pipefail`: Standard bash options for robust scripting (exit on error, undefined variable, pipe failure; print commands).
*   `export VAR_NAME="VALUE"`: This is how environment variables are set. The Android build system (Gradle) and other tools can then pick these up.
*   `chmod +x "$SETUP_SCRIPT_PATH"`: Ensures the setup script has execute permissions.
*   `"$SETUP_SCRIPT_PATH"`: Executes the main environment setup.

By using this startup script, you ensure that your sensitive API keys are available to your development environment within the Jules VM without hardcoding them into your repository or manually exporting them every session.
The main `setup_jules_env.sh` script will then prepare the Android SDK, Java, and other dependencies.
