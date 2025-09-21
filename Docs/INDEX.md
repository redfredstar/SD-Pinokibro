# INDEX.md - The Rosetta Stone

## **BOOTSTRAPPING INSTRUCTIONS FOR NEW AI AGENTS**

**Project Goal**: You are to execute the complete ground-up rebuild of the PinokioCloud system. Your mission is to create a cloud-native Pinokio alternative using `ipywidgets`, guided by the definitive 22-phase development plan detailed in `MASTER_GUIDE.md`. The project is currently in an **active rebuild phase**; all previous v1 implementations are considered non-functional, deprecated references.

**Your Prime Directives**:
1.  **Read the Constitution First**: Before writing a single line of code or executing any task, you MUST read, fully comprehend, and internalize the contents of `RULES.md`. It contains the non-negotiable laws, philosophies, and operational protocols for this project. Adherence is mandatory and absolute.
2.  **Consult The Blueprint**: The `MASTER_GUIDE.md` contains the complete, authoritative 22-phase roadmap. All development must align with this plan. It dictates *what* you will build and in what order. This is your single source of truth for the project's architecture and scope.
3.  **Check The Captain's Log**: You MUST read the most recent entry in `CAPTAINS_LOG.md` to gain the immediate, up-to-the-minute context from the previous work session. This is your primary tool for ensuring seamless continuity.
4.  **Follow The Reading Order**: To gain full and correct context, you must read the project documents in the specified "Reading Order for Full Context" listed below. This is not an optional suggestion; it is the required procedure for project onboarding.
5.  **Update The Indexes**: It is a mandatory part of your duties that at the end of every Stage Audit phase (P06, P12, P18, P20), you MUST update both the Document Index and the Script & File Index within this document to reflect all new assets created during that stage. This is a critical protocol for maintaining this document as the project's master map.

---

## **DOCUMENTATION READING ORDER & INDEX**

### **Reading Order for Full Context**

To ensure a complete and accurate understanding of the project's goals, architecture, and current state, all agents must consume the documentation in the following precise sequence:

1.  **`INDEX.md` (This Document)** - To understand the master map of the project and the location of all other knowledge.
2.  **`RULES.md`** - To understand the fundamental laws and philosophies you must operate under.
3.  **`MASTER_GUIDE.md`** - To understand the complete 22-phase project plan and the specifics of what you are building.
4.  **`CAPTAINS_LOG.md`** - To understand the immediate, up-to-the-minute status, history, and context of the project's development.
5.  **(Reference as needed)** `PINOKIO_SCROLLS.md`, `AI_VM_TESTING_GUIDE.md`, `SECURITY_MEMO.md` - To consult for specific technical details during implementation.

### **The Document Index**

| Filename | Title | Detailed Description & Contents | Crucial for Stage(s) |
| :--- | :--- | :--- | :--- |
| **`INDEX.md`** | **The Rosetta Stone** | This is the master map and single entry point for the entire project. Its primary function is to bootstrap the context of any AI agent, providing a comprehensive, searchable index of all project documents and the codebase itself. It contains the mandatory reading order, detailed descriptions of all other documents, and a file index that is updated at the end of each development stage. It is the first document an agent should read and the last document updated during an audit. | **ALL STAGES**, especially project start and all Audit Phases (P06, P12, P18, P20). |
| **`RULES.md`** | **The Constitution** | This document contains the immutable, non-negotiable laws of the project. It is not a guide but a set of direct, enforceable rules. It codifies the four cardinal principles (Zero Placeholder, Maximum Debug, ipywidgets First, Conda-First), the code of conduct, and operational protocols. The contents of this document are the final authority, superseding any conflicting information in any other project document, including the v1 codebase archive. | **ALL STAGES**. This document must be read and understood before any code is written. |
| **`MASTER_GUIDE.md`** | **The Blueprint** | The complete 22-phase development plan that dictates *what* you will build and in what order. This is your single source of truth for the project's architecture and scope. It contains the detailed roadmap, objectives, deliverables, and success criteria for each phase, along with the Stage Validation Checklists that serve as acceptance criteria. | **ALL STAGES**. This document is the roadmap for the entire project. |
| **`CAPTAINS_LOG.md`** | **The Live Handover & Changelog** | The single source of truth for the momentum, context, and history of the project. It is a living, dynamic logbook that captures the development process as it happens. The top of the file always contains the "Current Session" details, which are finalized and moved to the "Previous Sessions" archive upon completion. | **ALL STAGES**. This document is updated continuously throughout every work session. |
| **`PINOKIO_SCROLLS.md`** | **The Ancient Knowledge** | Contains the essential, token-efficient knowledge extracted from the original Pinokio documentation. It serves as a quick reference for core concepts and API patterns, preserving the critical understanding needed to work with Pinokio applications. Includes installer patterns, configuration structures, and migration insights. | **STAGE 1+**. Essential for understanding Pinokio application structure and installer patterns. |
| **`AI_VM_TESTING_GUIDE.md`** | **The Proving Grounds** | The authoritative guide for becoming a self-sufficient and rigorous tester of the PinokioCloud project. It provides procedures for creating isolated, repeatable, and automated testing environments. Contains specific methodologies for headless execution and the iterative "test-diagnose-fix" loop. | **ALL STAGES**. Critical for implementing the "Maximum Debug" philosophy and ensuring code quality. |
| **`SECURITY_MEMO.md`** | **The Security Stance** | The definitive and final directive on project security scope, priorities, and permitted practices. It provides clear direction to prevent misallocation of development resources towards out-of-scope security features. Formally states that functionality and development velocity are prioritized over enterprise-grade security. | **ALL STAGES**. Establishes the security boundaries and philosophy for the project. |

---

## **SCRIPT & FILE INDEX**

*(This section will be populated with file details at the conclusion of each Stage Audit, as mandated by `RULES.md`)*

### **Stage 1: System Foundation & Core Engines (Phases P01-P06)**
*   **`launcher_notebook.ipynb`** - **Launcher Notebook** - The primary user interface and application entry point. A Jupyter notebook with 3-cell structure: Cell 1 (Repo clone & dependencies), Cell 2 (Engine init & platform detection verification), Cell 3 (Foundational ipywidgets UI skeleton with main Tab and empty Output widgets). Serves as the complete application interface following the "notebook is the application" philosophy.
*   **`App/Utils/p01_cloud_detector.py`** - **P01 Cloud Detector** - Core platform detection engine that identifies the cloud environment (Colab, Vast.ai, Lightning.ai, etc.) through hierarchical checks. Outputs a standardized PlatformInfo data object used throughout the system for platform-specific adaptations.
*   **`App/Utils/P01_PathMapper.py`** - **P01 Path Mapper** - Platform-agnostic path abstraction layer that consumes PlatformInfo and provides semantic path requests (get_base_path, get_apps_path, get_data_path, get_temp_path, get_config_path). Ensures code portability across different cloud filesystems.
*   **`App/Core/p02_process_manager.py`** - **P02 Process Manager** - Real-time monitoring engine implementing the "Maximum Debug" philosophy. Uses asyncio to execute shell commands non-blockingly with callback architecture for immediate stdout/stderr streaming. Includes PID tracking for all spawned processes.
*   **`App/Utils/p03_translator.py`** - **P03 Universal Translator** - Installer conversion engine that parses diverse Pinokio formats (.json, .js, requirements.txt) into standardized Python recipes. JavaScript parsing uses advanced regex patterns to avoid Node.js dependency while preserving execution order.
*   **`App/Core/p04_environment_manager.py`** - **P04 Environment Manager** - Platform-aware environment management engine implementing Conda-first, venv fallback strategy. Automatically switches to venv on Lightning AI platform. Provides create() and get_run_prefix() methods for environment isolation.
*   **`App/Core/p05_search_engine.py`** - **P05 Search Engine** - Intelligent application discovery engine with weighted relevance ranking. Loads cleaned_pinokio_apps.json into efficient in-memory structures and provides fast search with multi-criteria filtering (category, tags, GPU, size).
*   **`App/Utils/p05_app_analyzer.py`** - **P05 App Analyzer** - Static analysis tool for pre-flight checks on selected applications. Provides detailed analysis of app requirements, dependencies, and potential issues before installation.
*   **`data/cleaned_pinokio_apps.json`** - **Pinokio Apps Database** - Cleaned and processed database of Pinokio applications used by the P05_SearchEngine. Contains application metadata, descriptions, tags, categories, and installation requirements. This file is loaded into memory for fast search operations.
*   **`App/Test/P01-Test_CloudDetector.py`** - **P01 Cloud Detector Test** - Comprehensive test suite for platform detection functionality. Tests hierarchical checks for various cloud environments and validates PlatformInfo object creation.
*   **`App/Test/P01-Test_PathMapper.py`** - **P01 Path Mapper Test** - Test suite for path abstraction layer. Verifies correct path generation and directory creation for all semantic path methods across different platform configurations.
*   **`App/Test/P02-Test_ProcessManager.py`** - **P02 Process Manager Test** - Test suite for real-time monitoring engine. Validates non-blocking command execution, callback architecture, PID tracking, and output streaming functionality.
*   **`App/Test/P03-Test_Translator.py`** - **P03 Universal Translator Test** - Test suite for installer conversion engine. Tests parsing of .json, .js, and requirements.txt files into standardized recipes with correct execution order preservation.
*   **`App/Test/P04-Test_EnvironmentManager.py`** - **P04 Environment Manager Test** - Test suite for environment management engine. Validates platform detection integration, Conda/venv creation, run prefix generation, and error handling scenarios.
*   **`App/Test/P05-Test_SearchEngine.py`** - **P05 Search Engine Test** - Test suite for application discovery engine. Tests weighted relevance ranking, search performance, multi-criteria filtering, and graceful error handling for malformed data.

### **Stage 2: The Installation Gauntlet (Phases P07-P12)**
*   **`app/core/P07_InstallManager.py`** - **P07 Installation Manager** - The core installation workhorse. It takes a standardized recipe, creates an isolated environment, and executes each step in sequence, dispatching tasks to the appropriate sub-manager (ProcessManager, FileManager) while streaming all output to the UI.
*   **`app/core/P08_FileManager.py`** - **P08 File Manager** - A robust, production-grade module that implements the full suite of Pinokio `fs.*` API calls, including atomic file writes, recursive copies, and downloads with progress reporting.
*   **`app/core/P08_StateManager.py`** - **P08 State Manager** - The single source of truth for the user's library. It manages an SQLite database to track the persistent state of all applications (e.g., INSTALLED, RUNNING, ERROR), ensuring data integrity.
*   **`app/core/P11_LibraryManager.py`** - **P11 Library Manager** - The engine for all post-installation actions. It orchestrates complex workflows like uninstallation, which involves removing the environment, deleting application files, and updating the state database.
*   **`app/Test/P12-Test_Stage2_E2E.py`** - **P12 Stage 2 E2E Test** - An end-to-end integration test that validates the `P07_InstallManager`'s ability to correctly process a multi-step recipe and delegate tasks to underlying managers.

### **Stage 3: The Launch Sequence (Phases P13-P18)**
*   *(To be populated at the end of Phase P18)*

### **Stage 4: Final Integration & Polish (Phases P19-P20)**
*   *(To be populated at the end of Phase P20)*
