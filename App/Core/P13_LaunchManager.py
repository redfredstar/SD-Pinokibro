"""
P13_LaunchManager.py - The Application Launch Orchestrator

Phase P13 of the PinokioCloud Rebuild Project
Objective: Provide the central orchestration engine for launching installed applications
as persistent background processes with comprehensive error handling and state management.

This module implements the core launch functionality that transforms installed applications
into running, accessible services. It follows the precise 5-step launch sequence defined
in the MASTER_GUIDE.md blueprint.
"""

import os
import traceback
from pathlib import Path
from typing import Callable, Any, Optional


class P13_LaunchManager:
    """
    The central orchestrator for launching installed Pinokio applications.

    This class manages the complete application launch lifecycle, from pre-flight checks
    through process execution to state management. It coordinates between the state manager,
    translator, environment manager, and process manager to ensure applications are launched
    correctly in their isolated environments.

    The launch process follows a precise 5-step sequence:
    1. Pre-flight validation of application state
    2. Run script discovery and translation
    3. Environment preparation and prefix generation
    4. Background process execution with PID tracking
    5. State update with process information

    All operations include comprehensive error handling with full traceback reporting
    to maintain the Maximum Debug philosophy.
    """

    def __init__(
        self,
        state_manager: Any,
        translator: Any,
        environment_manager: Any,
        process_manager: Any
    ) -> None:
        """
        Initialize the LaunchManager with required dependencies.

        Args:
            state_manager: P08_StateManager instance for application state management
            translator: P03_Translator instance for script conversion
            environment_manager: P04_EnvironmentManager instance for environment handling
            process_manager: P02_ProcessManager instance for command execution

        Raises:
            ValueError: If any dependency is None or invalid
        """
        if not all([state_manager, translator, environment_manager, process_manager]):
            raise ValueError("All manager dependencies must be provided")

        self.state_manager = state_manager
        self.translator = translator
        self.environment_manager = environment_manager
        self.process_manager = process_manager

    def _validate_app_state(self, app_name: str) -> dict:
        """
        Validate that the application is in the correct state for launching.

        Args:
            app_name: Name of the application to validate

        Returns:
            dict: Application details including installation path

        Raises:
            ValueError: If application is not found or not in INSTALLED state
        """
        app_details = self.state_manager.get_app_details(app_name)
        if not app_details:
            raise ValueError(f"Application '{app_name}' not found in state database")

        if app_details.get('status') != 'INSTALLED':
            raise ValueError(
                f"Application '{app_name}' is not in INSTALLED state. "
                f"Current status: {app_details.get('status')}"
            )

        return app_details

    def _find_run_script(self, install_path: Path) -> Optional[Path]:
        """
        Locate the primary run script for the application.

        Args:
            install_path: Path to the application's installation directory

        Returns:
            Optional[Path]: Path to the run script, or None if not found

        Raises:
            FileNotFoundError: If installation path does not exist
        """
        if not install_path.exists():
            raise FileNotFoundError(f"Installation path does not exist: {install_path}")

        # Priority order for run scripts as per MASTER_GUIDE.md
        script_candidates = ['start.json', 'run.js', 'start.js', 'run.json']

        for script_name in script_candidates:
            script_path = install_path / script_name
            if script_path.exists():
                return script_path

        return None

    def _translate_run_script(self, script_path: Path) -> list:
        """
        Translate the run script into a standardized recipe format.

        Args:
            script_path: Path to the run script file

        Returns:
            list: Standardized recipe steps for execution

        Raises:
            Exception: If script translation fails
        """
        try:
            # Use P03_Translator to convert script to recipe format
            recipe = self.translator.translate_script(str(script_path))
            return recipe
        except Exception as e:
            raise Exception(f"Failed to translate run script '{script_path}': "
                          f"{str(e)}\n{traceback.format_exc()}")

    def _extract_primary_command(self, recipe: list) -> str:
        """
        Extract the primary shell command from the recipe.

        Args:
            recipe: List of recipe steps from translation

        Returns:
            str: The primary shell command to execute

        Raises:
            ValueError: If no shell command is found in recipe
        """
        for step in recipe:
            if step.get('step_type') == 'shell':
                return step.get('command', '')

        raise ValueError("No shell command found in recipe")

    def _prepare_environment_prefix(self, app_name: str) -> str:
        """
        Get the environment run prefix for the application.

        Args:
            app_name: Name of the application

        Returns:
            str: Command prefix for running in the correct environment

        Raises:
            Exception: If environment preparation fails
        """
        try:
            # Get environment details from state manager
            app_details = self.state_manager.get_app_details(app_name)
            environment_name = app_details.get('environment_name')

            if not environment_name:
                raise ValueError(f"No environment name found for application '{app_name}'")

            # Get run prefix from environment manager
            run_prefix = self.environment_manager.get_run_prefix(environment_name)
            return run_prefix

        except Exception as e:
            raise Exception(f"Failed to prepare environment for '{app_name}': "
                          f"{str(e)}\n{traceback.format_exc()}")

    def launch_app(
        self,
        app_name: str,
        primary_callback: Callable[[str], None],
        secondary_callback: Optional[Callable[[str], None]] = None
    ) -> int:
        """
        Launch an installed application as a persistent background process.

        This method orchestrates the complete launch workflow following the precise
        5-step sequence defined in MASTER_GUIDE.md:

        1. Pre-flight validation of application state
        2. Run script discovery and translation
        3. Environment preparation and prefix generation
        4. Background process execution with PID tracking
        5. State update with process information

        The method implements the dual-purpose callback architecture where each line
        of process output is sent to both the primary callback (for terminal display)
        and the secondary callback (for WebUI detection) if provided.

        Args:
            app_name: Name of the application to launch
            primary_callback: Function to call for each line of process output (terminal display)
            secondary_callback: Optional function for WebUI detection processing

        Returns:
            int: Process ID of the launched application

        Raises:
            Exception: If any step in the launch process fails, with full traceback
        """
        def dual_callback(line: str) -> None:
            """Dual-purpose callback that calls both primary and secondary callbacks."""
            primary_callback(line)
            if secondary_callback:
                secondary_callback(line)

        try:
            # Step 1: Pre-flight validation
            app_details = self._validate_app_state(app_name)
            install_path = Path(app_details['install_path'])

            # Step 2: Find and translate run script
            run_script_path = self._find_run_script(install_path)
            if not run_script_path:
                raise FileNotFoundError(
                    f"No run script found in {install_path}. "
                    f"Expected one of: start.json, run.js, start.js, run.json"
                )

            recipe = self._translate_run_script(run_script_path)
            primary_command = self._extract_primary_command(recipe)

            # Step 3: Prepare environment prefix
            run_prefix = self._prepare_environment_prefix(app_name)

            # Step 4: Execute as background process with dual callback
            full_command = f"{run_prefix} {primary_command}"
            process_pid = self.process_manager.shell_run(
                command=full_command,
                callback=dual_callback
            )

            # Step 5: Update state with PID and RUNNING status
            self.state_manager.set_app_status(
                app_name=app_name,
                status='RUNNING',
                process_pid=process_pid
            )

            return process_pid

        except Exception as e:
            # Set ERROR status before re-raising
            try:
                self.state_manager.set_app_status(
                    app_name=app_name,
                    status='ERROR',
                    error_message=str(e)
                )
            except Exception:
                # If state update fails, log but don't mask original error
                pass

            # Re-raise with full traceback for Maximum Debug philosophy
            raise Exception(f"Failed to launch application '{app_name}': "
                          f"{str(e)}\n{traceback.format_exc()}")

    def stop_app(self, app_name: str, callback: Callable[[str], None]) -> None:
        """
        Gracefully stop a running application.

        This method retrieves the application's PID from the state manager,
        terminates the process using the process manager, and updates the
        application status back to INSTALLED.

        Args:
            app_name: Name of the application to stop
            callback: Function to call for process termination output

        Raises:
            ValueError: If application is not found or not in RUNNING state
            Exception: If process termination or state update fails, with full traceback
        """
        try:
            # Get application details to retrieve PID
            app_details = self.state_manager.get_app_details(app_name)
            if not app_details:
                raise ValueError(f"Application '{app_name}' not found in state database")

            if app_details.get('status') != 'RUNNING':
                raise ValueError(
                    f"Application '{app_name}' is not in RUNNING state. "
                    f"Current status: {app_details.get('status')}"
                )

            process_pid = app_details.get('process_pid')
            if not process_pid:
                raise ValueError(f"No process PID found for application '{app_name}'")

            # Terminate the process
            self.process_manager.kill_process(
                pid=process_pid,
                callback=callback
            )

            # Update state to INSTALLED and clear PID
            self.state_manager.set_app_status(
                app_name=app_name,
                status='INSTALLED',
                process_pid=None
            )

        except Exception as e:
            # Set ERROR status before re-raising
            try:
                self.state_manager.set_app_status(
                    app_name=app_name,
                    status='ERROR',
                    error_message=str(e)
                )
            except Exception:
                # If state update fails, log but don't mask original error
                pass

            # Re-raise with full traceback for Maximum Debug philosophy
            raise Exception(f"Failed to stop application '{app_name}': "
                          f"{str(e)}\n{traceback.format_exc()}")