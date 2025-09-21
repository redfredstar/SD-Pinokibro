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