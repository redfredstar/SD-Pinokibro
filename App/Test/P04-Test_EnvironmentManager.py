#!/usr/bin/env python3
"""
Test script for P04_EnvironmentManager.py

This script demonstrates how to use the EnvironmentManager class
to create environments and get run prefixes.

Location: App/Test/test_p04_environment_manager.py
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from Core.P04_EnvironmentManager import EnvironmentManager
from Utils.P01_CloudDetector import CloudDetector
from Core.P02_ProcessManager import ProcessManager
from Utils.P01_PathMapper import PathMapper

def test_callback(line: str) -> None:
    """Test callback function for streaming output."""
    print(f"[CALLBACK] {line}")

def main():
    """Test the EnvironmentManager functionality."""
    try:
        print("Testing P04_EnvironmentManager...")

        # Initialize dependencies
        cloud_detector = CloudDetector()
        process_manager = ProcessManager()
        path_mapper = PathMapper(cloud_detector)

        # Initialize environment manager
        env_manager = EnvironmentManager(cloud_detector, process_manager, path_mapper)

        # Display platform info
        platform_info = env_manager.get_platform_info()
        print(f"Platform: {platform_info['platform_info'].get('platform_name', 'Unknown')}")
        print(f"Strategy: {platform_info['strategy']}")
        print(f"Environment path: {platform_info['env_path']}")

        # Test environment creation
        test_env_name = "test_pinokio_env"
        print(f"\nCreating test environment: {test_env_name}")

        exit_code = env_manager.create(test_env_name, test_callback)
        print(f"Environment creation completed with exit code: {exit_code}")

        # Test run prefix generation
        run_prefix = env_manager.get_run_prefix(test_env_name)
        print(f"Run prefix for '{test_env_name}': {run_prefix}")

        # List available environments
        envs = env_manager.list_environments()
        print(f"Available environments: {envs}")

        print("Test completed successfully!")

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())