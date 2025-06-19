# LuxoAI Planning Tasks Backlog

This document tracks the granular tasks required for the development of LuxoAI. It is organized by epic and will be updated as the project progresses.

---
## Epic 1: Environment & CI Foundation

This epic focuses on establishing a robust and automated build, test, and deployment environment for the LuxoAI Android application.

---
### <!-- Task ID: ENV-001 --> Setup Android Build Environment Script

**Type:** `chore`
**Background:** To ensure consistent and reproducible Android builds, we need a script that automates the setup of the build environment on a headless Linux system. This script will handle the installation of the Android SDK and its dependencies. This is foundational for CI/CD.
**Acceptance Criteria:**
- [ ] Script successfully installs all necessary dependencies for Android SDK command-line tools (e.g., Java Development Kit, required libraries).
- [ ] Script downloads and installs a specified version of the Android SDK command-line tools.
- [ ] Script sets up required environment variables (e.g., `ANDROID_HOME`, `PATH` updates).
- [ ] Script can be run idempotently without errors on a clean Ubuntu LTS environment.
- [ ] Script includes basic error handling and provides informative output messages.
**Dependencies:** None
**Parallelizable?:** `yes`
**Suggested Labels:** `ci`, `android`, `build`, `linux`, `script`
**Effort Estimate:** M
**Definition of Done:** A Bash script (e.g., `scripts/setup_android_env.sh`) is committed to the repository. The script is documented with comments explaining each step and its usage.
<!-- Note: Consider if Docker is a better long-term solution, but a Bash script is a good starting point as per the epic. This task focuses on the core SDK installation. Emulator setup will be a separate task. -->
---
### <!-- Task ID: ENV-002 --> Android Emulator Setup and Management Script

**Type:** `chore`
**Background:** For automated testing, we need to programmatically create, launch, and manage Android Virtual Devices (AVDs). This script will handle emulator setup.
**Acceptance Criteria:**
- [ ] Script can create a new AVD with a specified system image and device definition.
- [ ] Script can launch an existing AVD in headless mode.
- [ ] Script can check the state of the emulator (e.g., booted, running).
- [ ] Script can gracefully shut down a running AVD.
- [ ] Script allows configuration of emulator options (e.g., screen size, memory).
**Dependencies:** `ENV-001` (Android SDK installed)
**Parallelizable?:** `yes` (once ENV-001 is complete)
**Suggested Labels:** `ci`, `android`, `emulator`, `test`, `script`
**Effort Estimate:** M
**Definition of Done:** A Bash script (e.g., `scripts/manage_android_emulator.sh`) is committed. The script is documented, and its functionality is verified.
<!-- This script will be crucial for running tests in the CI pipeline. It should be robust enough to handle common emulator issues. -->
---
### <!-- Task ID: ENV-003 --> Integrate Chaquopy into Gradle Build

**Type:** `feature`
**Background:** To enable Python code execution within the Android app, Chaquopy needs to be integrated into the Gradle build process. This involves configuring Gradle files and ensuring Python code can be bundled with the APK.
**Acceptance Criteria:**
- [ ] `build.gradle` (app level) is configured to use the Chaquopy plugin.
- [ ] Python source directory (e.g., `src/main/python`) is correctly configured.
- [ ] A simple Python script can be called from Android (Java/Kotlin) code.
- [ ] The APK builds successfully with Chaquopy, including Python runtime and scripts.
- [ ] Basic Python dependencies (if any for a simple test) are correctly packaged.
**Dependencies:** `ENV-001` (Basic Android project structure)
**Parallelizable?:** `yes`
**Suggested Labels:** `android`, `python`, `chaquopy`, `gradle`, `build`
**Effort Estimate:** M
**Definition of Done:** The Android project's Gradle files are updated to include Chaquopy. A sample "hello world" Python script is successfully executed from the Android app. Build artifacts include Python components.
<!-- This is a key step for enabling Python capabilities. Future tasks will depend on this integration. We should consider a small PoC to verify this. -->
---
### <!-- Task ID: ENV-004 --> GitHub Actions CI Workflow for Build and Test

**Type:** `chore`
**Background:** A CI workflow is needed to automate the build and test process on every push or pull request. This workflow will use the scripts created in previous tasks to set up the environment, build the APK, launch an emulator, and run tests.
**Acceptance Criteria:**
- [ ] GitHub Actions workflow is triggered on pushes to `main` and PRs to `main`.
- [ ] Workflow job checks out the correct version of the code.
- [ ] Workflow job uses `scripts/setup_android_env.sh` (or equivalent Docker setup) to prepare the build environment.
- [ ] Workflow job builds the Android APK using Gradle.
- [ ] Workflow job uses `scripts/manage_android_emulator.sh` to launch an emulator.
- [ ] Workflow job runs placeholder tests on the emulator (actual tests to be defined later).
- [ ] Workflow job reports build and test status (success/failure).
**Dependencies:** `ENV-001`, `ENV-002`, `ENV-003` (to have something meaningful to build and test)
**Parallelizable?:** `no` (depends on other tasks in this epic)
**Suggested Labels:** `ci`, `github-actions`, `android`, `build`, `test`, `automation`
**Effort Estimate:** L
**Definition of Done:** A `.github/workflows/android_ci.yml` file is committed. The workflow successfully completes a build and (placeholder) test run on a pushed commit.
<!-- This ties everything together. Initially, the "tests" might just be launching the app or a very simple UI test. -->
---
### <!-- Task ID: ENV-005 --> Secrets Management Design and Implementation

**Type:** `chore`
**Background:** The application will require API keys and other secrets. A secure method for managing these secrets is needed for both local development (Jules VMs) and CI (GitHub Actions). Secrets should never be committed to the repository.
**Acceptance Criteria:**
- [ ] Design document outlines the chosen secrets management strategy (e.g., env vars, `.env` files, GitHub Secrets).
- [ ] An example `.env.example` file is created in the repository, listing required secret keys without their values.
- [ ] `.gitignore` is updated to exclude actual `.env` files.
- [ ] Clear instructions are provided on how to set up secrets for local development.
- [ ] GitHub Actions workflow is configured to use GitHub Secrets to inject API keys at runtime.
- [ ] A placeholder mechanism in the app demonstrates accessing a secret (e.g., logging a masked version of a test key).
**Dependencies:** None (can be designed in parallel, implementation might depend on ENV-004 for CI part)
**Parallelizable?:** `yes` (design phase), `partial` (implementation)
**Suggested Labels:** `security`, `ci`, `devops`, `secrets`
**Effort Estimate:** M
**Definition of Done:** A secrets management strategy is documented. `.env.example` and `.gitignore` updates are committed. GitHub Actions workflow demonstrates successful injection and use of a test secret. Local setup instructions are clear.
<!-- This is critical for security. The chosen method should be simple yet effective. Environment variables are a common and good practice. -->
---

---
## Epic 2: Repo Audit & Architecture Doc

This epic focuses on understanding the current codebase and producing initial architectural documentation.

---
### <!-- Task ID: RAD-001 --> Python Code Structure Analysis and Documentation

**Type:** `documentation`
**Background:** To understand the existing Python backend, we need to analyze its structure, identify key components, and document their interactions. This will inform the architecture diagram.
**Acceptance Criteria:**
- [ ] Identify main Python modules and their primary responsibilities.
- [ ] Document key classes and functions, including their purpose and parameters.
- [ ] Map out dependencies between Python modules.
- [ ] Produce a textual description of the Python component's architecture.
- [ ] List any external Python libraries used and their roles.
**Dependencies:** Access to the current Python codebase.
**Parallelizable?:** `yes`
**Suggested Labels:** `documentation`, `python`, `architecture`, `audit`
**Effort Estimate:** M
**Definition of Done:** A Markdown document (e.g., `docs/python_architecture.md`) is committed, detailing the Python code structure, components, and dependencies.
<!-- This is a manual analysis task. Tools like `pyreverse` or `pydeps` might assist, but the core is understanding and documenting. -->
---
### <!-- Task ID: RAD-002 --> Android Stub Analysis and Interface Documentation

**Type:** `documentation`
**Background:** The Android application acts as a frontend. We need to understand its current capabilities, how it intends to interact with the Python backend (via Chaquopy), and document this interface.
**Acceptance Criteria:**
- [ ] Identify how the Android stub invokes or plans to invoke Python code.
- [ ] Document the data structures exchanged between Android (Java/Kotlin) and Python.
- [ ] Analyze any existing UI components in the Android stub relevant to Python interaction.
- [ ] Produce a textual description of the Android stub's relevant architectural aspects.
**Dependencies:** Access to the Android project stub. `ENV-003` might provide context if Chaquopy is already partially integrated.
**Parallelizable?:** `yes`
**Suggested Labels:** `documentation`, `android`, `architecture`, `interface`, `chaquopy`
**Effort Estimate:** S
**Definition of Done:** A section in the main architecture document or a separate file (e.g., `docs/android_interface.md`) details the Android stub's interaction points with the Python layer.
<!-- This task focuses on the bridge between Android and Python. -->
---
### <!-- Task ID: RAD-003 --> Auto-generate Initial Architecture Diagram and README Section

**Type:** `documentation`
**Background:** Based on the analysis from RAD-001 and RAD-002, create a visual representation of the architecture and a summary for the main README. The "auto-generate" aspect refers to using tools to help create diagrams from code if possible, or at least basing the diagram heavily on the documented code structure.
**Acceptance Criteria:**
- [ ] Select a suitable tool or format for the architecture diagram (e.g., PlantUML, Mermaid, or a simple manually drawn diagram committed as an image).
- [ ] Create a high-level architecture diagram showing the main components (Android app, Python layer, key modules within Python).
- [ ] Diagram illustrates primary data flows and interactions between components.
- [ ] Write a concise "Architecture" section for the main `README.md` that embeds or links to the diagram and provides a brief overview.
- [ ] The README section should explain how the Android app and Python components are intended to work together.
**Dependencies:** `RAD-001`, `RAD-002`
**Parallelizable?:** `no` (depends on the completion of analysis tasks)
**Suggested Labels:** `documentation`, `architecture`, `diagram`, `readme`
**Effort Estimate:** M
**Definition of Done:** An architecture diagram is created and stored in the `docs` folder. The main `README.md` is updated with an "Architecture" section that includes this diagram and a textual summary.
<!-- While the epic says "auto-generate", this might mean "tool-assisted" generation. For a minimal diagram, manual creation based on analysis is also fine. The key is to get a foundational document. -->
---

---
## Epic 3: Core Android App (MVP)

This epic covers the development of the Minimum Viable Product for the LuxoAI Android application, enabling basic user interaction and background operation.

---
### <!-- Task ID: APP-001 --> Minimal GUI for Task Input

**Type:** `feature`
**Background:** The core user interaction for the MVP is to input a task. This requires a simple GUI with a text field and a button to initiate the agent.
**Acceptance Criteria:**
- [ ] Main activity displays a single text input field.
- [ ] Main activity displays a "Start Agent" button.
- [ ] User can type a task description into the text field.
- [ ] Pressing the "Start Agent" button captures the text from the input field.
- [ ] (Placeholder) Action is triggered when the button is pressed (e.g., logs the task string, displays a Toast). Actual agent invocation will be a separate task.
**Dependencies:** Basic Android project setup (`ENV-001`).
**Parallelizable?:** `yes`
**Suggested Labels:** `android`, `ui`, `mvp`, `feature`
**Effort Estimate:** S
**Definition of Done:** An Android Activity with a text input field and a button is implemented. The button click retrieves the text and performs a placeholder action. UI layouts are defined in XML.
<!-- This is the primary entry point for the user. Keep it extremely simple for MVP. -->
---
### <!-- Task ID: APP-002 --> Android Foreground Service for Background Operation

**Type:** `feature`
**Background:** To allow LuxoAI to operate even when the main app UI is not visible, a Foreground Service is necessary. This service will host the core agent logic and maintain app liveliness.
**Acceptance Criteria:**
- [ ] A Foreground Service is implemented.
- [ ] The service starts when the "Start Agent" button is pressed.
- [ ] The service displays a persistent notification, as required for foreground services.
- [ ] The service can receive the task description from the main activity.
- [ ] The service remains running even if the main activity is closed.
- [ ] A mechanism exists to stop the service (e.g., from the notification or app UI).
**Dependencies:** `APP-001` (for triggering service start). `ENV-003` (Chaquopy for Python integration if agent logic is in Python).
**Parallelizable?:** `yes`, but integrates with APP-001.
**Suggested Labels:** `android`, `service`, `background`, `mvp`, `feature`
**Effort Estimate:** M
**Definition of Done:** An Android Foreground Service is implemented. It starts correctly, displays a notification, and can be stopped. The task string is passed to the service.
<!-- This is crucial for long-running tasks. The notification content can be basic for now. -->
---
### <!-- Task ID: APP-003 --> Accessibility Service for UI Interaction

**Type:** `feature`
**Background:** LuxoAI needs to interact with other applications and the Android system UI by simulating touch and keyboard events. An Accessibility Service is a robust way to achieve this.
**Acceptance Criteria:**
- [ ] An Android Accessibility Service is implemented and configured.
- [ ] User is guided to enable the Accessibility Service through system settings.
- [ ] The service can find UI elements on the screen (e.g., by ID, text, or content description).
- [ ] The service can perform basic actions on found UI elements (e.g., click, input text).
- [ ] (Placeholder) A simple test case demonstrates the service interacting with another app or system UI element (e.g., opening an app, clicking a button in settings).
**Dependencies:** `APP-002` (service to host/control the accessibility interactions).
**Parallelizable?:** `yes`
**Suggested Labels:** `android`, `accessibility`, `ui-automation`, `mvp`, `feature`
**Effort Estimate:** L
**Definition of Done:** An Accessibility Service is implemented. It can be enabled by the user and perform a basic UI interaction on another app or the system UI. Necessary permissions are declared.
<!-- This is a complex but powerful part of the app. Initial scope should be a simple proof-of-concept of interaction. Security and privacy implications of Accessibility Services should be kept in mind. -->
---

---
## Epic 4: Python Agent Embedding

This epic details the integration of the existing Python-based agent orchestrator into the Android application using Chaquopy.

---
### <!-- Task ID: EMBED-001 --> Adapt Python Orchestrator for Android Embedding

**Type:** `engineering`
**Background:** The existing desktop Python orchestrator needs to be evaluated and potentially modified to run within the Android environment via Chaquopy. This includes handling Android-specific constraints like file system access, resource limitations, and threading.
**Acceptance Criteria:**
- [ ] Identify parts of the Python orchestrator that are incompatible with Android (e.g., direct hardware access not available, GUI dependencies).
- [ ] Refactor or provide shims for incompatible OS-level interactions.
- [ ] Ensure Python dependencies are compatible with Chaquopy and packageable in Android.
- [ ] Python orchestrator can be initialized from a simple Python script run by Chaquopy.
- [ ] Basic orchestrator functions (e.g., task processing loop start/stop) are callable.
**Dependencies:** `ENV-003` (Chaquopy integrated), `RAD-001` (Python code analysis).
**Parallelizable?:** `yes`
**Suggested Labels:** `python`, `chaquopy`, `android`, `porting`, `refactor`
**Effort Estimate:** L
**Definition of Done:** The Python orchestrator code is updated to be Android-compatible. A test script within `src/main/python` can successfully initialize and perform a basic health check of the orchestrator. Necessary Python dependencies are listed for Chaquopy.
<!-- This might involve significant refactoring if the orchestrator is tightly coupled to a desktop environment. Focus on core logic first. -->
---
### <!-- Task ID: EMBED-002 --> Define and Implement Android-Python Communication Bridge

**Type:** `feature`
**Background:** A communication mechanism (IPC or in-proc bridge) is needed for the Android Foreground Service (Java/Kotlin) to send commands/events (like new tasks or UI observations) to the Python orchestrator and for Python to send actions/results back to the Android service.
**Acceptance Criteria:**
- [ ] Design a clear contract (API) for Java/Kotlin <-> Python communication (e.g., data structures for tasks, actions, UI events).
- [ ] Implement functions in Python, callable via Chaquopy, to receive data from Android (e.g., `onNewTask(taskString)`, `onScreenObservation(imageData)`).
- [ ] Implement callbacks or another mechanism in Java/Kotlin to receive data from Python (e.g., `executeDeviceAction(actionParameters)`).
- [ ] Communication is asynchronous to prevent blocking UI or service threads.
- [ ] Data serialization/deserialization between Java/Kotlin and Python types is handled correctly.
**Dependencies:** `APP-002` (Foreground Service), `EMBED-001` (Python orchestrator ready).
**Parallelizable?:** `no` (highly dependent on both sides being somewhat ready)
**Suggested Labels:** `android`, `python`, `chaquopy`, `ipc`, `bridge`, `api`
**Effort Estimate:** L
**Definition of Done:** A documented communication bridge is implemented. The Android Foreground Service can send a task string to the Python orchestrator, and the Python orchestrator can send a simple "action" string back to the Android service, which logs it.
<!-- Chaquopy's direct call capabilities are good for in-proc. Consider thread safety carefully. For more complex data, JSON strings might be a simple and robust choice. -->
---
### <!-- Task ID: EMBED-003 --> Integrate Python Agent Actions with Accessibility Service

**Type:** `integration`
**Background:** The actions determined by the Python agent (e.g., "click button X", "type Y in field Z") need to be translated into commands executed by the Android Accessibility Service.
**Acceptance Criteria:**
- [ ] Python agent can formulate an action request (e.g., `{type: "click", element_id: "some.id"}`).
- [ ] This action request is successfully passed from Python to the Android Foreground Service via the communication bridge.
- [ ] The Android Foreground Service parses the action request and commands the Accessibility Service.
- [ ] The Accessibility Service successfully executes the requested UI interaction.
- [ ] A basic end-to-end test: input a task, Python agent decides an action, action is performed on a test/dummy app UI.
**Dependencies:** `APP-003` (Accessibility Service), `EMBED-002` (Communication Bridge).
**Parallelizable?:** `no` (integrates multiple components)
**Suggested Labels:** `android`, `python`, `accessibility`, `integration`, `ui-automation`
**Effort Estimate:** XL
**Definition of Done:** The system demonstrates a full loop: a task is given via UI, Python agent processes it, decides an action, and the Accessibility Service performs that action on the Android device screen.
<!-- This is the culmination of the MVP's core functionality. Start with very simple, predefined actions. -->
---

---
## Epic 5: OCR On-Device Integration

This epic focuses on integrating an Optical Character Recognition (OCR) model into the Android application for on-device text extraction from screen captures.

---
### <!-- Task ID: OCR-001 --> OCR Model Conversion and Mobile Runtime Setup

**Type:** `engineering`
**Background:** An existing OCR model needs to be converted to a mobile-friendly format (e.g., TFLite, ONNX Mobile) and integrated into the Android app with a suitable runtime. Performance is key.
**Acceptance Criteria:**
- [ ] Evaluate and choose the best mobile runtime (TFLite, ONNX Mobile, etc.) for the existing OCR model, prioritizing speed and ease of integration.
- [ ] Convert the OCR model to the chosen format.
- [ ] Integrate the chosen mobile runtime library into the Android project.
- [ ] Load the converted OCR model into the Android app (likely within the Python environment managed by Chaquopy, or directly in Java/Kotlin if runtime is more suitable there).
- [ ] Perform a basic inference test with a sample image to ensure the model loads and runs.
**Dependencies:** `ENV-003` (Chaquopy, if Python handles OCR), access to the existing OCR model.
**Parallelizable?:** `yes`
**Suggested Labels:** `ocr`, `ml`, `android`, `tflite`, `onnx`, `performance`
**Effort Estimate:** L
**Definition of Done:** The OCR model is successfully converted and loaded into the Android application. A basic inference call with a test image returns a non-error result. The chosen runtime is added to the project dependencies.
<!-- The choice of runtime might depend on where preprocessing/postprocessing logic for OCR is easier to implement (Python vs Java/Kotlin). TFLite is generally well-supported on Android. -->
---
### <!-- Task ID: OCR-002 --> Implement OCR Inference and Data Flow

**Type:** `feature`
**Background:** The OCR model needs to be fed screen capture data, and its output (recognized text and bounding boxes) needs to be processed and made available to the Python agent.
**Acceptance Criteria:**
- [ ] Implement functionality to capture the screen content as an image (Bitmap or similar).
- [ ] Preprocess the captured image as required by the OCR model.
- [ ] Pass the preprocessed image to the OCR model for inference.
- [ ] Postprocess the model's output to extract usable text and bounding box information.
- [ ] Make the OCR results available to the Python orchestrator through the Android-Python bridge.
- [ ] Test OCR accuracy with a few sample screen contents.
**Dependencies:** `OCR-001` (Model loaded), `EMBED-002` (Android-Python bridge), `APP-003` (potentially, for screen capture permissions or context).
**Parallelizable?:** `no` (depends on OCR-001 and EMBED-002)
**Suggested Labels:** `ocr`, `ml`, `android`, `feature`, `python`, `accessibility_event`
**Effort Estimate:** L
**Definition of Done:** The Android app can capture the screen, perform OCR, and the recognized text (and optionally basic layout/bounding box info) is successfully passed to the Python agent. Basic accuracy is validated.
<!-- Screen capture might require specific permissions. The format of OCR data passed to Python needs to be well-defined. -->
---
### <!-- Task ID: OCR-003 --> OCR Performance Testing and CI Integration

**Type:** `testing`
**Background:** The OCR inference must be fast enough for a responsive user experience. Performance tests need to be automated and integrated into the CI pipeline to prevent regressions.
**Acceptance Criteria:**
- [ ] Develop a standardized OCR performance test scenario (e.g., using a set of predefined screen images).
- [ ] Measure average inference time on a CI emulator environment.
- [ ] Test asserts that average inference time is less than 1 second.
- [ ] Test asserts that no single inference exceeds 10 seconds (hard cap).
- [ ] The performance test is integrated into the GitHub Actions CI workflow.
- [ ] CI build fails if performance targets are not met.
**Dependencies:** `OCR-002` (OCR functional), `ENV-004` (CI workflow setup).
**Parallelizable?:** `no` (depends on functional OCR and CI setup)
**Suggested Labels:** `ocr`, `ml`, `performance`, `testing`, `ci`, `android`
**Effort Estimate:** M
**Definition of Done:** An automated performance test for OCR is implemented and runs as part of the CI pipeline. The test correctly measures inference time and fails the build if specified performance criteria (<1s average, <10s max) are breached on the CI emulator.
<!-- Emulator performance can vary. Define a baseline emulator configuration for consistent testing. This task ensures ongoing performance. -->
---

---
## Epic 6: Remote Model Harnesses

This epic covers the integration of remote, cloud-hosted AI models for tasks like advanced visual understanding (Grounding DINO) and high-level planning (LLMs).

---
### <!-- Task ID: REMOTE-001 --> Grounding DINO Replicate API Integration

**Type:** `feature`
**Background:** Grounding DINO is a powerful model for zero-shot object detection based on text prompts. Using a hosted version via Replicate API can provide this capability to the Python agent without requiring on-device model deployment for this specific, potentially heavy, model.
**Acceptance Criteria:**
- [ ] Python agent includes a module/wrapper for interacting with the Replicate API for a chosen Grounding DINO model.
- [ ] API calls are correctly authenticated using secrets management.
- [ ] Functionality to send an image (e.g., screen capture) and a text prompt to the Replicate API.
- [ ] Functionality to parse the bounding box and label results from the API response.
- [ ] Error handling for API failures (e.g., network issues, API errors, quota limits).
- [ ] Cost considerations and API usage limits are documented.
**Dependencies:** `EMBED-001` (Python orchestrator), `ENV-005` (Secrets Management for API keys).
**Parallelizable?:** `yes`
**Suggested Labels:** `ml`, `vision`, `grounding-dino`, `replicate`, `api`, `python`
**Effort Estimate:** M
**Definition of Done:** The Python agent can successfully call a Replicate-hosted Grounding DINO model with a sample image and prompt, and receive and parse the object detection results. API key is handled securely.
<!-- Ensure the Replicate API client library is added to Python requirements. Consider a simple caching mechanism if appropriate, but Replicate might have its own. -->
---
### <!-- Task ID: REMOTE-002 --> LLM Provider Abstraction Layer and Integration

**Type:** `feature`
**Background:** The agent will rely on Large Language Models (LLMs) for planning and decision-making. These will be accessed via remote APIs (e.g., OpenAI, Anthropic). An abstraction layer is needed to allow flexibility in choosing LLM providers and to centralize API interaction logic.
**Acceptance Criteria:**
- [ ] Define a common interface (e.g., abstract base class or protocol) in Python for LLM interactions (e.g., `generate_plan(prompt_text, history)`).
- [ ] Implement concrete classes for at least one LLM provider (e.g., OpenAI or Anthropic), adhering to the interface.
- [ ] API calls are correctly authenticated using secrets management.
- [ ] Configuration mechanism to select the desired LLM provider at runtime or build time.
- [ ] Python agent uses the abstraction layer to make LLM calls for planning.
- [ ] Error handling for API failures.
- [ ] Cost and usage considerations for different providers are documented.
**Dependencies:** `EMBED-001` (Python orchestrator), `ENV-005` (Secrets Management).
**Parallelizable?:** `yes`
**Suggested Labels:** `llm`, `planning`, `api`, `openai`, `anthropic`, `python`, `abstraction`
**Effort Estimate:** L
**Definition of Done:** The Python agent can make planning-related calls to a configured LLM provider through an abstraction layer. API keys are handled securely. It's possible to switch providers (even if only one is implemented initially) with configuration changes.
<!-- This abstraction is key for future flexibility and avoiding vendor lock-in. Start with one provider, but design the interface to be provider-agnostic. -->
---

---
## Epic 7: Safety & Human-in-the-Loop

This epic focuses on implementing safety mechanisms, including user confirmations for sensitive actions and providing manual control overrides.

---
### <!-- Task ID: SAFETY-001 --> Action Confirmation Checkpoints

**Type:** `feature`
**Background:** To prevent unintended consequences, the agent must seek user confirmation before performing potentially sensitive or irreversible actions (e.g., making purchases, sending messages, deleting files, capturing screenshots of sensitive apps).
**Acceptance Criteria:**
- [ ] Identify a preliminary list of action types requiring user confirmation.
- [ ] Python agent, before executing a sensitive action, sends a confirmation request to the Android app via the communication bridge.
- [ ] The Android app displays a clear confirmation dialog to the user, detailing the proposed action.
- [ ] User can approve or deny the action.
- [ ] The user's decision is sent back to the Python agent.
- [ ] Python agent proceeds with the action only if approved.
- [ ] Confirmation requests are opt-in or configurable where appropriate.
**Dependencies:** `EMBED-002` (Android-Python bridge), `EMBED-003` (Action execution flow).
**Parallelizable?:** `no` (integrates with existing action execution)
**Suggested Labels:** `safety`, `ui`, `android`, `python`, `ux`, `feature`
**Effort Estimate:** M
**Definition of Done:** For at least two types of sensitive actions (e.g., a simulated purchase and taking a screenshot), the system prompts the user for confirmation via an Android dialog before proceeding. The agent respects the user's decision.
<!-- The list of sensitive actions will evolve. The UI for confirmation should be clear and unambiguous. -->
---
### <!-- Task ID: SAFETY-002 --> Manual Override and Cancel Mechanism

**Type:** `feature`
**Background:** The user must always have a straightforward way to stop or pause the agent's current operation, regardless of what it's doing. This is crucial for safety and user trust.
**Acceptance Criteria:**
- [ ] A persistent "Stop Agent" or "Pause Agent" control is available in the Android app's UI (e.g., in the foreground service notification and/or main app screen).
- [ ] Activating this control immediately signals the Python agent via the communication bridge.
- [ ] The Python agent attempts to gracefully halt its current operation (e.g., stop current task, cancel pending actions).
- [ ] The Accessibility Service is instructed to cease any ongoing UI interactions.
- [ ] Visual feedback is provided to the user that the agent has stopped/paused.
- [ ] (If paused) A mechanism to resume the agent's operation.
**Dependencies:** `APP-002` (Foreground Service for UI control), `EMBED-002` (Android-Python bridge).
**Parallelizable?:** `yes` (can be developed in parallel with agent capabilities)
**Suggested Labels:** `safety`, `ui`, `android`, `python`, `ux`, `feature`, `interruption`
**Effort Estimate:** M
**Definition of Done:** A user can effectively stop the agent's operation at any point using a UI control. The agent responds promptly by halting its actions and interactions. The UI reflects the agent's stopped state.
<!-- This needs to be a high-priority signal that can interrupt even long-running Python operations if possible. Consider using thread interruption or similar mechanisms in Python. -->
---

---
## Epic 8: Automated Testing Suite

This epic establishes a comprehensive suite of automated tests to ensure code quality, prevent regressions, and validate application functionality across different layers.

---
### <!-- Task ID: TEST-001 --> Python Unit Test Setup and Initial Coverage

**Type:** `testing`
**Background:** The Python agent core logic, utilities, and helper modules need to be unit tested to ensure their correctness in isolation. Pytest is the chosen framework.
**Acceptance Criteria:**
- [ ] Pytest is configured in the project for the Python codebase.
- [ ] GitHub Actions CI workflow (`ENV-004`) is updated to run Python unit tests.
- [ ] Unit tests are written for critical Python utility functions.
- [ ] Unit tests cover core logic of the Python agent orchestrator (mocking dependencies like Android bridge and remote models).
- [ ] Initial test coverage target of X% for key Python modules is met (e.g., 50% for core agent logic).
**Dependencies:** `EMBED-001` (Python orchestrator structure), `ENV-004` (CI Workflow).
**Parallelizable?:** `yes`
**Suggested Labels:** `testing`, `python`, `pytest`, `ci`, `unit-test`
**Effort Estimate:** M
**Definition of Done:** Pytest is integrated, runs in CI, and provides initial unit test coverage for essential Python components. Coverage report is generated.
<!-- Focus on testing logic that doesn't require Android runtime first. Mocking will be essential. -->
---
### <!-- Task ID: TEST-002 --> Android UI and Service Tests

**Type:** `testing`
**Background:** The Android application's UI components (Activities, Composables) and services need testing to ensure they behave as expected. This includes testing UI interactions, service lifecycle, and communication between them.
**Acceptance Criteria:**
- [ ] Android instrumentation tests (e.g., using Espresso or UI Automator) are set up for UI components.
- [ ] Jetpack Compose tests are used if Compose is adopted for UI.
- [ ] Tests for the Foreground Service lifecycle and its interaction with the main activity (e.g., starting, stopping, passing data).
- [ ] Basic UI interaction tests (e.g., inputting text in `APP-001`, button clicks).
- [ ] CI workflow (`ENV-004`) is updated to run these Android tests on an emulator.
**Dependencies:** `APP-001`, `APP-002`. `ENV-002` (Emulator for tests), `ENV-004` (CI).
**Parallelizable?:** `yes`
**Suggested Labels:** `testing`, `android`, `espresso`, `ui-automator`, `compose`, `service`, `instrumentation-test`
**Effort Estimate:** L
**Definition of Done:** Android instrumentation/Compose tests are implemented for core UI elements and service interactions. These tests run successfully in the CI emulator.
<!-- These tests will run on an Android emulator. Ensure emulator setup is robust in CI. -->
---
### <!-- Task ID: TEST-003 --> End-to-End (E2E) Flow Testing in Emulator

**Type:** `testing`
**Background:** E2E tests are crucial for validating complete user scenarios, involving interaction across the Android UI, services, Python agent, and potentially (mocked) remote models. These will run in the CI emulator.
**Acceptance Criteria:**
- [ ] Define 1-2 critical E2E user flows (e.g., user inputs task -> agent processes -> accessibility action performed).
- [ ] Develop E2E tests that automate these flows using Android UI testing frameworks and potentially custom scripts.
- [ ] Tests verify the correct sequence of operations and outcomes, including UI changes and (mocked) agent actions.
- [ ] E2E tests run as part of the CI pipeline on an emulator.
- [ ] Clear reporting of E2E test results.
**Dependencies:** `EMBED-003` (Full MVP loop), `TEST-001`, `TEST-002`.
**Parallelizable?:** `no` (depends on most other components being integrated)
**Suggested Labels:** `testing`, `e2e`, `android`, `python`, `ci`, `integration-test`
**Effort Estimate:** L
**Definition of Done:** At least one key E2E user flow is implemented as an automated test and runs successfully in the CI emulator, validating the integration of multiple system components.
<!-- E2E tests can be brittle; focus on stable core flows. Mock external dependencies like actual remote API calls to ensure test reliability and control costs. -->
---
### <!-- Task ID: TEST-004 --> (Optional) Firebase Test Lab Integration Feasibility Study

**Type:** `research`
**Background:** Firebase Test Lab (FTL) offers testing on a wide range of real devices, which can catch issues not found on emulators. This task is to investigate its feasibility and cost-effectiveness.
**Acceptance Criteria:**
- [ ] Research FTL capabilities for Android instrumentation tests and custom E2E tests.
- [ ] Estimate cost per run for the current/planned test suite size on FTL.
- [ ] Document steps required to integrate existing Android tests with FTL.
- [ ] Provide a recommendation: proceed with FTL integration if cost per full test run is ≤ $0.15, otherwise, stick to emulator-only for CI.
**Dependencies:** `TEST-002`, `TEST-003` (having a test suite to estimate).
**Parallelizable?:** `yes`
**Suggested Labels:** `testing`, `firebase`, `research`, `android`, `ci`, `cost-analysis`
**Effort Estimate:** S
**Definition of Done:** A short document is produced summarizing FTL's pros/cons for this project, cost estimation, and a clear recommendation on whether to proceed with integration based on the defined cost cap.
<!-- This is a decision point. If FTL is too expensive, we double down on robust emulator testing. -->
---

---
## Epic 9: Docs & Developer UX

This epic ensures the project is easy for developers to understand, set up, and contribute to, through clear documentation and defined contribution guidelines.

---
### <!-- Task ID: DOCS-001 --> Update Root README with Comprehensive Setup and Usage Instructions

**Type:** `documentation`
**Background:** The main `README.md` is the entry point for new developers. It needs to provide clear, concise instructions on how to get the project running locally, including setup, build, run, and test commands.
**Acceptance Criteria:**
- [ ] `README.md` includes a "Getting Started" section.
- [ ] Instructions for installing prerequisites (Android SDK, Python, Chaquopy, etc.). Refer to `ENV-001` script where applicable.
- [ ] One-command or minimal-command instructions for building the project.
- [ ] Instructions for running the app on an emulator or device.
- [ ] Instructions for running all types of tests (Python unit, Android instrumentation, E2E). Refer to `TEST-001`, `TEST-002`, `TEST-003`.
- [ ] `README.md` is well-formatted and easy to follow.
**Dependencies:** `ENV-001`, `TEST-001`, `TEST-002`, `TEST-003` (to document actual commands).
**Parallelizable?:** `yes` (can be drafted and updated as other tasks complete)
**Suggested Labels:** `documentation`, `readme`, `developer-ux`, `setup`
**Effort Estimate:** M
**Definition of Done:** The root `README.md` contains clear, accurate, and tested instructions for project setup, build, run, and test execution. A new developer can follow it to get the project operational.
<!-- This should be a living document, updated as build/test commands evolve. -->
---
### <!-- Task ID: DOCS-002 --> Document Secrets Management Mechanism

**Type:** `documentation`
**Background:** Developers need to understand how to manage API keys and other secrets for both local development and how they are handled in CI. This was designed in `ENV-005`.
**Acceptance Criteria:**
- [ ] Create a new document (e.g., `docs/secrets_management.md` or a section in `CONTRIBUTING.md`).
- [ ] Explain the use of `.env` files and the `.env.example` template.
- [ ] Detail how to add new secrets for local development.
- [ ] Briefly describe how secrets are injected in GitHub Actions (referencing GitHub Secrets, not values).
- [ ] Link to this document from the main `README.md`.
**Dependencies:** `ENV-005` (Secrets management implemented).
**Parallelizable?:** `yes`
**Suggested Labels:** `documentation`, `secrets`, `developer-ux`, `security`
**Effort Estimate:** S
**Definition of Done:** Clear documentation exists explaining the secrets management process for developers, covering both local and CI environments.
<!-- Do NOT include any actual secrets in this documentation. -->
---
### <!-- Task ID: DOCS-003 --> Define and Document Commit Message Conventions and Code Style

**Type:** `documentation`
**Background:** Consistent commit messages and code style improve readability, maintainability, and the ability to automate changelog generation or version bumping.
**Acceptance Criteria:**
- [ ] Choose a commit message convention (e.g., Conventional Commits).
- [ ] Document the chosen convention in `CONTRIBUTING.md` or a similar file.
- [ ] Provide examples of good commit messages.
- [ ] Document code style guidelines for Python (e.g., PEP 8, using Black/Flake8 if adopted) and Java/Kotlin (e.g., Android Kotlin Style Guide).
- [ ] Include tips on setting up IDEs for auto-formatting if applicable.
- [ ] (Optional) Add linting tools to CI to enforce style for Python and/or Java/Kotlin.
**Dependencies:** None.
**Parallelizable?:** `yes`
**Suggested Labels:** `documentation`, `developer-ux`, `style-guide`, `contributing`, `linting`
**Effort Estimate:** M
**Definition of Done:** A document outlining commit message conventions and code style guidelines is created and accessible. Optionally, linters are added to CI.
<!-- This helps maintain consistency as the team grows or new contributors join. -->
---

---
## Epic 10: Sideloadable Release

This epic covers the process of creating shareable, installable APKs for testing, demos, or manual distribution, along with basic release documentation.

---
### <!-- Task ID: RELEASE-001 --> CI Job for Signed and Versioned APK

**Type:** `chore`
**Background:** To distribute the app for manual installation (sideloading), we need a CI job that builds a release-ready APK. This involves versioning the app and signing the APK with a release key.
**Acceptance Criteria:**
- [ ] Android project configured for release builds (e.g., `buildTypes` in `build.gradle`).
- [ ] Securely manage a release signing key and alias (e.g., using GitHub Secrets to store keystore and credentials).
- [ ] CI job (e.g., a dedicated GitHub Actions workflow or an extension to `ENV-004`) that:
    - [ ] Checks out the code.
    - [ ] Sets the app version name and version code (e.g., from a tag, or manually specified).
    - [ ] Builds a release APK.
    - [ ] Signs the APK using the release key.
    - [ ] Archives the signed APK as a downloadable artifact.
- [ ] Document how to trigger this CI job and retrieve the APK.
**Dependencies:** `ENV-004` (Base CI setup), `ENV-005` (Secrets management for signing key).
**Parallelizable?:** `yes` (can be set up once CI basics are in place)
**Suggested Labels:** `ci`, `android`, `build`, `release`, `apk`, `signing`
**Effort Estimate:** L
**Definition of Done:** A CI job is implemented that successfully builds, versions, signs, and archives a release APK. The APK can be downloaded and installed on an Android device. Signing key is securely managed.
<!-- Keystore generation and management is critical here. The keystore itself should NOT be committed to the repo. -->
---
### <!-- Task ID: RELEASE-002 --> Release Notes Template and Process

**Type:** `documentation`
**Background:** When creating releases, even for internal/sideload purposes, it's important to document what has changed. A template and a simple process for generating release notes will ensure consistency.
**Acceptance Criteria:**
- [ ] Create a release notes template (e.g., `RELEASE_NOTES_TEMPLATE.md`).
- [ ] Template includes sections for:
    - [ ] Release Version (e.g., v0.1.0)
    - [ ] Release Date
    - [ ] New Features
    - [ ] Bug Fixes
    - [ ] Known Issues
    - [ ] Installation Instructions (link to README or sideloading guide)
- [ ] Document a lightweight process for populating the release notes (e.g., based on commit messages since last tag, manual compilation).
- [ ] Store populated release notes in the repository (e.g., in a `docs/releases` folder or as GitHub Releases).
**Dependencies:** `DOCS-003` (Commit message conventions can help automate parts of this).
**Parallelizable?:** `yes`
**Suggested Labels:** `documentation`, `release`, `changelog`, `process`
**Effort Estimate:** S
**Definition of Done:** A release notes template is created. A process for creating and storing release notes for each generated APK is documented. At least one example set of release notes is created for a test release.
<!-- This doesn't need to be overly complex for now. A simple Markdown template is sufficient. -->
---
