from pathlib import Path
from typing import TYPE_CHECKING
import traceback

if TYPE_CHECKING:
    from App.Utils.P01_CloudDetector import PlatformInfo


class P01_PathMapper:
    """
    A platform-agnostic path abstraction layer for the PinokioCloud project.

    This class consumes a PlatformInfo object and provides semantic path requests,
    ensuring all file system operations work correctly across different cloud
    environments without using any hardcoded paths. This module is the single
    source of truth for file system locations.
    """

    def __init__(self, platform_info: "PlatformInfo") -> None:
        """
        Initialize the PathMapper with platform information.

        Args:
            platform_info: A PlatformInfo object containing platform-specific
                          information including the base path.

        Raises:
            TypeError: If platform_info is not a PlatformInfo object.
            ValueError: If platform_info does not contain a valid base_path.
        """
        try:
            if not hasattr(platform_info, "base_path") or not platform_info.base_path:
                raise ValueError("PlatformInfo must contain a valid base_path")

            self._platform_info = platform_info
            self._base_path = Path(platform_info.base_path)

            # Ensure the base directory exists
            self._base_path.mkdir(parents=True, exist_ok=True)

        except Exception as e:
            # Re-raise with full traceback for maximum debug transparency
            full_traceback = traceback.format_exc()
            raise RuntimeError(
                f"P01_PathMapper initialization failed: {str(e)}\n{full_traceback}"
            )

    def get_base_path(self) -> Path:
        """
        Get the root working directory for the entire application.

        Returns:
            Path: The base path as a pathlib.Path object.
        """
        try:
            # Ensure the base directory exists
            self._base_path.mkdir(parents=True, exist_ok=True)
            return self._base_path
        except Exception as e:
            full_traceback = traceback.format_exc()
            raise RuntimeError(f"Failed to get base path: {str(e)}\n{full_traceback}")

    def get_apps_path(self) -> Path:
        """
        Get the path to the directory where all Pinokio applications will be installed.

        Returns:
            Path: The apps path as a pathlib.Path object ([base_path]/apps/).
        """
        try:
            apps_path = self._base_path / "apps"
            # Ensure the directory exists
            apps_path.mkdir(parents=True, exist_ok=True)
            return apps_path
        except Exception as e:
            full_traceback = traceback.format_exc()
            raise RuntimeError(f"Failed to get apps path: {str(e)}\n{full_traceback}")

    def get_data_path(self) -> Path:
        """
        Get the path for persistent data storage (e.g., databases, models).

        Returns:
            Path: The data path as a pathlib.Path object ([base_path]/data/).
        """
        try:
            data_path = self._base_path / "data"
            # Ensure the directory exists
            data_path.mkdir(parents=True, exist_ok=True)
            return data_path
        except Exception as e:
            full_traceback = traceback.format_exc()
            raise RuntimeError(f"Failed to get data path: {str(e)}\n{full_traceback}")

    def get_temp_path(self) -> Path:
        """
        Get the path for temporary files.

        Returns:
            Path: The temp path as a pathlib.Path object ([base_path]/temp/).
        """
        try:
            temp_path = self._base_path / "temp"
            # Ensure the directory exists
            temp_path.mkdir(parents=True, exist_ok=True)
            return temp_path
        except Exception as e:
            full_traceback = traceback.format_exc()
            raise RuntimeError(f"Failed to get temp path: {str(e)}\n{full_traceback}")

    def get_config_path(self) -> Path:
        """
        Get the path for configuration files.

        Returns:
            Path: The config path as a pathlib.Path object ([base_path]/config/).
        """
        try:
            config_path = self._base_path / "config"
            # Ensure the directory exists
            config_path.mkdir(parents=True, exist_ok=True)
            return config_path
        except Exception as e:
            full_traceback = traceback.format_exc()
            raise RuntimeError(f"Failed to get config path: {str(e)}\n{full_traceback}")
