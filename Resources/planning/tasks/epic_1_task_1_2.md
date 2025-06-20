Status: Not Started

# Epic 1 -- Task 1.2: Script Android SDK & Emulator Installation and Management

**Type:** `chore`

**Background:** Automated tests require an Android emulator. This task focuses on scripting the installation of the Android SDK (if not fully covered by 1.1) and, crucially, the setup and management of an Android Virtual Device (AVD).

**Acceptance Criteria:**
*   Script can download and install specific Android SDK platform versions and build tools.
*   Script can create a new AVD with specified characteristics (e.g., API level, screen size, hardware profile).
*   Script can start and stop the created AVD in headless mode.
*   Emulator runs stably.

**Dependencies:** Task 1.1 (or its core components)

**Parallelizable?:** `yes`

**Suggested Labels:** `ci`, `android`, `emulator`, `linux`

**Effort Estimate:** M

**Definition of Done:** Scripts to install SDK components and create/manage a headless AVD, integrated with the environment from Task 1.1.
---
