"""
P05-Test_AppAnalyzer.py - Test script for the P05_AppAnalyzer module

This script provides comprehensive unit tests for the AppAnalyzer functionality,
ensuring all components work correctly according to the architectural blueprint.
"""

import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Add the App directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Utils.P05_AppAnalyzer import P05_AppAnalyzer


class MockTranslator:
    """Mock translator for testing purposes"""
    
    def parse_file(self, file_path: str) -> list:
        """Mock implementation that returns a sample recipe"""
        return [
            {
                "step_type": "shell",
                "params": {
                    "command": "pip install torch gradio",
                    "cwd": "/tmp"
                }
            },
            {
                "step_type": "shell",
                "params": {
                    "command": "apt-get install -y ffmpeg",
                    "cwd": "/tmp"
                }
            },
            {
                "step_type": "shell",
                "params": {
                    "command": "git clone https://github.com/example/model.git",
                    "cwd": "/tmp"
                }
            }
        ]


def test_app_analyzer_initialization():
    """Test that the AppAnalyzer initializes correctly"""
    print("Testing AppAnalyzer initialization...")
    
    try:
        mock_translator = MockTranslator()
        analyzer = P05_AppAnalyzer(mock_translator)
        
        # Verify initialization
        assert analyzer.translator is not None
        assert len(analyzer.supported_installer_types) == 3
        assert '.js' in analyzer.supported_installer_types
        assert '.json' in analyzer.supported_installer_types
        assert '.txt' in analyzer.supported_installer_types
        
        print("✓ AppAnalyzer initialization test passed")
        return True
        
    except Exception as e:
        print(f"✗ AppAnalyzer initialization test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_analyze_app_basic():
    """Test basic app analysis functionality"""
    print("Testing basic app analysis...")
    
    try:
        mock_translator = MockTranslator()
        analyzer = P05_AppAnalyzer(mock_translator)
        
        # Sample app data
        app_data = {
            "name": "Test App",
            "install_url": "https://example.com/install.js",
            "description": "A test application for unit testing",
            "tags": ["test", "demo"],
            "gpu_required": False,
            "install_size_mb": 500
        }
        
        # Mock the requests.get call
        mock_response = Mock()
        mock_response.text = """
        shell.run("pip install torch gradio");
        shell.run("apt-get install -y ffmpeg");
        """
        mock_response.raise_for_status = Mock()
        
        with patch('requests.get', return_value=mock_response):
            with patch('requests.head', return_value=Mock(status_code=200)):
                result = analyzer.analyze_app(app_data)
        
        # Verify result structure
        assert "app_name" in result
        assert "installer_validation" in result
        assert "dependencies" in result
        assert "resource_estimates" in result
        assert "analysis_timestamp" in result
        assert "overall_status" in result
        
        # Verify app name
        assert result["app_name"] == "Test App"
        
        # Verify installer validation
        assert result["installer_validation"]["installer_url_accessible"] == True
        assert result["installer_validation"]["installer_type_supported"] == True
        
        # Verify dependencies
        assert "python_packages" in result["dependencies"]
        assert "system_packages" in result["dependencies"]
        
        print("✓ Basic app analysis test passed")
        return True
        
    except Exception as e:
        print(f"✗ Basic app analysis test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_dependency_checking():
    """Test dependency detection functionality"""
    print("Testing dependency checking...")
    
    try:
        mock_translator = MockTranslator()
        analyzer = P05_AppAnalyzer(mock_translator)
        
        # Create a temporary installer file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as temp_file:
            temp_file.write("""
            shell.run("pip install torch numpy pandas");
            shell.run("conda install pytorch torchvision");
            shell.run("apt-get install -y ffmpeg libssl-dev");
            """)
            temp_file_path = temp_file.name
        
        try:
            # Mock URL for the installer
            install_url = f"file://{temp_file_path}"
            
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.text = open(temp_file_path, 'r').read()
                mock_response.raise_for_status = Mock()
                mock_get.return_value = mock_response
                
                with patch('requests.head', return_value=Mock(status_code=200)):
                    dependencies, recipe = analyzer._check_dependencies(install_url)
            
            # Verify dependencies were detected
            assert "python_packages" in dependencies
            assert "system_packages" in dependencies
            
            # Check for specific packages
            python_packages = dependencies["python_packages"]
            system_packages = dependencies["system_packages"]
            
            # Should find torch, numpy, pandas, pytorch, torchvision
            found_torch = any("torch" in pkg for pkg in python_packages)
            found_numpy = any("numpy" in pkg for pkg in python_packages)
            found_ffmpeg = any("ffmpeg" in pkg for pkg in system_packages)
            
            assert found_torch, "Should detect torch package"
            assert found_numpy, "Should detect numpy package"
            assert found_ffmpeg, "Should detect ffmpeg package"
            
            print("✓ Dependency checking test passed")
            return True
            
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        print(f"✗ Dependency checking test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_resource_estimation():
    """Test resource estimation functionality"""
    print("Testing resource estimation...")
    
    try:
        mock_translator = MockTranslator()
        analyzer = P05_AppAnalyzer(mock_translator)
        
        # Test app data with GPU requirement
        app_data = {
            "name": "GPU App",
            "description": "An LLM application that requires GPU",
            "tags": ["llm", "ai", "model"],
            "gpu_required": True,
            "install_size_mb": 2000
        }
        
        # Sample recipe with GPU commands
        recipe = [
            {
                "step_type": "shell",
                "params": {
                    "command": "pip install torch --index-url https://download.pytorch.org/whl/cu118",
                    "cwd": "/tmp"
                }
            },
            {
                "step_type": "shell",
                "params": {
                    "command": "wget https://example.com/large_model.bin",
                    "cwd": "/tmp"
                }
            }
        ]
        
        estimates = analyzer._estimate_resources(app_data, recipe)
        
        # Verify estimates
        assert estimates["gpu_required"] == True
        assert estimates["estimated_ram_gb"] >= 16  # Should be high due to LLM keyword
        assert estimates["estimated_disk_mb"] >= 10000  # Should be high due to model.bin
        assert len(estimates["high_intensity_indicators"]) > 0
        
        print("✓ Resource estimation test passed")
        return True
        
    except Exception as e:
        print(f"✗ Resource estimation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_installer_validation():
    """Test installer validation functionality"""
    print("Testing installer validation...")
    
    try:
        mock_translator = MockTranslator()
        analyzer = P05_AppAnalyzer(mock_translator)
        
        # Test with valid URL
        valid_url = "https://example.com/install.js"
        
        with patch('requests.head', return_value=Mock(status_code=200)):
            result = analyzer._validate_installer(valid_url)
        
        assert result["installer_type_supported"] == True
        assert result["installer_url_accessible"] == True
        assert len(result["issues"]) == 0
        
        # Test with unsupported file type
        unsupported_url = "https://example.com/install.exe"
        
        result = analyzer._validate_installer(unsupported_url)
        
        assert result["installer_type_supported"] == False
        assert len(result["issues"]) > 0
        assert any("Unsupported file type" in issue for issue in result["issues"])
        
        # Test with inaccessible URL
        inaccessible_url = "https://example.com/nonexistent.js"
        
        with patch('requests.head', side_effect=Exception("Connection error")):
            result = analyzer._validate_installer(inaccessible_url)
        
        assert result["installer_url_accessible"] == False
        assert len(result["issues"]) > 0
        
        print("✓ Installer validation test passed")
        return True
        
    except Exception as e:
        print(f"✗ Installer validation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling with maximum debug philosophy"""
    print("Testing error handling...")
    
    try:
        mock_translator = MockTranslator()
        analyzer = P05_AppAnalyzer(mock_translator)
        
        # Test with missing install_url
        app_data_no_url = {
            "name": "Invalid App",
            "description": "App without install URL"
        }
        
        try:
            analyzer.analyze_app(app_data_no_url)
            assert False, "Should have raised an exception"
        except Exception as e:
            assert "install_url" in str(e)
            print(f"✓ Correctly caught missing install_url error: {str(e)}")
        
        # Test with invalid URL
        app_data_invalid_url = {
            "name": "Invalid URL App",
            "install_url": "https://nonexistent-domain.com/install.js"
        }
        
        with patch('requests.get', side_effect=Exception("Network error")):
            try:
                analyzer.analyze_app(app_data_invalid_url)
                assert False, "Should have raised an exception"
            except Exception as e:
                assert "Network error" in str(e) or "failed" in str(e)
                print(f"✓ Correctly caught network error: {str(e)}")
        
        print("✓ Error handling test passed")
        return True
        
    except Exception as e:
        print(f"✗ Error handling test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("=" * 60)
    print("P05_AppAnalyzer Test Suite")
    print("=" * 60)
    
    tests = [
        test_app_analyzer_initialization,
        test_analyze_app_basic,
        test_dependency_checking,
        test_resource_estimation,
        test_installer_validation,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! P05_AppAnalyzer is working correctly.")
        return True
    else:
        print(f"❌ {total - passed} test(s) failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)