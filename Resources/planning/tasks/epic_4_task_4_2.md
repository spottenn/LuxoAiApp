Status: Not Started

# Epic 4 -- Task 4.2: Implement IPC/In-Proc Bridge for UI-Python Communication

**Type:** `feature`

**Background:** Beyond initial invocation, the Python agent will need to communicate ongoing status or request actions from the Android side (e.g., perform a screen capture, simulate a tap via Accessibility Service). Similarly, Android UI events might need to trigger Python logic.

**Acceptance Criteria:**
*   A clear communication channel (either in-process callbacks via Chaquopy's Java/Python interop, or a simple local IPC if necessary) is established between the running Python agent and the Android service/UI.
*   Python agent can send a status message (e.g., "Thinking...", "Performing action X") back to the Android side, which can be displayed in the UI (e.g., a simple TextView update).
*   Android side can invoke a specific function in the Python agent to, for example, pause or cancel the current operation.
*   The chosen mechanism is justified (e.g., Chaquopy's direct interop is generally preferred for simplicity if sufficient).

**Dependencies:** Task 4.1 (Python agent running), Task 3.3 (Accessibility Service for actions)

**Parallelizable?:** `no`

**Suggested Labels:** `android`, `python`, `chaquopy`, `ipc`

**Effort Estimate:** M

**Definition of Done:** A robust communication bridge allowing two-way calls between Python logic and Android (service/UI) components. Status updates from Python can be reflected in the Android UI.
---
## Epic 5 -- OCR On-Device Integration
