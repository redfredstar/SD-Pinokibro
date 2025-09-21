"""
P02-Test_ProcessManager.py - Test Suite for P02_ProcessManager

This test suite validates the functionality of the P02_ProcessManager module,
ensuring it correctly implements the "Maximum Debug" philosophy with real-time
output streaming, process tracking, and proper error handling.

Author: Pinokiobro Architect
Phase: P02 - The All-Seeing Eye
"""

import unittest
import asyncio
import time
import threading
from unittest.mock import Mock, patch
import sys
import os

# Add the App directory to the path to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from App.Core.P02_ProcessManager import P02_ProcessManager, ProcessInfo


class TestP02ProcessManager(unittest.TestCase):
    """Test cases for the P02_ProcessManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.process_manager = P02_ProcessManager()
        self.captured_output = []
        
    def mock_callback(self, line: str):
        """Mock callback function to capture output."""
        self.captured_output.append(line)
        
    def test_initialization(self):
        """Test that ProcessManager initializes correctly."""
        self.assertIsNotNone(self.process_manager._event_loop)
        self.assertIsNotNone(self.process_manager._thread)
        self.assertTrue(self.process_manager._thread.is_alive())
        self.assertEqual(len(self.process_manager.active_processes), 0)
        
    def test_shell_run_simple_command(self):
        """Test running a simple shell command and capturing output."""
        # Run a simple echo command
        pid = self.process_manager.shell_run(
            "echo 'Hello, World!'", 
            self.mock_callback
        )
        
        # Verify PID is returned
        self.assertIsInstance(pid, int)
        self.assertGreater(pid, 0)
        
        # Verify process is tracked
        self.assertIn(pid, self.process_manager.active_processes)
        self.assertEqual(self.process_manager.active_processes[pid].status, 'running')
        
        # Wait a moment for output to be captured
        time.sleep(0.5)
        
        # Verify output was captured
        self.assertGreater(len(self.captured_output), 0)
        self.assertIn("STDOUT: Hello, World!", self.captured_output)
        
    def test_shell_run_with_stderr(self):
        """Test running a command that produces stderr output."""
        # Run a command that outputs to stderr
        pid = self.process_manager.shell_run(
            "bash -c 'echo \"Error message\" >&2'", 
            self.mock_callback
        )
        
        # Wait for output
        time.sleep(0.5)
        
        # Verify stderr was captured with prefix
        self.assertIn("STDERR: Error message", self.captured_output)
        
    def test_get_active_processes(self):
        """Test retrieving list of active processes."""
        # Start a process
        pid1 = self.process_manager.shell_run(
            "sleep 1", 
            self.mock_callback
        )
        
        # Get active processes
        active = self.process_manager.get_active_processes()
        
        # Verify our process is in the list
        self.assertIn(pid1, active)
        self.assertEqual(active[pid1].command, "sleep 1")
        self.assertEqual(active[pid1].status, 'running')
        
    def test_kill_process(self):
        """Test terminating a running process."""
        # Start a long-running process
        pid = self.process_manager.shell_run(
            "sleep 10", 
            self.mock_callback
        )
        
        # Verify process is running
        self.assertIn(pid, self.process_manager.active_processes)
        
        # Kill the process
        result = self.process_manager.kill_process(pid)
        
        # Verify kill was successful
        self.assertTrue(result)
        self.assertEqual(self.process_manager.active_processes[pid].status, 'killed')
        
    def test_kill_nonexistent_process(self):
        """Test killing a process that doesn't exist."""
        result = self.process_manager.kill_process(99999)
        self.assertFalse(result)
        
    def test_shell_run_with_working_directory(self):
        """Test running a command in a specific working directory."""
        # Create a temporary directory for testing
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file in the temp directory
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, 'w') as f:
                f.write("test content")
                
            # Run ls command in the temp directory
            pid = self.process_manager.shell_run(
                "ls", 
                self.mock_callback,
                cwd=temp_dir
            )
            
            # Wait for output
            time.sleep(0.5)
            
            # Verify the command ran in the correct directory
            output_text = ' '.join(self.captured_output)
            self.assertIn("test.txt", output_text)
            
    @patch('os.kill')
    def test_kill_process_permission_error(self, mock_kill):
        """Test handling of permission error when killing process."""
        # Mock os.kill to raise PermissionError
        mock_kill.side_effect = PermissionError("Permission denied")
        
        # Start a process
        pid = self.process_manager.shell_run(
            "sleep 1", 
            self.mock_callback
        )
        
        # Try to kill it
        result = self.process_manager.kill_process(pid)
        
        # Verify it failed gracefully
        self.assertFalse(result)
        
    def test_concurrent_process_execution(self):
        """Test running multiple processes concurrently."""
        pids = []
        
        # Start multiple processes
        for i in range(3):
            pid = self.process_manager.shell_run(
                f"echo 'Process {i}'", 
                self.mock_callback
            )
            pids.append(pid)
            
        # Verify all PIDs are different
        self.assertEqual(len(set(pids)), len(pids))
        
        # Verify all processes are tracked
        for pid in pids:
            self.assertIn(pid, self.process_manager.active_processes)
            
        # Wait for output
        time.sleep(0.5)
        
        # Verify all outputs were captured
        for i in range(3):
            self.assertIn(f"STDOUT: Process {i}", self.captured_output)


class TestProcessInfo(unittest.TestCase):
    """Test cases for the ProcessInfo dataclass."""
    
    def test_process_info_creation(self):
        """Test creating a ProcessInfo object."""
        info = ProcessInfo(pid=123, command="test command", status="running")
        
        self.assertEqual(info.pid, 123)
        self.assertEqual(info.command, "test command")
        self.assertEqual(info.status, "running")


if __name__ == '__main__':
    # Configure logging to see debug output
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Run the tests
    unittest.main(verbosity=2)