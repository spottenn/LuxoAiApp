Status: Started

# Epic 1 -- Task 1.2: Integrate with Mobile Test Platform (MTP) for CI Testing [WAS: Configure Firebase Test Lab Integration]

**Type:** `chore`

**Background:** Automated testing will now use a self-hosted Mobile Test Platform (MTP) utilizing Dockerized Android emulators, instead of Firebase Test Lab or local emulators. This task focuses on integrating the `farm-cli-client` (from the MTP project) into the CI pipeline to run Android instrumentation tests using Marathon. The user will set up the `farm-server`.

**Acceptance Criteria:**
*   The `farm-cli-client` is accessible and usable within the CI environment.
*   CI workflow can successfully build the application APK and test APK.
*   A `Marathonfile` is created and configured in the `LuxoAI` project to define test execution parameters (app/test APK paths, etc.).
*   CI workflow uses `farm-cli-client` to:
    *   Acquire the required number of devices from the MTP `farm-server` for a specific group.
    *   Execute Android instrumentation tests using Marathon via the `farm-cli-client`.
    *   Release the devices after test completion.
*   Test results from Marathon (via `farm-cli-client`) are captured, and pass/fail status is reported in the CI workflow.
*   Basic documentation is added explaining how to run tests via `farm-cli-client` (relevant for CI and potentially for local developer testing against MTP).
*   Secrets for `farm-server` URL and any other MTP client configurations are securely managed in CI.

**Dependencies:** Task 1.1 (Build environment for app/test APKs), Task 1.5 (Secrets management for MTP server URL/credentials)

**Parallelizable?:** `yes`

**Suggested Labels:** `ci`, `android`, `mtp`, `testing`, `marathon`, `farm-cli-client`

**Effort Estimate:** L

**Definition of Done:** CI can successfully execute Android instrumentation tests on the Mobile Test Platform using `farm-cli-client` and Marathon. Basic documentation for MTP client usage is available.
