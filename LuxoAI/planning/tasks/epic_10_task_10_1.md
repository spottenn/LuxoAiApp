# Epic 10 -- Task 10.1: Create CI Job for Signing and Outputting a Versioned APK

**Type:** `chore`

**Background:** To easily distribute the app for testing or to stakeholders, the CI pipeline should produce a signed, sideloadable APK. Versioning helps track releases.

**Acceptance Criteria:**
*   A new CI job (or an extension to the existing one from Task 1.4) is created.
*   The job takes the APK built by the standard build process.
*   The job signs the APK using a dedicated Android signing key.
    *   <!-- The signing key itself should be stored securely, e.g., as a base64 encoded secret in GitHub Actions secrets, and imported into a temporary keystore during the CI run. -->
*   The output APK is versioned (e.g., using `git describe --tags` or a build number). The version should be part of the APK filename and ideally in `BuildConfig` as well.
*   The signed, versioned APK is uploaded as a build artifact in GitHub Actions.

**Dependencies:** Task 1.4 (Base CI workflow), Task 1.5 (for secure handling of signing key password/alias if needed)

**Parallelizable?:** `yes`

**Suggested Labels:** `ci`, `android`, `release`, `apk`, `signing`

**Effort Estimate:** M

**Definition of Done:** The CI pipeline produces a signed, versioned APK as a downloadable artifact on every successful build of the `main` branch (or on tagged releases).
---
