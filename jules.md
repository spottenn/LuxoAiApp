# LuxoAI Project: Core Directives & Context for AI Agents

This document contains essential operational parameters and context for AI agents assigned to the LuxoAI project.

## 1. Core Objective

Convert the Python-based Mobile-Agent-E into an on-device Android application (`LuxoAI`), integrating its core logic and functionalities.

## 2. Critical Repository Paths

*   **`LuxoAI/`**: Android application project.
    *   `app/`: Main Android application module (Java/Kotlin, XML/Compose).
    *   `build.gradle.kts`, `settings.gradle.kts`: Gradle build configuration. Chaquopy (Python integration) is configured here.
*   **`Resources/`**: Contains project resources.
    *   `environment_summary_report.md`: Overview of the execution environment.
    *   `planning/tasks/`: Detailed Markdown task specifications (e.g., `epic_1_task_1_1.md`). **Strictly adhere to the assigned task file.**
*   **`Mobile-Agent-E/`**: Legacy Python desktop agent codebase.
    *   `MobileAgentE/`: Core Python agent logic (control, OCR, model interaction). Source OCR models reside here.
    *   `requirements.txt`: Python dependencies for the legacy agent.

## 3. Target System Architecture

*   **Host Application**: Android App (`LuxoAI`).
    *   **UI**: Implement minimal GUI for task input.
    *   **Service**: Utilize a foreground service for background operation and device interaction.
    *   **Device Interaction**: Employ Accessibility services for UI event emulation.
    *   **Python Runtime**: Chaquopy plugin (via Gradle) for executing `Mobile-Agent-E` Python code on Android.
    *   **SDK Versions**: Min/target Android SDKs are defined in `LuxoAI/build.gradle.kts`. Do not alter without explicit instruction.
*   **Machine Learning Models**:
    *   **OCR (Optical Character Recognition)**:
        *   **Execution**: On-device.
        *   **Source**: Utilize existing model/code from `Mobile-Agent-E/`.
        *   **Performance Mandate**: Average inference < 1s; hard maximum 10s. Enforced by CI.
    *   **Grounding DINO (Vision Model)**:
        *   **Execution**: Remote via Replicate API.
    *   **LLM (Planning)**:
        *   **Execution**: Remote via designated external APIs (e.g., OpenAI, Anthropic).

## 4. Development & CI Protocol

*   **Environment**: Headless Linux.
*   **Setup**: Refer to `epic_1_task_1_1.md` for environment setup script.
*   **Build System**: Gradle for `LuxoAI`.
*   **Testing Rig**:
    *   **Primary**: Android emulator within CI.
    *   **Auxiliary (Conditional)**: Firebase Test Lab (if per-run cost <= $0.15).
    *   **Required Coverage**: Unit, integration, and end-to-end tests.
*   **Secrets Management**:
    *   **ABSOLUTE DIRECTIVE**: **No hardcoded secrets in the repository.**
    *   **CI (GitHub Actions)**: Inject via GitHub Actions Secrets as environment variables.
    *   **Local/Jules VM**: Runtime injection mechanism defined in `epic_1_task_1_5.md`. Adhere to this standard.

## 5. Operational Guardrails

*   **Safety Protocol**: For actions with potential user impact (e.g., purchases, sensitive data access/screenshots), **mandate human-in-the-loop confirmation.**
*   **Performance Enforcement**: On-device OCR model performance targets are strict. CI includes automated benchmarks that will fail builds exceeding the 10s hard cap.

## 6. Task Execution Protocol

Upon assignment of a task (e.g., `LuxoAI/planning/tasks/epic_X_task_Y_Z.md`):

1.  **Internalize Task File**: Parse and comprehend all details within the specified Markdown task file. This is your primary source of truth for the task.
    *   Focus on: **Background**, **Acceptance Criteria**, **Definition of Done**.
    *   Verify all **Dependencies** are met before proceeding.
2.  **Implement Solution**: Develop code, tests, and documentation as per task requirements.
3.  **Validate rigorously**: Confirm all acceptance criteria are satisfied. Ensure all existing and new tests pass.
4.  **Commit Artifacts**:
    *   Employ clear, structured commit messages.
    *   Prefix messages with type (e.g., `feat:`, `fix:`, `test:`, `docs:`).
    *   Reference the full task filename in the commit body or subject.
