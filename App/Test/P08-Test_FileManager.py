"""
P08-Test_FileManager.py - Unit Test for P08_FileManager

Test script for validating the P08_FileManager implementation.
This test demonstrates the write and copy functionality using a temporary
directory for safe testing without affecting the project structure.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock

# Add the App directory to the Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Core.P08_FileManager import P08_FileManager


class MockP01PathMapper:
    """Mock implementation of P01_PathMapper for testing."""
    
    def get_base_path(self):
        return Path.cwd()
    
    def get_temp_path(self):
        return Path(tempfile.gettempdir())


def test_p08_file_manager_write_and_copy():
    """
    Test the write and copy functionality of P08_FileManager.
    Demonstrates atomic file writing and file copying operations.
    """
    print("=== P08_FileManager Write and Copy Test ===")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"Using temporary directory: {temp_path}")
        
        # Step 1: Initialize P08_FileManager with mock path mapper
        print("\n1. Creating P08_FileManager instance...")
        mock_path_mapper = MockP01PathMapper()
        file_manager = P08_FileManager(mock_path_mapper)
        
        # Step 2: Test file writing
        print("2. Testing file write operation...")
        test_content = """# Test Configuration File
app_name: test_application
version: 1.0.0
dependencies:
  - python>=3.8
  - requests>=2.25.0
settings:
  debug: true
  timeout: 30
"""
        
        test_file_path = temp_path / "test_config.yml"
        
        try:
            file_manager.write(test_file_path, test_content)
            print(f"✅ File written successfully: {test_file_path}")
            
            # Verify file exists and content matches
            if test_file_path.exists():
                with open(test_file_path, 'r', encoding='utf-8') as f:
                    read_content = f.read()
                assert read_content == test_content, "File content mismatch!"
                print("✅ File content verified successfully")
            else:
                raise Exception("File was not created")
                
        except Exception as e:
            print(f"❌ File write test failed: {e}")
            return False
        
        # Step 3: Test file copying
        print("3. Testing file copy operation...")
        copy_dest_path = temp_path / "copied_config.yml"
        
        try:
            file_manager.copy(test_file_path, copy_dest_path)
            print(f"✅ File copied successfully: {copy_dest_path}")
            
            # Verify copied file exists and content matches
            if copy_dest_path.exists():
                with open(copy_dest_path, 'r', encoding='utf-8') as f:
                    copied_content = f.read()
                assert copied_content == test_content, "Copied file content mismatch!"
                print("✅ Copied file content verified successfully")
            else:
                raise Exception("Copied file was not created")
                
        except Exception as e:
            print(f"❌ File copy test failed: {e}")
            return False
        
        # Step 4: Test directory operations
        print("4. Testing directory operations...")
        
        # Create a test directory structure
        test_dir = temp_path / "test_directory"
        test_subdir = test_dir / "subdir"
        test_subfile = test_subdir / "nested_file.txt"
        
        try:
            # Create directory structure
            file_manager.mkdir(test_subdir, parents=True)
            file_manager.write(test_subfile, "This is a nested file for testing.")
            print("✅ Directory structure created successfully")
            
            # Test directory copying
            copied_dir = temp_path / "copied_directory"
            file_manager.copy(test_dir, copied_dir)
            
            # Verify directory copy
            copied_subfile = copied_dir / "subdir" / "nested_file.txt"
            if copied_subfile.exists():
                with open(copied_subfile, 'r') as f:
                    nested_content = f.read()
                assert nested_content == "This is a nested file for testing."
                print("✅ Directory copy verified successfully")
            else:
                raise Exception("Directory copy failed")
                
        except Exception as e:
            print(f"❌ Directory operation test failed: {e}")
            return False
        
        # Step 5: Test error handling
        print("5. Testing error handling...")
        
        try:
            # Test writing to invalid path (should handle gracefully)
            invalid_path = Path("/invalid/nonexistent/path/file.txt")
            try:
                file_manager.write(invalid_path, "test")
                print("❌ Expected error for invalid path write")
                return False
            except Exception as e:
                print(f"✅ Correctly handled invalid path error: {type(e).__name__}")
            
            # Test copying non-existent file
            nonexistent_file = temp_path / "does_not_exist.txt"
            copy_target = temp_path / "copy_target.txt"
            try:
                file_manager.copy(nonexistent_file, copy_target)
                print("❌ Expected error for non-existent file copy")
                return False
            except Exception as e:
                print(f"✅ Correctly handled non-existent file error: {type(e).__name__}")
            
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            return False
        
        print("\n" + "="*50)
        print("🎉 ALL P08_FILEMANAGER TESTS PASSED! 🎉")
        print("P08_FileManager write and copy operations are working correctly.")
        print("="*50)
        
        return True


if __name__ == "__main__":
    """Main test execution."""
    try:
        print("Starting P08_FileManager test suite...\n")
        
        # Run write and copy functionality test
        success = test_p08_file_manager_write_and_copy()
        
        if success:
            print("\n✅ P08_FileManager implementation is ready for integration!")
        else:
            print("\n❌ P08_FileManager tests failed!")
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)