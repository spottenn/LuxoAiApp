Status: Not Started

# Epic 8 -- Task 8.2: Implement Android Instrumentation/Compose Tests for UI & Service on MTP

**Type:** `test`

**Background:** Android-specific components like UI elements (Jetpack Compose or XML), ViewModel interactions, and the foreground service logic need testing. These tests will run on the Mobile Test Platform (MTP) emulators.

**Acceptance Criteria:**
*   Android instrumentation tests are set up in the project.
*   Tests for UI elements:
    *   Verify correct display of UI components from Task 3.1.
    *   Test basic interactions (e.g., text input, button click).
    *   If using Compose, use Compose testing APIs.
*   Tests for foreground service (Task 3.2):
    *   Verify service starts and stops correctly.
    *   Verify notification is displayed.
*   These tests run on MTP emulators (via `farm-cli-client` and Marathon) as part of the CI workflow (Task 1.4). This includes tests for accessibility features using Espresso/UI Automator.

**Dependencies:** Task 3.1 (UI), Task 3.2 (Service), Task 1.4 (CI integration with MTP)

**Parallelizable?:** `yes` (once features are available)

**Suggested Labels:** `android`, `test`, `instrumentation-test`, `jetpack-compose`, `ci`, `mtp`, `accessibility`

**Effort Estimate:** L

**Definition of Done:** Android instrumentation tests covering basic UI, service functionality, and accessibility, integrated into and passing on the MTP via CI.
