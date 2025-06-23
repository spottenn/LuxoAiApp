# Contributing to LuxoAI

We welcome contributions to the LuxoAI project! Please adhere to the following guidelines to ensure a smooth development process.

## Commit Message Conventions

This project follows the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification. This leads to more readable commit history and makes it easier to automate tasks like generating changelogs.

### Format

Each commit message consists of a **header**, a **body**, and a **footer**.

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

*   **Header**:
    *   `<type>`: Describes the kind of change that this commit is providing. Common types include:
        *   `feat`: A new feature.
        *   `fix`: A bug fix.
        *   `docs`: Documentation only changes.
        *   `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc).
        *   `refactor`: A code change that neither fixes a bug nor adds a feature.
        *   `perf`: A code change that improves performance.
        *   `test`: Adding missing tests or correcting existing tests.
        *   `build`: Changes that affect the build system or external dependencies (example scopes: gradle, npm, pip).
        *   `ci`: Changes to our CI configuration files and scripts (example scopes: GitHub Actions).
        *   `chore`: Other changes that don't modify src or test files (e.g., updating build tasks, package manager configs).
    *   `[optional scope]`: A noun describing a section of the codebase surrounded by parenthesis, e.g., `feat(parser):`.
    *   `<description>`: A short summary of the code changes.
        *   Use the imperative, present tense: "change" not "changed" nor "changes".
        *   Don't capitalize the first letter.
        *   No dot (.) at the end.

*   **Body** (Optional):
    *   Should also use the imperative, present tense.
    *   Include motivation for the change and contrast this with previous behavior.
    *   **Project Specific**: As per `jules.md`, please reference the full task filename (e.g., `epic_X_task_X_Y.md`) in the commit body if the commit pertains to a specific task.

*   **Footer** (Optional):
    *   Used for referencing issue tracker IDs (e.g., `Fixes #123`) or for breaking changes.
    *   **BREAKING CHANGE**: A commit that has a footer beginning with `BREAKING CHANGE:` introduces a breaking API change. A BREAKING CHANGE can be part of any type of commit.

### Examples

```
feat: allow provided config object to extend other configs

This feature allows users to extend existing configuration files by
providing a path to a base config in the new `extends` property.

Task: epic_3_task_3_1.md
```

```
fix(android): correct button alignment on small screens

The primary action button was previously misaligned on devices with
screen widths below 360dp. This commit adjusts the layout constraints
to ensure proper alignment.

Task: epic_2_task_2_4.md
Closes #42
```

```
docs: explain commit convention and code style

Task: epic_9_task_9_3.md
```

### Tips for Good Commit Messages

*   Keep the subject line concise (ideally under 50 characters, hard limit around 72).
*   Explain *what* the change is and *why* you are making it, not *how* (the code itself shows how).
*   If your commit addresses multiple unrelated changes, split it into separate commits.

## Code Style Guidelines

Consistent code style makes the codebase easier to read and maintain.

### Python

*   Follow **[PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)**.
*   We may introduce linters (e.g., Flake8) and formatters (e.g., Black) in the future to help enforce these guidelines.

### Kotlin

*   Follow the **[official Kotlin Coding Conventions](https://kotlinlang.org/docs/coding-conventions.html)** by JetBrains.
*   Android Studio's default formatter generally aligns with these conventions. Use it to format your Kotlin code.

### General

*   Write clear and readable code. Add comments where necessary to explain complex logic.
*   Keep lines to a reasonable length (e.g., aim for under 100-120 characters).

## Development Workflow

1.  **Understand your task**: Refer to the specific task file in `docs/planning/tasks/`.
2.  **Create a branch**: Use a descriptive branch name (e.g., `feat/user-authentication`, `fix/payment-gateway-bug`).
3.  **Implement and test**: Write your code and ensure it's accompanied by relevant tests.
4.  **Commit your changes**: Follow the commit message conventions outlined above.
5.  **Push and create a Pull Request** (if applicable to the workflow).

By following these guidelines, you help us maintain a clean, understandable, and collaborative development environment. Thank you for contributing!
