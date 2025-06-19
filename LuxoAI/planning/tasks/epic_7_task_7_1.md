# Epic 7 -- Task 7.1: Implement Opt-in Confirmation Checkpoints for Potentially Destructive Actions

**Type:** `feature`

**Background:** To prevent the agent from taking irreversible or sensitive actions without user consent (e.g., making purchases, deleting files, sharing sensitive info), confirmation checkpoints are needed. These should be opt-in to avoid excessive interruptions for safe tasks.

**Acceptance Criteria:**
*   Identify categories of actions that should be considered "potentially destructive" or "sensitive."
*   Before executing such an action, the Python agent (via the bridge in Task 4.2) requests confirmation from the Android UI.
*   The Android UI displays a clear confirmation dialog (e.g., "Agent wants to [action]. Allow? Yes/No").
*   The agent pauses execution until the user responds.
*   The user's decision (allow/deny) is sent back to the Python agent, which proceeds or cancels accordingly.
*   This confirmation mechanism can be globally enabled/disabled or configured per category of action (e.g., via settings).

**Dependencies:** Task 4.2 (IPC/In-Proc Bridge)

**Parallelizable?:** `no` (relies on core agent-UI communication)

**Suggested Labels:** `safety`, `ui`, `android`, `python`, `human-in-the-loop`

**Effort Estimate:** M

**Definition of Done:** A system where the agent requests user confirmation via a UI dialog before performing defined sensitive/destructive actions.
---
