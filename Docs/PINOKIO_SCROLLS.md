# PINOKIO_SCROLLS.md - The Ancient Texts

## **PREAMBLE: THE TECHNICAL COMPENDIUM**

This document is the **definitive, token-efficient, and highly focused technical reference** for the original Pinokio scripting language and API. It is not a user guide, a tutorial, or a philosophical text. It is a practical, stripped-down compendium designed exclusively for you, the AI development agent, to use as a primary reference when implementing the PinokioCloud emulation engine.

All non-essential information—including desktop installation instructions, community links, introductory narratives, and troubleshooting for the desktop application—has been surgically removed. What remains is the pure, concentrated knowledge required to accurately replicate the functionality of the Pinokio v1 ecosystem.

---

### **INTRODUCTION: THE DESKTOP VS. CLOUD PARADIGM**

The very existence of the PinokioCloud project is necessitated by the fundamental differences between a persistent, user-controlled desktop environment and a temporary, restricted cloud notebook environment. Understanding these differences is critical to implementing the API correctly.

*   **Environment Context**:
    *   **Desktop**: Assumes a persistent environment with full system access, a stable file system, and native process management.
    *   **Cloud Notebook**: Operates in an **ephemeral**, containerized environment. Storage can be temporary, processes are tied to a session, and direct system access is limited.
*   **File System**:
    *   **Desktop**: Can access any path on the local machine (e.g., `/home/user/`).
    *   **Cloud Notebook**: Is restricted to a specific workspace (e.g., `/content/`, `/workspace/`). **Therefore, our engine's `fs.*` methods must be built on the `P01_PathMapper` to correctly translate paths.**
*   **Process Management**:
    *   **Desktop**: Can spawn true background daemons that persist after the main application closes.
    *   **Cloud Notebook**: Processes are session-bound. A "daemon" in our context is a process that outlives the script that started it but will be terminated when the notebook session ends. Our `P02_ProcessManager` must manage this lifecycle.
*   **Networking**:
    *   **Desktop**: Can easily expose services on `localhost` for the user to access directly. Tunneling is optional for sharing.
    *   **Cloud Notebook**: `localhost` is inaccessible from the user's browser. **Therefore, tunneling is mandatory for any application with a web UI.** Our `P14_TunnelManager` is a critical, not optional, component.

This document details the API as it was designed for the desktop. Your mission is to re-implement these capabilities, adapting them to overcome the challenges of the cloud notebook paradigm.

---

### **SECTION 1: CORE CONCEPTS & FILE STRUCTURE**

This section provides a concise overview of the essential files that constitute a Pinokio project. This is the foundational knowledge required to understand how scripts are structured and launched.

*   **1.1 Script Files (`.json` or `.js`)**
    *   **Purpose**: The heart of any Pinokio application. These files contain the sequence of operations to be executed.
    *   **Format**: Can be either declarative JSON or programmatic JavaScript.
    *   **Core Syntax (`.json`)**:
        ```json
        {
          "version": "4.0",
          "run": [ /* Array of operation steps */ ],
          "daemon": true,
          "env": [ "REQUIRED_ENV_VAR_1" ]
        }
        ```
    *   **Key Attributes**:
        *   `run`: An array of JSON objects, where each object is a single step (an API call) to be executed sequentially.
        *   `daemon`: A boolean. If `true`, the final long-running process in the `run` array will not be terminated when the script finishes. This is essential for web servers and background services.
        *   `env`: An array of strings. Each string is the name of an environment variable that the Pinokio system will ensure is set before executing the script, prompting the user if necessary.

*   **1.2 Launcher (`pinokio.js`)**
    *   **Purpose**: The user interface definition file. It uses JavaScript to dynamically generate the menu of actions a user can take.
    *   **Core Syntax**:
        ```javascript
        module.exports = {
          "version": "4.0",
          "menu": async (kernel) => {
            // JS logic to check system state (e.g., is app installed? is it running?)
            // Returns an array of menu item objects.
            return [{
              "html": "Clickable Menu Item Text (can include HTML)",
              "href": "script_to_run.json" // Runs a script
            }]
          }
        }
        ```
    *   **Key Attributes**:
        *   `menu`: A function (often `async`) that receives the `kernel` object as an argument. This function's logic determines what menu items are displayed to the user. It must return an array of menu item objects.

*   **1.3 Configuration (`pinokio.json`)**
    *   **Purpose**: A metadata file that stores display information for the project, such as its title, description, and icon. Our system will read this to populate the UI.

*   **1.4 Environment (`ENVIRONMENT`)**
    *   **Purpose**: A simple text file in the standard Unix `.env` format (`KEY=VALUE`) for storing persistent, project-specific environment variables. Our engine must load this file and inject its variables into the execution context of all scripts.

---

### **SECTION 2: THE SCRIPTING LANGUAGE - COMPLETE API REFERENCE**

This is the core technical specification of the Pinokio API. Each method that can be called from a script's `run` array is detailed here. Your engine must re-implement the behavior of each of these methods.

#### **2.1 `shell.run` - Command Execution**
*   **Description**: The most fundamental method. Executes any shell command.
*   **Syntax**:
    ```json
    {
      "method": "shell.run",
      "params": {
        "message": "<string | array of strings>",
        "path": "<optional: working directory path>",
        "env": { /* optional: object of env vars */ },
        "venv": "<optional: path to venv>",
        "conda": "<optional: conda env name>",
        "on": [{
          "event": "/regex_pattern_to_match_in_output/",
          "done": true
        }],
        "sudo": false
      }
    }
    ```
*   **Parameters**:
    *   `message`: A single command string or an array of strings to be executed sequentially.
    *   `path`: The working directory from which to execute the command. Defaults to the script's root.
    *   `env`: An object of key-value pairs to be set as environment variables for this specific command.
    *   `venv`: Path to a Python virtual environment to activate before running the command.
    *   `conda`: Name of a Conda environment to activate before running the command.
    *   `on`: An array of event handlers to monitor the command's real-time output. This is critical for managing long-running services.
        *   `event`: A regex pattern to match against `stdout` or `stderr`.
        *   `done`: If `true`, the script execution will proceed to the next step once the event is matched, but the underlying process will be left running. This is used in conjunction with `daemon: true` for starting servers.
    *   `sudo`: If `true`, the command will be executed with administrator privileges.

#### **2.2 `fs.*` - File System Operations**
*   **Description**: A suite of platform-agnostic functions for interacting with the file system.
*   **Methods**:
    *   `fs.write`: Writes text to a file. Params: `path`, `text`.
    *   `fs.read`: Reads the content of a file. Params: `path`.
    *   `fs.rm`: Deletes a file or directory. Params: `path`.
    *   `fs.copy`: Copies a file or directory. Params: `src`, `dest`.
    *   `fs.download`: Downloads a file from a URL. Params: `uri`, `dir`.
    *   `fs.link`: Creates symbolic links, the basis of the virtual drive system. Params: `src`, `dest`.
    *   `fs.open`: Opens a file or folder in the system's default application. (Note: May have limited utility in a headless cloud environment).
    *   `fs.cat`: Prints the contents of a file to the terminal log.

#### **2.3 `script.*` - Script Orchestration**
*   **Description**: Methods for managing the lifecycle of other Pinokio scripts.
*   **Methods**:
    *   `script.start`: Starts another script. Can pass parameters to the target script. Params: `uri`, `params`.
    *   `script.stop`: Stops a running script. Params: `uri`.
    *   `script.return`: Used inside a script to return a value to a calling script. Params: `value`.
    *   `script.download`: Downloads a Pinokio project from a git repository.

#### **2.4 `json.*` - JSON Data Management**
*   **Description**: Methods for atomically reading from and writing to JSON files.
*   **Methods**:
    *   `json.get`: Reads a JSON file and can assign its contents to a local variable. Params: `path`.
    *   `json.set`: Writes or updates keys and values within a JSON file. Params: `path`, `json`.
    *   `json.rm`: Removes an attribute from a JSON file. Params: `path`, `key`.

#### **2.5 `input` - User Interaction**
*   **Description**: Prompts the user for input via a modal dialog form. In our `ipywidgets` implementation, this will trigger the UI to display a form.
*   **Syntax**:
    ```json
    {
      "method": "input",
      "params": {
        "title": "Dialog Title",
        "description": "A description of what is needed.",
        "form": [
          { "key": "variable_name", "title": "Field Label", "type": "text" }
        ]
      }
    }
    ```
*   **Form Field Types**: `text`, `email`, `password`, `textarea`, `file`, `select`, `checkbox`.

#### **2.6 Other Utility Methods**
*   `local.set`: Sets a temporary local variable for the current script execution.
*   `log`: Prints a message to the terminal log.
*   `notify`: Displays a system notification.
*   `web.open`: Opens a URL in the user's default web browser.
*   `hf.download`: A specialized method for downloading files from Hugging Face.

---

### **SECTION 3: THE MEMORY SYSTEM - COMPLETE VARIABLE REFERENCE**

This section details all the built-in memory variables that can be used within script parameters using the `{{variable_name}}` syntax. Our engine's variable substitution system must support all of these.

*   `{{input}}`: The value returned from the immediately preceding step in the `run` array.
*   `{{args.*}}`: Accesses parameters passed to the script via `script.start`. Example: `{{args.message}}`.
*   `{{local.*}}`: Accesses temporary variables set by `local.set`. Example: `{{local.greeting}}`.
*   `{{self}}`: The script object itself, providing access to its own properties.
*   `{{cwd}}`: The absolute path to the current working directory of the script. In our system, this will be resolved by the `P01_PathMapper`.
*   `{{port}}`: A utility that returns the next available network port on the system.
*   `{{platform}}`: The host operating system. Resolves to `darwin` (macOS), `linux`, or `win32` (Windows). Our system will extend this to include cloud platform identifiers.
*   `{{arch}}`: The system's CPU architecture (e.g., `x64`, `arm64`).
*   `{{gpu}}`: An object containing information about the primary GPU, including `{{gpu.type}}` and `{{gpu.vram}}`.
*   `{{envs.*}}`: Accesses system-wide environment variables. Example: `{{envs.HOME}}`.

---

### **SECTION 4: PRACTICAL USAGE PATTERNS (THE CODE COOKBOOK)**

This section provides a set of clean, practical code examples demonstrating common patterns that our engine must be able to handle.

*   **Pattern: Creating a Virtual Environment and Installing a Package**
    ```json
    {
      "run": [{
        "method": "shell.run",
        "params": { "message": "python -m venv env" }
      }, {
        "method": "shell.run",
        "params": {
          "venv": "env",
          "message": "pip install gradio"
        }
      }]
    }
    ```

*   **Pattern: Starting a Web Server as a Daemon**
    ```json
    {
      "daemon": true,
      "run": [{
        "method": "shell.run",
        "params": {
          "venv": "env",
          "message": "python server.py",
          "on": [{
            "event": "/Running on http:\\/\\/127.0.0.1:[0-9]+/",
            "done": true
          }]
        }
      }]
    }
    ```

*   **Pattern: Dynamic, Context-Aware `pinokio.js` Launcher**
    ```javascript
    module.exports = {
      menu: async (kernel) => {
        let installed = await kernel.exists("app");
        if (installed) {
          let running = await kernel.script.running("start.json");
          if (running) {
            return [{ html: "Stop", click: () => kernel.script.stop("start.json") }];
          } else {
            return [{ html: "Start", href: "start.json" }];
          }
        } else {
          return [{ html: "Install", href: "install.json" }];
        }
      }
    }
    ```

*   **Pattern: Conditional Execution Based on Platform**
    ```json
    {
      "run": [{
        "when": "{{platform === 'darwin'}}",
        "method": "shell.run",
        "params": { "message": "brew install ffmpeg" }
      }, {
        "when": "{{platform === 'linux'}}",
        "method": "shell.run",
        "params": { "message": "sudo apt-get install -y ffmpeg" }
      }]
    }
    ```
