# wrokflow.md

This is the core operational protocol for all development. It's an iterative loop followed to implement features and fix bugs, ensuring a methodical and efficient workflow.

## Steps

1.  **Hypothesize & Implement**: Implement the required feature or bug fix in the relevant `/app` directory `.py` file(s).
2.  **Isolate & Prepare**: Create a new, clean, isolated test workspace.
3.  **Execute Test**: Run the appropriate test, starting with a full Headless Execution Run for any new feature or significant bug fix.
4.  **Capture & Analyze**: Capture the complete `test_run.log` file and scan it for tracebacks, errors, or unexpected output.
5.  **Diagnose & Refine**: Based on the log analysis, form a precise hypothesis about the root cause of the failure and implement a refined solution.
6.  **Repeat**: Delete the old test workspace and loop back to Step 2, continuing the cycle relentlessly until the test executes successfully.