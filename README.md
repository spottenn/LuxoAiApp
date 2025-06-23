# LuxoAI Project

Welcome to the LuxoAI project! This project aims to convert the Python-based Mobile-Agent-E into an on-device Android application (`LuxoAI`), integrating its core logic and functionalities.

## Modules

*   **`LuxoAI/`**: Contains the Android application project.
    *   The app uses Chaquopy for Python integration.
*   **`Mobile-Agent-E/`**: The legacy Python desktop agent codebase. Core logic for OCR, UI interaction, and model communication originates here.
*   **`Resources/`**: Project-related resources, including planning documents, task definitions, and scripts.
    *   `Resources/planning/tasks/`: Detailed task specifications.
    *   `Resources/scripts/`: Utility and setup scripts.
*   **`jules.md`**: Core directives and context for AI agents working on this project. **All contributors (human or AI) must read this.**

## Getting Started

1.  **Familiarize yourself with `jules.md`**: This document contains crucial information about the project architecture, development protocols, and operational guardrails.
2.  **Environment Setup**:
    *   For general development and Jules VM setup, refer to the script `Resources/scripts/setup_jules_env.sh`.
    *   Specific task requirements might have additional setup notes (e.g., `epic_1_task_1_1.md`).
3.  **Secrets Management**:
    *   API keys and other sensitive credentials are required for development and interacting with external services (OpenAI, Replicate, etc.).
    *   **Never commit secrets directly to the repository.**
    *   For detailed instructions on how to set up and manage secrets for local development (including Jules VMs and Android Studio) and CI/CD, please refer to:
        *   [`Resources/SECRETS.md`](Resources/SECRETS.md)
        *   [`jules_startup_script.md`](Resources/jules_startup_script.md) (for Jules VM specific startup)
        *   `.env.example` (for a template of required environment variables)

## Building the Android App (`LuxoAI`)

*   The Android app is located in the `LuxoAI/` directory.
*   It is built using Gradle. Ensure you have a compatible JDK (see `jules.md` or `Resources/scripts/setup_jules_env.sh` for details) and the Android SDK configured.
*   From the `LuxoAI/` directory:
    *   To build: `./gradlew build`
    *   To run unit tests: `./gradlew test`
    *   To install on a connected device/emulator: `./gradlew installDebug` (or `installRelease`)

## Contributing

*   Follow the task execution protocol outlined in `jules.md`.
*   Ensure all code changes are accompanied by relevant tests.
*   Adhere to commit message conventions (e.g., `feat:`, `fix:`, `docs:`).

## Key Technologies

*   Android (Java/Kotlin)
*   Python (via Chaquopy)
*   Gradle
*   GitHub Actions for CI
*   Machine Learning Models (OCR, Vision, LLM) - see `jules.md` for details on execution environments.

---

*This `README.md` is a work in progress and will be updated as the project evolves.*