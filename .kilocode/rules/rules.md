# rules.md

This document is the supreme law governing the PinokioCloud Rebuild project. It is a binding contract that dictates every action the AI development agent will take. Adherence to these rules is not optional; it is the primary measure of success and capability. Any deviation, assumption, or action taken contrary to these rules constitutes a critical failure of the mission. The contents of this document are the final authority, superseding any conflicting information in any other project document.

## Guidelines - Cardinal Principles

-   **The Absolute Zero Placeholder Rule**
    -   **MANDATE**: You will not, under any circumstances, create code that is incomplete, non-functional, or simulated. Every function, class, and file you produce must be 100% complete and production-ready at the moment of its creation.
    -   Forbidden keywords include `TODO`, `FIXME`, `NOT_IMPLEMENTED`, `PLACEHOLDER`.
    -   Forbidden practices include using `pass` as a substitute for logic, returning mock values, simulating processes with `time.sleep()`, creating fake progress bars, or writing function signatures without a full implementation.

-   **The Maximum Debug Philosophy**
    -   **MANDATE**: The system's primary role is to provide the user with a complete, raw, unfiltered, and transparent stream of diagnostic information to empower them to debug.
    -   All `stdout` and `stderr` from shell commands must be streamed to the UI in real-time without modification.
    -   Any `try...except` block must log the full, multi-line Python traceback. Simplified error messages are forbidden.
    -   No operation may fail silently; all failures must produce explicit, detailed output.

-   **The `ipywidgets` First Mandate**
    -   **MANDATE**: The exclusive focus of all user interface development is `ipywidgets` within the Jupyter Notebook.
    -   No code related to Streamlit, Flask, or any other web UI framework will be written.
    -   Streamlit is documented as a post-rebuild deprecated goal and is strictly out of scope.

-   **The Conda-First, `venv` Fallback Strategy**
    -   **MANDATE**: The system will default to using Conda for environment management and will only use `venv` in explicitly defined exceptional circumstances.
    -   The `P04_EnvironmentManager` must default to creating Conda environments.
    -   It must automatically switch to `venv` if, and only if, the Lightning AI platform is detected.

## Guidelines - Code of Conduct

-   **File & Class Structure**
    -   A single Python file shall not exceed 500 lines.
    -   All functionality must be encapsulated in a class (Keep Object-Oriented, Please).
    -   Every file, class, and function must adhere to the Single Responsibility Principle (SRP).
    -   "God classes" are forbidden; logic must be split into UI, State, Handlers, etc.
    -   Classes growing beyond 200 lines must be assessed for refactoring.

-   **Function & Method Design**
    -   A single function or method shall not exceed 40 lines of code.
    -   Code must be modular, loosely coupled, and reusable, avoiding hardcoded dependencies.

-   **Naming & Readability**
    -   All class, method, and variable names must be descriptive and intention-revealing. Vague names like `data`, `info`, or `helper` are forbidden.
    -   Every new Python file in the `/app` directory must be prefixed with its phase of origin (e.g., `P01_CloudDetector.py`).

-   **Architectural Mindset**
    -   Code must be designed for scalability with extension points.
    -   Use patterns like Manager/Coordinator to separate business logic from UI code.

## Guidelines - Operational Protocols

-   **The End-of-Stage Audit Protocol**
    -   At the conclusion of phases P06, P12, P18, and P20, a mandatory Audit Phase must be performed.
    -   The audit includes: linting, comprehensive review against `MASTER_GUIDE.md` and `RULES.md`, completing the Stage Validation Checklist, and updating `CAPTAINS_LOG.md` and `INDEX.md`.

-   **The `CAPTAINS_LOG.md` Update Protocol**
    -   The log must be updated continuously throughout a work session.
    -   A "CURRENT SESSION" block is created at the start and finalized/archived at the end of the session.

-   **The `INDEX.md` Update Protocol**
    -   The `INDEX.md` file will only be updated during an official End-of-Stage Audit phase.

-   **Version Control Protocol (Single `main` Branch Rule)**
    -   All development will occur on the single, existing `main` branch.
    -   Creating, checking out, or pushing to any other branches is strictly forbidden.

## Guidelines - Adherence & Enforcement

-   **The Prime Directive**
    -   These rules are the foundation of the project's success. Adherence demonstrates your capability.
    -   Any deviation will be considered a failure to follow instructions and will require immediate correction.
    -   There is no ambiguity in these laws. You will follow them to the letter.