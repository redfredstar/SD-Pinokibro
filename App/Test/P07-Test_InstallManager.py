"""
P07-Test_InstallManager.py - Unit Test for P07_InstallManager

Test script for validating the P07_InstallManager implementation.
This test uses mock objects to simulate P02_ProcessManager and P04_EnvironmentManager
dependencies, allowing isolated testing of the installation orchestration logic.
"""

import sys
import os
from unittest.mock import Mock, MagicMock
from typing import List

# Add the App directory to the Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Core.P07_InstallManager import P07_InstallManager, P07_InstallationResult


class MockP02ProcessManager:
    """Mock implementation of P02_ProcessManager for testing."""
    
    def __init__(self):
        self.commands_executed = []
    
    def shell_run(self, command: str, callback):
        """Mock shell_run method that logs commands and simulates output."""
        self.commands_executed.append(command)
        callback(f"[MOCK_P02] Executing: {command}")
        callback(f"[MOCK_P02] Command completed successfully")


class MockP04EnvironmentManager:
    """Mock implementation of P04_EnvironmentManager for testing."""
    
    def __init__(self):
        self.environments_created = []
        self.run_prefix = "conda activate test_env &&"
    
    def create(self, env_name: str, callback):
        """Mock create method that simulates environment creation."""
        self.environments_created.append(env_name)
        callback(f"[MOCK_P04] Creating environment: {env_name}")
        callback(f"[MOCK_P04] Environment {env_name} created successfully")
    
    def get_run_prefix(self, env_name: str) -> str:
        """Mock get_run_prefix method that returns test prefix."""
        return f"conda activate {env_name} &&"


def test_p07_install_manager():
    """
    Comprehensive test of P07_InstallManager functionality.
    Tests the complete installation workflow with mock dependencies.
    """
    print("=== P07_InstallManager Test Suite ===")
    
    # Step 1: Create mock dependencies
    print("\n1. Creating mock dependencies...")
    mock_process_manager = MockP02ProcessManager()
    mock_env_manager = MockP04EnvironmentManager()
    
    # Step 2: Instantiate P07_InstallManager
    print("2. Instantiating P07_InstallManager...")
    install_manager = P07_InstallManager(mock_process_manager, mock_env_manager)
    
    # Step 3: Create test recipe
    print("3. Creating test recipe...")
    test_recipe = [
        {
            "step_type": "shell",
            "command": "pip install requests",
            "line_number": 1
        },
        {
            "step_type": "shell", 
            "command": "pip install numpy",
            "line_number": 2
        }
    ]
    
    # Step 4: Define callback for capturing output
    captured_output = []
    
    def test_callback(message: str):
        """Test callback that captures all output messages."""
        captured_output.append(message)
        print(f"[CALLBACK] {message}")
    
    # Step 5: Execute installation
    print("4. Executing installation...")
    result = install_manager.install_app(
        recipe=test_recipe,
        app_name="test_application",
        callback=test_callback
    )
    
    # Step 6: Validate results
    print("\n5. Validating results...")
    
    # Check installation result
    assert isinstance(result, P07_InstallationResult), "Result should be P07_InstallationResult"
    assert result.success == True, f"Installation should succeed, got: {result.error_message}"
    assert result.app_name == "test_application", "App name should match"
    assert result.steps_completed == 2, f"Should complete 2 steps, got: {result.steps_completed}"
    assert result.total_steps == 2, f"Should have 2 total steps, got: {result.total_steps}"
    
    # Check environment creation
    assert "test_application" in mock_env_manager.environments_created, "Environment should be created"
    
    # Check commands executed
    expected_commands = [
        "conda activate test_application && pip install requests",
        "conda activate test_application && pip install numpy"
    ]
    assert mock_process_manager.commands_executed == expected_commands, \
        f"Commands mismatch. Expected: {expected_commands}, Got: {mock_process_manager.commands_executed}"
    
    # Check callback output
    assert len(captured_output) > 0, "Should capture output through callback"
    
    print("\n✅ All tests passed successfully!")
    print(f"✅ Environment created: {mock_env_manager.environments_created}")
    print(f"✅ Commands executed: {mock_process_manager.commands_executed}")
    print(f"✅ Installation result: {result}")
    
    return True


def test_p07_error_handling():
    """
    Test error handling scenarios for P07_InstallManager.
    """
    print("\n=== P07_InstallManager Error Handling Test ===")
    
    # Create mocks that will raise exceptions
    mock_process_manager = Mock()
    mock_env_manager = Mock()
    
    # Configure mock to raise exception on create
    mock_env_manager.create.side_effect = Exception("Mock environment creation failure")
    
    install_manager = P07_InstallManager(mock_process_manager, mock_env_manager)
    
    test_recipe = [{"step_type": "shell", "command": "pip install test"}]
    captured_output = []
    
    def error_callback(message: str):
        captured_output.append(message)
        print(f"[ERROR_CALLBACK] {message}")
    
    result = install_manager.install_app(
        recipe=test_recipe,
        app_name="error_test",
        callback=error_callback
    )
    
    # Validate error handling
    assert result.success == False, "Should fail when environment creation fails"
    assert "Failed to create application environment" in result.error_message
    assert any("CRITICAL ERROR" in msg for msg in captured_output), "Should log critical error"
    
    print("✅ Error handling test passed!")
    return True


if __name__ == "__main__":
    """Main test execution."""
    try:
        print("Starting P07_InstallManager test suite...\n")
        
        # Run main functionality test
        test_p07_install_manager()
        
        # Run error handling test
        test_p07_error_handling()
        
        print("\n" + "="*50)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY! 🎉")
        print("P07_InstallManager is ready for integration.")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)