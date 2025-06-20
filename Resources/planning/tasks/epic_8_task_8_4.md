# Epic 8 -- Task 8.4: (Optional) Hook to Firebase Test Lab if Cost-Effective

**Type:** `test`

**Background:** Firebase Test Lab (FTL) offers running tests on a wide range of real devices. This could be beneficial if emulator testing proves insufficient or too different from real-world conditions. However, cost is a factor.

**Acceptance Criteria:**
*   Research FTL pricing and integration effort.
*   If total cost per run for relevant tests (e.g., instrumentation, E2E) is ≤ $0.15, proceed.
*   Integrate Android instrumentation/E2E tests with FTL.
*   CI workflow (Task 1.4) can trigger FTL runs.
*   Test results from FTL are reported back to CI.
*   If cost > $0.15, document the findings and stick to emulator-only testing for CI.

**Dependencies:** Task 8.2, Task 8.3

**Parallelizable?:** `yes`

**Suggested Labels:** `test`, `android`, `firebase`, `ci`, `research`

**Effort Estimate:** M (if pursued)

**Definition of Done:** Either FTL is integrated for test runs within the budget, or a documented decision is made not to use it based on cost.
---
## Epic 9 -- Docs & Developer UX
