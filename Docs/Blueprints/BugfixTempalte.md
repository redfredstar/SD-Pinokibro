You are a Senior Systems Architect. Your mission is to execute a critical corrective action on the official project documentation, which was found to contain severe factual inaccuracies. You will generate the corrected documentation fragment, **SAVE** it to a file, and then document this action in the `CAPTAINS_LOG.md`.

**Authoritative Sources**:
Your actions are governed by the `MASTER_GUIDE.md` (for the true purpose of each module) and the `T2_Critique_And_Selection.md` (for the official gauntlet tests used for validation).

---

### **Detailed Failure Analysis**

This directive is to resolve **[Failure ID]: [Failure Description]**.

* **The Failure**: The previous "As-Built" specification incorrectly stated that the purpose of `[PXX_ModuleName.py]` was "[Incorrect Purpose]" and cited a fabricated "[Fabricated Test Name]" for its validation.
* **The Ground Truth**: The module's true purpose is "[Correct Purpose]". Its validation comes from the official "[Official Gauntlet Test Name]".

---

**Your Task - A Four-Step Process:**

**1. Generate the Corrected Documentation Fragment**:
Generate a single, corrected markdown bullet point for the `[PXX_ModuleName.py]` module. This fragment must be written in the official "As-Built" format and contain the correct "Purpose" and "Validation" information from the ground truth specified above.

**2. CRITICAL ACTION: SAVE THE CORRECTION**:
This is the most critical step. You will take the corrected markdown fragment you just generated and **execute the action to SAVE it to a new file named `[CORRECTION-PXX_ModuleName.md]`**. This creates a persistent, auditable artifact of the fix. **FAILURE TO SAVE THIS FILE IS A FAILURE OF THE ENTIRE TASK.**

**3. Generate the `CAPTAINS_LOG.md` Entry**:
Provide the complete markdown content for a new `CAPTAINS_LOG.md` entry that documents this specific corrective action. You **MUST** use the following template exactly.

**Log Entry Template:**

```markdown
### ✅ SESSION ENDED - [YYYY-MM-DD]

*   **Agent**: [Your Agent Name]
*   **Phase(s) in Focus**: CORRECTIVE ACTION: [Failure ID] Documentation Alignment
*   **Session Summary**: [Executed a critical corrective action to rectify inaccuracies regarding `[PXX_ModuleName.py]`. The official documentation fragment has been corrected to reflect its true purpose and validation, and the fix has been saved to `[CORRECTION-PXX_ModuleName.md]`.]

---
#### **Log Entries**

*   **[HH:MM]**: Session initiated. Objective: Correct the misstated purpose and validation claims for the `[PXX_ModuleName.py]` module.
*   **[HH:MM]**: **Failure Analysis**: [Confirmed that previous reports incorrectly described the module's purpose and cited a non-existent validation test.]
*   **[HH:MM]**: **Documentation Correction**: [Generated the new, corrected "As-Built Specification" markdown fragment for the module, accurately describing its purpose and validation.]
*   **[HH:MM]**: **CRITICAL SAVE ACTION**: [The corrected documentation fragment was successfully saved to `[CORRECTION-PXX_ModuleName.md]` as a permanent record of this fix.]
*   **[HH:MM]**: Corrective action complete. [Failure ID] is resolved.
```
