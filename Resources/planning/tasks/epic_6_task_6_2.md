# Epic 6 -- Task 6.2: Abstract LLM Planning Calls Behind a Provider Interface

**Type:** `feature`

**Background:** The agent will use Large Language Models (LLMs) for planning and decision making. To maintain flexibility (e.g., switch between OpenAI, Anthropic, or others), these calls should be abstracted behind a common interface.

**Acceptance Criteria:**
*   Define a Python abstract base class or interface (e.g., `LLMProvider`) with methods for common LLM tasks (e.g., `generate_plan(prompt, history)`).
*   Implement at least one concrete implementation for a specific LLM provider (e.g., `OpenAILLMProvider`).
*   The implementation handles API calls, including authentication (using secrets from Task 1.5) and error handling.
*   The agent's core logic uses the `LLMProvider` interface, not a concrete implementation directly.
*   Configuration allows easy switching between LLM providers (e.g., via an environment variable or a config file).

**Dependencies:** Task 1.5 (Secrets management)

**Parallelizable?:** `yes`

**Suggested Labels:** `python`, `ml`, `llm`, `api`, `architecture`

**Effort Estimate:** M

**Definition of Done:** An LLM provider interface and at least one concrete implementation, allowing the agent to make LLM calls without being tied to a specific provider.
---
## Epic 7 -- Safety & Human-in-the-Loop
