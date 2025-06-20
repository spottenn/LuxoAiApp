Status: Not Started

# Epic 7 -- Task 7.2: Add Easy Manual Override / Cancel Functionality

**Type:** `feature`

**Background:** The user must always be able to easily stop or override the agent's current operation, regardless of what it's doing.

**Acceptance Criteria:**
*   A persistent "Cancel Agent" button or notification action is available in the Android UI while the agent is running.
*   Activating this "Cancel" mechanism immediately signals the Python agent (via Task 4.2) to halt its current operations gracefully.
*   The Python agent stops as quickly as possible, cleaning up any intermediate state if necessary.
*   The Android UI updates to reflect that the agent has been cancelled.
*   Consider a "Pause/Resume" functionality as an extension if straightforward.

**Dependencies:** Task 3.2 (Foreground service for persistent UI), Task 4.2 (IPC/In-Proc Bridge)

**Parallelizable?:** `no` (relies on core agent-UI communication)

**Suggested Labels:** `safety`, `ui`, `android`, `python`, `human-in-the-loop`

**Effort Estimate:** M

**Definition of Done:** A reliable way for the user to cancel the agent's current task at any time through the Android UI.
---
## Epic 8 -- Automated Testing Suite
