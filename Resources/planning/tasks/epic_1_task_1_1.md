Status: Not Started

# Epic 1 -- Task 1.1: Create Script for Headless Linux Android Build & Test Environment

**Type:** `chore`

**Background:** To enable automated testing and CI, we need a script that can set up a consistent Android build and test environment on a headless Linux server. This forms the base for all subsequent CI tasks.

**Acceptance Criteria:**
*   Script successfully installs all necessary dependencies for building an Android app (Java, Android SDK tools, Gradle).
*   Script can perform a clean build of the LuxoAI Android app.
*   Script can execute placeholder unit tests (even if they just pass trivially initially).
*   The script is idempotent (can be run multiple times without negative side-effects).
*   Consider using Docker if it significantly simplifies dependency management and provides better isolation than a bash script. Justify the choice.

**Dependencies:** None

**Parallelizable?:** `yes`

**Suggested Labels:** `ci`, `android`, `build`, `linux`

**Effort Estimate:** M

**Definition of Done:** A functional bash script (or Dockerfile and accompanying script) committed to the repository that sets up the build environment and successfully builds the app.
---
