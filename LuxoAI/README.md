# LuxoAI Android Application

This directory contains the LuxoAI Android application.

## Development Setup

### Secrets Management

The application requires API keys and other secrets for various services (e.g., OpenAI, Replicate). These are managed using environment variables and are not committed to the repository.

**1. Local Development:**

*   **Create a `.env` file:**
    In the `LuxoAI/` directory (this directory), create a file named `.env`.
*   **Copy from example:**
    You can copy the structure from `LuxoAI/.env.example`.
    ```bash
    cp .env.example .env
    ```
*   **Fill in values:**
    Edit the `.env` file and replace the placeholder values with your actual secrets.
    ```
    OPENAI_API_KEY=sk-yourActualOpenAIKey...
    ANTHROPIC_API_KEY=sk-ant-yourActualAnthropicKey...
    REPLICATE_API_TOKEN=r8_yourActualReplicateToken...
    ```
*   **How it works:**
    The root `LuxoAI/build.gradle.kts` file will automatically load variables from this `.env` file if it exists and make them available to the build process. The `LuxoAI/app/build.gradle.kts` file then exposes these as `BuildConfig` fields, which can be accessed in the Android app's Java/Kotlin code (e.g., `BuildConfig.OPENAI_API_KEY`).
    Environment variables set in your shell (e.g., in your `~/.bashrc` or `~/.zshrc`) will take precedence over values in the `.env` file.

**2. CI/GitHub Actions:**

*   **Repository Secrets:**
    Secrets are injected into the GitHub Actions workflow as environment variables. These need to be configured in the GitHub repository settings:
    *   Go to your repository on GitHub.
    *   Navigate to `Settings` -> `Secrets and variables` -> `Actions`.
    *   Click `New repository secret` for each secret required by the project (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `REPLICATE_API_TOKEN`).
*   **Workflow Usage:**
    The `.github/workflows/main.yml` (or other relevant workflow files) will have an `env` block in the job steps to pass these secrets to the build commands:
    ```yaml
    jobs:
      build:
        runs-on: ubuntu-latest
        steps:
          - name: Build with Gradle
            env:
              OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
              ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
              REPLICATE_API_TOKEN: ${{ secrets.REPLICATE_API_TOKEN }}
            run: cd LuxoAI && ./gradlew build
    ```
    The Gradle scripts are configured to pick up these environment variables directly.

**Important:**
*   The `.env` file is listed in `LuxoAI/.gitignore` and should **never** be committed to the repository.
*   Always use the `.env.example` file as a template for required secrets.
---

Further instructions on building, testing, and contributing will be added here.
