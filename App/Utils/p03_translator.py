"""
app/utils/P03_Translator.py
Universal Installer Parser

Converts diverse Pinokio installer formats (.js, .json, requirements.txt) into
standardized Python recipes without requiring a Node.js runtime.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class JavaScriptPatterns:
    """Comprehensive regex patterns for extracting Pinokio API calls from JavaScript."""
    
    # shell.run() with optional options object
    SHELL_RUN: re.Pattern = re.compile(
        r'shell\.run\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*(?:,\s*(\{[^}]*\}))?\s*\)',
        re.MULTILINE | re.DOTALL
    )
    
    # fs.download() with URL, destination, and optional options
    FS_DOWNLOAD: re.Pattern = re.compile(
        r'fs\.download\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*,\s*[\'"`]([^\'"`]+)[\'"`]\s*(?:,\s*(\{[^}]*\}))?\s*\)',
        re.MULTILINE | re.DOTALL
    )
    
    # fs.copy() with source and destination
    FS_COPY: re.Pattern = re.compile(
        r'fs\.copy\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*,\s*[\'"`]([^\'"`]+)[\'"`]\s*\)',
        re.MULTILINE
    )
    
    # fs.link() for symbolic links
    FS_LINK: re.Pattern = re.compile(
        r'fs\.link\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*,\s*[\'"`]([^\'"`]+)[\'"`]\s*\)',
        re.MULTILINE
    )
    
    # fs.write() with path and content
    FS_WRITE: re.Pattern = re.compile(
        r'fs\.write\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*,\s*[\'"`]([^\'"`]+)[\'"`]\s*\)',
        re.MULTILINE | re.DOTALL
    )
    
    # input() for user prompts
    INPUT: re.Pattern = re.compile(
        r'input\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*(?:,\s*[\'"`]([^\'"`]+)[\'"`])?\s*\)',
        re.MULTILINE
    )
    
    # git.clone() operations
    GIT_CLONE: re.Pattern = re.compile(
        r'git\.clone\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*(?:,\s*[\'"`]([^\'"`]+)[\'"`])?\s*\)',
        re.MULTILINE
    )
    
    # npm operations
    NPM_INSTALL: re.Pattern = re.compile(
        r'npm\.install\s*\(\s*(?:[\'"`]([^\'"`]+)[\'"`])?\s*\)',
        re.MULTILINE
    )
    
    # pip operations
    PIP_INSTALL: re.Pattern = re.compile(
        r'pip\.install\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*\)',
        re.MULTILINE
    )

class P03_Translator:
    """
    Translates Pinokio installer scripts into standardized Python recipes.
    
    Supports:
    - JavaScript (.js) files with Pinokio API calls
    - JSON (.json) installer manifests
    - Python requirements.txt files
    """
    
    def __init__(self):
        """Initialize the translator with regex patterns."""
        self.patterns = JavaScriptPatterns()
    
    def parse_js(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse JavaScript installer files using regex patterns.
        
        Args:
            file_path: Path to the .js installer file
            
        Returns:
            Standardized recipe as list of step dictionaries
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                js_content = f.read()
        except Exception as e:
            print(f"[ERROR] Failed to read JS file {file_path}: {e}")
            return []
        
        # Preprocess JavaScript content
        js_content = self._preprocess_js(js_content)
        
        # Extract all API calls with line numbers
        extracted_calls = []
        
        # Process shell.run calls
        for match in self.patterns.SHELL_RUN.finditer(js_content):
            command = match.group(1)
            options = match.group(2) if match.group(2) else "{}"
            
            extracted_calls.append({
                "raw_type": "shell.run",
                "command": command,
                "options": self._parse_js_object(options),
                "line_number": js_content[:match.start()].count('\n') + 1
            })
        
        # Process fs.download calls
        for match in self.patterns.FS_DOWNLOAD.finditer(js_content):
            url = match.group(1)
            destination = match.group(2)
            options = match.group(3) if match.group(3) else "{}"
            
            extracted_calls.append({
                "raw_type": "fs.download",
                "url": url,
                "destination": destination,
                "options": self._parse_js_object(options),
                "line_number": js_content[:match.start()].count('\n') + 1
            })
        
        # Process fs.copy calls
        for match in self.patterns.FS_COPY.finditer(js_content):
            source = match.group(1)
            destination = match.group(2)
            
            extracted_calls.append({
                "raw_type": "fs.copy",
                "source": source,
                "destination": destination,
                "line_number": js_content[:match.start()].count('\n') + 1
            })
        
        # Process fs.link calls
        for match in self.patterns.FS_LINK.finditer(js_content):
            source = match.group(1)
            destination = match.group(2)
            
            extracted_calls.append({
                "raw_type": "fs.link",
                "source": source,
                "destination": destination,
                "line_number": js_content[:match.start()].count('\n') + 1
            })
        
        # Process fs.write calls
        for match in self.patterns.FS_WRITE.finditer(js_content):
            path = match.group(1)
            content = match.group(2)
            
            extracted_calls.append({
                "raw_type": "fs.write",
                "path": path,
                "content": content,
                "line_number": js_content[:match.start()].count('\n') + 1
            })
        
        # Process input calls
        for match in self.patterns.INPUT.finditer(js_content):
            prompt = match.group(1)
            default = match.group(2) if match.group(2) else None
            
            extracted_calls.append({
                "raw_type": "input",
                "prompt": prompt,
                "default": default,
                "line_number": js_content[:match.start()].count('\n') + 1
            })
        
        # Process git.clone calls
        for match in self.patterns.GIT_CLONE.finditer(js_content):
            repo_url = match.group(1)
            destination = match.group(2) if match.group(2) else None
            
            extracted_calls.append({
                "raw_type": "git.clone",
                "repo_url": repo_url,
                "destination": destination,
                "line_number": js_content[:match.start()].count('\n') + 1
            })
        
        # Process npm.install calls
        for match in self.patterns.NPM_INSTALL.finditer(js_content):
            package = match.group(1) if match.group(1) else None
            
            extracted_calls.append({
                "raw_type": "npm.install",
                "package": package,
                "line_number": js_content[:match.start()].count('\n') + 1
            })
        
        # Process pip.install calls
        for match in self.patterns.PIP_INSTALL.finditer(js_content):
            package = match.group(1)
            
            extracted_calls.append({
                "raw_type": "pip.install",
                "package": package,
                "line_number": js_content[:match.start()].count('\n') + 1
            })
        
        # Sort by line number to preserve execution order
        extracted_calls.sort(key=lambda x: x["line_number"])
        
        # Convert to standardized format
        standardized_recipe = []
        for call in extracted_calls:
            standardized_step = self._standardize_step(call)
            if standardized_step:
                standardized_recipe.append(standardized_step)
        
        return standardized_recipe
    
    def parse_json(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse JSON installer manifest files.
        
        Args:
            file_path: Path to the .json installer file
            
        Returns:
            Standardized recipe as list of step dictionaries
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to read JSON file {file_path}: {e}")
            return []
        
        standardized_recipe = []
        
        # Handle both list and dict formats
        if isinstance(json_data, list):
            for step in json_data:
                standardized_step = self._convert_json_step(step)
                if standardized_step:
                    standardized_recipe.append(standardized_step)
        elif isinstance(json_data, dict):
            # Check for 'run' array (common Pinokio format)
            if 'run' in json_data and isinstance(json_data['run'], list):
                for step in json_data['run']:
                    standardized_step = self._convert_json_step(step)
                    if standardized_step:
                        standardized_recipe.append(standardized_step)
            else:
                # Single step JSON file
                standardized_step = self._convert_json_step(json_data)
                if standardized_step:
                    standardized_recipe.append(standardized_step)
        
        return standardized_recipe
    
    def parse_requirements(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse Python requirements.txt files.
        
        Args:
            file_path: Path to the requirements.txt file
            
        Returns:
            Standardized recipe as list of pip install steps
        """
        standardized_recipe = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Handle environment markers and version specifiers
                    # Clean but preserve the full requirement specification
                    standardized_recipe.append({
                        "step_type": "shell_run",
                        "params": {
                            "command": f"pip install {line}",
                            "args": [],
                            "options": {}
                        },
                        "conditions": {},
                        "error_handling": "stop"
                    })
        except Exception as e:
            print(f"[ERROR] Failed to read requirements file {file_path}: {e}")
            return []
        
        return standardized_recipe
    
    def _preprocess_js(self, js_content: str) -> str:
        """
        Clean JavaScript content for better regex matching.
        
        Args:
            js_content: Raw JavaScript content
            
        Returns:
            Preprocessed JavaScript content
        """
        # Remove single-line comments
        js_content = re.sub(r'//.*?$', '', js_content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
        
        # Normalize whitespace around function calls
        js_content = re.sub(r'\s*\(\s*', '(', js_content)
        js_content = re.sub(r'\s*\)\s*', ')', js_content)
        
        return js_content
    
    def _parse_js_object(self, js_obj_str: str) -> Dict[str, Any]:
        """
        Parse simple JavaScript object literals.
        
        Args:
            js_obj_str: JavaScript object string
            
        Returns:
            Python dictionary representation
        """
        if not js_obj_str or js_obj_str.strip() == "{}":
            return {}
        
        # Simple key-value extraction for basic objects
        obj_pattern = re.compile(r'(\w+)\s*:\s*([\'"`]?)([^,}]+)\2')
        
        result = {}
        for match in obj_pattern.finditer(js_obj_str):
            key = match.group(1)
            value = match.group(3).strip()
            
            # Convert to appropriate Python type
            if value.isdigit():
                result[key] = int(value)
            elif value.replace('.', '', 1).isdigit():
                result[key] = float(value)
            elif value.lower() in ['true', 'false']:
                result[key] = value.lower() == 'true'
            elif value.lower() == 'null':
                result[key] = None
            else:
                result[key] = value
        
        return result
    
    def _standardize_step(self, step_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert raw parsed data to standardized format.
        
        Args:
            step_data: Raw extracted step data
            
        Returns:
            Standardized step dictionary or None if unknown type
        """
        raw_type = step_data.get("raw_type")
        
        if raw_type == "shell.run":
            return {
                "step_type": "shell_run",
                "params": {
                    "command": step_data["command"],
                    "args": [],
                    "options": step_data.get("options", {})
                },
                "conditions": {},
                "error_handling": "stop"
            }
        
        elif raw_type == "fs.download":
            return {
                "step_type": "fs_download",
                "params": {
                    "url": step_data["url"],
                    "destination": step_data["destination"],
                    "checksum": step_data.get("options", {}).get("checksum"),
                    "options": step_data.get("options", {})
                },
                "conditions": {},
                "error_handling": "stop"
            }
        
        elif raw_type == "fs.copy":
            return {
                "step_type": "fs_copy",
                "params": {
                    "source": step_data["source"],
                    "destination": step_data["destination"]
                },
                "conditions": {},
                "error_handling": "stop"
            }
        
        elif raw_type == "fs.link":
            return {
                "step_type": "fs_link",
                "params": {
                    "source": step_data["source"],
                    "destination": step_data["destination"]
                },
                "conditions": {},
                "error_handling": "stop"
            }
        
        elif raw_type == "fs.write":
            return {
                "step_type": "fs_write",
                "params": {
                    "path": step_data["path"],
                    "content": step_data["content"]
                },
                "conditions": {},
                "error_handling": "stop"
            }
        
        elif raw_type == "input":
            return {
                "step_type": "input",
                "params": {
                    "prompt": step_data["prompt"],
                    "default": step_data.get("default"),
                    "variable_name": step_data.get("variable_name", "user_input")
                },
                "conditions": {},
                "error_handling": "stop"
            }
        
        elif raw_type == "git.clone":
            destination = step_data.get("destination", "")
            if not destination:
                # Extract repo name from URL for default destination
                repo_url = step_data["repo_url"]
                destination = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
            
            return {
                "step_type": "shell_run",
                "params": {
                    "command": f"git clone {step_data['repo_url']} {destination}",
                    "args": [],
                    "options": {}
                },
                "conditions": {},
                "error_handling": "stop"
            }
        
        elif raw_type == "npm.install":
            package = step_data.get("package", "")
            command = f"npm install {package}" if package else "npm install"
            
            return {
                "step_type": "shell_run",
                "params": {
                    "command": command,
                    "args": [],
                    "options": {}
                },
                "conditions": {},
                "error_handling": "stop"
            }
        
        elif raw_type == "pip.install":
            return {
                "step_type": "shell_run",
                "params": {
                    "command": f"pip install {step_data['package']}",
                    "args": [],
                    "options": {}
                },
                "conditions": {},
                "error_handling": "stop"
            }
        
        else:
            # Unknown step type - return generic step for debugging
            return {
                "step_type": "unknown",
                "params": step_data,
                "conditions": {},
                "error_handling": "continue"
            }
    
    def _convert_json_step(self, step: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert a JSON step object to standardized format.
        
        Args:
            step: JSON step object
            
        Returns:
            Standardized step dictionary
        """
        # Determine step type from JSON structure
        if "method" in step:
            # Pinokio JSON format with method field
            method = step["method"]
            params = step.get("params", {})
            
            if method == "shell.run":
                return {
                    "step_type": "shell_run",
                    "params": {
                        "command": params.get("command", ""),
                        "args": params.get("args", []),
                        "options": params.get("options", {})
                    },
                    "conditions": step.get("conditions", {}),
                    "error_handling": step.get("error_handling", "stop")
                }
            elif method == "fs.download":
                return {
                    "step_type": "fs_download",
                    "params": params,
                    "conditions": step.get("conditions", {}),
                    "error_handling": step.get("error_handling", "stop")
                }
            elif method == "fs.copy":
                return {
                    "step_type": "fs_copy",
                    "params": params,
                    "conditions": step.get("conditions", {}),
                    "error_handling": step.get("error_handling", "stop")
                }
            elif method == "input":
                return {
                    "step_type": "input",
                    "params": params,
                    "conditions": step.get("conditions", {}),
                    "error_handling": step.get("error_handling", "stop")
                }
        
        # Alternative format detection
        if "command" in step:
            # Direct command format
            return {
                "step_type": "shell_run",
                "params": {
                    "command": step["command"],
                    "args": step.get("args", []),
                    "options": step.get("options", {})
                },
                "conditions": step.get("conditions", {}),
                "error_handling": step.get("error_handling", "stop")
            }
        
        # If we can't determine the format, return None
        return None