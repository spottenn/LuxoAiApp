Status: Not Started

# Epic 1 -- Task 1.8: Integrate GCP Gradle Build Cache

**Type:** `chore`

**Background:** To significantly speed up Android builds, especially in CI and for repeated local builds, a distributed build cache is highly beneficial. This task involves integrating the `androidx/gcp-gradle-build-cache` plugin to leverage Google Cloud Storage for caching. The user will handle GCP account creation and provide a placeholder project name.

**Acceptance Criteria:**
*   The `com.google.cloud.buildcache.gradle` plugin is correctly added and configured in the relevant Gradle files (e.g., `LuxoAI/settings.gradle.kts` or `LuxoAI/build.gradle.kts`).
*   Build cache configuration supports both local development (developer machines, Jules VMs) and CI environments.
*   For CI (GitHub Actions), GCP service account credentials for accessing the cache bucket are securely handled via GitHub Actions secrets and made available to the Gradle build (as per Task 1.5).
*   The configuration includes placeholders for `GCP_PROJECT_ID` and `GCP_BUCKET_NAME` that the user will fill in.
*   Successful build execution demonstrates cache usage (e.g., `> Task ... FROM-CACHE` messages in Gradle output, or by observing build times for previously built modules).
*   Documentation is added (e.g., in `README.md` or a new doc in `docs/`) explaining:
    *   How to create/provide GCP credentials (service account JSON).
    *   How to set the `GCP_PROJECT_ID` and `GCP_BUCKET_NAME` (e.g., via environment variables or `local.properties`).
    *   How to enable the cache for local builds.

**Dependencies:** Task 1.1 (Build environment), Task 1.5 (Secrets management for CI)

**Parallelizable?:** `yes` (once dependencies are met)

**Suggested Labels:** `ci`, `android`, `build`, `performance`, `gradle`, `gcp`, `build-cache`

**Effort Estimate:** M

**Definition of Done:**
*   GCP Gradle Build Cache plugin is integrated and configured.
*   Builds successfully utilize the cache in both local (with placeholder config) and CI environments (with secrets).
*   Documentation for setup and configuration is provided.
*   The `PLANNING_TASKS.md` file and its generated task file are updated.
