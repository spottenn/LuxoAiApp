# Epic 1 -- Task 1.4: Develop GitHub Actions Workflow for Build, Emulator Launch, and Tests

**Type:** `chore`

**Background:** To ensure code quality and catch regressions, a CI workflow is needed. This workflow will use the scripts from previous tasks to build the app, run an emulator, and execute tests on every push/PR.

**Acceptance Criteria:**
*   Workflow triggers on pushes to `main` and pull requests targeting `main`.
*   Workflow successfully checks out the code.
*   Workflow uses scripts from Task 1.1 and 1.2 to set up the build environment and an emulator.
*   Workflow builds the Android APK.
*   Workflow runs placeholder Android unit tests and (later) instrumentation tests within the emulator.
*   Workflow status (pass/fail) is correctly reported in GitHub.

**Dependencies:** Task 1.1, Task 1.2

**Parallelizable?:** `yes`

**Suggested Labels:** `ci`, `github-actions`, `android`, `testing`

**Effort Estimate:** L

**Definition of Done:** A functional GitHub Actions workflow file (`.github/workflows/main.yml`) that automates the build and (placeholder) test process in an emulator.
---
