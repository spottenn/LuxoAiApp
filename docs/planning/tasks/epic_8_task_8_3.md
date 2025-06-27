Status: Not Started

# Epic 8 -- Task 8.3: Develop End-to-End Tests Running on Mobile Test Platform (MTP)

**Type:** `test`

**Background:** To verify the entire system works together, end-to-end (E2E) tests are needed. These simulate a user providing a task and the agent attempting to complete it, involving UI interaction (including accessibility controls), Python logic, and potentially external API calls (mocked if necessary for CI). These tests will run on the Mobile Test Platform (MTP).

**Acceptance Criteria:**
*   E2E test framework/strategy is chosen (e.g., using Android Espresso/UI Automator driven by a test script, executed via Marathon).
*   At least one E2E test case is implemented:
    *   User enters a simple task (e.g., "Open settings and turn on Wi-Fi" - initially can be a very simple, self-contained task on a test app).
    *   Agent simulates interactions to achieve the task, including exercising accessibility controls.
    *   Test verifies the expected outcome (e.g., Wi-Fi is enabled, or a specific UI state is reached).
*   These tests run on the MTP (via `farm-cli-client` and Marathon) as part of the CI workflow (Task 1.4).
*   Consider how to handle variability in app UIs and agent behavior. Start with very deterministic scenarios.

**Dependencies:** Task 3.3 (Accessibility for interaction), Task 4.1 (Python agent callable), Task 1.4 (CI integration with MTP)

**Parallelizable?:** `no` (integrates many components)

**Suggested Labels:** `test`, `e2e`, `android`, `python`, `ci`, `mtp`, `accessibility`

**Effort Estimate:** XL

**Definition of Done:** At least one E2E test scenario that runs the full agent loop (UI input -> Python -> UI interaction via accessibility) on the MTP via CI and verifies a successful outcome.
