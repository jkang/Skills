---
name: help-doc-creator
description: Updates project help documentation (README, guides, CLI help) to be visually engaging, highlight-focused, and workflow-oriented. Use when the user wants to improve documentation quality with "highlights", "visuals", and "complete workflows".
---

# Help Doc Creator

## Overview

This skill guides the creation of high-quality, visually engaging, and user-centric documentation. It focuses on transforming dry technical text into compelling "Getting Started" guides that highlight key features and provide clear, step-by-step workflows.

## Core Philosophy

1.  **Visual First**: Use ASCII art, emojis, badges, and diagrams (Mermaid/PlantUML) to break up text.
2.  **Highlight Driven**: Clearly articulate "Why this project?" at the top.
3.  **Workflow Centric**: Focus on *doing* rather than just *configuring*.

## Workflow

### Phase 0: Discovery & Audit (Crucial)

**Always start here.** Do not write a single word until you know what already exists.

1.  **Check Existing Documentation**:
    *   Look for `README.md`, `CONTRIBUTING.md`, `docs/`, `examples/`.
    *   Run `--help` or `man` if it's a CLI tool.
    *   Read code comments in entry points.

2.  **Evaluate Current State**:
    *   **If docs exist**: Your goal is **Renovation**.
        *   Keep accurate technical details.
        *   Identify what is outdated or missing.
        *   Restructure content into the "High Impact" format below.
        *   *Do not delete valid content* unless it is incorrect; instead, move it to "Advanced" sections.
    *   **If no docs exist**: Your goal is **Creation**.
        *   Infer functionality from code.
        *   Draft from scratch using the template below.

### Phase 1: Content Strategy

Before writing, analyze the target project.

1.  **Identify the "One Thing"**: What is the primary problem this project solves?
2.  **Extract Highlights**: Find 3-5 distinct features or benefits.
    *   *Good*: "Zero-config deployment"
    *   *Bad*: "Uses JSON configuration"
3.  **Map the "Happy Path"**: Define the exact sequence of commands for a new user to go from 0 to "Success".

### Phase 2: Structuring the Document

Use this standard high-impact structure for READMEs or Guides:

#### 1. Header Section
*   **Title**: Clear and bold.
*   **Badges**: Status, Version, License (use shields.io format if applicable).
*   **Visual Hook**: ASCII Art logo or a placeholder for a screenshot/GIF.
*   **Elevator Pitch**: 1 sentence summary.

#### 2. Highlights (The "Why")
*   Use a bulleted list with emojis.
*   Format: `[Emoji] **Feature Name**: Benefit description.`
*   Example:
    *   🚀 **Instant Start**: Pre-compiled binaries mean no installation wait.
    *   🛡️ **Type Safe**: Catch errors at compile time, not runtime.

#### 3. Quick Start (The "How")
*   **Prerequisites**: Minimal list.
*   **Installation**: Single command block (e.g., `npm install` or `pip install`).
*   **The "Hello World"**: The immediate command to see a result.
*   **Visual Feedback**: Show what the output should look like (use code blocks).

#### 4. Complete Workflow (The "Journey")
*   Guide the user through a common real-world scenario.
*   Use numbered steps.
*   Include "Pro Tips" or "Note" callouts.

### Phase 3: Visual Enhancement

Enhance the text with visual elements.

*   **File Trees**: Use `tree` style ASCII to show directory structure.
    ```text
    project/
    ├── src/
    │   └── main.py
    └── config.json
    ```
*   **Diagrams**: If explaining flow, propose a Mermaid diagram.
    ```mermaid
    graph LR
    A[User] --> B(CLI)
    B --> C{Database}
    ```
*   **Callouts**: Use blockquotes for emphasis.
    > 💡 **Tip**: Use the `--verbose` flag for more details.

## Checklist for Review

*   [ ] Does the top section explain *what* it is immediately?
*   [ ] Are the highlights compelling?
*   [ ] Is the Quick Start copy-pasteable?
*   [ ] Are there visual breaks (emojis, code blocks, diagrams)?
*   [ ] Is the tone active and encouraging?
