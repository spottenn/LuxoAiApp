Status: Not Started

# Epic 1 -- Task 1.1: Create Script for Headless Linux Android Build & Test Environment

**Type:** `chore`

**Background:** To enable automated testing and CI, we need a script that can set up a consistent Android build and test environment on a headless Linux server. This forms the base for all subsequent CI tasks.
This environment has significant disk space constraints: approximately 8.7 GB of usable disk space on the main filesystem (an overlayfs, meaning space cannot be reclaimed from the base layer) and around 3.9 GB available in `/dev/shm`. The script must be designed with these limitations in mind.

**Acceptance Criteria:**
*   A bash script successfully installs all necessary dependencies for building an Android app. This includes specific, pinned versions of Java, Android SDK command-line tools, and Gradle.
*   The script can perform a clean build of the LuxoAI Android app.
*   The script can execute placeholder unit tests (even if they just pass trivially initially).
*   The script is idempotent (can be run multiple times without negative side-effects).
*   The script's successful execution and achievement of all other relevant acceptance criteria are verified through a documented test run (e.g., logs showing successful installation, build, and test execution).

**Implementation Notes:**
*   **Disk Space Management:** The script must be highly conservative with disk space. Only essential packages should be installed. Pinned versions will help control size.
*   **No Docker:** Docker should not be used for this task due to disk space overhead and the availability of pre-existing packages in the base system. The solution must be a bash script that directly installs and configures tools.
*   **Pinned Versions:** All critical tools (Java, Android SDK tools, Gradle) must be installed at specific, known-stable versions to ensure reproducibility and manage disk footprint. These versions should be documented within the script or this task.
*   **Consider Future Needs:** While this script focuses on the core build tools, it must leave adequate space for subsequent Epic 1 tasks, such as Android SDK system images (for Task 1.2) and Python dependencies via Chaquopy (for Task 1.3). This means avoiding unnecessary packages or very large versions of tools if smaller, viable alternatives exist.

**Dependencies:** None

**Parallelizable?:** `yes`

**Suggested Labels:** `ci`, `android`, `build`, `linux`, `disk-space`

**Effort Estimate:** M

**Definition of Done:** A functional bash script committed to the repository. The script's functionality must be verified by executing it in a representative environment, demonstrating that it successfully sets up the build environment (installing pinned versions of Java, Android SDK tools, and Gradle), performs a clean build of the LuxoAI app, executes placeholder unit tests, and adheres to disk space constraints.
---
