# Epic 5 -- Task 5.2: Implement OCR Inference with < 1s Average Speed

**Type:** `feature`

**Background:** For a responsive agent, on-device OCR needs to be fast. This task focuses on implementing the actual OCR inference logic and ensuring it meets performance targets.

**Acceptance Criteria:**
*   A function is implemented that takes a captured image (e.g., Bitmap from a screen capture) as input.
*   Image preprocessing steps required by the OCR model are implemented.
*   The preprocessed image is fed to the OCR model (from Task 5.1) for inference.
*   Postprocessing of model output is implemented to extract recognized text and bounding boxes.
*   Average inference time (preprocessing, inference, postprocessing) is less than 1 second on the CI emulator.
*   A hard cap of 10 seconds for inference is never exceeded.
*   The OCR functionality is callable from the Python agent (via the bridge in Task 4.2).

**Dependencies:** Task 5.1 (OCR runtime), Task 4.2 (Python-Android bridge)

**Parallelizable?:** `no` (depends on model integration)

**Suggested Labels:** `android`, `ml`, `ocr`, `performance`

**Effort Estimate:** L

**Definition of Done:** OCR inference is functional, meets the <1s average speed target on the CI emulator, and can be invoked from Python code with image input, returning structured text output.
---
