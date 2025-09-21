"""
P11-Test_LibraryManager.py - Unit Test for P11_LibraryManager

Test script for validating the P11_LibraryManager implementation.
This test demonstrates the uninstall_app workflow using mock dependencies
to simulate the complete application removal process.
"""

import sys
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add the App directory to the Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Core.P11_LibraryManager import P11_LibraryManager


class MockP08StateManager:
    """Mock implementation of P08_StateManager for testing."""
    
    def __init__(self):
        self.apps_data = {
            "test_app": {
                "app_name": "test_app",
                "status": "INSTALLED",
                "install_path": "/tmp/test_app",
                "environment_name": "test_app_env",
                "installed_at": "2025-01-01T12:00:00"
            }
        }
    
    def get_app_details(self, app_name: str):
        return self.apps_data.get(app_name)
    
    def remove_app(self, app_name: str):
        if app_name in self.apps_data:
            del self.apps_data[app_name]
            return True
        return False
    
    def set_app_status(self, app_name: str, status: str, **kwargs):
        if app_name in self.apps_data:
            self.apps_data[app_name]['status'] = status
            self.apps_data[app_name].update(kwargs)


class MockP04EnvironmentManager:
    """Mock implementation of P04_EnvironmentManager for testing."""
    
    def __init__(self):
        self.cloud_detector = Mock()
        self.cloud_detector.detect_platform.return_value = Mock(platform_name="Localhost")


class MockP02ProcessManager:
    """Mock implementation of P02_ProcessManager for testing."""
    
    def __init__(self):
        self.commands_executed = []
    
    def shell_run(self, command: str, callback):
        self.commands_executed.append(command)
        callback(f"[MOCK_P02] Executing: {command}")
        callback(f"[MOCK_P02] Command completed successfully")


class MockP01PathMapper:
    """Mock implementation of P01_PathMapper for testing."""
    
    def get_base_path(self):
        return Path("/tmp")


def test_p11_library_manager_uninstall():
    """
    Test the complete uninstall workflow of P11_LibraryManager.
    Demonstrates the logical flow: get info -> remove env -> remove files -> remove state.
    """
    print("=== P11_LibraryManager Uninstall Test ===")
    
    # Step 1: Create mock dependencies
    print("\n1. Creating mock dependencies...")
    mock_state_manager = MockP08StateManager()
    mock_env_manager = MockP04EnvironmentManager()
    mock_path_mapper = MockP01PathMapper()
    mock_process_manager = MockP02ProcessManager()
    
    # Step 2: Instantiate P11_LibraryManager
    print("2. Instantiating P11_LibraryManager...")
    library_manager = P11_LibraryManager(
        mock_state_manager,
        mock_env_manager, 
        mock_path_mapper,
        mock_process_manager
    )
    
    # Step 3: Create test application directory structure
    print("3. Setting up test application structure...")
    with tempfile.TemporaryDirectory() as temp_dir:
        app_install_path = Path(temp_dir) / "test_app"
        app_install_path.mkdir(parents=True, exist_ok=True)
        
        # Create test config file
        config_file = app_install_path / "config.json"
        test_config = {"version": "1.0.0", "debug": True}
        with open(config_file, 'w') as f:
            json.dump(test_config, f)
        
        # Update mock with actual path
        mock_state_manager.apps_data["test_app"]["install_path"] = str(app_install_path)
        
        # Step 4: Define callback for capturing output
        captured_output = []
        
        def test_callback(message: str):
            """Test callback that captures all output messages."""
            captured_output.append(message)
            print(f"[CALLBACK] {message}")
        
        # Step 5: Test get_app_config before uninstall
        print("4. Testing get_app_config...")
        try:
            retrieved_config = library_manager.get_app_config("test_app")
            assert retrieved_config == test_config, "Config should match"
            print("✅ Configuration retrieved successfully")
        except Exception as e:
            print(f"❌ Config retrieval failed: {e}")
            return False
        
        # Step 6: Test set_app_config
        print("5. Testing set_app_config...")
        try:
            new_config = {"version": "2.0.0", "debug": False, "new_setting": "test"}
            library_manager.set_app_config("test_app", new_config)
            
            # Verify config was written
            with open(config_file, 'r') as f:
                written_config = json.load(f)
            assert written_config == new_config, "Written config should match"
            print("✅ Configuration updated successfully")
        except Exception as e:
            print(f"❌ Config update failed: {e}")
            return False
        
        # Step 7: Execute uninstall
        print("6. Executing uninstall...")
        uninstall_result = library_manager.uninstall_app("test_app", test_callback)
        
        # Step 8: Validate results
        print("\n7. Validating uninstall results...")
        
        # Check uninstall result
        assert uninstall_result == True, "Uninstall should succeed"
        
        # Check state manager was called to remove app
        assert "test_app" not in mock_state_manager.apps_data, "App should be removed from state"
        
        # Check conda remove command was executed
        expected_command = "conda env remove -n test_app_env -y"
        assert expected_command in mock_process_manager.commands_executed, \
            f"Expected command not found. Commands: {mock_process_manager.commands_executed}"
        
        # Check callback output
        assert len(captured_output) > 0, "Should capture output through callback"
        assert any("Starting complete uninstallation" in msg for msg in captured_output), \
            "Should show uninstall start message"
        assert any("completed successfully" in msg for msg in captured_output), \
            "Should show completion message"
        
        print("✅ All uninstall validations passed!")
        print(f"✅ Commands executed: {mock_process_manager.commands_executed}")
        print(f"✅ Apps remaining in state: {list(mock_state_manager.apps_data.keys())}")
        
        print("\n" + "="*50)
        print("🎉 ALL P11_LIBRARYMANAGER TESTS PASSED! 🎉")
        print("P11_LibraryManager uninstall workflow is working correctly.")
        print("="*50)
        
        return True


def test_p11_library_manager_error_handling():
    """
    Test error handling scenarios for P11_LibraryManager.
    """
    print("\n=== P11_LibraryManager Error Handling Test ===")
    
    # Create mocks
    mock_state_manager = MockP08StateManager()
    mock_env_manager = MockP04EnvironmentManager()
    mock_path_mapper = MockP01PathMapper()
    mock_process_manager = MockP02ProcessManager()
    
    library_manager = P11_LibraryManager(
        mock_state_manager, mock_env_manager, mock_path_mapper, mock_process_manager
    )
    
    captured_output = []
    
    def error_callback(message: str):
        captured_output.append(message)
        print(f"[ERROR_CALLBACK] {message}")
    
    # Test uninstalling non-existent app
    result = library_manager.uninstall_app("non_existent_app", error_callback)
    
    # Should fail gracefully
    assert result == False, "Should fail for non-existent app"
    assert any("not found" in msg for msg in captured_output), "Should indicate app not found"
    
    print("✅ Error handling test passed!")
    return True


if __name__ == "__main__":
    """Main test execution."""
    try:
        print("Starting P11_LibraryManager test suite...\n")
        
        # Run main functionality test
        main_success = test_p11_library_manager_uninstall()
        
        # Run error handling test
        error_success = test_p11_library_manager_error_handling()
        
        if main_success and error_success:
            print("\n✅ P11_LibraryManager implementation is ready for integration!")
        else:
            print("\n❌ P11_LibraryManager tests failed!")
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)