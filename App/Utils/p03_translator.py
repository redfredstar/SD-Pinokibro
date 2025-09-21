"""
P03_Translator.py - The Universal Translator (Installer Conversion Engine)

This module implements an abstraction layer that tames the complexity of Pinokio's
diverse installer formats, converting them into a single, standardized Python-based
"recipe". It supports parsing .json, .js, and requirements.txt files without
requiring a Node.js runtime for JavaScript parsing.

Author: Pinokiobro Architect
Phase: P03 - The Universal Translator
"""

import json
import re
import os
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import logging


@dataclass
class RecipeStep:
    """
    Represents a single step in a standardized installation recipe.

    This dataclass provides a consistent structure for all installation steps,
    regardless of the original installer format.
    """

    step_type: str  # 'shell', 'download', 'git_clone', 'input', 'env_create', etc.
    params: Dict[str, Any]  # Parameters specific to the step type
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata like line number

    def __post_init__(self):
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = {}


class P03_Translator:
    """
    A class for parsing various Pinokio installer formats into standardized recipes.

    This translator supports parsing .json, .js, and requirements.txt files,
    converting them into a consistent list of RecipeStep objects that can be
    executed by the installation engine.
    """

    def __init__(self):
        """Initialize the translator with regex patterns for JavaScript parsing."""
        # Define regex patterns for extracting Pinokio API calls from JavaScript
        self.js_patterns = {
            "shell.run": re.compile(
                r'shell\.run\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*(?:,\s*\{[^}]*\})?\s*\)',
                re.MULTILINE,
            ),
            "fs.download": re.compile(
                r'fs\.download\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*(?:,\s*[\'"`]([^\'"`]*)[\'"`])?\s*\)',
                re.MULTILINE,
            ),
            "git.clone": re.compile(
                r'git\.clone\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*(?:,\s*[\'"`]([^\'"`]*)[\'"`])?\s*\)',
                re.MULTILINE,
            ),
            "input": re.compile(
                r'input\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*(?:,\s*[\'"`]([^\'"`]*)[\'"`])?\s*\)',
                re.MULTILINE,
            ),
            "env.create": re.compile(
                r'env\.create\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*(?:,\s*[\'"`]([^\'"`]*)[\'"`])?\s*\)',
                re.MULTILINE,
            ),
            "pip.install": re.compile(
                r'pip\.install\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*\)', re.MULTILINE
            ),
            "npm.install": re.compile(
                r'npm\.install\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*\)', re.MULTILINE
            ),
            "os.chdir": re.compile(
                r'os\.chdir\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*\)', re.MULTILINE
            ),
            "fs.mkdir": re.compile(
                r'fs\.mkdir\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*\)', re.MULTILINE
            ),
        }

    def parse_file(self, file_path: str) -> List[RecipeStep]:
        """
        Parse an installer file based on its extension.

        Args:
            file_path: Path to the installer file.

        Returns:
            A list of RecipeStep objects representing the installation workflow.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            ValueError: If the file format is unsupported.
            Exception: For parsing errors, with full traceback.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Installer file not found: {file_path}")

        file_ext = os.path.splitext(file_path)[1].lower()

        try:
            if file_ext == ".json":
                return self.parse_json(file_path)
            elif file_ext == ".js":
                return self.parse_js(file_path)
            elif file_ext == ".txt":
                # Check if it's a requirements.txt file
                if os.path.basename(file_path).startswith("requirements"):
                    return self.parse_requirements_txt(file_path)
                else:
                    raise ValueError(f"Unsupported .txt file: {file_path}")
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
        except Exception as e:
            logging.error(
                f"Failed to parse installer file {file_path}: {str(e)}", exc_info=True
            )
            raise

    def parse_json(self, file_path: str) -> List[RecipeStep]:
        """
        Parse a JSON installer file into a recipe.

        Args:
            file_path: Path to the JSON installer file.

        Returns:
            A list of RecipeStep objects.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        recipe = []

        # Handle different JSON structures
        if isinstance(data, list):
            # List of commands
            for i, item in enumerate(data):
                if isinstance(item, str):
                    recipe.append(
                        RecipeStep(
                            step_type="shell",
                            params={"command": item},
                            metadata={"line_number": i + 1},
                        )
                    )
                elif isinstance(item, dict):
                    # Handle structured commands
                    step_type = item.get("type", "shell")
                    params = {k: v for k, v in item.items() if k != "type"}
                    recipe.append(
                        RecipeStep(
                            step_type=step_type,
                            params=params,
                            metadata={"line_number": i + 1},
                        )
                    )
        elif isinstance(data, dict):
            # Single command object
            step_type = data.get("type", "shell")
            params = {k: v for k, v in data.items() if k != "type"}
            recipe.append(
                RecipeStep(
                    step_type=step_type, params=params, metadata={"line_number": 1}
                )
            )

        return recipe

    def parse_js(self, file_path: str) -> List[RecipeStep]:
        """
        Parse a JavaScript installer file using regex patterns.

        This method avoids requiring a Node.js runtime by using advanced regex
        pattern matching to extract Pinokio API calls.

        Args:
            file_path: Path to the JavaScript installer file.

        Returns:
            A list of RecipeStep objects ordered by line number.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        recipe = []

        # Find all matches with their line numbers
        matches = []

        for api_call, pattern in self.js_patterns.items():
            for match in pattern.finditer(content):
                line_num = content[: match.start()].count("\n") + 1
                matches.append((line_num, api_call, match.groups()))

        # Sort matches by line number to preserve execution order
        matches.sort(key=lambda x: x[0])

        # Convert matches to recipe steps
        for line_num, api_call, groups in matches:
            step = self._convert_js_match_to_step(api_call, groups, line_num)
            if step:
                recipe.append(step)

        return recipe

    def _convert_js_match_to_step(
        self, api_call: str, groups: tuple, line_num: int
    ) -> Optional[RecipeStep]:
        """
        Convert a regex match from JavaScript to a RecipeStep.

        Args:
            api_call: The Pinokio API call name (e.g., 'shell.run').
            groups: The regex match groups.
            line_num: The line number where the match was found.

        Returns:
            A RecipeStep object or None if the conversion failed.
        """
        try:
            if api_call == "shell.run":
                return RecipeStep(
                    step_type="shell",
                    params={"command": groups[0]},
                    metadata={"line_number": line_num},
                )
            elif api_call == "fs.download":
                params = {"url": groups[0]}
                if len(groups) > 1 and groups[1]:
                    params["dest"] = groups[1]
                return RecipeStep(
                    step_type="download",
                    params=params,
                    metadata={"line_number": line_num},
                )
            elif api_call == "git.clone":
                params = {"repo": groups[0]}
                if len(groups) > 1 and groups[1]:
                    params["dest"] = groups[1]
                return RecipeStep(
                    step_type="git_clone",
                    params=params,
                    metadata={"line_number": line_num},
                )
            elif api_call == "input":
                params = {"prompt": groups[0]}
                if len(groups) > 1 and groups[1]:
                    params["default"] = groups[1]
                return RecipeStep(
                    step_type="input", params=params, metadata={"line_number": line_num}
                )
            elif api_call == "env.create":
                params = {"name": groups[0]}
                if len(groups) > 1 and groups[1]:
                    params["type"] = groups[1]
                return RecipeStep(
                    step_type="env_create",
                    params=params,
                    metadata={"line_number": line_num},
                )
            elif api_call == "pip.install":
                return RecipeStep(
                    step_type="pip_install",
                    params={"package": groups[0]},
                    metadata={"line_number": line_num},
                )
            elif api_call == "npm.install":
                return RecipeStep(
                    step_type="npm_install",
                    params={"package": groups[0]},
                    metadata={"line_number": line_num},
                )
            elif api_call == "os.chdir":
                return RecipeStep(
                    step_type="chdir",
                    params={"path": groups[0]},
                    metadata={"line_number": line_num},
                )
            elif api_call == "fs.mkdir":
                return RecipeStep(
                    step_type="mkdir",
                    params={"path": groups[0]},
                    metadata={"line_number": line_num},
                )
        except Exception as e:
            logging.warning(f"Failed to convert JS match at line {line_num}: {str(e)}")

        return None

    def parse_requirements_txt(self, file_path: str) -> List[RecipeStep]:
        """
        Parse a requirements.txt file into a recipe.

        Args:
            file_path: Path to the requirements.txt file.

        Returns:
            A list of RecipeStep objects.
        """
        recipe = []

        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Handle package specifications
                if line:
                    recipe.append(
                        RecipeStep(
                            step_type="pip_install",
                            params={"package": line},
                            metadata={"line_number": line_num},
                        )
                    )

        return recipe

    def validate_recipe(self, recipe: List[RecipeStep]) -> bool:
        """
        Validate a parsed recipe for basic consistency.

        Args:
            recipe: The list of RecipeStep objects to validate.

        Returns:
            True if the recipe is valid, False otherwise.
        """
        if not recipe:
            logging.warning("Recipe is empty")
            return False

        required_params = {
            "shell": ["command"],
            "download": ["url"],
            "git_clone": ["repo"],
            "input": ["prompt"],
            "env_create": ["name"],
            "pip_install": ["package"],
            "npm_install": ["package"],
            "chdir": ["path"],
            "mkdir": ["path"],
        }

        for step in recipe:
            step_type = step.step_type
            if step_type in required_params:
                for param in required_params[step_type]:
                    if param not in step.params:
                        logging.error(
                            f"Missing required parameter '{param}' "
                            f"for step type '{step_type}' at line "
                            f"{step.metadata.get('line_number', 'unknown')}"
                        )
                        return False

        return True
