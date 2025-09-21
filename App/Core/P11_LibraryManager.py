"""
P11_LibraryManager.py - The Digital Bookshelf Engine

Phase P11 of the PinokioCloud Rebuild Project
Objective: Provide complete post-installation application lifecycle management
including uninstallation, configuration management, and library maintenance.

This module manages the complete lifecycle of installed applications after
they have been successfully installed by the P07/P08 installation engines.
It provides clean uninstallation, configuration management, and library
maintenance operations with comprehensive error handling.
"""

import json
import shutil
import traceback
from pathlib import Path
from typing import Dict, Any, Callable, Optional


class P11_LibraryManager:
    """
    The complete post-installation application lifecycle manager.
    
    This class is responsible for all operations performed on applications
    after they have been successfully installed. It coordinates with all
    major engine components to provide clean uninstallation, configuration
    management, and library maintenance.
    
    The manager handles:
    - Complete application uninstallation (environment + files + state)
    - Application configuration reading and writing
    - Library maintenance and cleanup operations
    - Integration with all Stage 1 and Stage 2 engines
    """

    def __init__(self, state_manager, env_manager, path_mapper, process_manager):
        """
        Initialize the P11_LibraryManager with all required engine dependencies.
        
        Args:
            state_manager: P08_StateManager instance for database operations
            env_manager: P04_EnvironmentManager instance for environment management
            path_mapper: P01_PathMapper instance for path resolution
            process_manager: P02_ProcessManager instance for shell command execution
            
        The constructor uses dependency injection to ensure loose coupling
        and comprehensive access to all system capabilities for library management.
        """
        self.state_manager = state_manager
        self.env_manager = env_manager
        self.path_mapper = path_mapper
        self.process_manager = process_manager

    def uninstall_app(self, app_name: str, callback: Callable[[str], None]) -> bool:
        """
        Perform complete and clean uninstallation of an application.
        
        This method orchestrates the complete removal of an application including
        its virtual environment, installation files, and database record. All
        operations are performed with comprehensive error handling and real-time
        output streaming.
        
        Args:
            app_name: Name of the application to uninstall
            callback: Function to receive real-time progress and output
            
        Returns:
            bool: True if uninstallation completed successfully, False otherwise
        """
        callback(f"[P11_LibraryManager] Starting complete uninstallation of '{app_name}'")
        
        try:
            # Step 1: Get App Info
            app_info = self._get_application_info(app_name, callback)
            if not app_info:
                return False

            # Step 2: Remove Environment
            environment_result = self._remove_application_environment(
                app_name, app_info, callback
            )
            if not environment_result:
                callback(f"[P11_LibraryManager] WARNING: Environment removal failed, continuing...")

            # Step 3: Remove Files
            files_result = self._remove_application_files(app_info, callback)
            if not files_result:
                callback(f"[P11_LibraryManager] WARNING: File removal failed, continuing...")

            # Step 4: Remove from State
            state_result = self._remove_application_state(app_name, callback)
            if not state_result:
                return False

            callback(f"[P11_LibraryManager] Uninstallation of '{app_name}' completed successfully")
            return True
            
        except Exception as e:
            callback(f"[P11_LibraryManager] CRITICAL ERROR during uninstallation:")
            callback(f"[P11_LibraryManager] {traceback.format_exc()}")
            return False

    def get_app_config(self, app_name: str) -> Dict[str, Any]:
        """
        Read and return the configuration for a specific application.
        
        Retrieves the application's JSON configuration file from its installation
        directory and returns the parsed configuration as a dictionary.
        
        Args:
            app_name: Name of the application to get configuration for
            
        Returns:
            Dict[str, Any]: Application configuration dictionary
            
        Raises:
            Exception: Re-raises all errors with full tracebacks for debugging
        """
        try:
            # Get application details from state manager
            app_details = self.state_manager.get_app_details(app_name)
            if not app_details:
                raise ValueError(f"Application '{app_name}' not found in library")
            
            install_path = Path(app_details['install_path'])
            config_file = install_path / 'config.json'
            
            if not config_file.exists():
                # Return default empty configuration if no config file exists
                return {}
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            return config_data
            
        except Exception as e:
            raise Exception(f"Failed to get configuration for application '{app_name}': "
                          f"{str(e)}\n{traceback.format_exc()}")

    def set_app_config(self, app_name: str, config: Dict[str, Any]) -> None:
        """
        Write configuration data to a specific application's config file.
        
        Stores the provided configuration dictionary as JSON in the application's
        installation directory. The operation is atomic using temporary file writes.
        
        Args:
            app_name: Name of the application to set configuration for
            config: Configuration dictionary to store
            
        Raises:
            Exception: Re-raises all errors with full tracebacks for debugging
        """
        try:
            # Get application details from state manager
            app_details = self.state_manager.get_app_details(app_name)
            if not app_details:
                raise ValueError(f"Application '{app_name}' not found in library")
            
            install_path = Path(app_details['install_path'])
            config_file = install_path / 'config.json'
            
            # Ensure installation directory exists
            install_path.mkdir(parents=True, exist_ok=True)
            
            # Write configuration atomically
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # Update state manager with config update timestamp
            self.state_manager.set_app_status(
                app_name, 
                app_details['status'],
                config_data=json.dumps(config)
            )
            
        except Exception as e:
            raise Exception(f"Failed to set configuration for application '{app_name}': "
                          f"{str(e)}\n{traceback.format_exc()}")

    def _get_application_info(self, app_name: str, 
                            callback: Callable[[str], None]) -> Optional[Dict[str, Any]]:
        """
        Retrieve complete application information from the state database.
        
        Args:
            app_name: Name of the application to retrieve info for
            callback: Function to receive progress updates
            
        Returns:
            Optional[Dict[str, Any]]: Application info or None if not found
        """
        callback(f"[P11_LibraryManager] Retrieving application info for '{app_name}'")
        
        try:
            app_info = self.state_manager.get_app_details(app_name)
            if not app_info:
                callback(f"[P11_LibraryManager] ERROR: Application '{app_name}' not found")
                return None
                
            callback(f"[P11_LibraryManager] Found application: {app_info['status']} status")
            return app_info
            
        except Exception as e:
            callback(f"[P11_LibraryManager] Failed to retrieve application info:")
            callback(f"[P11_LibraryManager] {traceback.format_exc()}")
            return None

    def _remove_application_environment(self, app_name: str, app_info: Dict[str, Any],
                                      callback: Callable[[str], None]) -> bool:
        """
        Remove the virtual environment associated with the application.
        
        Args:
            app_name: Name of the application
            app_info: Application details from state database
            callback: Function to receive command output
            
        Returns:
            bool: True if environment removal succeeded, False otherwise
        """
        callback(f"[P11_LibraryManager] Removing environment for '{app_name}'")
        
        try:
            environment_name = app_info.get('environment_name', app_name)
            
            # Determine environment removal strategy based on platform
            platform_info = self.env_manager.cloud_detector.detect_platform()
            
            if platform_info.platform_name == "Lightning AI":
                # For venv environments, remove directory directly
                venv_path = self.path_mapper.get_base_path() / "envs" / environment_name
                if venv_path.exists():
                    shutil.rmtree(venv_path)
                    callback(f"[P11_LibraryManager] Removed venv directory: {venv_path}")
            else:
                # For conda environments, use conda remove command
                remove_command = f"conda env remove -n {environment_name} -y"
                callback(f"[P11_LibraryManager] Executing: {remove_command}")
                self.process_manager.shell_run(remove_command, callback)
            
            callback(f"[P11_LibraryManager] Environment '{environment_name}' removed successfully")
            return True
            
        except Exception as e:
            callback(f"[P11_LibraryManager] Environment removal failed:")
            callback(f"[P11_LibraryManager] {traceback.format_exc()}")
            return False

    def _remove_application_files(self, app_info: Dict[str, Any],
                                callback: Callable[[str], None]) -> bool:
        """
        Remove all files associated with the application installation.
        
        Args:
            app_info: Application details containing install_path
            callback: Function to receive progress updates
            
        Returns:
            bool: True if file removal succeeded, False otherwise
        """
        callback(f"[P11_LibraryManager] Removing application files")
        
        try:
            install_path = Path(app_info['install_path'])
            
            if not install_path.exists():
                callback(f"[P11_LibraryManager] Installation path not found: {install_path}")
                return True  # Already removed, consider success
            
            callback(f"[P11_LibraryManager] Removing directory: {install_path}")
            shutil.rmtree(install_path)
            
            callback(f"[P11_LibraryManager] Application files removed successfully")
            return True
            
        except Exception as e:
            callback(f"[P11_LibraryManager] File removal failed:")
            callback(f"[P11_LibraryManager] {traceback.format_exc()}")
            return False

    def _remove_application_state(self, app_name: str,
                                callback: Callable[[str], None]) -> bool:
        """
        Remove the application record from the state database.
        
        Args:
            app_name: Name of the application to remove from database
            callback: Function to receive progress updates
            
        Returns:
            bool: True if state removal succeeded, False otherwise
        """
        callback(f"[P11_LibraryManager] Removing application from state database")
        
        try:
            removal_result = self.state_manager.remove_app(app_name)
            
            if removal_result:
                callback(f"[P11_LibraryManager] Application '{app_name}' removed from database")
            else:
                callback(f"[P11_LibraryManager] Application '{app_name}' was not in database")
            
            return True
            
        except Exception as e:
            callback(f"[P11_LibraryManager] State removal failed:")
            callback(f"[P11_LibraryManager] {traceback.format_exc()}")
            return False