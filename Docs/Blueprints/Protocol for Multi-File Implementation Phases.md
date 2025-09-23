**STANDING DIRECTIVE: PROTOCOL FOR MULTI-FILE IMPLEMENTATION PHASES**

You are about to begin a development phase that requires the creation of multiple, distinct modules. This directive outlines the strict protocol you must follow for such phases.

The phase in focus is: **[Phase Number/Name will be inserted here]**

This phase requires the creation of the following **[Number]** modules:
**[A bulleted list of filenames and their single, clear responsibilities will be inserted here]**

**Architectural Rationale:**
As per the **Single Responsibility Principle** mandated in `RULES.md`, the logic for this phase is intentionally separated into distinct files. Each file has one, and only one, reason to change. This ensures our architecture remains clean, modular, and maintainable.

**Operational Protocol:**
1.  You will be given this directive first to establish the multi-part nature of the task.
2.  I will then provide you with a series of self-contained implementation prompts, one for each file listed above, in the correct sequence.
3.  You are to treat each prompt as a **separate, atomic task**. The completion of one file marks the end of that task, and you will await the prompt for the next file.

**Critical Prohibitions:**
*   You are strictly forbidden from merging the logic of these separate files into a single implementation.
*   You are strictly forbidden from overwriting a previously generated file when you receive a prompt for a new file within the same phase.

Acknowledge this standing directive to confirm you understand the protocol for multi-file phases. Upon your confirmation, I will provide the prompt for the *first* file in the sequence.