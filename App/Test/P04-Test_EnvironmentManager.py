#!/usr/bin/env python3
"""
P04-Test_EnvironmentManager.py - Comprehensive test suite for P04_EnvironmentManager

This test script validates the complete functionality of the EnvironmentManager
including Conda-first, venv fallback strategy, platform detection, and error handling.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add the app directory to the path
app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, app_dir)

# Import the modules directly from their paths
from App.Utils.p01_cloud_detector import CloudDetector
from App.Core.p04_environment_manager import EnvironmentManager


class TestEnvironmentManager:
    """Test suite for EnvironmentManager functionality"""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = None
        self.cloud_detector = None
        self.env_manager = None
    
    def setup(self):
        """Set up test environment"""
        print("Setting up test environment...")
        
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp(prefix="pinokio_test_")
        print(f"Created temporary test directory: {self.temp_dir}")
        
        # Initialize components
        self.cloud_detector = CloudDetector()
        self.env_manager = EnvironmentManager(self.cloud_detector)
        
        print("✅ Test environment setup complete")
    
    def teardown(self):
        """Clean up test environment"""
        print("\n🧹 Cleaning up test environment...")
        
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"🗑️ Removed temporary test directory: {self.temp_dir}")
        
        print("✅ Test environment cleanup complete")
    
    def log_test(self, test_name, result, details=""):
        """Log test result"""
        status = "✅ PASS" if result else "❌ FAIL"
        self.test_results.append((test_name, result, details))
        print(f"{status} - {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def test_platform_detection(self):
        """Test platform detection functionality"""
        print("\n🔍 Testing platform detection...")
        
        try:
            platform_info = self.cloud_detector.detect_platform()
            print(f"   Platform: {platform_info.platform_name}")
            print(f"   Is Cloud: {platform_info.is_cloud}")
            print(f"   Cloud Provider: {platform_info.cloud_provider}")
            
            # Verify platform info structure
            required_attrs = ['platform_name', 'is_cloud', 'cloud_provider']
            for attr in required_attrs:
                if not hasattr(platform_info, attr):
                    self.log_test("Platform Detection - Required Attributes", False, f"Missing attribute: {attr}")
                    return
            
            self.log_test("Platform Detection", True, f"Detected: {platform_info.platform_name}")
            
        except Exception as e:
            self.log_test("Platform Detection", False, f"Exception: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def test_environment_type_detection(self):
        """Test environment type detection"""
        print("\n🔍 Testing environment type detection...")
        
        try:
            # Test with non-existent environment
            env_type = self.env_manager._detect_environment_type("nonexistent_env")
            expected_type = "conda" if not self.cloud_detector.detect_platform().is_cloud else "venv"
            
            if env_type == expected_type:
                self.log_test("Environment Type Detection - Default", True, f"Expected: {expected_type}, Got: {env_type}")
            else:
                self.log_test("Environment Type Detection - Default", False, f"Expected: {expected_type}, Got: {env_type}")
            
        except Exception as e:
            self.log_test("Environment Type Detection", False, f"Exception: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def test_conda_environment_creation(self):
        """Test Conda environment creation (if Conda is available)"""
        print("\n🔍 Testing Conda environment creation...")
        
        try:
            # Check if conda is available
            import subprocess
            result = subprocess.run(['conda', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                self.log_test("Conda Environment Creation", False, "Conda not available")
                return
            
            # Test environment creation
            test_env_name = "test_conda_env"
            
            def capture_output(line):
                print(f"   CONDA: {line.strip()}")
            
            success = self.env_manager.create(test_env_name, callback=capture_output)
            
            if success:
                self.log_test("Conda Environment Creation", True, f"Created: {test_env_name}")
                
                # Test environment detection
                env_type = self.env_manager._detect_environment_type(test_env_name)
                if env_type == "conda":
                    self.log_test("Conda Environment Detection", True, f"Detected as: {env_type}")
                else:
                    self.log_test("Conda Environment Detection", False, f"Expected: conda, Got: {env_type}")
                
                # Test run prefix
                prefix = self.env_manager.get_run_prefix(test_env_name)
                if prefix and "conda" in prefix.lower():
                    self.log_test("Conda Run Prefix", True, f"Prefix: {prefix}")
                else:
                    self.log_test("Conda Run Prefix", False, f"Invalid prefix: {prefix}")
                
                # Clean up test environment
                subprocess.run(['conda', 'env', 'remove', '-n', test_env_name, '-y'], 
                             capture_output=True)
                print(f"   Cleaned up test environment: {test_env_name}")
            else:
                self.log_test("Conda Environment Creation", False, "Creation failed")
                
        except Exception as e:
            self.log_test("Conda Environment Creation", False, f"Exception: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def test_venv_environment_creation(self):
        """Test venv environment creation"""
        print("\n🔍 Testing venv environment creation...")
        
        try:
            # Test environment creation
            test_env_name = "test_venv_env"
            
            def capture_output(line):
                print(f"   VENV: {line.strip()}")
            
            # Temporarily force venv by mocking platform detection
            original_detect = self.cloud_detector.detect_platform
            self.cloud_detector.detect_platform = lambda: type('PlatformInfo', (), {
                'platform_name': 'lightning',
                'is_cloud': True,
                'cloud_provider': 'lightning'
            })()
            
            success = self.env_manager.create(test_env_name, callback=capture_output)
            
            # Restore original detection
            self.cloud_detector.detect_platform = original_detect
            
            if success:
                self.log_test("Venv Environment Creation", True, f"Created: {test_env_name}")
                
                # Test environment detection
                env_type = self.env_manager._detect_environment_type(test_env_name)
                if env_type == "venv":
                    self.log_test("Venv Environment Detection", True, f"Detected as: {env_type}")
                else:
                    self.log_test("Venv Environment Detection", False, f"Expected: venv, Got: {env_type}")
                
                # Test run prefix
                prefix = self.env_manager.get_run_prefix(test_env_name)
                if prefix and "activate" in prefix.lower():
                    self.log_test("Venv Run Prefix", True, f"Prefix: {prefix}")
                else:
                    self.log_test("Venv Run Prefix", False, f"Invalid prefix: {prefix}")
                
                # Clean up test environment
                venv_path = Path(self.env_manager.base_path) / "venvs" / test_env_name
                if venv_path.exists():
                    shutil.rmtree(venv_path)
                    print(f"   Cleaned up test environment: {venv_path}")
            else:
                self.log_test("Venv Environment Creation", False, "Creation failed")
                
        except Exception as e:
            self.log_test("Venv Environment Creation", False, f"Exception: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n🔍 Testing error handling...")
        
        try:
            # Test with invalid environment name
            def capture_output(line):
                print(f"   ERROR: {line.strip()}")
            
            # Test with empty name
            try:
                self.env_manager.create("", callback=capture_output)
                self.log_test("Error Handling - Empty Name", False, "Should have raised an exception")
            except Exception as e:
                self.log_test("Error Handling - Empty Name", True, f"Correctly raised exception: {str(e)}")
            
            # Test with invalid characters
            try:
                self.env_manager.create("invalid/name", callback=capture_output)
                self.log_test("Error Handling - Invalid Characters", False, "Should have raised an exception")
            except Exception as e:
                self.log_test("Error Handling - Invalid Characters", True, f"Correctly raised exception: {str(e)}")
                
        except Exception as e:
            self.log_test("Error Handling", False, f"Exception: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def run_all_tests(self):
        """Run all tests"""
        print("Starting EnvironmentManager test suite...")
        print("=" * 60)
        
        self.setup()
        
        # Run all test methods
        self.test_platform_detection()
        self.test_environment_type_detection()
        self.test_conda_environment_creation()
        self.test_venv_environment_creation()
        self.test_error_handling()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result, _ in self.test_results if result)
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for test_name, result, details in self.test_results:
                if not result:
                    print(f"   - {test_name}: {details}")
        
        self.teardown()
        
        return passed == total


if __name__ == "__main__":
    # Run the test suite
    test_suite = TestEnvironmentManager()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)