# Pinokio Application Ecosystem Guide

## Overview
This document provides comprehensive guidance on the Pinokio application ecosystem, integration patterns, and development practices based on authoritative documentation research.

## Pinokio Application Structure

### 1. Core Application Files
```javascript
// pinokio.js - Main application configuration
module.exports = {
  version: "2.0",
  title: "Application Name",
  description: "Application description",
  icon: "icon.png",
  menu: async (kernel, info) => {
    // Dynamic menu generation
    return [
      { icon: "fa-solid fa-plug", text: "Install", href: "install.json" }
    ]
  }
}
```

### 2. Installation Scripts (install.json)
```json
{
  "run": [
    {
      "method": "shell.run",
      "params": {
        "message": "git clone https://github.com/user/repo.git app"
      }
    },
    {
      "method": "fs.link",
      "params": {
        "drive": {
          "checkpoints": "app/models/checkpoints",
          "loras": "app/models/loras"
        },
        "peers": [
          "https://github.com/other/app1.git",
          "https://github.com/other/app2.git"
        ]
      }
    }
  ]
}
```

### 3. Launch Scripts (start.json)
```json
{
  "run": [
    {
      "method": "shell.run",
      "params": {
        "message": "cd app && python app.py",
        "env": {
          "PORT": "7860"
        }
      }
    }
  ]
}
```

## Dynamic Menu System

### 1. Kernel and Info Objects
```javascript
menu: async (kernel, info) => {
  // info object provides 4 key methods:
  // - info.local(filepath): get local variables from running script
  // - info.running(filepath): check if script is running
  // - info.exists(filepath): check if file exists
  // - info.path(filepath): get absolute path

  let installed = info.exists("app/env")
  let running = info.running("start.json")

  if (installed && running) {
    return [
      { icon: "fa-solid fa-rocket", text: "Web UI", href: "start.json" },
      { icon: "fa-solid fa-terminal", text: "Terminal", href: "start.json" }
    ]
  } else if (installed) {
    return [
      { icon: "fa-solid fa-power-off", text: "Start", href: "start.json" }
    ]
  } else {
    return [
      { icon: "fa-solid fa-plug", text: "Install", href: "install.json" }
    ]
  }
}
```

### 2. State-Based Menu Logic
```javascript
menu: async (kernel, info) => {
  // Check multiple conditions for complex state management
  let installing = info.running("install.json")
  let installed = info.exists("app/env")
  let updating = info.running("update.json")

  if (updating) {
    return [{ icon: "fa-solid fa-rotate", text: "Updating...", href: "update.json" }]
  } else if (installing) {
    return [{ icon: "fa-solid fa-plug", text: "Installing...", href: "install.json" }]
  } else if (installed) {
    return [
      { icon: "fa-solid fa-power-off", text: "Start", href: "start.json" },
      { icon: "fa-solid fa-rotate", text: "Update", href: "update.json" }
    ]
  } else {
    return [{ icon: "fa-solid fa-plug", text: "Install", href: "install.json" }]
  }
}
```

## Virtual Drive System (fs.link)

### 1. Basic Drive Mapping
```json
{
  "method": "fs.link",
  "params": {
    "drive": {
      "checkpoints": "app/models/checkpoints",
      "loras": "app/models/loras",
      "vae": "app/models/vae",
      "embeddings": "app/models/embeddings"
    }
  }
}
```

### 2. Peer Repository Integration
```json
{
  "method": "fs.link",
  "params": {
    "drive": {
      "checkpoints": "app/models/checkpoints",
      "loras": "app/models/loras"
    },
    "peers": [
      "https://github.com/user/stable-diffusion-webui.git",
      "https://github.com/user/comfyui.git"
    ]
  }
}
```

### 3. Complex Drive Configuration
```json
{
  "method": "fs.link",
  "params": {
    "drive": {
      "checkpoints": "app/models/checkpoints",
      "clip": "app/models/clip",
      "clip_vision": "app/models/clip_vision",
      "configs": "app/models/configs",
      "controlnet": "app/models/controlnet",
      "diffusers": "app/models/diffusers",
      "embeddings": "app/models/embeddings",
      "gligen": "app/models/gligen",
      "hypernetworks": "app/models/hypernetworks",
      "inpaint": "app/models/inpaint",
      "loras": "app/models/loras",
      "prompt_expansion": "app/models/prompt_expansion",
      "style_models": "app/models/style_models",
      "unet": "app/models/unet",
      "upscale_models": "app/models/upscale_models",
      "vae": "app/models/vae",
      "vae_approx": "app/models/vae_approx"
    },
    "peers": [
      "https://github.com/user/automatic1111.git",
      "https://github.com/user/fooocus.git",
      "https://github.com/user/comfyui.git"
    ]
  }
}
```

## Application State Management

### 1. Installation State Detection
```javascript
// Check if app is installed
let installed = info.exists("app/env")

// Check if app is currently installing
let installing = info.running("install.json")

// Check if app is currently running
let running = info.running("start.json")
```

### 2. Dynamic URL Detection
```javascript
// Get local variables from running script
let memory = info.local("start.json")

if (memory && memory.url) {
  // App has exposed a web UI
  return [
    { icon: "fa-solid fa-rocket", text: "Web UI", href: memory.url },
    { icon: "fa-solid fa-terminal", text: "Terminal", href: "start.json" }
  ]
}
```

### 3. Multi-Step Installation Tracking
```javascript
// Track installation progress
let installProgress = info.local("install.json")

if (installProgress) {
  let step = installProgress.current_step || 0
  let total = installProgress.total_steps || 1
  return [{
    icon: "fa-solid fa-plug",
    text: `Installing... (${step}/${total})`,
    href: "install.json"
  }]
}
```

## Integration Patterns

### 1. Environment Variables
```json
{
  "method": "shell.run",
  "params": {
    "message": "cd app && python app.py",
    "env": {
      "PORT": "7860",
      "HOST": "0.0.0.0",
      "MODEL_PATH": "{{drive.checkpoints}}"
    }
  }
}
```

### 2. Conditional Execution
```json
{
  "run": [
    {
      "method": "shell.run",
      "params": {
        "message": "git clone https://github.com/user/repo.git app",
        "if": "!fs.exists('app')"
      }
    }
  ]
}
```

### 3. Error Handling
```json
{
  "run": [
    {
      "method": "shell.run",
      "params": {
        "message": "python setup.py",
        "on_error": "continue"
      }
    }
  ]
}
```

## Pinokio API Methods

### 1. File System Operations
```javascript
// Common fs.* methods available in Pinokio
{
  "method": "fs.download",
  "params": {
    "url": "https://example.com/model.bin",
    "path": "app/models/model.bin"
  }
}

{
  "method": "fs.copy",
  "params": {
    "from": "source/path",
    "to": "dest/path"
  }
}

{
  "method": "fs.unlink",
  "params": {
    "path": "app/models/old_model.bin"
  }
}
```

### 2. Shell Operations
```javascript
{
  "method": "shell.run",
  "params": {
    "message": "pip install -r requirements.txt",
    "path": "app",
    "env": {
      "PYTHONPATH": "{{kernel.path}}"
    }
  }
}
```

### 3. Input Handling
```javascript
{
  "method": "input",
  "params": {
    "title": "Configuration Required",
    "message": "Enter your API key:",
    "type": "password"
  }
}
```

## Best Practices for PinokioCloud Integration

### 1. Application Structure
```
my-app/
├── pinokio.js          # Main configuration
├── install.json        # Installation script
├── start.json         # Launch script
├── app/               # Application files
│   └── env            # Installation marker
└── icon.png           # Application icon
```

### 2. State Management
```javascript
// Robust state checking
menu: async (kernel, info) => {
  try {
    let appPath = info.path("app")
    let installed = info.exists("app/env")
    let running = info.running("start.json")
    let memory = info.local("start.json")

    // Comprehensive state logic here...

  } catch (error) {
    console.error("Menu generation error:", error)
    return [{ icon: "fa-solid fa-exclamation-triangle", text: "Error", href: "" }]
  }
}
```

### 3. Error Recovery
```json
{
  "run": [
    {
      "method": "shell.run",
      "params": {
        "message": "python app.py",
        "on_error": "stop",
        "retry": 3
      }
    }
  ]
}
```

## PinokioCloud Translation Strategy

### 1. Script Format Conversion
```python
# Pinokio JSON to Python recipe conversion
def translate_pinokio_script(pinokio_json):
    \"\"\"Convert Pinokio JSON script to Python recipe format.\"\"\"

    recipe = []
    for step in pinokio_json.get('run', []):
        method = step.get('method')
        params = step.get('params', {})

        if method == 'shell.run':
            recipe.append({
                'step_type': 'shell',
                'command': params.get('message'),
                'path': params.get('path'),
                'env': params.get('env', {})
            })
        elif method == 'fs.link':
            recipe.append({
                'step_type': 'link_drive',
                'drive': params.get('drive', {}),
                'peers': params.get('peers', [])
            })

    return recipe
```

### 2. Dynamic Menu Translation
```python
def translate_pinokio_menu(pinokio_js):
    \"\"\"Convert Pinokio dynamic menu to Python state logic.\"\"\"

    # Extract menu logic and convert to Python conditionals
    # This would analyze the async function and convert to
    # equivalent Python state checking logic
    pass
```

## Ecosystem Integration

### 1. Model Sharing
```json
{
  "method": "fs.link",
  "params": {
    "drive": {
      "checkpoints": "app/models/checkpoints",
      "loras": "app/models/loras",
      "vae": "app/models/vae"
    },
    "peers": [
      "https://github.com/user/stable-diffusion-webui.git",
      "https://github.com/user/comfyui.git",
      "https://github.com/user/fooocus.git"
    ]
  }
}
```

### 2. Configuration Sharing
```javascript
// Share configuration between applications
const sharedConfig = {
  theme: "dark",
  api_keys: {
    openai: process.env.OPENAI_API_KEY,
    stability: process.env.STABILITY_API_KEY
  }
}
```

## Summary

This guide provides:
- **Complete Pinokio application structure** understanding
- **Dynamic menu system** implementation patterns
- **Virtual drive system** for resource sharing
- **State management** best practices
- **Integration patterns** for multi-app ecosystems
- **Translation strategies** for PinokioCloud compatibility

All patterns maintain compliance with the project's core principles and provide a solid foundation for Pinokio application ecosystem integration.