#!/usr/bin/env python3
"""
Test script for P01_PathMapper module.

This script creates a mock PlatformInfo object and tests all path methods
of the P01_PathMapper class to ensure they return correct paths and
create directories as expected.
"""

import sys
import tempfile
import shutil
from pathlib import Path

# Add the App directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from App.Utils.P01_CloudDetector import PlatformInfo
from App.Utils.P01_PathMapper import P01_PathMapper


def create_mock_platform_info(base_path: str) -> PlatformInfo:
    """Create a mock PlatformInfo object for testing."""
    return PlatformInfo(
        platform_name="TestPlatform",
        is_cloud=False,
        supports_conda=True,
        supports_venv=True,
        base_path=base_path,
        has_gpu=False,
        gpu_info=None,
        memory_gb=8.0,
        cpu_count=4,
        special_requirements=[],
    )


def test_path_mapper():
    """Test the P01_PathMapper class with a temporary directory."""
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    print(f"Testing with temporary directory: {temp_dir}")

    try:
        # Create mock platform info
        platform_info = create_mock_platform_info(temp_dir)

        # Instantiate the PathMapper
        path_mapper = P01_PathMapper(platform_info)

        # Test all path methods
        print("\n=== Testing P01_PathMapper ===")

        # Test base path
        base_path = path_mapper.get_base_path()
        print(f"Base Path: {base_path}")
        assert base_path.exists(), f"Base path does not exist: {base_path}"
        assert base_path == Path(
            temp_dir
        ), f"Base path mismatch: {base_path} != {temp_dir}"

        # Test apps path
        apps_path = path_mapper.get_apps_path()
        print(f"Apps Path: {apps_path}")
        assert apps_path.exists(), f"Apps path does not exist: {apps_path}"
        assert apps_path == Path(temp_dir) / "apps", f"Apps path mismatch: {apps_path}"

        # Test data path
        data_path = path_mapper.get_data_path()
        print(f"Data Path: {data_path}")
        assert data_path.exists(), f"Data path does not exist: {data_path}"
        assert data_path == Path(temp_dir) / "data", f"Data path mismatch: {data_path}"

        # Test temp path
        temp_path = path_mapper.get_temp_path()
        print(f"Temp Path: {temp_path}")
        assert temp_path.exists(), f"Temp path does not exist: {temp_path}"
        assert temp_path == Path(temp_dir) / "temp", f"Temp path mismatch: {temp_path}"

        # Test config path
        config_path = path_mapper.get_config_path()
        print(f"Config Path: {config_path}")
        assert config_path.exists(), f"Config path does not exist: {config_path}"
        assert (
            config_path == Path(temp_dir) / "config"
        ), f"Config path mismatch: {config_path}"

        print("\n=== All Tests Passed! ===")
        print("All paths were correctly generated and directories were created.")

        # Show directory structure
        print("\n=== Directory Structure ===")
        for item in Path(temp_dir).iterdir():
            if item.is_dir():
                print(f"📁 {item.name}/")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)
        print(f"\nCleaned up temporary directory: {temp_dir}")

    return True


if __name__ == "__main__":
    success = test_path_mapper()
    sys.exit(0 if success else 1)
