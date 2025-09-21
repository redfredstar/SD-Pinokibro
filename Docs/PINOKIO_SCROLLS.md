# PINOKIO_SCROLLS.md - The Ancient Knowledge

## **PREAMBLE: THE COMPRESSED WISDOM**

This document contains the essential, token-efficient knowledge extracted from the original Pinokio documentation. It serves as a quick reference for core concepts and API patterns, preserving the critical understanding needed to work with Pinokio applications while maintaining the rebuild's focus on the new architecture.

---

### **SECTION 1: THE PINOKIO WAY - CORE CONCEPTS**

#### **1.1 The Pinokio Philosophy**
Pinokio is a simple, powerful application installation and management system designed for AI/ML workflows. It uses JavaScript-based installers that define a series of steps to download, configure, and run applications in isolated environments.

#### **1.2 Application Structure**
A Pinokio application consists of:
- **Directory Structure**: Organized with `config.js`, `install.js`, `run.js`, and other assets
- **Configuration**: `config.js` defines metadata, dependencies, and UI elements
- **Installation**: `install.js` contains the installation script using Pinokio API calls
- **Execution**: `run.js` defines how to launch the application after installation

#### **1.3 The Pinokio API**
The Pinokio API provides a set of functions for common operations in install scripts:

```javascript
// Shell execution
shell.run(command, options)
shell.exec(command, options)

// File system operations
fs.download(url, path, options)
fs.copy(source, destination)
fs.write(path, content)
fs.read(path)
fs.mkdir(path)
fs.rm(path)

// Git operations
git.clone(url, path, options)
git.pull(path)

// User interaction
input.prompt(message, options)
input.select(message, choices, options)

// Environment management
env.create(name, type)
env.activate(name)
```

---

### **SECTION 2: INSTALLER PATTERNS & TRANSLATION**

#### **2.1 Common Installation Patterns**

**Pattern 1: Basic Download and Setup**
```javascript
// Original JavaScript
shell.run("wget https://example.com/app.tar.gz");
shell.run("tar -xzf app.tar.gz");
shell.run("cd app && ./setup.sh");

// Translated to Python recipe
[
    {"step_type": "shell", "command": "wget https://example.com/app.tar.gz"},
    {"step_type": "shell", "command": "tar -xzf app.tar.gz"},
    {"step_type": "shell", "command": "cd app && ./setup.sh"}
]
```

**Pattern 2: Git Repository with Dependencies**
```javascript
// Original JavaScript
git.clone("https://github.com/user/repo.git", "repo");
shell.run("cd repo && pip install -r requirements.txt");

// Translated to Python recipe
[
    {"step_type": "git", "url": "https://github.com/user/repo.git", "path": "repo"},
    {"step_type": "shell", "command": "cd repo && pip install -r requirements.txt"}
]
```

**Pattern 3: Environment Creation**
```javascript
// Original JavaScript
env.create("myenv", "python3");
env.activate("myenv");
shell.run("pip install torch torchvision");

// Translated to Python recipe
[
    {"step_type": "env_create", "name": "myenv", "type": "python3"},
    {"step_type": "env_activate", "name": "myenv"},
    {"step_type": "shell", "command": "pip install torch torchvision"}
]
```

#### **2.2 File Operations with Checksums**
```javascript
// Original JavaScript
fs.download("https://example.com/large_file.bin", "data.bin", {
    checksum: "sha256:abc123...",
    onprogress: (percent) => console.log(`${percent}%`)
});

// Translated to Python recipe
[
    {
        "step_type": "fs_download",
        "url": "https://example.com/large_file.bin",
        "path": "data.bin",
        "checksum": "sha256:abc123..."
    }
]
```

---

### **SECTION 3: CONFIGURATION STRUCTURE**

#### **3.1 Basic config.js Format**
```javascript
module.exports = {
    title: "My Application",
    description: "A sample Pinokio application",
    icon: "icon.png",
    menu: [
        {
            icon: "fa-solid fa-plug",
            text: "Install",
            href: "install.js"
        },
        {
            icon: "fa-solid fa-power-off",
            text: "Start",
            href: "run.js"
        }
    ],
    platform: {
        os: "linux",
        arch: "x64"
    }
};
```

#### **3.2 Advanced Configuration with Dependencies**
```javascript
module.exports = {
    title: "AI Application",
    description: "Advanced AI tool with GPU support",
    icon: "ai.png",
    menu: [
        {
            icon: "fa-solid fa-download",
            text: "Install",
            href: "install.js"
        },
        {
            icon: "fa-solid fa-play",
            text: "Run",
            href: "run.js",
            params: {
                env: "aienv",
                command: "python app.py"
            }
        }
    ],
    dependencies: [
        "python3",
        "git",
        "wget"
    ],
    requirements: {
        gpu: true,
        ram: "8GB"
    }
};
```

---

### **SECTION 4: APPLICATION CATEGORIES**

Pinokio applications are typically organized into categories:

- **AI/ML**: Machine learning frameworks, training tools, inference engines
- **Development**: Programming environments, IDEs, development tools
- **Productivity**: Office applications, utilities, system tools
- **Media**: Image/video processing, audio tools, viewers
- **Gaming**: Game engines, emulators, game-related tools

Each category has specific patterns and common dependencies that the SearchEngine can leverage for better relevance scoring.

---

### **SECTION 5: MIGRATION INSIGHTS**

#### **5.1 Key Differences in v2 Architecture**
- **Environment Management**: v2 uses explicit Conda/venv management vs. Pinokio's simplified env API
- **Process Execution**: v2 provides real-time streaming output vs. buffered output in v1
- **State Management**: v2 uses SQLite for persistent state vs. file-based state in v1
- **UI Framework**: v2 uses ipywidgets exclusively vs. web-based UI in v1

#### **5.2 Compatibility Considerations**
- All Pinokio API calls must be translated to the new recipe format
- Environment creation must be handled by the P04_EnvironmentManager
- File operations require checksum validation and atomic operations
- Shell commands must be executed through the P02_ProcessManager for proper streaming

---

### **SECTION 6: QUICK REFERENCE**

#### **6.1 API Translation Mapping**
| Pinokio JS API | v2 Recipe Step Type |
|----------------|-------------------|
| `shell.run()` | `shell` |
| `fs.download()` | `fs_download` |
| `git.clone()` | `git` |
| `env.create()` | `env_create` |
| `env.activate()` | `env_activate` |

#### **6.2 Common Command Patterns**
- **Python package installation**: `pip install -r requirements.txt`
- **Node.js setup**: `npm install` or `yarn install`
- **Model downloading**: `wget` or `curl` with checksum validation
- **Service startup**: `python server.py` or `node app.js`

#### **6.3 Environment Types**
- **Python**: `python3` - Creates Python virtual environments
- **Conda**: `conda` - Creates Conda environments for complex dependencies
- **Node**: `node` - Sets up Node.js environments
- **System**: `system` - Uses system-wide package managers

---

This document preserves the essential knowledge from the original Pinokio system while focusing on the patterns and concepts most relevant to the v2 rebuild implementation.
