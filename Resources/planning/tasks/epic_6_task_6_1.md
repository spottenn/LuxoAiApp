# Epic 6 -- Task 6.1: Create Grounding DINO Wrapper for Replicate API

**Type:** `feature`

**Background:** Grounding DINO is useful for object detection based on free-text prompts. This task involves creating a Python wrapper to call a Grounding DINO model hosted on Replicate (or a similar pay-as-you-go model hosting service if a better one is found).

**Acceptance Criteria:**
*   A Python function/class is created that takes an image and a text prompt as input.
*   The wrapper makes an API call to a Replicate endpoint for Grounding DINO.
*   API key for Replicate is securely managed (using system from Task 1.5).
*   The wrapper handles API responses, including potential errors.
*   The function returns structured output (e.g., bounding boxes, labels, confidence scores).
*   Consider rate limits and add basic retry logic if appropriate.
*   This wrapper is callable from the main Python agent orchestrator.

**Dependencies:** Task 1.5 (Secrets management)

**Parallelizable?:** `yes`

**Suggested Labels:** `python`, `ml`, `object-detection`, `grounding-dino`, `replicate`, `api`

**Effort Estimate:** M

**Definition of Done:** A Python wrapper that allows the agent to get object detection results from Grounding DINO via Replicate using an image and a text prompt.
---
