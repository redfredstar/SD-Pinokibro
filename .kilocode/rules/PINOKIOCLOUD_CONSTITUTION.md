
# The PinokioCloud Constitution (v1.0)

## **PREAMBLE: THE SUPREME LAW OF THE PROJECT**

This document is the single, consolidated, and supreme law governing the PinokioCloud Rebuild project. It is a binding contract that dictates every action the AI development agent will take. Adherence to these rules is not optional; it is the primary measure of success and capability. This Constitution supersedes any conflicting information in any other project document or general knowledge.

---

### **ARTICLE I: THE IMPLEMENTER'S MANDATES (The Four Laws)**

These are the unbreakable laws governing the execution of the Mandatory Operational Loop.

* **Section 1. The Law of Evidence**
  * **MANDATE**: All actions, plans, and code must be based exclusively on evidence gathered from the Architect's directive and an investigation of the project's authoritative files. Thou shalt not guess.
* **Section 2. The Law of Precision**
  * **MANDATE**: When debugging, modifications must be as minimal and targeted as possible to resolve the specific issue. Thou shalt not perform broad, unnecessary refactoring.
* **Section 3. The Law of Transparency**
  * **MANDATE**: All solutions must uphold or enhance the project's "Maximum Debug" philosophy. Thou shalt not remove, obscure, or simplify existing logging or error handling.
* **Section 4. The Law of Persistence**
  * **MANDATE**: A task is only complete upon a successful and verified SAVE operation. An artifact that is only printed to the chat is a failure.

---

### **ARTICLE II: CARDINAL PRINCIPLES (The Four Pillars)**

These are the four foundational philosophies upon which the entire project is built. They are the "spirit of the law."

* **Section 1. The Absolute Zero Placeholder Rule**
  * **MANDATE**: You will not, under any circumstances, create code that is incomplete, non-functional, or simulated. Every function, class, and file you produce must be 100% complete and production-ready at the moment of its creation.
  * **Forbidden Keywords**: `TODO`, `FIXME`, `NOT_IMPLEMENTED`, `PLACEHOLDER`.
  * **Forbidden Practices**: Using `pass` as a substitute for logic, returning mock values, simulating processes with `time.sleep()`, creating fake progress bars, or writing function signatures without a full implementation.
* **Section 2. The Maximum Debug Philosophy**
  * **MANDATE**: The system's primary role is to provide the user with a complete, raw, unfiltered, and transparent stream of diagnostic information to empower them to debug.
  * **Raw Output is Law**: All `stdout` and `stderr` from shell commands must be streamed to the UI in real-time without modification.
  * **Full Tracebacks Required**: Any `try...except` block must log the full, multi-line Python traceback. Simplified, "user-friendly" error messages are strictly forbidden.
  * **No Silent Failures**: No operation may fail without producing explicit, detailed output.
* **Section 3. The `ipywidgets` First Mandate**
  * **MANDATE**: The exclusive focus of all user interface development is `ipywidgets` within the Jupyter Notebook. The architectural principle is "the notebook is the application."
  * **Out of Scope**: No code related to Streamlit, Flask, or any other web UI framework will be written. Streamlit is a post-rebuild, out-of-scope goal.
* **Section 4. The Conda-First, `venv` Fallback Strategy**
  * **MANDATE**: The system will default to using Conda for environment management due to its robust handling of complex dependencies.
  * **The Exception**: The `P04_EnvironmentManager` MUST automatically switch its strategy to use `venv` if, and only if, the Lightning AI platform is detected by the `P01_CloudDetector`.

---

### **ARTICLE III: CODE OF CONDUCT (Strict Coding Standards)**

These are the specific, measurable standards for all code written for this project.

* **Section 1. File & Class Structure**
  * A single Python file (`.py`) shall not exceed 500 lines.
  * All functionality must be encapsulated in a class (Keep Object-Oriented, Please).
  * Every file, class, and function must adhere to the Single Responsibility Principle (SRP).
  * "God classes" are forbidden; logic must be split into UI, State, Handlers, Managers, etc.
* **Section 2. Function & Method Design**
  * A single function or method shall not exceed 40 lines of code.
  * Code must be modular, loosely coupled, and reusable, avoiding hardcoded dependencies in favor of dependency injection.
* **Section 3. Naming & Readability**
  * All names must be descriptive and intention-revealing. Vague names like `data`, `info`, or `helper` are forbidden.
  * **Phase-Prefix Mandate**: Every new Python file in the `/app` directory **MUST** be prefixed with its phase of origin (e.g., `P01_CloudDetector.py`).
  * **Test File Naming Convention**: All test files in the `/app/Test` directory **MUST** follow the format `PXX-Test_ModuleName.py` (e.g., `P01-Test_CloudDetector.py`).

---

### **ARTICLE IV: OPERATIONAL PROTOCOLS (Mandatory Workflows)**

These are the rules governing the development workflow.

* **Section 1. The End-of-Stage Audit Protocol**
  * At the conclusion of phases P06, P12, P18, and P20, a mandatory Audit Phase must be performed.
  * The audit includes: linting, comprehensive review, completing the Stage Validation Checklist, and updating both `CAPTAINS_LOG.md` and `INDEX.md`.
* **Section 2. The `CAPTAINS_LOG.md` Update Protocol**
  * The log must be updated continuously throughout a work session as part of every implementation prompt's final deliverable. A "CURRENT SESSION" block is used for live work and is archived upon completion.
* **Section 3. The `INDEX.md` Update Protocol**
  * The `INDEX.md` file will **only** be updated during an official End-of-Stage Audit phase to ensure it remains a stable reference.
* **Section 4. Version Control Protocol (Single `main` Branch Rule)**
  * All development will occur on the single, existing `main` branch. Creating, checking out, or pushing to any other branches is strictly forbidden.

---

### **ARTICLE V: ADHERENCE & ENFORCEMENT**

* **Section 1. The Prime Directive**
  * These rules are the foundation of the project's success. Adherence demonstrates your capability. Any deviation will be considered a failure to follow instructions and will require immediate correction. There is no ambiguity in these laws.
