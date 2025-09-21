"""
P01_CloudDetector.py - System Foundation & Cloud Adaptation

This module provides hierarchical cloud platform detection and system resource assessment.
It identifies the operating environment (Colab, Vast.ai, Lightning.ai, etc.) and returns
standardized platform information for use by other system components.
"""

import os
import sys
import subprocess
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any

try:
    import psutil
except ImportError:
    psutil = None

try:
    import GPUtil
except ImportError:
    GPUtil = None


@dataclass
class PlatformInfo:
    """
    Standardized data container for detected platform information.

    This dataclass provides a consistent interface for platform detection results,
    including cloud environment identification, system resources, and capabilities.
    """

    platform_name: str
    is_cloud: bool
    supports_conda: bool
    supports_venv: bool
    base_path: str
    has_gpu: bool
    gpu_info: Optional[Dict[str, Any]] = None
    memory_gb: float = 0.0
    cpu_count: int = 0
    special_requirements: Optional[Dict[str, Any]] = None


class CloudDetector:
    """
    Performs hierarchical environment detection and system resource assessment.

    This class implements a robust detection system that identifies the current
    cloud platform through hierarchical checks and assesses available system
    resources including GPU, memory, and CPU capabilities.
    """

    def __init__(self) -> None:
        """
        Initialize the CloudDetector.

        This method performs no actions as initialization is handled in detect_platform.
        """
        pass

    def detect_platform(self) -> PlatformInfo:
        """
        Main detection logic that identifies the current platform and resources.

        This method performs hierarchical platform detection by calling private
        detection methods in sequence. The first method that returns True determines
        the platform. If no cloud platform is detected, defaults to Localhost.

        Returns:
            PlatformInfo: A fully populated dataclass with platform and resource information.

        Raises:
            Exception: Propagates any exceptions with full traceback for Maximum Debug philosophy.
        """
        try:
            # Hierarchical platform detection
            platform_name = "Localhost"
            is_cloud = False
            supports_conda = True
            supports_venv = True
            base_path = os.getcwd()
            special_requirements = {}

            # Check cloud platforms in hierarchical order
            if self._check_colab():
                platform_name = "Google Colab"
                is_cloud = True
                base_path = "/content/"
                special_requirements = {"notebook_environment": "colab"}
            elif self._check_vast():
                platform_name = "Vast.ai"
                is_cloud = True
                base_path = "/workspace/"
                special_requirements = {"gpu_instance": True}
            elif self._check_lightning():
                platform_name = "Lightning AI"
                is_cloud = True
                base_path = "/teamspace/studios/this_studio/"
                supports_conda = False  # Lightning AI requires venv
                special_requirements = {"requires_venv": True}
            elif self._check_kaggle():
                platform_name = "Kaggle"
                is_cloud = True
                base_path = "/kaggle/working/"
                special_requirements = {"notebook_environment": "kaggle"}
            elif self._check_sagemaker():
                platform_name = "AWS SageMaker"
                is_cloud = True
                base_path = "/home/ec2-user/SageMaker/"
                special_requirements = {"aws_managed": True}

            # Get system resources
            resources = self._get_system_resources()

            # Construct and return PlatformInfo
            return PlatformInfo(
                platform_name=platform_name,
                is_cloud=is_cloud,
                supports_conda=supports_conda,
                supports_venv=supports_venv,
                base_path=base_path,
                has_gpu=resources.get("has_gpu", False),
                gpu_info=resources.get("gpu_info"),
                memory_gb=resources.get("memory_gb", 0.0),
                cpu_count=resources.get("cpu_count", 0),
                special_requirements=special_requirements,
            )

        except Exception as e:
            # Re-raise with full traceback for Maximum Debug philosophy
            import traceback

            print(f"ERROR in CloudDetector.detect_platform():")
            traceback.print_exc()
            raise

    def _check_colab(self) -> bool:
        """
        Detect Google Colab environment.

        Checks for the presence of COLAB_GPU environment variable which is
        consistently available in Google Colab environments.

        Returns:
            bool: True if running in Google Colab, False otherwise.
        """
        try:
            return "COLAB_GPU" in os.environ
        except Exception as e:
            import traceback

            print(f"ERROR in CloudDetector._check_colab():")
            traceback.print_exc()
            return False

    def _check_vast(self) -> bool:
        """
        Detect Vast.ai environment.

        Checks for the presence of VAST_AI_INSTANCE_ID environment variable
        which is set in Vast.ai instances.

        Returns:
            bool: True if running on Vast.ai, False otherwise.
        """
        try:
            return "VAST_AI_INSTANCE_ID" in os.environ
        except Exception as e:
            import traceback

            print(f"ERROR in CloudDetector._check_vast():")
            traceback.print_exc()
            return False

    def _check_lightning(self) -> bool:
        """
        Detect Lightning AI environment.

        Checks for the presence of LIGHTNING_APP_STATE_URL environment variable
        which is specific to Lightning AI platform.

        Returns:
            bool: True if running on Lightning AI, False otherwise.
        """
        try:
            return "LIGHTNING_APP_STATE_URL" in os.environ
        except Exception as e:
            import traceback

            print(f"ERROR in CloudDetector._check_lightning():")
            traceback.print_exc()
            return False

    def _check_kaggle(self) -> bool:
        """
        Detect Kaggle environment.

        Checks for the presence of KAGGLE_KERNEL_RUN_TYPE environment variable
        which indicates execution within a Kaggle kernel.

        Returns:
            bool: True if running on Kaggle, False otherwise.
        """
        try:
            return "KAGGLE_KERNEL_RUN_TYPE" in os.environ
        except Exception as e:
            import traceback

            print(f"ERROR in CloudDetector._check_kaggle():")
            traceback.print_exc()
            return False

    def _check_sagemaker(self) -> bool:
        """
        Detect AWS SageMaker environment.

        Checks for the presence of AWS_SAGEMAKER_JUPYTER_KERNEL_IMAGE_NAME
        environment variable which is set in SageMaker notebook instances.

        Returns:
            bool: True if running on AWS SageMaker, False otherwise.
        """
        try:
            return "AWS_SAGEMAKER_JUPYTER_KERNEL_IMAGE_NAME" in os.environ
        except Exception as e:
            import traceback

            print(f"ERROR in CloudDetector._check_sagemaker():")
            traceback.print_exc()
            return False

    def _get_system_resources(self) -> Dict[str, Any]:
        """
        Get GPU, memory, and CPU information.

        This method attempts to gather comprehensive system resource information
        including GPU details (using GPUtil or nvidia-smi fallback), system memory,
        and CPU core count.

        Returns:
            Dict[str, Any]: Dictionary containing system resource information with keys:
                - has_gpu: Boolean indicating GPU presence
                - gpu_info: Dictionary with GPU details if present
                - memory_gb: Total system memory in GB
                - cpu_count: Number of logical CPU cores

        Raises:
            Exception: Propagates exceptions with full traceback for debugging.
        """
        try:
            resources = {
                "has_gpu": False,
                "gpu_info": None,
                "memory_gb": 0.0,
                "cpu_count": 0,
            }

            # GPU Detection
            gpu_info = self._detect_gpu()
            resources["has_gpu"] = gpu_info is not None
            resources["gpu_info"] = gpu_info

            # Memory Detection
            if psutil is not None:
                try:
                    memory_bytes = psutil.virtual_memory().total
                    resources["memory_gb"] = round(memory_bytes / (1024**3), 2)
                except Exception as e:
                    import traceback

                    print(f"ERROR getting memory info:")
                    traceback.print_exc()

            # CPU Detection
            if psutil is not None:
                try:
                    resources["cpu_count"] = psutil.cpu_count(logical=True)
                except Exception as e:
                    import traceback

                    print(f"ERROR getting CPU count:")
                    traceback.print_exc()

            return resources

        except Exception as e:
            import traceback

            print(f"ERROR in CloudDetector._get_system_resources():")
            traceback.print_exc()
            raise

    def _detect_gpu(self) -> Optional[Dict[str, Any]]:
        """
        Detect GPU information using GPUtil or nvidia-smi fallback.

        This method first attempts to use the GPUtil library for GPU detection.
        If GPUtil is not available, it falls back to parsing nvidia-smi output.

        Returns:
            Optional[Dict[str, Any]]: Dictionary with GPU information if GPU is present,
                                     None if no GPU is detected.
        """
        try:
            # Try GPUtil first
            if GPUtil is not None:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]  # Get first GPU
                        return {
                            "name": gpu.name,
                            "memory_total": gpu.memoryTotal,
                            "memory_free": gpu.memoryFree,
                            "memory_used": gpu.memoryUsed,
                            "driver_version": gpu.driver,
                            "id": gpu.id,
                        }
                except Exception as e:
                    import traceback

                    print(f"ERROR using GPUtil:")
                    traceback.print_exc()

            # Fallback to nvidia-smi
            try:
                result = subprocess.run(
                    [
                        "nvidia-smi",
                        "--query-gpu=name,memory.total,memory.used,memory.free,driver_version",
                        "--format=csv,noheader,nounits",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    gpu_data = result.stdout.strip().split(",")
                    if len(gpu_data) >= 4:
                        return {
                            "name": gpu_data[0].strip(),
                            "memory_total": int(gpu_data[1].strip()),
                            "memory_used": int(gpu_data[2].strip()),
                            "memory_free": int(gpu_data[3].strip()),
                            "driver_version": (
                                gpu_data[4].strip() if len(gpu_data) > 4 else "unknown"
                            ),
                        }
            except (
                subprocess.TimeoutExpired,
                subprocess.SubprocessError,
                FileNotFoundError,
            ):
                # nvidia-smi not available or failed
                pass

            return None

        except Exception as e:
            import traceback

            print(f"ERROR in CloudDetector._detect_gpu():")
            traceback.print_exc()
            return None
