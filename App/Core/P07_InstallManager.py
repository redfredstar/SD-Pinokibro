"""
P07_InstallManager.py - The Installation Engine Core Logic

Phase P07 of the PinokioCloud Rebuild Project
Objective: Build the core "workhorse" engine component that orchestrates 
the installation process by executing standardized recipes step-by-step.

This module implements the Orchestration and Delegation architectural pattern,
where the InstallManager coordinates the workflow but delegates specific tasks
to specialized engines from Stage 1.
"""

import traceback
from typing import List, Dict, Callable, Optional
from dataclasses import dataclass


@dataclass
class P07_InstallationResult:
    """
    Data class representing the result of an installation operation.
    Provides structured output for installation success/failure tracking.
    """
    success: bool
    app_name: str
    environment_name: str
    error_message: Optional[str] = None
    steps_completed: int = 0
    total_steps: int = 0


class P07_InstallManager:
    """
    The core installation orchestration engine for the PinokioCloud project.
    
    This class is responsible for executing standardized recipes (list of dicts)
    by delegating specific tasks to appropriate Stage 1 engines. It follows the
    Orchestration and Delegation pattern - coordinating workflow without performing
    low-level operations directly.
    
    The manager handles:
    - Environment creation through P04_EnvironmentManager
    - Shell command execution through P02_ProcessManager
    - Recipe step orchestration with proper error handling
    - Real-time output streaming via callback mechanism
    """

    def __init__(self, process_manager, env_manager):
        """
        Initialize the P07_InstallManager with required dependencies.
        
        Args:
            process_manager: P02_ProcessManager instance for shell command execution
            env_manager: P04_EnvironmentManager instance for environment management
            
        The constructor uses dependency injection to ensure loose coupling
        and testability of the installation engine.
        """
        self.process_manager = process_manager
        self.env_manager = env_manager
        self.current_run_prefix = ""
        self.input_callback = None

    def install_app(self, recipe: List[Dict], app_name: str,
                    callback: Callable[[str], None],
                    progress_callback: Optional[Callable[[int], None]] = None,
                    input_callback: Optional[Callable[[Dict], Dict]] = None) -> P07_InstallationResult:
        """
        Execute the complete installation workflow for an application.
        
        This is the primary public method that orchestrates the entire installation
        process using the provided recipe. It follows a precise workflow:
        1. Create isolated environment
        2. Get environment run prefix
        3. Execute recipe steps in order
        
        Args:
            recipe: List of standardized recipe steps from P03_Translator
            app_name: Name of the application being installed
            callback: Function to stream real-time output to UI
            progress_callback: Optional function to report installation progress (0-100%)
            input_callback: Optional function to handle interactive user input requests
            
        Returns:
            P07_InstallationResult: Structured result with success status and details
            
        Raises:
            No exceptions are raised - all errors are captured and returned in result
        """
        callback(f"[P07_InstallManager] Starting installation of '{app_name}'")

        # Report initial progress (10%)
        if progress_callback:
            progress_callback(10)

        try:
            # Step 1: Create Environment
            environment_result = self._create_application_environment(
                app_name, callback
            )
            if not environment_result:
                return P07_InstallationResult(
                    success=False,
                    app_name=app_name,
                    environment_name=app_name,
                    error_message="Failed to create application environment",
                    total_steps=len(recipe)
                )

            # Report progress after environment creation (50%)
            if progress_callback:
                progress_callback(50)

            # Step 2: Get Run Prefix
            prefix_result = self._get_environment_run_prefix(app_name, callback)
            if not prefix_result:
                return P07_InstallationResult(
                    success=False,
                    app_name=app_name,
                    environment_name=app_name,
                    error_message="Failed to get environment run prefix",
                    total_steps=len(recipe)
                )

            # Step 3: Execute Recipe Steps
            execution_result = self._execute_recipe_steps(
                recipe, app_name, callback
            )
            
            return execution_result
            
        except Exception as e:
            callback(f"[P07_InstallManager] CRITICAL ERROR during installation:")
            callback(f"[P07_InstallManager] {traceback.format_exc()}")
            return P07_InstallationResult(
                success=False,
                app_name=app_name,
                environment_name=app_name,
                error_message=f"Critical installation failure: {str(e)}",
                total_steps=len(recipe)
            )

    def _create_application_environment(self, app_name: str, 
                                      callback: Callable[[str], None]) -> bool:
        """
        Create an isolated environment for the application installation.
        
        Args:
            app_name: Name of the application (used as environment name)
            callback: Function to stream environment creation output
            
        Returns:
            bool: True if environment creation succeeded, False otherwise
        """
        callback(f"[P07_InstallManager] Creating isolated environment: {app_name}")
        
        try:
            self.env_manager.create(app_name, callback)
            callback(f"[P07_InstallManager] Environment '{app_name}' created successfully")
            return True
            
        except Exception as e:
            callback(f"[P07_InstallManager] Environment creation FAILED:")
            callback(f"[P07_InstallManager] {traceback.format_exc()}")
            return False

    def _get_environment_run_prefix(self, app_name: str, 
                                  callback: Callable[[str], None]) -> bool:
        """
        Get the command prefix needed for running commands in the environment.
        
        Args:
            app_name: Name of the environment
            callback: Function to stream prefix retrieval output
            
        Returns:
            bool: True if prefix retrieval succeeded, False otherwise
        """
        callback(f"[P07_InstallManager] Getting run prefix for environment: {app_name}")
        
        try:
            self.current_run_prefix = self.env_manager.get_run_prefix(app_name)
            callback(f"[P07_InstallManager] Run prefix: {self.current_run_prefix}")
            return True
            
        except Exception as e:
            callback(f"[P07_InstallManager] Run prefix retrieval FAILED:")
            callback(f"[P07_InstallManager] {traceback.format_exc()}")
            return False

    def _execute_recipe_steps(self, recipe: List[Dict], app_name: str,
                            callback: Callable[[str], None]) -> P07_InstallationResult:
        """
        Execute all steps in the recipe sequentially.
        
        Args:
            recipe: List of standardized recipe steps
            app_name: Name of the application being installed
            callback: Function to stream step execution output
            
        Returns:
            P07_InstallationResult: Result of recipe execution
        """
        total_steps = len(recipe)
        callback(f"[P07_InstallManager] Executing {total_steps} recipe steps")
        
        for step_index, step in enumerate(recipe, 1):
            callback(f"[P07_InstallManager] Step {step_index}/{total_steps}: {step.get('step_type', 'unknown')}")
            
            try:
                step_result = self._execute_single_step(step, callback)
                if not step_result:
                    return P07_InstallationResult(
                        success=False,
                        app_name=app_name,
                        environment_name=app_name,
                        error_message=f"Step {step_index} failed: {step.get('step_type', 'unknown')}",
                        steps_completed=step_index - 1,
                        total_steps=total_steps
                    )
                    
            except Exception as e:
                callback(f"[P07_InstallManager] Step {step_index} CRITICAL ERROR:")
                callback(f"[P07_InstallManager] {traceback.format_exc()}")
                return P07_InstallationResult(
                    success=False,
                    app_name=app_name,
                    environment_name=app_name,
                    error_message=f"Critical error in step {step_index}: {str(e)}",
                    steps_completed=step_index - 1,
                    total_steps=total_steps
                )

        callback(f"[P07_InstallManager] All {total_steps} steps completed successfully")

        # Report final progress (100%)
        if progress_callback:
            progress_callback(100)

        return P07_InstallationResult(
            success=True,
            app_name=app_name,
            environment_name=app_name,
            steps_completed=total_steps,
            total_steps=total_steps
        )

    def _execute_single_step(self, step: Dict, 
                           callback: Callable[[str], None]) -> bool:
        """
        Execute a single recipe step based on its step_type.
        
        Args:
            step: Dictionary containing step_type and parameters
            callback: Function to stream step execution output
            
        Returns:
            bool: True if step execution succeeded, False otherwise
            
        Raises:
            NotImplementedError: For step types not yet implemented (explicit design)
        """
        step_type = step.get('step_type', '')
        callback(f"[P07_InstallManager] Executing step type: {step_type}")
        
        if step_type == 'shell':
            return self._execute_shell_step(step, callback)
        elif step_type == 'input':
            return self._execute_input_step(step, callback)
        else:
            # Explicit temporary limitation - will be handled by P08_FileManager
            error_msg = (f"Step type '{step_type}' not yet implemented. "
                        f"File operations will be handled by P08_FileManager in next phase.")
            callback(f"[P07_InstallManager] {error_msg}")
            raise NotImplementedError(error_msg)

    def _execute_shell_step(self, step: Dict, 
                          callback: Callable[[str], None]) -> bool:
        """
        Execute a shell command step with proper environment activation.
        
        Args:
            step: Dictionary containing shell command parameters
            callback: Function to stream command execution output
            
        Returns:
            bool: True if command execution succeeded, False otherwise
        """
        command = step.get('command', '')
        if not command:
            callback("[P07_InstallManager] ERROR: Shell step missing command")
            return False

        # Construct full command with environment prefix
        full_command = f"{self.current_run_prefix} {command}".strip()
        callback(f"[P07_InstallManager] Executing: {full_command}")
        
        try:
            # Delegate shell execution to P02_ProcessManager
            self.process_manager.shell_run(full_command, callback)
            callback(f"[P07_InstallManager] Shell command completed successfully")
            return True
            
        except Exception as e:
            callback(f"[P07_InstallManager] Shell command FAILED:")
            callback(f"[P07_InstallManager] {traceback.format_exc()}")
            return False

    def _execute_input_step(self, step: Dict,
                           callback: Callable[[str], None]) -> bool:
        """
        Execute an input step by requesting user input through the UI callback.

        Args:
            step: Dictionary containing input step parameters
            callback: Function to stream input request output

        Returns:
            bool: True if input was successfully collected, False otherwise
        """
        callback(f"[P07_InstallManager] Input step requires user interaction")

        if not self.input_callback:
            callback(f"[P07_InstallManager] ERROR: No input_callback provided for input step")
            return False

        try:
            # Call the UI callback to collect user input
            # The callback should return a dict with 'event' and 'result' keys
            input_response = self.input_callback(step.get('params', {}))

            if not input_response or 'event' not in input_response:
                callback(f"[P07_InstallManager] ERROR: Invalid input response from UI")
                return False

            # Block until user provides input
            callback(f"[P07_InstallManager] Waiting for user input...")
            input_response['event'].wait()

            # Check if input was successfully collected
            if 'result' not in input_response or input_response['result'] is None:
                callback(f"[P07_InstallManager] ERROR: User input collection failed")
                return False

            callback(f"[P07_InstallManager] User input collected successfully")
            return True

        except Exception as e:
            callback(f"[P07_InstallManager] Input step FAILED:")
            callback(f"[P07_InstallManager] {traceback.format_exc()}")
            return False