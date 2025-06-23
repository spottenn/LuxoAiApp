# LuxoAI Project

Welcome to the LuxoAI project!

## Project Overview

The LuxoAI project is focused on transforming `Mobile-Agent-E`, a Python-based desktop agent, into a fully on-device Android application named `LuxoAI`. The core objective is to integrate `Mobile-Agent-E`'s logic and functionalities, enabling intelligent mobile task automation directly on Android devices.

**Key Architectural Features:**

*   **Host Application**: `LuxoAI` is an Android application that will provide a minimal user interface for task input and will utilize a foreground service for robust background operation.
*   **Python Integration**: [Chaquopy](https://chaquo.com/chaquopy/) is used to embed and execute the core Python logic from `Mobile-Agent-E` within the Android environment.
*   **Device Interaction**: The application will leverage Android's Accessibility services to emulate user interactions (e.g., taps, swipes, text input) for navigating and operating other applications.
*   **Machine Learning Models**:
    *   **On-Device OCR**: Optical Character Recognition will run locally on the device, utilizing models and code from the legacy `Mobile-Agent-E` project. Performance is critical, with a target of <1s average inference time.
    *   **Remote Vision & LLM**: More computationally intensive models, such as Grounding DINO for vision tasks and Large Language Models for planning, will be accessed via remote APIs (e.g., Replicate, OpenAI).

For a detailed, auto-generated visualization of the system's components and their interactions, please see the [Architecture Diagram](docs/ARCHITECTURE.md). This diagram is generated from the codebase and provides a snapshot of the Python agent and Android application structures.

## Modules

*   **`LuxoAI/`**: Contains the Android application project.
    *   The app uses Chaquopy for Python integration.
*   **`Mobile-Agent-E/`**: The legacy Python desktop agent codebase. Core logic for OCR, UI interaction, and model communication originates here.
*   **`resources/`**: Project-related resources, including planning documents, task definitions, and scripts.
    *   `docs/planning/tasks/`: Detailed task specifications.
    *   `scripts/`: Utility and setup scripts.
*   **`jules.md`**: Core directives and context for AI agents working on this project. **All contributors (human or AI) must read this.**

## Getting Started

1.  **Familiarize yourself with `jules.md`**: This document contains crucial information about the project architecture, development protocols, and operational guardrails.
2.  **Environment Setup**:
    *   For general development and Jules VM setup, refer to the script `scripts/setup_jules_env.sh`.
    *   Specific task requirements might have additional setup notes (e.g., `epic_1_task_1_1.md`).
3.  **Secrets Management**:
    *   API keys and other sensitive credentials are required for development and interacting with external services (OpenAI, Replicate, etc.).
    *   **Never commit secrets directly to the repository.**
    *   For detailed instructions on how to set up and manage secrets for local development (including Jules VMs and Android Studio) and CI/CD, please refer to:
        *   [`docs/SECRETS.md`](docs/SECRETS.md)
        *   [`jules_startup_script.md`](scripts/jules_startup_script.md) (for Jules VM specific startup)
        *   `.env.example` (for a template of required environment variables)

## Building the Android App (`LuxoAI`)

*   The Android app is located in the `LuxoAI/` directory.
*   It is built using Gradle. Ensure you have a compatible JDK (see `jules.md` or `scripts/setup_jules_env.sh` for details) and the Android SDK configured.
*   From the `LuxoAI/` directory:
    *   To build: `./gradlew build`
    *   To run unit tests: `./gradlew test`
    *   To install on a connected device/emulator: `./gradlew installDebug` (or `installRelease`)

## Contributing

For details on how to contribute to this project, including commit message conventions and code style guidelines, please see our **[Contributing Guidelines](docs/CONTRIBUTING.md)**.

A few key points:
*   Follow the task execution protocol outlined in `jules.md`.
*   Ensure all code changes are accompanied by relevant tests.

## Generating Architecture Documentation

To help understand the codebase structure, a script is provided to automatically generate an architecture overview. This script scans the Python agent code (`Mobile-Agent-E/MobileAgentE/`) and the Android app code (`LuxoAI/app/src/main/`) to identify key components and their relationships.

**How to run:**

1.  Ensure you have Python installed and are in the root directory of the project.
2.  Execute the script:
    ```bash
    python scripts/generate_architecture_docs.py
    ```
3.  This will generate/update the `docs/ARCHITECTURE.md` file. This file contains:
    *   A component diagram in PlantUML format.
    *   A textual summary of the identified components and their interactions.

**Purpose:**

The `resources/ARCHITECTURE.MD` file provides a high-level, auto-generated snapshot of the system's structure. It can be useful for:
*   New developers or agents trying to understand the project layout.
*   Visualizing dependencies between different parts of the system.
*   Tracking major components as the codebase evolves (by re-running the script).

Note: The analysis is based on static code analysis and may not capture all dynamic behaviors or a complete picture of every interaction. However, it serves as a good starting point for architectural exploration.

## Key Technologies

*   Android (Java/Kotlin)
*   Python (via Chaquopy)
*   Gradle
*   GitHub Actions for CI
*   Machine Learning Models (OCR, Vision, LLM) - see `jules.md` for details on execution environments.

---

*This `README.md` is a work in progress and will be updated as the project evolves.*