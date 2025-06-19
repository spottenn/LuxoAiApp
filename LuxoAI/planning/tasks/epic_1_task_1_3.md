# Epic 1 -- Task 1.3: Integrate Chaquopy (Python-on-Android) into Gradle

**Type:** `feature`

**Background:** The core agent logic is in Python. Chaquopy allows running Python code within an Android app. This task is to set up the initial Chaquopy integration in the Android project.

**Acceptance Criteria:**
*   Chaquopy SDK is correctly configured in `build.gradle.kts` files.
*   A simple Python script (e.g., `print("Hello from Python")`) can be packaged into the APK.
*   The Python script can be successfully executed from Android (Kotlin/Java) code and its output captured (e.g., logged).
*   Basic Python dependencies (e.g., a small utility from pip) can be included and used.

**Dependencies:** Task 1.1

**Parallelizable?:** `no` (fundamental for Python embedding)

**Suggested Labels:** `android`, `python`, `chaquopy`, `gradle`

**Effort Estimate:** M

**Definition of Done:** The LuxoAI app successfully builds with Chaquopy, and a basic Python script runs on app startup, with its output visible in Android's Logcat.
---
