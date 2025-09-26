"""
P16_LaunchUIController.py - The Launch UI Control Engine

Phase P16 of the PinokioCloud Rebuild Project
Objective: Provide the complete UI control layer for application lifecycle management,
including URL display, application control, and status monitoring within the Jupyter notebook.

This module serves as the bridge between the notebook UI and the underlying launch
infrastructure, providing a complete user experience for application management.
"""

import threading
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime
import traceback


class P16_LaunchUIController:
    """
    The comprehensive launch UI control engine for the PinokioCloud project.

    This class provides the complete user interface layer for application lifecycle
    management, including URL display, application control, and real-time status
    monitoring. It serves as the primary interface between users and the launch
    infrastructure.

    The controller ensures:
    - Complete application lifecycle management through UI controls
    - Real-time status updates and monitoring
    - Public URL display and management
    - Thread-safe operations for UI responsiveness
    - Comprehensive error handling with full traceback reporting
    """

    def __init__(self, state_manager, launch_manager, tunnel_manager):
        """
        Initialize the P16_LaunchUIController with required dependencies.

        Args:
            state_manager: P08_StateManager instance for database operations
            launch_manager: P13_LaunchManager instance for application control
            tunnel_manager: P14_TunnelManager instance for tunnel operations

        The constructor immediately establishes connections to all required
        engines and prepares the controller for UI operations.
        """
        self.state_manager = state_manager
        self.launch_manager = launch_manager
        self.tunnel_manager = tunnel_manager
        self.active_controls: Dict[str, Dict] = {}
        self.status_callbacks: List[Callable] = []
        self.lock = threading.Lock()

    def register_status_callback(self, callback: Callable) -> None:
        """
        Register a callback function for status updates.

        The callback will be called whenever application status changes,
        enabling real-time UI updates across the interface.

        Args:
            callback: Function to call when status updates occur

        Raises:
            Exception: Re-raises all errors with full tracebacks
        """
        try:
            with self.lock:
                self.status_callbacks.append(callback)
        except Exception as e:
            raise Exception(f"Failed to register status callback: "
                          f"{str(e)}\n{traceback.format_exc()}")

    def get_application_status_summary(self) -> Dict[str, Dict]:
        """
        Retrieve a comprehensive status summary for all applications.

        Returns a dictionary containing complete status information for all
        applications, including their current state, URLs, and metadata.

        Returns:
            Dict[str, Dict]: Complete status information for all applications

        Raises:
            Exception: Re-raises all database errors with full tracebacks
        """
        try:
            with self.lock:
                apps = self.state_manager.get_all_apps()
                status_summary = {}

                for app in apps:
                    app_name = app['app_name']
                    status_summary[app_name] = {
                        'status': app['status'],
                        'tunnel_url': app.get('tunnel_url', ''),
                        'process_pid': app.get('process_pid'),
                        'installed_at': app.get('installed_at'),
                        'updated_at': app.get('updated_at'),
                        'environment_name': app.get('environment_name', ''),
                        'config_data': app.get('config_data', ''),
                        'error_message': app.get('error_message', '')
                    }

                return status_summary

        except Exception as e:
            raise Exception(f"Failed to get application status summary: "
                          f"{str(e)}\n{traceback.format_exc()}")

    def start_application_with_ui_feedback(self, app_name: str,
                                         primary_callback: Callable,
                                         secondary_callback: Optional[Callable] = None) -> bool:
        """
        Start an application with complete UI feedback and monitoring.

        This method provides the complete application startup experience,
        including status updates, error handling, and callback management.

        Args:
            app_name: Name of the application to start
            primary_callback: Callback for primary output (logs)
            secondary_callback: Optional callback for secondary processing

        Returns:
            bool: True if startup initiated successfully

        Raises:
            Exception: Re-raises all errors with full tracebacks
        """
        try:
            with self.lock:
                # Update status to indicate startup process
                self.state_manager.set_app_status(app_name, 'STARTING')
                self._notify_status_callbacks()

                # Create background thread for startup
                startup_thread = threading.Thread(
                    target=self._execute_startup_sequence,
                    args=(app_name, primary_callback, secondary_callback)
                )
                startup_thread.daemon = True
                startup_thread.start()

                return True

        except Exception as e:
            # Update status to reflect error
            self.state_manager.set_app_status(app_name, 'ERROR',
                                            error_message=str(e))
            self._notify_status_callbacks()
            raise Exception(f"Failed to start application {app_name}: "
                          f"{str(e)}\n{traceback.format_exc()}")

    def stop_application_with_ui_feedback(self, app_name: str) -> bool:
        """
        Stop an application with complete UI feedback and monitoring.

        This method provides the complete application shutdown experience,
        including status updates, cleanup, and callback notifications.

        Args:
            app_name: Name of the application to stop

        Returns:
            bool: True if shutdown initiated successfully

        Raises:
            Exception: Re-raises all errors with full tracebacks
        """
        try:
            with self.lock:
                # Update status to indicate shutdown process
                self.state_manager.set_app_status(app_name, 'STOPPING')
                self._notify_status_callbacks()

                # Create background thread for shutdown
                shutdown_thread = threading.Thread(
                    target=self._execute_shutdown_sequence,
                    args=(app_name,)
                )
                shutdown_thread.daemon = True
                shutdown_thread.start()

                return True

        except Exception as e:
            # Update status to reflect error
            self.state_manager.set_app_status(app_name, 'ERROR',
                                            error_message=str(e))
            self._notify_status_callbacks()
            raise Exception(f"Failed to stop application {app_name}: "
                          f"{str(e)}\n{traceback.format_exc()}")

    def refresh_tunnel_status(self, app_name: str) -> Optional[str]:
        """
        Refresh and return the current tunnel status for an application.

        This method checks the current tunnel status and updates the database
        if the tunnel configuration has changed.

        Args:
            app_name: Name of the application to check

        Returns:
            Optional[str]: Current public URL if tunnel exists, None otherwise

        Raises:
            Exception: Re-raises all errors with full tracebacks
        """
        try:
            with self.lock:
                app_details = self.state_manager.get_app_details(app_name)

                if not app_details:
                    return None

                # Check if tunnel is still active
                current_url = app_details.get('tunnel_url', '')

                if current_url:
                    # Verify tunnel is still functional
                    tunnel_status = self.tunnel_manager.check_tunnel_status(current_url)

                    if not tunnel_status:
                        # Tunnel is no longer active, clear it
                        self.state_manager.set_app_status(app_name, 'INSTALLED')
                        self._notify_status_callbacks()
                        return None
                    else:
                        return current_url
                else:
                    return None

        except Exception as e:
            raise Exception(f"Failed to refresh tunnel status for {app_name}: "
                          f"{str(e)}\n{traceback.format_exc()}")

    def get_control_interface_for_app(self, app_name: str) -> Dict:
        """
        Generate the complete control interface configuration for an application.

        This method returns all the information needed to render the UI controls
        for a specific application, including buttons, status, and URLs.

        Args:
            app_name: Name of the application

        Returns:
            Dict: Complete control interface configuration

        Raises:
            Exception: Re-raises all errors with full tracebacks
        """
        try:
            with self.lock:
                app_details = self.state_manager.get_app_details(app_name)

                if not app_details:
                    return {'available': False, 'reason': 'Application not found'}

                status = app_details['status']
                tunnel_url = app_details.get('tunnel_url', '')
                process_pid = app_details.get('process_pid')

                control_config = {
                    'available': True,
                    'app_name': app_name,
                    'status': status,
                    'tunnel_url': tunnel_url,
                    'process_pid': process_pid,
                    'controls': []
                }

                # Determine available controls based on status
                if status == 'INSTALLED':
                    control_config['controls'].append({
                        'type': 'start',
                        'label': f'Start {app_name}',
                        'action': 'start',
                        'style': 'success'
                    })

                elif status == 'RUNNING':
                    control_config['controls'].append({
                        'type': 'stop',
                        'label': f'Stop {app_name}',
                        'action': 'stop',
                        'style': 'danger'
                    })

                    if tunnel_url:
                        control_config['controls'].append({
                            'type': 'link',
                            'label': 'Open Application',
                            'url': tunnel_url,
                            'style': 'primary'
                        })

                elif status == 'ERROR':
                    control_config['controls'].append({
                        'type': 'restart',
                        'label': f'Restart {app_name}',
                        'action': 'restart',
                        'style': 'warning'
                    })

                return control_config

        except Exception as e:
            raise Exception(f"Failed to get control interface for {app_name}: "
                          f"{str(e)}\n{traceback.format_exc()}")

    def _execute_startup_sequence(self, app_name: str,
                                primary_callback: Callable,
                                secondary_callback: Optional[Callable]) -> None:
        """
        Execute the complete startup sequence for an application.

        This private method handles the complete startup process in a
        background thread, including error handling and status updates.

        Args:
            app_name: Name of the application to start
            primary_callback: Callback for primary output
            secondary_callback: Optional callback for secondary processing
        """
        try:
            # Execute the launch with callbacks
            self.launch_manager.launch_app(
                app_name=app_name,
                primary_callback=primary_callback,
                secondary_callback=secondary_callback
            )

            # Update final status
            self.state_manager.set_app_status(app_name, 'RUNNING')
            self._notify_status_callbacks()

        except Exception as e:
            # Update status to reflect error
            self.state_manager.set_app_status(app_name, 'ERROR',
                                            error_message=str(e))
            self._notify_status_callbacks()

            # Log error for debugging
            print(f"❌ Startup failed for {app_name}: {e}")
            traceback.print_exc()

    def _execute_shutdown_sequence(self, app_name: str) -> None:
        """
        Execute the complete shutdown sequence for an application.

        This private method handles the complete shutdown process in a
        background thread, including cleanup and status updates.

        Args:
            app_name: Name of the application to stop
        """
        try:
            # Stop the application
            self.launch_manager.stop_app(app_name)

            # Update status
            self.state_manager.set_app_status(app_name, 'INSTALLED')
            self._notify_status_callbacks()

        except Exception as e:
            # Update status to reflect error
            self.state_manager.set_app_status(app_name, 'ERROR',
                                            error_message=str(e))
            self._notify_status_callbacks()

            # Log error for debugging
            print(f"❌ Shutdown failed for {app_name}: {e}")
            traceback.print_exc()

    def _notify_status_callbacks(self) -> None:
        """
        Notify all registered status callbacks of changes.

        This private method safely calls all registered callbacks to
        ensure UI updates are propagated throughout the interface.
        """
        try:
            with self.lock:
                for callback in self.status_callbacks:
                    try:
                        callback()
                    except Exception as e:
                        print(f"❌ Status callback error: {e}")
                        traceback.print_exc()

        except Exception as e:
            print(f"❌ Error notifying status callbacks: {e}")
            traceback.print_exc()