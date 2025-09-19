# MASTER_GUIDE.md - The Blueprint

## **PREAMBLE: THE AUTHORITATIVE ROADMAP**

This document is the definitive architectural and strategic plan for the PinokioCloud Rebuild project. It dictates **what** will be built and in **what sequence**. While `RULES.md` defines the laws of *how* to build, this Master Guide provides the complete, phase-by-phase roadmap. All development must be executed in precise alignment with this plan. There is no other authoritative source for the project's structure or timeline.

---

### **SECTION 1: THE DEFINITIVE 22-PHASE ROADMAP**

The project is organized into five distinct stages, each comprising granular development phases. Each stage concludes with a mandatory audit phase to ensure quality and adherence to the project's principles.

---

#### **Stage 1: System Foundation & Core Engines (Phases 1-6)**
*   **P01**: System Foundation & Cloud Adaptation
*   **P02**: The All-Seeing Eye (Real-Time Monitoring Engine)
*   **P03**: The Universal Translator (Installer Conversion Engine)
*   **P04**: The Environment Architect (Conda/Venv Engine)
*   **P05**: The App Analyzer (Pre-Installation Engine)
*   **P06**: **Stage 1 Audit, Lint & Documentation Review**

#### **Stage 2: The Installation Gauntlet (Phases 7-12)**
*   **P07**: Part A: In-Repo Installation Engine (Core Logic)
*   **P08**: Part B: In-Repo Installation Engine (Advanced Logic & State)
*   **P09**: Part C: In-Notebook Installation UI (Integration & Feedback)
*   **P10**: Part D: In-Notebook Installation UI (State & User Input)
*   **P11**: The Digital Bookshelf (Library Engine & UI)
*   **P12**: **Stage 2 Audit, Lint & Documentation Review**

#### **Stage 3: The Launch Sequence (Phases 13-18)**
*   **P13**: Part A: In-Repo Launch Engine (Core Process Management)
*   **P14**: Part B: In-Repo Launch Engine (WebUI & Tunneling)
*   **P15**: Part C: In-Notebook Launch UI (Initiation & Monitoring)
*   **P16**: Part D: In-Notebook Launch UI (URL Display & Control)
*   **P17**: The Gatekeeper (Post-Launch Validation & Certification)
*   **P18**: **Stage 3 Audit, Lint & Documentation Review**

#### **Stage 4: Final Integration & Polish (Phases 19-20)**
*   **P19**: Full System Integration & User Experience Polish
*   **P20**: **Stage 4 Audit & Final Handover Documentation**

#### **Stage 5: The Testing Gauntlet & Project Completion (Phases T1-T4)**
*   **T1**: Test Environment Design (Invent 5 Methods)
*   **T2**: Critical Analysis & Selection (Critique & Choose 3)
*   **T3**: The Gauntlet Run (Execute Tests)
*   **T4**: Project Completion & Post-Mortem

---
---

### **SECTION 2: DETAILED PHASE-BY-PHASE IMPLEMENTATION PLAN**

---

### **Stage 1: System Foundation & Core Engines (Phases 1-6)**

**Overarching Objective**: To construct the complete, robust, and cloud-aware foundation upon which the entire PinokioCloud application will be built. This stage is the most critical, as it establishes the core architectural patterns, development philosophies, and essential backend engines.

---

#### **Phase P01: System Foundation & Cloud Adaptation**
*   **Objective**: To establish the project's core structure and prove its fundamental promise: the ability to intelligently adapt to any target cloud environment from the very first run.
*   **In-Repo Engine Development**:
    1.  **Repository Structure**: Create the master directory structure: `/v1_deprecated/` (for old code), `/docs/` (for new docs), and `/app/` (subdivided into `/core/` and `/utils/`).
    2.  **Cloud Detection Module (`app/utils/P01_CloudDetector.py`)**: Develop a class-based module to perform hierarchical checks and identify the operating environment (Colab, Vast.ai, Lightning.ai, etc.), outputting a standardized `PlatformInfo` data object.
    3.  **Path Mapping Module (`app/utils/P01_PathMapper.py`)**: Develop an abstraction layer for all file system paths that consumes the `PlatformInfo` object and provides semantic path requests (e.g., `get_base_path()`). No other module will ever construct a hardcoded path.
*   **In-Notebook UI Development**:
    1.  Create the `launcher.ipynb` with its initial 3-cell structure: Cell 1 (Repo clone & dependencies), Cell 2 (Engine init & platform detection verification), Cell 3 (Foundational `ipywidgets` UI skeleton with main `Tab` and empty `Output` widgets for each tab).
*   **Success Criteria**: The `launcher.ipynb` executes without error, correctly identifies its cloud environment, and displays a basic, non-functional UI shell. The core architectural pattern is validated.

---

#### **Phase P02: The All-Seeing Eye (Real-Time Monitoring Engine)**
*   **Objective**: To physically implement the "Maximum Debug" philosophy by creating the engine and UI components for a real-time, unfiltered feedback loop.
*   **In-Repo Engine Development**:
    1.  **Process Manager (`app/core/P02_ProcessManager.py`)**: Develop the core `ProcessManager` class. Its `shell_run` method must use Python's `asyncio` to execute commands non-blockingly.
    2.  **Callback Architecture**: The `shell_run` method must be architected to accept a `callback` function. For every line of `stdout` or `stderr` generated, this callback must be invoked immediately with the line of text.
    3.  **PID Tracking**: The manager must capture and store the Process ID (PID) for every process it spawns.
*   **In-Notebook UI Development**:
    1.  Implement a `stream_to_terminal(line)` callback function in the notebook that appends text to the "Terminal" `Output` widget.
    2.  Create a diagnostic button in the UI that calls `shell_run` with a test command, passing the `stream_to_terminal` callback to demonstrate the end-to-end feedback loop.
*   **Success Criteria**: Clicking the diagnostic button results in the complete, live, unfiltered output of the shell command being streamed line-by-line into the "Terminal" tab of the `ipywidgets` UI.

---

#### **Phase P03: The Universal Translator (Installer Conversion Engine)**
*   **Objective**: To build an abstraction layer that tames the complexity of Pinokio's diverse installer formats, converting them into a single, standardized Python-based "recipe".
*   **In-Repo Engine Development**:
    1.  **Translator Module (`app/utils/P03_Translator.py`)**: Develop a class with parsing methods for `.json`, `requirements.txt`, and `.js` files.
    2.  **JavaScript Parsing**: The `parse_js` method must **avoid a Node.js runtime**, instead using advanced regex and pattern matching to extract commands and parameters from the common structures found in Pinokio `install.js` files.
    3.  **Standardized Output**: All parsing methods must return a consistent data structure: a Python `list` of `dict`, representing the standardized installation workflow.
*   **In-Notebook UI Development**:
    1.  Create a temporary development tool in the notebook with a file upload widget and a "Translate" button to allow for rapid testing and validation of the translation logic against real installer files.
*   **Success Criteria**: The `P03_Translator` can successfully parse real-world `install.json`, `install.js`, and `requirements.txt` files and output a valid, standardized Python recipe.

---

#### **Phase P04: The Environment Architect (Conda/Venv Engine)**
*   **Objective**: To build the specialized, platform-aware engine responsible for managing application isolation through virtual environments.
*   **In-Repo Engine Development**:
    1.  **Environment Manager (`app/core/P04_EnvironmentManager.py`)**: Develop a class that uses the `P01_CloudDetector` at initialization to determine its strategy. If Lightning AI is detected, it must internally disable all Conda operations and use `venv` exclusively.
    2.  **Core Abstractions**: It must provide an abstracted `create(env_name)` method and a critical `get_run_prefix(env_name)` method that returns the exact command-line prefix required to execute a command within a given environment.
*   **In-Notebook UI Development**:
    1.  Create a simple development UI in the notebook to test the creation of Conda and `venv` environments and view the raw output in the terminal.
*   **Success Criteria**: The engine can successfully create Conda environments on standard platforms and correctly falls back to creating `venv` environments on Lightning AI. The `get_run_prefix` method returns the correct activation command for both scenarios.

---

#### **Phase P05: The App Analyzer (Pre-Installation Engine)**
*   **Objective**: To build the intelligence that allows the system to perform a "pre-flight check" on any application, informing the user of its requirements before installation begins.
*   **In-Repo Engine Development**:
    1.  **Analyzer Module (`app/utils/P05_AppAnalyzer.py`)**: Develop this as a static analysis tool. Its primary method will take the standardized Python recipe from the `P03_Translator` as input and will not execute any commands.
    2.  **Metadata Extraction**: It will iterate through the recipe data structure and use pattern matching to extract pre-flight metadata: required environment type, key dependencies, resource hints (VRAM, disk space), and `daemon: true` flags.
*   **In-Notebook UI Development**:
    1.  Build the first functional version of the "Discover" tab, loading the application list from `apps.json`.
    2.  The UI will be wired to orchestrate the sequence on user selection: `select app` -> `call P03_Translator` -> `call P05_AppAnalyzer` -> `display formatted metadata in the details pane`.
*   **Success Criteria**: A user can select any app in the "Discover" tab and immediately see a clear, human-readable summary of its technical requirements in the UI.

---

#### **Phase P06: Stage 1 Audit, Lint & Documentation Review**
*   **Objective**: To harden the entire foundation, ensuring the codebase is clean, professional, and extensively documented before proceeding.
*   **Audit Tasks**:
    1.  Lint and review all code from P01-P05.
    2.  Perform the first major integration test of the P05 user flow.
    3.  Complete the "Stage 1 Validation Checklist" below.
*   **Documentation Tasks**:
    1.  Flesh out the initial documents: `RULES.md`, `MASTER_GUIDE.md`, `AI_VM_TESTING_GUIDE.md`, `SECURITY_MEMO.md`.
    2.  Create the token-efficient `PINOKIO_SCROLLS.md` from the original documentation.
    3.  Perform the first major update to `INDEX.md`, populating the Document Index and creating the Script Index for all files from Stage 1.
    4.  Write a detailed summary of Stage 1 in `CAPTAINS_LOG.md`.
*   **Success Criteria**: The project has a professional-grade, stable, and fully documented foundational codebase and documentation suite.

---
### **Stage 1 Validation Checklist**
*(To be completed by the AI agent during the Phase P06 Audit. This checklist ensures feature parity with the v1 codebase by focusing on core capabilities.)*

*   **[ ] Platform Detection**: Does the system now provide the capability to reliably detect the current cloud platform (Colab, Vast.ai, etc.) and load platform-specific configurations?
*   **[ ] Path Abstraction**: Does the system now provide the capability to abstract file paths, ensuring code is portable and works correctly across different cloud filesystems?
*   **[ ] Resource Assessment**: Does the system now provide the capability to assess basic system resources like GPU type and available memory?
*   **[ ] Real-Time Output Streaming**: Does the system now provide the capability to execute a shell command and stream its raw, unfiltered `stdout` and `stderr` in real-time to a callback function?
*   **[ ] Installer Translation**: Does the system now provide the capability to parse both `.json` and `.js` Pinokio install scripts into a standardized, internal Python recipe?
*   **[ ] Environment Management**: Does the system now provide the capability to create isolated Conda environments and, specifically, fall back to `venv` when on the Lightning AI platform?

---
---

### **Stage 2: The Installation Gauntlet (Phases 7-12)**

**Overarching Objective**: To construct a completely reliable, transparent, and robust system for installing any Pinokio application. This stage transforms the project from a system that *understands* installers to one that can *execute* them flawlessly.

---

#### **Phase P07: Part A: In-Repo Installation Engine (Core Logic)**
*   **Objective**: To build the core "workhorse" engine component that can take a standardized installation recipe and execute it step-by-step.
*   **In-Repo Engine Development**:
    1.  **Installation Manager (`app/core/P07_InstallManager.py`)**: Develop a new headless class to orchestrate the installation process.
    2.  **Workflow Execution (`install_app` method)**: This method will accept the standardized Python recipe and an application name. It will loop through each step, dispatching the task to the appropriate engine module (`P02_ProcessManager`, `P04_EnvironmentManager`, etc.) and constructing the correct run prefixes for commands.
*   **Success Criteria**: A headless engine function that can take a translated Pinokio script and fully execute its installation steps, creating the correct environment and running all necessary commands in the proper context.

---

#### **Phase P08: Part B: In-Repo Installation Engine (Advanced Logic & State)**
*   **Objective**: To upgrade the installation engine to handle complex file operations and maintain a persistent state.
*   **In-Repo Engine Development**:
    1.  **File Manager (`app/core/P08_FileManager.py`)**: Create a new, dedicated module to contain the robust, production-grade implementations of all `fs.*` methods (download with checksums, atomic copy/write, etc.).
    2.  **State Manager (`app/core/P08_StateManager.py`)**: Develop a critical module to manage the system's persistent state using an SQLite database. It will provide a clean API for all database interactions (e.g., `set_app_status()`).
    3.  **Engine Integration**: Enhance the `P07_InstallManager` to call the `P08_FileManager` for all `fs.*` steps and the `P08_StateManager` at the start (`INSTALLING`), success (`INSTALLED`), and failure (`ERROR`) points of the installation process.
*   **Success Criteria**: The installation engine is now feature-complete, capable of handling all Pinokio API file operations and maintaining a persistent, transactional record of every application's state.

---

#### **Phase P09: Part C: In-Notebook Installation UI (Integration & Feedback)**
*   **Objective**: To bridge the gap between the powerful backend engine and the user, providing real-time feedback and control.
*   **In-Notebook UI Development**:
    1.  **Activate "Install" Button**: The "Install" button in the "Discover" tab will be made functional.
    2.  **Event Handling & Threading**: The `on_click` handler will call the `install_app` method in a **separate background thread** to keep the UI responsive. It will pass the `stream_to_terminal` callback to the engine.
    3.  **Progress Indicators**: An `ipywidgets.IntProgress` bar will be added. The `install_app` method will be modified to accept an `update_progress(percent)` callback, which it will call at key milestones.
*   **Success Criteria**: A user can click "Install" and see the raw logs stream into the terminal in real-time, while a progress bar shows the overall status.

---

#### **Phase P10: Part D: In-Notebook Installation UI (State & User Input)**
*   **Objective**: To make the installation process fully interactive and to make the UI "smart" by having it react to the persistent state of the application library.
*   **In-Notebook UI Development**:
    1.  **Interactive Input Handling**: Implement the logic for Pinokio's `input` method. The engine will pause and signal the UI when it needs input. The UI will then dynamically generate an `ipywidgets` form, collect the user's data, and resume the engine's execution.
    2.  **State-Aware UI**: A master `refresh_ui()` function will be created. It will query the `P08_StateManager` and redraw the entire UI based on the current state of all applications. This function will be called after any major action.
*   **Success Criteria**: The installation process is now fully interactive. The UI is dynamic and intelligently adapts based on the persistent state of the application library.

---

#### **Phase P11: The Digital Bookshelf (Library Engine & UI)**
*   **Objective**: To build the "My Library" tab, providing a central hub for users to manage their installed applications.
*   **In-Repo Engine Development**:
    1.  **Library Manager (`app/core/P11_LibraryManager.py`)**: Create a dedicated manager for post-installation actions like `uninstall_app()`, `get_app_config()`, and `set_app_config()`.
*   **In-Notebook UI Development**:
    1.  **"My Library" Tab**: This tab will be fully implemented, populated by querying the `P08_StateManager` for all installed applications.
    2.  **Controls**: Each app will have "Start," "Configure," and "Uninstall" buttons wired to the `P11_LibraryManager` methods.
*   **Success Criteria**: The user has a fully functional library to view, manage, configure, and cleanly uninstall their applications.

---

#### **Phase P12: Stage 2 Audit, Lint & Documentation Review**
*   **Objective**: To conduct a comprehensive audit of the entire installation and library management system.
*   **Audit Tasks**:
    1.  Lint and review all code from P07-P11.
    2.  Perform an end-to-end test: install, configure, and uninstall a real Pinokio application.
    3.  Complete the "Stage 2 Validation Checklist" below.
*   **Documentation Tasks**:
    1.  Update `CAPTAINS_LOG.md` with a summary of Stage 2.
    2.  Update the `INDEX.md` Script Index with all new files from this stage (`P07_InstallManager`, `P08_FileManager`, `P08_StateManager`, `P11_LibraryManager`).
*   **Success Criteria**: A robust, professionally engineered, and thoroughly tested installation and library system.

---
### **Stage 2 Validation Checklist**
*(To be completed by the AI agent during the Phase P12 Audit.)*

*   **[ ] Installation Execution**: Does the system provide the capability to execute the steps from a translated Pinokio recipe, including running shell commands within the correct virtual environment?
*   **[ ] File Operations**: Does the system now support all `fs.*` operations (download, copy, link, write, etc.) as defined in the Pinokio API?
*   **[ ] State Management**: Does the system provide the capability to track the persistent state of applications (e.g., `INSTALLING`, `INSTALLED`, `ERROR`) in a database?
*   **[ ] Interactive Input**: Does the system provide the capability to handle an `input` step in an installer, pausing execution to request data from the user via the UI?
*   **[ ] Library Management**: Does the system provide the capability to list all installed applications and perform lifecycle actions on them, such as `uninstall`?
