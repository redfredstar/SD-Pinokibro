#!/usr/bin/env python3
"""
P12-Test_Stage2_E2E.py - Stage 2 End-to-End Integration Test

This script performs comprehensive end-to-end testing of the entire Stage 2 installation system.
It validates that the P07_InstallManager correctly orchestrates the installation process,
properly dispatches tasks to underlying managers, and maintains state integrity throughout.

Test Coverage:
- Installation workflow orchestration
- Step dispatcher functionality
- Manager integration (ProcessManager, FileManager, StateManager)
- Environment management integration
- State persistence and transitions
- Error handling and recovery
- Progress callback integration
- Input handling preparation

Author: Pinokiobro Architect
Date: 2025-09-21
Phase: P12 - Stage 2 Audit & Documentation Review
"""

import asyncio
import os
import tempfile
import shutil
import sqlite3
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from unittest.mock import Mock, MagicMock, patch
import traceback


class MockProcessManager:
    """Mock implementation of P02_ProcessManager for testing."""

    def __init__(self):
        """Initialize the mock process manager."""
        self.executed_commands = []
        self.process_counter = 0
        self.active_processes = {}

    def shell_run(self, command: str, callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
        """
        Mock shell_run that simulates command execution.

        Args:
            command: The command to execute
            callback: Optional callback for output streaming

        Returns:
            Dict containing execution results
        """
        try:
            self.executed_commands.append(command)
            self.process_counter += 1
            process_id = f"mock_pid_{self.process_counter}"

            # Simulate command execution with output
            if callback:
                callback(f"[MOCK] Executing: {command}")
                callback(f"[MOCK] Process ID: {process_id}")
                callback(f"[MOCK] Command completed successfully")

            return {
                'success': True,
                'process_id': process_id,
                'command': command,
                'output': f"Mock output for: {command}"
            }

        except Exception as e:
            if callback:
                callback(f"[MOCK] ERROR: {str(e)}")
                callback(f"[MOCK] {traceback.format_exc()}")
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }


class MockFileManager:
    """Mock implementation of P08_FileManager for testing."""

    def __init__(self, temp_dir: str):
        """Initialize the mock file manager."""
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
        self.downloaded_files = []
        self.created_files = []

    def download_file(self, url: str, destination: str, callback: Optional[Callable[[int], None]] = None) -> Dict[str, Any]:
        """
        Mock download_file that simulates file download.

        Args:
            url: Source URL
            destination: Destination path
            callback: Optional progress callback

        Returns:
            Dict containing download results
        """
        try:
            dest_path = self.temp_dir / destination

            # Create destination directory if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Simulate download with progress
            if callback:
                for progress in [0, 25, 50, 75, 100]:
                    callback(progress)
                    time.sleep(0.01)  # Small delay to simulate real download

            # Create a mock file
            dest_path.write_text(f"Mock content downloaded from {url}")
            self.downloaded_files.append(str(dest_path))

            return {
                'success': True,
                'file_path': str(dest_path),
                'url': url,
                'size': dest_path.stat().st_size
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Mock write_file that simulates atomic file writing.

        Args:
            file_path: Path to write to
            content: Content to write

        Returns:
            Dict containing write results
        """
        try:
            full_path = self.temp_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Simulate atomic write
            temp_file = full_path.with_suffix('.tmp')
            temp_file.write_text(content)
            temp_file.rename(full_path)

            self.created_files.append(str(full_path))

            return {
                'success': True,
                'file_path': str(full_path),
                'size': full_path.stat().st_size
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }


class MockStateManager:
    """Mock implementation of P08_StateManager for testing."""

    def __init__(self, temp_dir: str):
        """Initialize the mock state manager."""
        self.db_path = Path(temp_dir) / "test_state.db"
        self.setup_database()
        self.state_changes = []

    def setup_database(self):
        """Set up the test database schema."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                name TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                installation_path TEXT,
                environment_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def set_app_status(self, app_name: str, status: str, **kwargs) -> Dict[str, Any]:
        """
        Mock set_app_status that simulates database updates.

        Args:
            app_name: Name of the application
            status: New status
            **kwargs: Additional status information

        Returns:
            Dict containing operation results
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Record the state change
            self.state_changes.append({
                'app_name': app_name,
                'status': status,
                'timestamp': time.time(),
                'kwargs': kwargs
            })

            # Insert or update application
            cursor.execute('''
                INSERT OR REPLACE INTO applications
                (name, status, installation_path, environment_name, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (app_name, status, kwargs.get('installation_path'), kwargs.get('environment_name')))

            conn.commit()
            conn.close()

            return {
                'success': True,
                'app_name': app_name,
                'status': status,
                'changes_recorded': len(self.state_changes)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    def get_app_status(self, app_name: str) -> Dict[str, Any]:
        """
        Mock get_app_status that retrieves application status.

        Args:
            app_name: Name of the application

        Returns:
            Dict containing application status
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM applications WHERE name = ?', (app_name,))
            row = cursor.fetchone()

            conn.close()

            if row:
                return {
                    'success': True,
                    'app_name': row[0],
                    'status': row[1],
                    'installation_path': row[2],
                    'environment_name': row[3],
                    'created_at': row[4],
                    'updated_at': row[5]
                }
            else:
                return {
                    'success': False,
                    'error': f'Application {app_name} not found'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }


class MockEnvironmentManager:
    """Mock implementation of P04_EnvironmentManager for testing."""

    def __init__(self):
        """Initialize the mock environment manager."""
        self.created_environments = []
        self.environment_prefixes = {}

    def create_environment(self, env_name: str, callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
        """
        Mock create_environment that simulates environment creation.

        Args:
            env_name: Name of the environment to create
            callback: Optional callback for output streaming

        Returns:
            Dict containing creation results
        """
        try:
            if callback:
                callback(f"[MOCK ENV] Creating environment: {env_name}")
                callback(f"[MOCK ENV] Installing base packages...")
                callback(f"[MOCK ENV] Environment {env_name} created successfully")

            self.created_environments.append(env_name)

            return {
                'success': True,
                'environment_name': env_name,
                'environment_type': 'conda',  # Mock as conda
                'created': True
            }

        except Exception as e:
            if callback:
                callback(f"[MOCK ENV] ERROR: {str(e)}")
                callback(f"[MOCK ENV] {traceback.format_exc()}")
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    def get_run_prefix(self, env_name: str) -> str:
        """
        Mock get_run_prefix that returns environment activation command.

        Args:
            env_name: Name of the environment

        Returns:
            str: Command prefix for running in environment
        """
        prefix = f"conda run -n {env_name}"
        self.environment_prefixes[env_name] = prefix
        return prefix


class Stage2EndToEndTester:
    """Main test class for Stage 2 end-to-end integration testing."""

    def __init__(self):
        """Initialize the test environment."""
        self.temp_dir = None
        self.mock_process_manager = None
        self.mock_file_manager = None
        self.mock_state_manager = None
        self.mock_environment_manager = None
        self.test_results = []

    def setup_test_environment(self):
        """Set up the test environment with temporary directories."""
        try:
            self.temp_dir = tempfile.mkdtemp(prefix="stage2_e2e_test_")
            print(f"[TEST] Created temporary directory: {self.temp_dir}")

            # Initialize mock managers
            self.mock_process_manager = MockProcessManager()
            self.mock_file_manager = MockFileManager(self.temp_dir)
            self.mock_state_manager = MockStateManager(self.temp_dir)
            self.mock_environment_manager = MockEnvironmentManager()

            print("[TEST] All mock managers initialized successfully")

        except Exception as e:
            print(f"[TEST] ERROR setting up test environment: {str(e)}")
            print(f"[TEST] {traceback.format_exc()}")
            raise

    def create_complex_test_recipe(self) -> List[Dict]:
        """
        Create a complex test recipe that exercises multiple step types.

        Returns:
            List of recipe steps
        """
        return [
            {
                "step_type": "shell",
                "command": "echo 'Starting installation process...'"
            },
            {
                "step_type": "env_create",
                "name": "test_app_env",
                "type": "python3"
            },
            {
                "step_type": "shell",
                "command": "echo 'Environment created, downloading dependencies...'"
            },
            {
                "step_type": "fs_download",
                "url": "https://example.com/test_package.tar.gz",
                "path": "downloads/test_package.tar.gz"
            },
            {
                "step_type": "shell",
                "command": "echo 'Download complete, extracting...'"
            },
            {
                "step_type": "fs_write",
                "path": "config/app_config.json",
                "content": '{"app_name": "test_app", "version": "1.0.0"}'
            },
            {
                "step_type": "shell",
                "command": "echo 'Configuration written, installation complete'"
            }
        ]

    def mock_stream_to_terminal(self, line: str):
        """Mock terminal streaming function."""
        print(f"[STREAM] {line}")

    def mock_update_progress(self, percent: int):
        """Mock progress update function."""
        print(f"[PROGRESS] {percent}%")

    def test_installation_workflow(self) -> Dict[str, Any]:
        """
        Test the complete installation workflow.

        Returns:
            Dict containing test results
        """
        test_result = {
            'test_name': 'Installation Workflow Test',
            'success': False,
            'details': {},
            'errors': []
        }

        try:
            print("\n[TEST] === Starting Installation Workflow Test ===")

            # Create test recipe
            recipe = self.create_complex_test_recipe()
            app_name = "test_app_e2e"

            print(f"[TEST] Created test recipe with {len(recipe)} steps")
            print(f"[TEST] Testing installation of: {app_name}")

            # Mock the P07_InstallManager dependencies
            with patch('app.core.P07_InstallManager.ProcessManager', return_value=self.mock_process_manager), \
                 patch('app.core.P07_InstallManager.FileManager', return_value=self.mock_file_manager), \
                 patch('app.core.P07_InstallManager.StateManager', return_value=self.mock_state_manager), \
                 patch('app.core.P07_InstallManager.EnvironmentManager', return_value=self.mock_environment_manager):

                # Import and instantiate the real P07_InstallManager
                from app.core.P07_InstallManager import InstallManager

                install_manager = InstallManager()

                # Test the installation workflow
                print("[TEST] Starting installation process...")
                result = install_manager.install_app(
                    recipe=recipe,
                    app_name=app_name,
                    stream_callback=self.mock_stream_to_terminal,
                    progress_callback=self.mock_update_progress
                )

            # Validate results
            print("[TEST] Validating installation results...")

            # Check that commands were executed
            expected_commands = [
                "echo 'Starting installation process...'",
                "echo 'Environment created, downloading dependencies...'",
                "echo 'Download complete, extracting...'",
                "echo 'Configuration written, installation complete'"
            ]

            executed_commands = self.mock_process_manager.executed_commands
            print(f"[TEST] Expected {len(expected_commands)} shell commands")
            print(f"[TEST] Actually executed {len(executed_commands)} commands")

            for expected_cmd in expected_commands:
                if expected_cmd in executed_commands:
                    print(f"[TEST] ✓ Command executed: {expected_cmd}")
                else:
                    print(f"[TEST] ✗ Command missing: {expected_cmd}")
                    test_result['errors'].append(f"Missing command: {expected_cmd}")

            # Check that files were downloaded/created
            print(f"[TEST] Files downloaded: {len(self.mock_file_manager.downloaded_files)}")
            print(f"[TEST] Files created: {len(self.mock_file_manager.created_files)}")

            if len(self.mock_file_manager.downloaded_files) > 0:
                print("[TEST] ✓ File download operation completed")
            else:
                print("[TEST] ✗ No files were downloaded")
                test_result['errors'].append("No file download operations recorded")

            # Check state changes
            print(f"[TEST] State changes recorded: {len(self.mock_state_manager.state_changes)}")
            if len(self.mock_state_manager.state_changes) >= 2:  # Should have at least INSTALLING and INSTALLED
                print("[TEST] ✓ State transitions recorded")
            else:
                print("[TEST] ✗ Insufficient state transitions")
                test_result['errors'].append("Insufficient state transitions recorded")

            # Check environment creation
            if len(self.mock_environment_manager.created_environments) > 0:
                print("[TEST] ✓ Environment creation completed")
            else:
                print("[TEST] ✗ No environments were created")
                test_result['errors'].append("No environment creation recorded")

            # Overall success determination
            if not test_result['errors']:
                test_result['success'] = True
                print("[TEST] ✓ Installation workflow test PASSED")
            else:
                test_result['success'] = False
                print(f"[TEST] ✗ Installation workflow test FAILED with {len(test_result['errors'])} errors")

            test_result['details'] = {
                'commands_executed': len(executed_commands),
                'files_downloaded': len(self.mock_file_manager.downloaded_files),
                'files_created': len(self.mock_file_manager.created_files),
                'state_changes': len(self.mock_state_manager.state_changes),
                'environments_created': len(self.mock_environment_manager.created_environments)
            }

        except Exception as e:
            print(f"[TEST] ERROR during installation workflow test: {str(e)}")
            print(f"[TEST] {traceback.format_exc()}")
            test_result['success'] = False
            test_result['errors'].append(str(e))
            test_result['traceback'] = traceback.format_exc()

        return test_result

    def test_error_handling(self) -> Dict[str, Any]:
        """
        Test error handling capabilities.

        Returns:
            Dict containing test results
        """
        test_result = {
            'test_name': 'Error Handling Test',
            'success': False,
            'details': {},
            'errors': []
        }

        try:
            print("\n[TEST] === Starting Error Handling Test ===")

            # Create a recipe that will cause errors
            error_recipe = [
                {
                    "step_type": "shell",
                    "command": "exit 1"  # This will fail
                }
            ]

            app_name = "test_error_app"

            # Mock the managers
            with patch('app.core.P07_InstallManager.ProcessManager', return_value=self.mock_process_manager), \
                 patch('app.core.P07_InstallManager.FileManager', return_value=self.mock_file_manager), \
                 patch('app.core.P07_InstallManager.StateManager', return_value=self.mock_state_manager), \
                 patch('app.core.P07_InstallManager.EnvironmentManager', return_value=self.mock_environment_manager):

                from app.core.P07_InstallManager import InstallManager

                install_manager = InstallManager()

                # Test error handling
                result = install_manager.install_app(
                    recipe=error_recipe,
                    app_name=app_name,
                    stream_callback=self.mock_stream_to_terminal,
                    progress_callback=self.mock_update_progress
                )

            # Check that error was handled gracefully
            if result.get('success') == False:
                print("[TEST] ✓ Error was handled gracefully")
                test_result['success'] = True
            else:
                print("[TEST] ✗ Error was not handled properly")
                test_result['errors'].append("Error handling did not work as expected")

        except Exception as e:
            print(f"[TEST] ERROR during error handling test: {str(e)}")
            test_result['errors'].append(str(e))

        return test_result

    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all Stage 2 E2E tests.

        Returns:
            Dict containing overall test results
        """
        print("=" * 60)
        print("STAGE 2 END-TO-END INTEGRATION TEST SUITE")
        print("=" * 60)

        overall_result = {
            'test_suite': 'Stage 2 E2E Tests',
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_results': []
        }

        try:
            # Setup test environment
            self.setup_test_environment()

            # Run individual tests
            test1 = self.test_installation_workflow()
            overall_result['test_results'].append(test1)
            overall_result['total_tests'] += 1
            if test1['success']:
                overall_result['passed_tests'] += 1
            else:
                overall_result['failed_tests'] += 1

            test2 = self.test_error_handling()
            overall_result['test_results'].append(test2)
            overall_result['total_tests'] += 1
            if test2['success']:
                overall_result['passed_tests'] += 1
            else:
                overall_result['failed_tests'] += 1

            # Overall assessment
            if overall_result['failed_tests'] == 0:
                overall_result['overall_success'] = True
                print(f"\n[SUCCESS] All {overall_result['total_tests']} tests PASSED!")
            else:
                overall_result['overall_success'] = False
                print(f"\n[FAILURE] {overall_result['failed_tests']}/{overall_result['total_tests']} tests FAILED!")

            print("=" * 60)

        except Exception as e:
            print(f"[FATAL ERROR] Test suite failed: {str(e)}")
            print(f"[FATAL ERROR] {traceback.format_exc()}")
            overall_result['overall_success'] = False
            overall_result['fatal_error'] = str(e)
            overall_result['fatal_traceback'] = traceback.format_exc()

        finally:
            # Cleanup
            self.cleanup_test_environment()

        return overall_result

    def cleanup_test_environment(self):
        """Clean up the test environment."""
        try:
            if self.temp_dir and Path(self.temp_dir).exists():
                shutil.rmtree(self.temp_dir)
                print(f"[TEST] Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            print(f"[TEST] Warning: Could not clean up temporary directory: {str(e)}")


def main():
    """Main test execution function."""
    print("PinokioCloud Stage 2 End-to-End Integration Test")
    print("Testing the complete installation system workflow")

    tester = Stage2EndToEndTester()
    results = tester.run_all_tests()

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Test Suite: {results['test_suite']}")
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed_tests']}")
    print(f"Failed: {results['failed_tests']}")

    if results['overall_success']:
        print("\n🎉 STAGE 2 E2E TESTS PASSED!")
        print("The installation system is ready for production use.")
        return 0
    else:
        print("\n❌ STAGE 2 E2E TESTS FAILED!")
        print("Issues must be resolved before proceeding.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)