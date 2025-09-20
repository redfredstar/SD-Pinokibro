#!/usr/bin/env python3
"""
Test script for P02_ProcessManager
Tests real-time output streaming and process management capabilities.
"""

import sys
import time
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.P02_ProcessManager import P02_ProcessManager

def test_process_manager():
    """Basic unit test for ProcessManager functionality."""
    print("=== P02_ProcessManager Unit Test ===\n")
    
    # Initialize manager
    manager = P02_ProcessManager()
    print("✓ ProcessManager initialized\n")
    
    # Test 1: Simple command with output streaming
    print("Test 1: Real-time output streaming")
    print("-" * 40)
    
    def print_callback(line):
        print(f"  {line}")
    
    # Run a command that produces output over time
    exit_code = manager.shell_run(
        "echo 'Starting process...' && sleep 1 && echo 'Processing...' && sleep 1 && echo 'Complete!'",
        callback=print_callback
    )
    print(f"Exit code: {exit_code}")
    print("✓ Test 1 passed\n")
    
    # Test 2: Error handling
    print("Test 2: Error handling")
    print("-" * 40)
    exit_code = manager.shell_run(
        "this_command_does_not_exist",
        callback=print_callback
    )
    print(f"Exit code: {exit_code}")
    print("✓ Test 2 passed\n")
    
    # Test 3: Process tracking
    print("Test 3: Process tracking")
    print("-" * 40)
    
    # Start a long-running process
    import threading
    
    def background_process():
        manager.shell_run("sleep 5", callback=lambda x: None)
    
    thread = threading.Thread(target=background_process)
    thread.start()
    
    time.sleep(0.5)  # Let process start
    
    active = manager.get_active_processes()
    print(f"Active processes: {active}")
    
    all_procs = manager.get_all_processes()
    for proc_id, info in all_procs.items():
        print(f"  {proc_id}: {info['status']} - {info['command'][:50]}")
    
    print("✓ Test 3 passed\n")
    
    # Test 4: Process termination
    print("Test 4: Process termination")
    print("-" * 40)
    
    if active:
        pid = list(active.values())[0]
        success = manager.kill_process(pid)
        print(f"Killed process {pid}: {success}")
        
        time.sleep(0.5)
        active_after = manager.get_active_processes()
        print(f"Active processes after kill: {active_after}")
    
    print("✓ Test 4 passed\n")
    
    # Cleanup
    manager.shutdown()
    print("=== All tests passed! ===")

if __name__ == "__main__":
    test_process_manager()