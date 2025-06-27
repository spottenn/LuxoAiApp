Status: Started

# Epic 1 -- Task 1.4: Develop GitHub Actions Workflow for Build and Mobile Test Platform (MTP) Execution

**Type:** `chore`

**Background:** To ensure code quality and catch regressions, a CI workflow is needed. This workflow will build the app and then use the `farm-cli-client` to execute tests on the self-hosted Mobile Test Platform (MTP).

**Acceptance Criteria:**
*   Workflow triggers on pushes to `main` and pull requests targeting `main`.
*   Workflow successfully checks out the code.
*   Workflow uses script from Task 1.1 to set up the build environment.
*   Workflow builds the Android application APK and the test APK.
*   Workflow uses `farm-cli-client` (as configured in Task 1.2) to run tests (unit, instrumentation, E2E) on the MTP. This includes accessibility tests written using Espresso/UI Automator.
*   Workflow status (pass/fail), based on MTP test results, is correctly reported in GitHub.

**Dependencies:** Task 1.1 (Build environment), Task 1.2 (MTP Integration with `farm-cli-client`), Task 1.3 (Chaquopy for full app build), Task 1.5 (Secrets for MTP)

**Parallelizable?:** `yes`

**Suggested Labels:** `ci`, `github-actions`, `android`, `testing`

**Effort Estimate:** L

**Definition of Done:** A functional GitHub Actions workflow file (`.github/workflows/main.yml`) that automates the build and triggers test execution on the Mobile Test Platform (MTP) using `farm-cli-client`, reporting pass/fail status.
