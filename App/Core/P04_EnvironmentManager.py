"""
P04_EnvironmentManager.py - The Environment Architect (Conda/Venv Engine)

This module provides platform-aware virtual environment management for the PinokioCloud system.
It implements the Conda-first, venv fallback strategy as mandated by the project rules.

The EnvironmentManager class is responsible for:
- Detecting the current platform and selecting the appropriate environment strategy
- Creating isolated environments using either Conda or venv
- Providing the correct command prefixes for executing commands within environments

Author: Pinokiobro Architect
Phase: P04 - The Environment Architect
"""

import os
import sys
from typing import Optional, Callable, Any
from pathlib import Path


class EnvironmentManager:
    """
    A platform-aware environment manager that provides isolated execution environments.

    This class implements the Conda-first, venv fallback strategy mandated by the project rules.
    It automatically detects the platform and switches to venv only when running on Lightning AI.

    Attributes:
        strategy (str): The environment strategy to use ('conda' or 'venv')
        env_path (Path): The base path where environments will be created
        platform_info (dict): Information about the detected platform
    """

    def __init__(
        self, cloud_detector: Any, process_manager: Any, path_mapper: Any
    ) -> None:
        """
        Initialize the EnvironmentManager with required dependencies.

        Args:
            cloud_detector: Instance of P01_CloudDetector for platform detection
            process_manager: Instance of P02_ProcessManager for command execution
            path_mapper: Instance of P01_PathMapper for path resolution

        Raises:
            RuntimeError: If any dependency is None or invalid
        """
        try:
            if not cloud_detector:
                raise RuntimeError(
                    "EnvironmentManager requires a valid P01_CloudDetector instance"
                )
            if not process_manager:
                raise RuntimeError(
                    "EnvironmentManager requires a valid P02_ProcessManager instance"
                )
            if not path_mapper:
                raise RuntimeError(
                    "EnvironmentManager requires a valid P01_PathMapper instance"
                )

            self.cloud_detector = cloud_detector
            self.process_manager = process_manager
            self.path_mapper = path_mapper

            # Detect platform and set strategy
            self.platform_info = self.cloud_detector.detect_platform()

            # Implement Conda-first, venv fallback strategy
            if self.platform_info.get("platform_name") == "LightningAI":
                self.strategy = "venv"
            else:
                self.strategy = "conda"

            # Get base path for environments
            self.env_path = Path(self.path_mapper.get_envs_path())

            # Ensure environments directory exists
            self.env_path.mkdir(parents=True, exist_ok=True)

        except Exception as e:
            error_msg = f"Failed to initialize EnvironmentManager: {str(e)}"
            print(f"ERROR: {error_msg}")
            print(f"Traceback: {sys.exc_info()}")
            raise RuntimeError(error_msg) from e

    def create(
        self, env_name: str, callback: Optional[Callable[[str], None]] = None
    ) -> int:
        """
        Create a new virtual environment using the appropriate strategy.

        Args:
            env_name (str): Name of the environment to create
            callback (callable, optional): Function to call with each line of output

        Returns:
            int: Exit code from the environment creation command (0 for success)

        Raises:
            ValueError: If env_name is empty or invalid
            RuntimeError: If environment creation fails
        """
        try:
            if not env_name or not env_name.strip():
                raise ValueError("Environment name cannot be empty")

            env_name = env_name.strip()

            if self.strategy == "conda":
                command = f"conda create -n {env_name} python=3.10 -y"
            elif self.strategy == "venv":
                env_full_path = self.env_path / env_name
                command = f"python -m venv {env_full_path}"
            else:
                raise RuntimeError(f"Unknown environment strategy: {self.strategy}")

            if callback:
                callback(f"INFO: Creating {self.strategy} environment '{env_name}'...")
                callback(f"INFO: Using strategy: {self.strategy}")
                callback(f"INFO: Executing command: {command}")

            # Execute the environment creation command
            exit_code = self.process_manager.shell_run(command, callback or print)

            if exit_code == 0:
                if callback:
                    callback(
                        f"SUCCESS: Environment '{env_name}' created successfully using {self.strategy}"
                    )
            else:
                error_msg = f"Failed to create environment '{env_name}' with exit code {exit_code}"
                if callback:
                    callback(f"ERROR: {error_msg}")
                raise RuntimeError(error_msg)

            return exit_code

        except Exception as e:
            error_msg = f"Environment creation failed for '{env_name}': {str(e)}"
            print(f"ERROR: {error_msg}")
            print(f"Traceback: {sys.exc_info()}")
            if callback:
                callback(f"ERROR: {error_msg}")
                callback(f"Traceback: {sys.exc_info()}")
            raise RuntimeError(error_msg) from e

    def get_run_prefix(self, env_name: str) -> str:
        """
        Get the command prefix needed to execute commands within the specified environment.

        Args:
            env_name (str): Name of the environment

        Returns:
            str: Command prefix string for executing commands in the environment

        Raises:
            ValueError: If env_name is empty or invalid
            RuntimeError: If the strategy is unknown
        """
        try:
            if not env_name or not env_name.strip():
                raise ValueError("Environment name cannot be empty")

            env_name = env_name.strip()

            if self.strategy == "conda":
                return f"conda run -n {env_name} -- "
            elif self.strategy == "venv":
                env_full_path = self.env_path / env_name
                if os.name == "nt":  # Windows
                    return f"{env_full_path}\\Scripts\\activate.bat && "
                else:  # Unix/Linux
                    return f"source {env_full_path}/bin/activate && "
            else:
                raise RuntimeError(f"Unknown environment strategy: {self.strategy}")

        except Exception as e:
            error_msg = (
                f"Failed to get run prefix for environment '{env_name}': {str(e)}"
            )
            print(f"ERROR: {error_msg}")
            print(f"Traceback: {sys.exc_info()}")
            raise RuntimeError(error_msg) from e

    def list_environments(self) -> list:
        """
        List all available environments for the current strategy.

        Returns:
            list: List of environment names
        """
        try:
            if self.strategy == "conda":
                # List conda environments
                exit_code = self.process_manager.shell_run("conda env list", print)
                if exit_code != 0:
                    print(
                        f"WARNING: Failed to list conda environments, exit code: {exit_code}"
                    )
                return []  # Would need to parse output in a real implementation
            elif self.strategy == "venv":
                # List venv environments
                envs = []
                if self.env_path.exists():
                    for item in self.env_path.iterdir():
                        if item.is_dir() and (item / "bin" / "activate").exists():
                            envs.append(item.name)
                return envs
            else:
                return []

        except Exception as e:
            error_msg = f"Failed to list environments: {str(e)}"
            print(f"ERROR: {error_msg}")
            print(f"Traceback: {sys.exc_info()}")
            return []

    def get_platform_info(self) -> dict:
        """
        Get information about the detected platform and strategy.

        Returns:
            dict: Platform information including strategy and environment path
        """
        return {
            "platform_info": self.platform_info,
            "strategy": self.strategy,
            "env_path": str(self.env_path),
            "available_environments": self.list_environments(),
        }
