"""
P16-Test_LaunchUIController.py - Comprehensive Test Suite for Launch UI Controller

This test suite provides complete validation of the P16_LaunchUIController functionality,
including UI control operations, status management, and error handling scenarios.
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import threading
import time
from datetime import datetime


class TestP16LaunchUIController(unittest.TestCase):
    """
    Comprehensive test suite for P16_LaunchUIController.

    This test class validates all aspects of the launch UI controller,
    including application control, status management, and error handling.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.

        Creates mock dependencies and initializes the controller
        for testing in a controlled environment.
        """
        # Create mock dependencies
        self.mock_state_manager = Mock()
        self.mock_launch_manager = Mock()
        self.mock_tunnel_manager = Mock()

        # Configure mock return values
        self.mock_state_manager.get_all_apps.return_value = [
            {
                'app_name': 'test_app',
                'status': 'INSTALLED',
                'tunnel_url': '',
                'process_pid': None,
                'installed_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'environment_name': 'test_env',
                'config_data': '{}',
                'error_message': ''
            }
        ]

        self.mock_state_manager.get_app_details.return_value = {
            'app_name': 'test_app',
            'status': 'INSTALLED',
            'tunnel_url': '',
            'process_pid': None,
            'installed_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'environment_name': 'test_env',
            'config_data': '{}',
            'error_message': ''
        }

        # Import and initialize the controller
        from app.core.P16_LaunchUIController import P16_LaunchUIController

        self.controller = P16_LaunchUIController(
            self.mock_state_manager,
            self.mock_launch_manager,
            self.mock_tunnel_manager
        )

        # Track callback calls
        self.callback_calls = []

        def mock_callback():
            self.callback_calls.append(True)

        self.mock_callback = mock_callback

    def test_initialization(self):
        """
        Test that the controller initializes correctly with dependencies.

        Validates that all required components are properly connected
        and the controller is ready for operation.
        """
        # Verify dependencies are stored
        self.assertEqual(self.controller.state_manager, self.mock_state_manager)
        self.assertEqual(self.controller.launch_manager, self.mock_launch_manager)
        self.assertEqual(self.controller.tunnel_manager, self.mock_tunnel_manager)

        # Verify internal state
        self.assertEqual(len(self.controller.active_controls), 0)
        self.assertEqual(len(self.controller.status_callbacks), 0)
        self.assertIsInstance(self.controller.lock, threading.Lock)

    def test_register_status_callback(self):
        """
        Test registering status update callbacks.

        Ensures that callbacks are properly registered and stored
        for status change notifications.
        """
        # Register callback
        self.controller.register_status_callback(self.mock_callback)

        # Verify callback was registered
        self.assertEqual(len(self.controller.status_callbacks), 1)
        self.assertEqual(self.controller.status_callbacks[0], self.mock_callback)

    def test_get_application_status_summary(self):
        """
        Test retrieving comprehensive application status summary.

        Validates that the controller can retrieve and format
        complete status information for all applications.
        """
        # Get status summary
        summary = self.controller.get_application_status_summary()

        # Verify structure
        self.assertIn('test_app', summary)
        app_info = summary['test_app']
        self.assertEqual(app_info['status'], 'INSTALLED')
        self.assertEqual(app_info['tunnel_url'], '')
        self.assertEqual(app_info['environment_name'], 'test_env')

    def test_start_application_with_ui_feedback_success(self):
        """
        Test successful application startup with UI feedback.

        Validates the complete startup workflow including status
        updates and background thread creation.
        """
        # Mock successful launch
        self.mock_launch_manager.launch_app.return_value = None

        # Start application
        result = self.controller.start_application_with_ui_feedback(
            'test_app',
            lambda x: None,
            lambda x: None
        )

        # Verify result
        self.assertTrue(result)

        # Verify status updates
        self.mock_state_manager.set_app_status.assert_called_with('test_app', 'STARTING')

        # Verify launch was called
        self.mock_launch_manager.launch_app.assert_called_once()

    def test_start_application_with_ui_feedback_error(self):
        """
        Test application startup failure with proper error handling.

        Ensures that startup errors are properly caught, logged,
        and reflected in the application status.
        """
        # Mock launch failure
        self.mock_launch_manager.launch_app.side_effect = Exception("Launch failed")

        # Attempt to start application
        with self.assertRaises(Exception) as context:
            self.controller.start_application_with_ui_feedback(
                'test_app',
                lambda x: None,
                lambda x: None
            )

        # Verify error message
        self.assertIn("Launch failed", str(context.exception))

        # Verify error status was set
        self.mock_state_manager.set_app_status.assert_called_with(
            'test_app', 'ERROR', error_message='Launch failed'
        )

    def test_stop_application_with_ui_feedback_success(self):
        """
        Test successful application shutdown with UI feedback.

        Validates the complete shutdown workflow including status
        updates and background thread creation.
        """
        # Mock successful stop
        self.mock_launch_manager.stop_app.return_value = None

        # Stop application
        result = self.controller.stop_application_with_ui_feedback('test_app')

        # Verify result
        self.assertTrue(result)

        # Verify status updates
        self.mock_state_manager.set_app_status.assert_called_with('test_app', 'STOPPING')

        # Verify stop was called
        self.mock_launch_manager.stop_app.assert_called_once_with('test_app')

    def test_stop_application_with_ui_feedback_error(self):
        """
        Test application shutdown failure with proper error handling.

        Ensures that shutdown errors are properly caught, logged,
        and reflected in the application status.
        """
        # Mock stop failure
        self.mock_launch_manager.stop_app.side_effect = Exception("Stop failed")

        # Attempt to stop application
        with self.assertRaises(Exception) as context:
            self.controller.stop_application_with_ui_feedback('test_app')

        # Verify error message
        self.assertIn("Stop failed", str(context.exception))

        # Verify error status was set
        self.mock_state_manager.set_app_status.assert_called_with(
            'test_app', 'ERROR', error_message='Stop failed'
        )

    def test_refresh_tunnel_status_active(self):
        """
        Test tunnel status refresh for active tunnels.

        Validates that active tunnels are properly verified and
        maintained in the system.
        """
        # Mock active tunnel
        self.mock_tunnel_manager.check_tunnel_status.return_value = True

        # Refresh tunnel status
        url = self.controller.refresh_tunnel_status('test_app')

        # Verify tunnel check was called
        self.mock_tunnel_manager.check_tunnel_status.assert_called_once()

        # Verify URL was returned
        self.assertIsNone(url)  # No tunnel URL in mock data

    def test_refresh_tunnel_status_inactive(self):
        """
        Test tunnel status refresh for inactive tunnels.

        Ensures that inactive tunnels are properly detected and
        cleaned up from the database.
        """
        # Mock inactive tunnel
        self.mock_tunnel_manager.check_tunnel_status.return_value = False

        # Set up mock with tunnel URL
        self.mock_state_manager.get_app_details.return_value = {
            'app_name': 'test_app',
            'status': 'RUNNING',
            'tunnel_url': 'http://test.ngrok.io',
            'process_pid': 12345,
            'installed_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'environment_name': 'test_env',
            'config_data': '{}',
            'error_message': ''
        }

        # Refresh tunnel status
        url = self.controller.refresh_tunnel_status('test_app')

        # Verify tunnel check was called
        self.mock_tunnel_manager.check_tunnel_status.assert_called_once_with('http://test.ngrok.io')

        # Verify status was updated to clear tunnel
        self.mock_state_manager.set_app_status.assert_called_with('test_app', 'INSTALLED')

        # Verify callback was notified
        self.assertEqual(len(self.callback_calls), 1)

        # Verify no URL was returned
        self.assertIsNone(url)

    def test_get_control_interface_for_app_installed(self):
        """
        Test control interface generation for installed applications.

        Validates that the correct control interface is generated
        for applications in INSTALLED state.
        """
        # Get control interface
        interface = self.controller.get_control_interface_for_app('test_app')

        # Verify structure
        self.assertTrue(interface['available'])
        self.assertEqual(interface['app_name'], 'test_app')
        self.assertEqual(interface['status'], 'INSTALLED')

        # Verify controls
        controls = interface['controls']
        self.assertEqual(len(controls), 1)
        self.assertEqual(controls[0]['type'], 'start')
        self.assertEqual(controls[0]['label'], 'Start test_app')
        self.assertEqual(controls[0]['action'], 'start')

    def test_get_control_interface_for_app_running(self):
        """
        Test control interface generation for running applications.

        Validates that the correct control interface is generated
        for applications in RUNNING state with tunnel URLs.
        """
        # Set up mock with running app and tunnel
        self.mock_state_manager.get_app_details.return_value = {
            'app_name': 'test_app',
            'status': 'RUNNING',
            'tunnel_url': 'http://test.ngrok.io',
            'process_pid': 12345,
            'installed_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'environment_name': 'test_env',
            'config_data': '{}',
            'error_message': ''
        }

        # Get control interface
        interface = self.controller.get_control_interface_for_app('test_app')

        # Verify structure
        self.assertTrue(interface['available'])
        self.assertEqual(interface['status'], 'RUNNING')
        self.assertEqual(interface['tunnel_url'], 'http://test.ngrok.io')

        # Verify controls
        controls = interface['controls']
        self.assertEqual(len(controls), 2)
        self.assertEqual(controls[0]['type'], 'stop')
        self.assertEqual(controls[1]['type'], 'link')
        self.assertEqual(controls[1]['url'], 'http://test.ngrok.io')

    def test_get_control_interface_for_app_not_found(self):
        """
        Test control interface generation for non-existent applications.

        Ensures proper error handling when application is not found
        in the database.
        """
        # Mock app not found
        self.mock_state_manager.get_app_details.return_value = None

        # Get control interface
        interface = self.controller.get_control_interface_for_app('nonexistent_app')

        # Verify error response
        self.assertFalse(interface['available'])
        self.assertEqual(interface['reason'], 'Application not found')

    def test_thread_safety(self):
        """
        Test thread-safe operations of the controller.

        Validates that concurrent operations are properly synchronized
        and do not cause race conditions.
        """
        # Create multiple threads
        def register_callback():
            self.controller.register_status_callback(self.mock_callback)

        threads = []
        for i in range(10):
            thread = threading.Thread(target=register_callback)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all callbacks were registered safely
        self.assertEqual(len(self.controller.status_callbacks), 10)

    def test_error_propagation(self):
        """
        Test that errors are properly propagated with full tracebacks.

        Ensures that all exceptions include comprehensive debugging
        information as required by the Maximum Debug Philosophy.
        """
        # Mock database error
        self.mock_state_manager.get_all_apps.side_effect = Exception("Database connection failed")

        # Attempt operation that triggers error
        with self.assertRaises(Exception) as context:
            self.controller.get_application_status_summary()

        # Verify error includes full traceback information
        error_message = str(context.exception)
        self.assertIn("Database connection failed", error_message)
        self.assertIn("traceback", error_message.lower())


if __name__ == '__main__':
    # Create test suite
    unittest.main(verbosity=2)