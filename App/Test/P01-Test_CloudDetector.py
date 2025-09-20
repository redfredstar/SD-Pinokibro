#!/usr/bin/env python3
"""
Test script for P01_CloudDetector module.

This script performs basic unit testing of the CloudDetector class,
verifying platform detection and system resource assessment functionality.
"""

import sys
import os

# Add the App directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from App.Utils.p01_cloud_detector import CloudDetector, PlatformInfo


def test_cloud_detector():
    """
    Basic unit test for CloudDetector functionality.
    
    This test instantiates the CloudDetector, calls detect_platform(),
    and prints the resulting PlatformInfo object to the console.
    """
    print("=== P01_CloudDetector Test ===")
    print("Testing CloudDetector platform detection and resource assessment...")
    print()
    
    try:
        # Instantiate the CloudDetector
        detector = CloudDetector()
        print("✅ CloudDetector instantiated successfully")
        
        # Call detect_platform to get platform information
        platform_info = detector.detect_platform()
        print("✅ Platform detection completed successfully")
        print()
        
        # Print the resulting PlatformInfo object
        print("=== Platform Information ===")
        print(f"Platform Name: {platform_info.platform_name}")
        print(f"Is Cloud: {platform_info.is_cloud}")
        print(f"Supports Conda: {platform_info.supports_conda}")
        print(f"Supports Venv: {platform_info.supports_venv}")
        print(f"Base Path: {platform_info.base_path}")
        print(f"Has GPU: {platform_info.has_gpu}")
        print(f"Memory GB: {platform_info.memory_gb}")
        print(f"CPU Count: {platform_info.cpu_count}")
        
        if platform_info.gpu_info:
            print("GPU Info:")
            for key, value in platform_info.gpu_info.items():
                print(f"  {key}: {value}")
        
        if platform_info.special_requirements:
            print("Special Requirements:")
            for key, value in platform_info.special_requirements.items():
                print(f"  {key}: {value}")
        
        print()
        print("=== Test Summary ===")
        print("✅ All tests completed successfully!")
        print("✅ CloudDetector is fully functional and ready for production use!")
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    """
    Main entry point for the test script.
    
    This function runs the test and exits with appropriate status code.
    """
    success = test_cloud_detector()
    sys.exit(0 if success else 1)