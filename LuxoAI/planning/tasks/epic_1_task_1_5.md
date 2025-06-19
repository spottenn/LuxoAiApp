# Epic 1 -- Task 1.5: Design and Implement Secrets Injection Mechanism

**Type:** `chore`

**Background:** The agent will need API keys for services like OpenAI, Replicate, etc. These secrets must not be committed to the repository. A secure way to inject them at runtime is needed for both local development (Jules VMs) and CI (GitHub Actions).

**Acceptance Criteria:**
*   Mechanism supports providing secrets via environment variables.
*   An example secrets file (e.g., `.env.example`) is committed, listing required keys without their values.
*   The actual secrets file (e.g., `.env`) is listed in `.gitignore`.
*   Android app can access these secrets at runtime (e.g., via `BuildConfig` fields populated from Gradle properties, which in turn read from env vars).
*   GitHub Actions workflow can securely provide secrets to the build and test environment (using GitHub encrypted secrets).
*   Documentation explains how to set up secrets for local dev and CI.

**Dependencies:** None (can be developed in parallel, but Task 1.4 will need it)

**Parallelizable?:** `yes`

**Suggested Labels:** `security`, `ci`, `android`, `devops`

**Effort Estimate:** M

**Definition of Done:** A working secrets management system with an example file, gitignore rules, and integration points for Android/Gradle and GitHub Actions. Documentation for usage.
---
## Epic 2 -- Repo Audit & Architecture Doc
