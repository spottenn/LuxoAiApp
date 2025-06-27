Status: Started

# Epic 9 -- Task 9.1: Update Root README with One-Command Setup, Run, and Test Instructions

**Type:** `docs`

**Background:** The main `README.md` is the entry point for new developers. It should provide clear, concise instructions on how to get the project set up, run the app, and execute tests with minimal commands.

**Acceptance Criteria:**
*   Root `README.md` has a "Getting Started" section.
*   Instructions for cloning the repository.
*   Clear prerequisites listed (e.g., specific Java version, Android Studio version if applicable, Python version).
*   One-command (or minimal command) instructions for:
    *   Setting up the development environment (dependencies, etc., potentially using scripts from Epic 1).
    *   Building the Android app and test APKs.
    *   Running Python unit tests (Task 8.1).
    *   Running Android tests (instrumentation, E2E) on the Mobile Test Platform (MTP) (as per Task 8.2, 8.3), including how to trigger them via `farm-cli-client` if relevant for local developer testing against MTP.
*   Instructions are verified to work on a clean checkout.

**Dependencies:** Task 1.1 (Setup scripts), Task 1.2 (MTP Integration for test execution info, `farm-cli-client` usage), Task 8.1 (Python tests), Task 8.2 (Android tests on MTP)

**Parallelizable?:** `yes` (can be updated as features become stable)

**Suggested Labels:** `documentation`, `readme`, `developer-ux`

**Effort Estimate:** M

**Definition of Done:** Root `README.md` is updated with comprehensive and easy-to-follow setup, run, and test instructions.
