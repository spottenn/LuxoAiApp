# Epic 5 -- Task 5.3: Create Automated Performance Test for OCR Inference Speed

**Type:** `test`

**Background:** To ensure OCR performance doesn't regress, an automated test is needed that measures inference speed and fails CI if it exceeds the defined cap.

**Acceptance Criteria:**
*   An Android instrumentation test (or a test runnable in a similar environment) is created.
*   The test loads a sample image (or captures one from a controlled UI state).
*   The test runs OCR inference (from Task 5.2) multiple times on the sample image.
*   The test calculates the average inference time.
*   The test asserts that the average time is below 1 second and no single run exceeds 10 seconds.
*   This test is integrated into the CI workflow (Task 1.4) and fails the build if performance criteria are not met.

**Dependencies:** Task 5.2 (Functional OCR), Task 1.4 (CI workflow)

**Parallelizable?:** `yes` (once OCR is functional)

**Suggested Labels:** `android`, `ml`, `ocr`, `performance`, `test`, `ci`

**Effort Estimate:** M

**Definition of Done:** An automated test that measures OCR inference speed and fails CI if the <1s average or 10s hard cap is breached.
---
## Epic 6 -- Remote Model Harnesses
