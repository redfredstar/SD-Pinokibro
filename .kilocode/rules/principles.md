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
    -   It must automatically switch to `venv` if, and only if, the Lightning AI platform is detected.# principles.md


