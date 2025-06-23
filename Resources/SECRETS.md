# Managing Secrets for LuxoAI Development

This document outlines how to manage API keys and other sensitive credentials (secrets) for the LuxoAI project, covering local development environments (including Jules VMs and Android Studio) and CI/CD pipelines via GitHub Actions.

**It is crucial that actual secret values are NEVER committed to the Git repository.**

## 1. Overview of Secret Types

The primary secrets you will need are:

*   `OPENAI_API_KEY`: For accessing OpenAI's language models.
*   `REPLICATE_API_TOKEN`: For accessing models hosted on Replicate (e.g., Grounding DINO).
*   `ANTHROPIC_API_KEY`: (If used) For accessing Anthropic's language models.

Refer to the `.env.example` file in the project root for an up-to-date list of expected secret keys.

## 2. Local Development Setup

There are a few scenarios for local development:

### a. General Python Scripts / Non-Android Context (e.g., `Mobile-Agent-E` utilities)

*   **Method**: Use a `.env` file.
*   **Steps**:
    1.  Create a file named `.env` in the **root directory** of the project.
    2.  Copy the contents of `.env.example` into your new `.env` file.
    3.  Replace the placeholder values with your actual API keys.
        ```dotenv
        OPENAI_API_KEY="sk-yourActualOpenAIKey..."
        REPLICATE_API_TOKEN="r8_yourActualReplicateToken..."
        # ANTHROPIC_API_KEY="yourActualAnthropicKey..."
        ```
*   **Git**: The `.env` file is already listed in the root `.gitignore` and should not be committed.

### b. Jules VM Environment

*   **Method**: Use a VM startup script to set environment variables.
*   **Steps**:
    1.  Refer to the `jules_startup_script.md` file in the project root.
    2.  This file contains a bash script template. Copy this template.
    3.  In your Jules VM configuration UI, paste the script into the "startup script" section.
    4.  **Crucially, edit the script within the VM configuration to replace placeholder keys (e.g., `YOUR_OPENAI_KEY_HERE`) with your actual secret values.**
    5.  Save the VM configuration.
*   **How it works**: The startup script will export the secrets as environment variables. The `Resources/scripts/setup_jules_env.sh` script (called by the startup script) and subsequent Gradle builds will then be able to access these environment variables.

### c. Android Studio / Local Gradle Builds for `LuxoAI`

*   **Method**: Use a `local.properties` file.
*   **Steps**:
    1.  Create a file named `local.properties` in the **root directory** of the project (i.e., at the same level as `LuxoAI/`, `Mobile-Agent-E/`, etc.).
    2.  Add your API keys to this file in the format `key=value`:
        ```properties
        OPENAI_API_KEY=sk-yourActualOpenAIKey...
        REPLICATE_API_TOKEN=r8_yourActualReplicateToken...
        # ANTHROPIC_API_KEY=yourActualAnthropicKey...
        ```
*   **Git**: `local.properties` is already listed in the root `.gitignore` and `LuxoAI/.gitignore` and should not be committed.
*   **How it works**: The `LuxoAI/app/build.gradle.kts` file is configured to read secrets from environment variables first, and then fall back to this `local.properties` file if the environment variables are not set.

## 3. CI/CD via GitHub Actions

*   **Method**: Use GitHub Encrypted Secrets.
*   **Steps**:
    1.  In your GitHub repository, go to `Settings` > `Secrets and variables` > `Actions`.
    2.  Click `New repository secret` for each secret you need to add (e.g., `OPENAI_API_KEY`, `REPLICATE_API_TOKEN`).
    3.  The name of the secret should match the environment variable key expected by the application (e.g., `OPENAI_API_KEY`).
    4.  Paste the actual secret value.
*   **How it works**: The `.github/workflows/android.yml` workflow file is configured to pass these GitHub secrets as environment variables to the build job. Gradle then picks up these environment variables.

## 4. Accessing Secrets in the Android Application (`LuxoAI`)

Once the secrets are correctly provided to the Gradle build process (either via environment variables or `local.properties`), they are compiled into the `BuildConfig` class.

You can access them in your Java/Kotlin code within the `LuxoAI` app like this:

```kotlin
import com.spottenn.luxoai.BuildConfig

// ... inside your Android component (Activity, Service, ViewModel, etc.)
val apiKey = BuildConfig.OPENAI_API_KEY
val replicateToken = BuildConfig.REPLICATE_API_TOKEN
```

**Important Security Note for Production Releases:**
Embedding API keys directly into `BuildConfig` means they are compiled into your APK. While convenient for development, this can be a security risk for production applications as APKs can be decompiled. For a production release, consider more secure strategies such as:
*   Fetching keys from a secure, dedicated backend service at runtime.
*   Using server-side operations for API calls that require sensitive keys.
*   Employing obfuscation techniques (though this is not foolproof).

This setup prioritizes ease of development and CI integration. Always reassess secret management strategies before a public release.
