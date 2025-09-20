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
| **`RULES.md`** | **The Constitution** | This document contains the immutable, non-negotiable laws of the project. It is not a guide but a set of direct, enforceable rules. It codifies the project's core philosophies (Maximum Debug, Zero Tolerance for Placeholders), the strict professional coding standards (File Size, KOOP, SRP, Naming Conventions), and the operational protocols that all AI agents must follow (End-of-Stage Audits, Log Updates, Single Main Branch). This document is the ultimate authority on *how* to build. | **ALL STAGES**. Must be read before any work begins and referenced continuously. |
| **`MASTER_GUIDE.md`**| **The Blueprint** | This is the definitive architectural and strategic plan for the project rebuild. It dictates *what* to build and in what sequence. It contains the complete, granular 22-phase (5-stage) roadmap, detailing the objectives, deliverables, and success criteria for each phase. It also includes the detailed `ipywidgets` UI blueprint and a summary of the core architectural decisions (Conda-first, Universal Translator, etc.). **Crucially, it contains the Stage Validation Checklists at the end of each stage description**, which serve as the acceptance criteria for ensuring feature parity with the v1 codebase. | **ALL STAGES**. It is the primary reference for planning and executing the work of each phase. |
| **`CAPTAINS_LOG.md`** | **The Live Handover & Changelog** | This document is the project's living memory, designed to solve context loss between work sessions. It is a single, reverse-chronological log that is updated continuously during a work session. The top of the file always contains the "Current Session" details, which are finalized and moved to the "Previous Sessions" archive upon completion. It is the primary tool for understanding the immediate, up-to-the-minute status, challenges faced, decisions made, and the narrative history of the development process. | **ALL STAGES**. It is the first document to read after the `INDEX.md`, `RULES.md`, and `MASTER_GUIDE.md` to gain immediate operational context. It must be updated frequently during any work session. |
| **`PINOKIO_SCROLLS.md`**| **The Ancient Texts**| A token-efficient, highly focused technical reference on the original Pinokio scripting language and API. All non-technical "fluff" (like desktop installation guides or community links) has been surgically removed. Its sole purpose is to provide a clean, quick reference for the engine implementation. It begins with a new introductory section, derived from v1's `notebook_vs_desktop_differences.md`, to explain the foundational challenges of running a desktop-first system in a cloud-notebook environment. The remainder details the exact syntax of `.json` and `.js` scripts, the complete API Reference (`shell.run`, `fs.*`, etc.), and the full list of Memory Variables. | **Stages 1-3**. Most critical during the development of the core engine that emulates the Pinokio API. |
| **`AI_VM_TESTING_GUIDE.md`**| **The Proving Grounds**| A practical guide for the AI agent to become a self-sufficient tester. It codifies the process of creating an isolated virtual machine environment for automated testing and debugging of the `launcher.ipynb`. It contains specific methodologies (e.g., "Headless Execution with `nbconvert`," "Import and Execute Test"), required tool setup instructions, and the conceptual framework for the iterative "test-diagnose-fix" loop that is crucial for a stable rebuild. | **ALL STAGES**, but especially **Stage 5 (The Testing Gauntlet)**. |
| **`SECURITY_MEMO.md`**| **The Security Stance**| An explicit and unambiguous document defining the project's security posture. It formally states that PinokioCloud is a personal development project where functionality and development velocity are prioritized over enterprise-grade security. It contains an explicit rule permitting the hardcoding of API keys and tokens (e.g., `ngrok` token) to prevent AI agents from wasting cycles on out-of-scope security enhancements. | **Stages 1 & 3**. Important to read during onboarding to understand the project's constraints and during the implementation of tunneling features. |

---

## **SCRIPT & FILE INDEX**

*(This section will be populated with file details at the conclusion of each Stage Audit, as mandated by `RULES.md`)*

### **Stage 1: System Foundation & Core Engines (Phases P01-P06)**
*   **`App/Core/p04_environment_manager.py`** - **P04 Environment Manager** - The core environment management engine implementing the Conda-first, venv fallback strategy. Provides methods for creating virtual environments and generating execution prefixes based on platform detection. Includes comprehensive error handling with full tracebacks and follows the Maximum Debug philosophy.
*   **`App/Test/P04-Test_EnvironmentManager.py`** - **P04 Environment Manager Test** - Comprehensive test suite for the P04_EnvironmentManager class. Tests platform detection, environment creation (both Conda and venv), run prefix generation, and error handling scenarios. Includes callback function testing for output streaming.

### **Stage 2: The Installation Gauntlet (Phases P07-P12)**
*   *(To be populated at the end of Phase P12)*

### **Stage 3: The Launch Sequence (Phases P13-P18)**
*   *(To be populated at the end of Phase P18)*

### **Stage 4: Final Integration & Polish (Phases P19-P20)**
*   *(To be populated at the end of Phase P20)*
