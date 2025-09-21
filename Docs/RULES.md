# RULES.md - The Constitution

## **PREAMBLE: THE SUPREME LAW OF THE PROJECT**

This document is the supreme law governing the PinokioCloud Rebuild project. It is not a guide, a suggestion, or a set of best practices. It is a **binding contract** that dictates every action you, the AI development agent, will take. Adherence to these rules is not optional; it is the primary measure of your success and capability.

Any deviation, assumption, or action taken contrary to these rules constitutes a critical failure of your mission. You will read, internalize, and obey these laws without exception. The contents of this document are the final authority, superseding any conflicting information in any other project document, including the v1 codebase archive.

---

### **SECTION 1: CARDINAL PRINCIPLES (THE PHILOSOPHIES OF THE REBUILD)**

These are the four foundational pillars upon which the entire project is built. They inform every architectural decision and every line of code. They are the "spirit of the law" that must be understood and respected at all times.

#### **1.1 The Absolute Zero Placeholder Rule**

**MANDATE**: You will not, under any circumstances, create code that is incomplete, non-functional, or simulated. Every function, class, and file you produce must be 100% complete and production-ready at the moment of its creation. This is the project's most important law, designed to prevent the cascading failures and hidden work of the v1 implementation.

*   **Forbidden Keywords**: The following strings are strictly forbidden in any code file, including comments: `TODO`, `FIXME`, `NOT_IMPLEMENTED`, `PLACEHOLDER`, `XXX`, `HACK`.
*   **Forbidden Practices**:
    *   You WILL NOT use `pass` in a function or method body as a substitute for logic. Every function must have a complete and functional implementation.
    *   You WILL NOT write a function that returns a hardcoded or mock value (e.g., `return True`, `return {"status": "ok"}`) to simulate a complex operation. The only exception is for genuine, simple cases like configuration getters that return a static, documented value.
    *   You WILL NOT simulate long-running processes with `time.sleep()` to give the appearance of work. All delays must be the result of actual computation, I/O operations, or network requests.
    *   You WILL NOT create fake progress bars. All progress indicators must be mathematically and logically tied to the real, measurable progress of a backend task (e.g., file download percentage, number of steps completed in a multi-step installation).
    *   You WILL NOT write a function signature and leave its implementation for a later phase. If a function is created, it must be completed in its entirety within that same phase, including docstrings, type hints, and error handling.

#### **1.2 The Maximum Debug Philosophy**

**MANDATE**: The system's primary role in handling errors and processes is to provide the user with a complete, raw, unfiltered, and transparent stream of diagnostic information. The system must empower the user to debug; it must not attempt to hide complexity, summarize errors, or solve problems autonomously. This is a direct response to the critical failures of the v1 project where opaque outputs hid fundamental problems.

*   **Raw Output is Law**: All output (`stdout` and `stderr`) from any shell command executed via the `P02_ProcessManager` MUST be captured and streamed to the user interface in real-time, without any summarization, simplification, or modification. The user must see exactly what the underlying process is doing, second-by-second, including all warnings, progress bars, and error messages.
*   **Full Tracebacks Required**: Any `try...except` block that catches an exception MUST log the full, multi-line Python traceback to the main terminal. You are expressly forbidden from catching an exception and only showing a simplified, one-line "user-friendly" error message like "An error occurred." The technical detail *is* the feature.
*   **No Silent Failures**: No operation, from a file copy to a network request, may fail without producing explicit, detailed output in the terminal explaining the failure.

#### **1.3 The `ipywidgets` First Mandate**

**MANDATE**: The exclusive focus of all user interface development is `ipywidgets` within the Jupyter Notebook. The architectural principle is "the notebook is the application."

*   **Exclusive Focus**: You will not write any code related to Streamlit, Flask, Dash, or any other web UI framework. All UI components will be built using the `ipywidgets` library and will be rendered directly in the output of a notebook cell.
*   **Out of Scope**: Streamlit is documented in `MASTER_GUIDE.md` as a "Post-Rebuild Deprecated Goal" and is strictly out of scope for the current development. You will not implement any features related to it or suggest it as an alternative.

#### **1.4 The Conda-First, `venv` Fallback Strategy**

**MANDATE**: The system will default to using Conda for its superior handling of complex AI/ML dependencies. It will only use `venv` in explicitly defined exceptional circumstances.

*   **Default Environment**: The `P04_EnvironmentManager` MUST default to creating and managing Conda environments for all Pinokio applications.
*   **Platform-Aware Fallback**: The `P04_EnvironmentManager` MUST use the `P01_CloudDetector` to identify the Lightning AI platform. If detected, and only if detected, it MUST automatically switch its strategy to use `venv` for all environment operations for any application being installed on that platform. This is the only approved exception to the Conda-first rule.

---

### **SECTION 2: THE CODE OF CONDUCT (STRICT CODING STANDARDS)**

These are the specific, measurable standards for all code written for this project, as directed by the project lead. They are not suggestions. They will be enforced during every Stage Audit.

#### **2.1 File & Class Structure**
*   **`file_length_and_structure`**: A single Python file (`.py`) WILL NOT exceed 500 lines. If you project a file will exceed this limit, you must immediately break it up into smaller, logically grouped modules. Use folders to keep these related small files organized.
*   **`koop_first` (Keep Object-Oriented, Please)**: Every distinct piece of functionality MUST be encapsulated within a dedicated class. Free-floating functions in a file are forbidden, unless they are simple, static utility helpers that do not manage state. Code must be built for reuse.
*   **`single_responsibility_principle` (SRP)**: Every file, class, and function must have one, and only one, reason to change. If a class designed for installation (`P07_InstallManager`) also contains logic for launching an application, it is a violation of this rule and must be refactored. Each component must be laser-focused on one concern.
*   **`avoid_god_classes`**: Never allow a single file or class to hold an excessive amount of responsibility (e.g., a massive `PinokioEngine` class). Logic must be split into UI, State, Handlers, Managers, etc.
*   **`class_size`**: If a class grows beyond 200 lines, you must assess if it can be split into smaller helper classes that follow the SRP.

#### **2.2 Function & Method Design**
*   **`function_size`**: A single function or method WILL NOT exceed 40 lines of code. This promotes clarity, testability, and single responsibility.
*   **`modular_design`**: Your code must be architected like Lego bricks. Components should be loosely coupled, testable in isolation, and reusable. Hardcoded dependencies between modules are to be avoided in favor of passing data objects and callback functions. Ask yourself: "Can I reuse this class in a different project?" If not, refactor it.

#### **2.3 Naming & Readability**
*   **`naming_and_readability`**: All class, method, and variable names must be descriptive and intention-revealing. Vague names like `data`, `info`, `temp`, `my_manager`, or `helper` are strictly forbidden. A class that manages application state must be named `StateManager`, not `DataHelper`.
*   **`Phase-Prefix Mandate`**: Every new Python file you create as part of the repository's application code (`/app` directory) MUST be prefixed with its phase of origin (e.g., `P01_CloudDetector.py`, `P08_StateManager.py`). This is non-negotiable and provides a clear audit trail of the project's construction.
*   **`Test File Naming Convention`**: All test files MUST follow the pattern `PXX-Test_ModuleName.py` where `PXX` is the phase number and `ModuleName` is the name of the module being tested. For example, a test file for `P01_CloudDetector.py` must be named `P01-Test_CloudDetector.py`. This ensures consistent organization and easy identification of test files.
*   **`Test File Naming Convention`**: All test files in the `/App/Test` directory MUST follow the format `PXX-Test_ModuleName.py` (e.g., `P01-Test_CloudDetector.py`, `P04-Test_EnvironmentManager.py`). This ensures consistency with the phase-prefix mandate and makes test files easily identifiable. The format uses hyphens to separate the phase, the word "Test", and the module name being tested.

#### **2.4 Architectural Mindset**
*   **`scalability_mindset`**: Always code as if another developer will need to extend and scale your work. Include extension points like protocol conformance and dependency injection from day one.
*   **`manager_and_coordinator_patterns`**: Use clear naming conventions for logic separation where appropriate: UI logic -> ViewModel/Controller, Business logic -> Manager, Navigation/state flow -> Coordinator. Business logic must never be mixed directly with UI code.

---

### **SECTION 3: OPERATIONAL PROTOCOLS (AI AGENT MANDATES)**

These are the rules governing your workflow and behavior as the development agent.

#### **3.1 The End-of-Stage Audit Protocol**
*   At the conclusion of the final development phase of each stage (P06, P12, P18, P20), you will enter a mandatory Audit Phase. You must perform the following actions in this exact order:
    1.  **Lint & Code Quality Check**: Run automated linters (`flake8`) and formatters (`black`) across all new code produced during the stage to ensure it meets the project's style guides.
    2.  **Comprehensive Review**: Manually review the architecture and implementation of the stage's features against the `MASTER_GUIDE.md` and this `RULES.md` document to ensure perfect compliance.
    3.  **Validation Checklist**: Complete the "Stage Validation Checklist" found at the end of the current stage's description in `MASTER_GUIDE.md`. This is a mandatory self-assessment to ensure feature parity.
    4.  **Update `CAPTAINS_LOG.md`**: Write a detailed summary of the stage's accomplishments, challenges faced, and solutions implemented.
    5.  **Update `INDEX.md`**: Meticulously update the "Script & File Index" with detailed entries for every single new file created during the stage, as per the format defined in the `INDEX.md` blueprint.

#### **3.2 The `CAPTAINS_LOG.md` Update Protocol**
*   You will update the `CAPTAINS_LOG.md` document **continuously** throughout your work session.
*   At the start of a session, you will create a new "CURRENT SESSION" block.
*   During the session, you will add timestamped log entries detailing your actions, any errors encountered, the root cause, and the solutions you implemented. This log is your primary workspace for tracking your thought process.
*   At the end of a session, you will finalize the "CURRENT SESSION" block by adding a `Session Summary` and moving it to the "Previous Sessions" archive.

#### **3.3 The `INDEX.md` Update Protocol**
*   You will **only** update the `INDEX.md` file during an official End-of-Stage Audit phase, as specified in Protocol 3.1. This ensures the master index remains a stable reference throughout a development stage and is only updated with fully audited code.

#### **3.4 Version Control Protocol (Single `main` Branch Rule)**
*   All development will occur on the single, existing `main` branch of the repository.
*   You are strictly forbidden from creating, checking out, or pushing to any other branches (e.g., `dev`, `master`, `feature/*`). Every commit will be made directly to `main`.

---

### **SECTION 4: THE PRIME DIRECTIVE: ADHERENCE & ENFORCEMENT**

These rules are the foundation of the project's success. Your adherence demonstrates your capability. Any deviation will be considered a failure to follow instructions and will require immediate correction. There is no ambiguity in these laws. You will follow them to the letter.
