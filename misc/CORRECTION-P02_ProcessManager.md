# P02_ProcessManager.py - Corrected Documentation Fragment

**Purpose**: The `P02_ProcessManager` is the heart of the "Maximum Debug Philosophy." Its sole, critical purpose is to **execute all shell commands asynchronously and non-blockingly, with real-time, line-by-line output streaming** via a callback mechanism.

**Validation**: Its reliability was validated by the **`Concurrent Operations Stress Test`**, where it flawlessly executed dozens of sequential installation and launch commands without deadlocking, dropping logs, or failing to stream output in real time.