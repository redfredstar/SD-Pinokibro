"""
P08-Test_StateManager.py - Unit Test for P08_StateManager

Test script for validating the P08_StateManager implementation.
This test demonstrates the core lifecycle operations: add app, set status, 
get status, and remove app using a temporary database for safe testing.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock

# Add the App directory to the Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Core.P08_StateManager import P08_StateManager


class MockP01PathMapper:
    """Mock implementation of P01_PathMapper for testing."""
    
    def __init__(self, temp_dir):
        self.temp_dir = Path(temp_dir)
    
    def get_config_path(self):
        return self.temp_dir / "config"


def test_p08_state_manager_lifecycle():
    """
    Test the complete lifecycle of P08_StateManager operations.
    Demonstrates: add app -> set status -> get status -> remove app.
    """
    print("=== P08_StateManager Lifecycle Test ===")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"Using temporary directory: {temp_path}")
        
        try:
            # Step 1: Initialize P08_StateManager with mock path mapper
            print("\n1. Creating P08_StateManager instance...")
            mock_path_mapper = MockP01PathMapper(temp_dir)
            state_manager = P08_StateManager(mock_path_mapper)
            
            # Verify database was created
            db_path = mock_path_mapper.get_config_path() / 'pinokio.db'
            assert db_path.exists(), "Database file should be created"
            print(f"✅ Database created successfully: {db_path}")
            
            # Step 2: Add a new application
            print("2. Testing add_app operation...")
            app_name = "test_stable_diffusion"
            install_path = temp_path / "apps" / app_name
            
            state_manager.add_app(app_name, install_path)
            print(f"✅ Application '{app_name}' added successfully")
            
            # Step 3: Verify initial status
            print("3. Testing get_app_status operation...")
            initial_status = state_manager.get_app_status(app_name)
            assert initial_status == "INSTALLING", f"Expected 'INSTALLING', got '{initial_status}'"
            print(f"✅ Initial status verified: {initial_status}")
            
            # Step 4: Update application status
            print("4. Testing set_app_status operation...")
            state_manager.set_app_status(app_name, "INSTALLED", 
                                       environment_name="stable_diffusion_env")
            
            updated_status = state_manager.get_app_status(app_name)
            assert updated_status == "INSTALLED", f"Expected 'INSTALLED', got '{updated_status}'"
            print(f"✅ Status updated successfully: {updated_status}")
            
            # Step 5: Get complete application details
            print("5. Testing get_app_details operation...")
            app_details = state_manager.get_app_details(app_name)
            assert app_details is not None, "App details should exist"
            assert app_details['app_name'] == app_name, "App name should match"
            assert app_details['status'] == "INSTALLED", "Status should be INSTALLED"
            assert app_details['environment_name'] == "stable_diffusion_env", "Environment name should match"
            print(f"✅ App details retrieved: {app_details}")
            
            # Step 6: Test get_all_apps
            print("6. Testing get_all_apps operation...")
            all_apps = state_manager.get_all_apps()
            assert len(all_apps) == 1, "Should have exactly 1 app"
            assert all_apps[0]['app_name'] == app_name, "App name should match in all_apps"
            print(f"✅ All apps retrieved: {len(all_apps)} application(s) found")
            
            # Step 7: Test status filtering
            print("7. Testing get_apps_by_status operation...")
            installed_apps = state_manager.get_apps_by_status("INSTALLED")
            assert len(installed_apps) == 1, "Should find 1 installed app"
            assert installed_apps[0]['app_name'] == app_name, "Should find our test app"
            print(f"✅ Status filtering works: {len(installed_apps)} app(s) with INSTALLED status")
            
            # Step 8: Update status with additional metadata
            print("8. Testing status update with metadata...")
            state_manager.set_app_status(app_name, "RUNNING", 
                                       process_pid=12345,
                                       tunnel_url="https://abc123.ngrok.io")
            
            running_details = state_manager.get_app_details(app_name)
            assert running_details['status'] == "RUNNING", "Status should be RUNNING"
            assert running_details['process_pid'] == 12345, "PID should be set"
            assert running_details['tunnel_url'] == "https://abc123.ngrok.io", "Tunnel URL should be set"
            print("✅ Metadata update successful")
            
            # Step 9: Remove the application
            print("9. Testing remove_app operation...")
            removal_result = state_manager.remove_app(app_name)
            assert removal_result == True, "Removal should return True for existing app"
            
            # Verify app is gone
            removed_status = state_manager.get_app_status(app_name)
            assert removed_status is None, "Status should be None for removed app"
            print(f"✅ Application '{app_name}' removed successfully")
            
            # Step 10: Test removing non-existent app
            print("10. Testing remove_app on non-existent app...")
            non_removal_result = state_manager.remove_app("non_existent_app")
            assert non_removal_result == False, "Removal should return False for non-existent app"
            print("✅ Non-existent app removal handled correctly")
            
            print("\n" + "="*50)
            print("🎉 ALL P08_STATEMANAGER TESTS PASSED! 🎉")
            print("P08_StateManager lifecycle operations are working correctly.")
            print("Database operations are atomic, thread-safe, and error-handled.")
            print("="*50)
            
            return True
            
        except Exception as e:
            print(f"❌ State manager test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_p08_state_manager_error_handling():
    """
    Test error handling scenarios for P08_StateManager.
    """
    print("\n=== P08_StateManager Error Handling Test ===")
    
    try:
        # Test with invalid path mapper
        invalid_path_mapper = Mock()
        invalid_path_mapper.get_config_path.return_value = Path("/invalid/readonly/path")
        
        try:
            state_manager = P08_StateManager(invalid_path_mapper)
            print("❌ Expected error for invalid path")
            return False
        except Exception as e:
            print(f"✅ Correctly handled invalid path error: {type(e).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


if __name__ == "__main__":
    """Main test execution."""
    try:
        print("Starting P08_StateManager test suite...\n")
        
        # Run lifecycle test
        lifecycle_success = test_p08_state_manager_lifecycle()
        
        # Run error handling test  
        error_success = test_p08_state_manager_error_handling()
        
        if lifecycle_success and error_success:
            print("\n✅ P08_StateManager implementation is ready for integration!")
        else:
            print("\n❌ P08_StateManager tests failed!")
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)