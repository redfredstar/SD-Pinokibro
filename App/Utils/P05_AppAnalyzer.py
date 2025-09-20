
"""
P05_AppAnalyzer.py - The Application Pre-Flight Analysis Engine

This module provides comprehensive static analysis capabilities for Pinokio applications,
performing pre-flight checks on application metadata to provide users with informed
assessments before installation.
"""

import os
import tempfile
import requests
from typing import Dict, Any, List, Optional
import re
import traceback
import logging

# Set up logging for maximum debug philosophy
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class P05_AppAnalyzer:
    """
    A comprehensive static analysis tool for Pinokio applications.
    
    This class performs pre-flight checks on application metadata, analyzing
    dependencies, resource requirements, and installer validity to provide
    users with detailed assessments before installation.
    """
    
    def __init__(self, translator):
        """
        Initialize the AppAnalyzer with a translator instance.
        
        Args:
            translator: An instance of P03_Translator for parsing installer files
        """
        self.translator = translator
        self.supported_installer_types = ['.js', '.json', '.txt']
        
        # Common dependency patterns for detection
        self.python_package_patterns = [
            r'pip\s+install\s+([^\s\n]+)',
            r'python\s+-m\s+pip\s+install\s+([^\s\n]+)',
            r'conda\s+install\s+([^\s\n]+)',
            r'mamba\s+install\s+([^\s\n]+)'
        ]
        
        self.system_package_patterns = [
            r'apt-get\s+install\s+([^\s\n]+)',
            r'apt\s+install\s+([^\s\n]+)',
            r'yum\s+install\s+([^\s\n]+)',
            r'brew\s+install\s+([^\s\n]+)'
        ]
        
        # Resource estimation keywords
        self.high_memory_keywords = ['llm', 'model', 'transformer', 'embedding', 'checkpoint']
        self.high_disk_keywords = ['download', 'model.bin', 'weights', 'dataset', 'checkpoint']
        
        logger.debug("P05_AppAnalyzer initialized with translator")
    
    def analyze_app(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on application metadata.
        
        Args:
            app_data: Dictionary containing application metadata
            
        Returns:
            Dictionary containing complete analysis report
            
        Raises:
            Exception: With full traceback if analysis fails
        """
        try:
            logger.debug(f"Starting analysis for app: {app_data.get('name', 'Unknown')}")
            
            # Extract essential information
            install_url = app_data.get('install_url', '')
            if not install_url:
                raise ValueError("Application metadata missing 'install_url'")
            
            # Perform analysis steps
            installer_validation = self._validate_installer(install_url)
            
            # Only proceed with dependency checking if installer is valid
            dependencies = {}
            recipe = []
            if installer_validation.get('installer_url_accessible', False):
                try:
                    dependencies, recipe = self._check_dependencies(install_url)
                except Exception as e:
                    logger.error(f"Dependency analysis failed: {str(e)}")
                    logger.error(traceback.format_exc())
                    dependencies = {"error": str(e), "python_packages": [], "system_packages": []}
            
            resource_estimates = self._estimate_resources(app_data, recipe)
            
            # Compile comprehensive report
            analysis_report = {
                "app_name": app_data.get('name', 'Unknown'),
                "installer_validation": installer_validation,
                "dependencies": dependencies,
                "resource_estimates": resource_estimates,
                "analysis_timestamp": self._get_current_timestamp(),
                "overall_status": self._determine_overall_status(installer_validation, dependencies, resource_estimates)
            }
            
            logger.debug(f"Analysis completed for {app_data.get('name', 'Unknown')}")
            return analysis_report
            
        except Exception as e:
            logger.error(f"App analysis failed: {str(e)}")
            logger.error(traceback.format_exc())
            # Re-raise with full traceback for maximum debug
            raise Exception(f"App analysis failed for {app_data.get('name', 'Unknown')}: {str(e)}") from e
    
    def _check_dependencies(self, install_url: str) -> tuple[Dict[str, Any], List[Dict]]:
        """
        Analyze installer file to identify dependencies.
        
        Args:
            install_url: URL to the installer file
            
        Returns:
            Tuple of (dependencies_dict, parsed_recipe)
            
        Raises:
            Exception: With full traceback if dependency checking fails
        """
        try:
            logger.debug(f"Checking dependencies for installer: {install_url}")
            
            # Fetch installer content
            response = requests.get(install_url, timeout=30)
            response.raise_for_status()
            installer_content = response.text
            
            # Save to temporary file for translator
            with tempfile.NamedTemporaryFile(mode='w', suffix=self._get_file_extension(install_url), delete=False) as temp_file:
                temp_file.write(installer_content)
                temp_file_path = temp_file.name
            
            try:
                # Use translator to parse the installer
                recipe = self.translator.parse_file(temp_file_path)
                
                # Analyze recipe for dependencies
                python_packages = set()
                system_packages = set()
                
                for step in recipe:
                    if step.get('step_type') == 'shell' and 'params' in step:
                        command = step['params'].get('command', '')
                        
                        # Check for Python packages
                        for pattern in self.python_package_patterns:
                            matches = re.findall(pattern, command, re.IGNORECASE)
                            for match in matches:
                                # Clean up package names (remove flags, etc.)
                                clean_match = re.split(r'[\s\-\=]', match)[0]
                                if clean_match:
                                    python_packages.add(clean_match)
                        
                        # Check for system packages
                        for pattern in self.system_package_patterns:
                            matches = re.findall(pattern, command, re.IGNORECASE)
                            for match in matches:
                                # Clean up package names
                                clean_match = re.split(r'[\s\-\=]', match)[0]
                                if clean_match:
                                    system_packages.add(clean_match)
                
                dependencies = {
                    "python_packages": sorted(list(python_packages)),
                    "system_packages": sorted(list(system_packages)),
                    "total_dependencies": len(python_packages) + len(system_packages)
                }
                
                logger.debug(f"Found {len(python_packages)} Python packages and {len(system_packages)} system packages")
                return dependencies, recipe
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Dependency checking failed: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to check dependencies for {install_url}: {str(e)}") from e
    
    def _estimate_resources(self, app_data: Dict[str, Any], recipe: List[Dict]) -> Dict[str, Any]:
        """
        Estimate resource requirements based on app metadata and recipe.
        
        Args:
            app_data: Application metadata dictionary
            recipe: Parsed installation recipe
            
        Returns:
            Dictionary with resource estimates
        """
        try:
            logger.debug("Estimating resource requirements")
            
            # Initialize estimates
            estimates = {
                "gpu_required": app_data.get('gpu_required', False),
                "estimated_ram_gb": 4,  # Default baseline
                "estimated_disk_mb": app_data.get('install_size_mb', 1000),
                "high_intensity_indicators": []
            }
            
            # Analyze description and tags for resource hints
            description = app_data.get('description', '').lower()
            tags = [tag.lower() for tag in app_data.get('tags', [])]
            all_text = f"{description} {' '.join(tags)}"
            
            # Check for high memory indicators
            for keyword in self.high_memory_keywords:
                if keyword in all_text:
                    estimates["estimated_ram_gb"] = max(estimates["estimated_ram_gb"], 16)
                    estimates["high_intensity_indicators"].append(f"high_memory_keyword:{keyword}")
            
            # Check for high disk indicators
            for keyword in self.high_disk_keywords:
                if keyword in all_text:
                    estimates["estimated_disk_mb"] = max(estimates["estimated_disk_mb"], 5000)
                    estimates["high_intensity_indicators"].append(f"high_disk_keyword:{keyword}")
            
            # Analyze recipe for additional resource hints
            for step in recipe:
                if step.get('step_type') == 'shell' and 'params' in step:
                    command = step['params'].get('command', '').lower()
                    
                    # Check for large downloads or model operations
                    if any(keyword in command for keyword in self.high_disk_keywords):
                        estimates["estimated_disk_mb"] = max(estimates["estimated_disk_mb"], 10000)
                    
                    # Check for GPU-specific commands
                    if 'cuda' in command or 'nvidia' in command:
                        estimates["gpu_required"] = True
            
            logger.debug(f"Resource estimates: {estimates}")
            return estimates
            
        except Exception as e:
            logger.error(f"Resource estimation failed: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to estimate resources: {str(e)}") from e
    
    def _validate_installer(self, install_url: str) -> Dict[str, Any]:
        """
        Perform basic validation checks on the installer URL.
        
        Args:
            install_url: URL to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            logger.debug(f"Validating installer URL: {install_url}")
            
            validation_result = {
                "installer_url_accessible": False,
                "installer_type_supported": False,
                "issues": []
            }
            
            # Check file extension support
            file_extension = self._get_file_extension(install_url)
            if file_extension not in self.supported_installer_types:
                validation_result["issues"].append(f"Unsupported file type: {file_extension}")
            else:
                validation_result["installer_type_supported"] = True
            
            # Check URL accessibility with HEAD request
            try:
                response = requests.head(install_url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    validation_result["installer_url_accessible"] = True
                else:
                    validation_result["issues"].append(f"URL returned status code: {response.status_code}")
            except requests.RequestException as e:
                validation_result["issues"].append(f"URL accessibility check failed: {str(e)}")
            
            logger.debug(f"Installer validation result: {validation_result}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Installer validation failed: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to validate installer {install_url}: {str(e)}") from e
    
    def _get_file_extension(self, url: str) -> str:
        """
        Extract file extension from URL.
        
        Args:
            url: URL to extract extension from
            
        Returns:
            File extension including dot (e.g., '.js')
        """
        try:
            # Extract filename from URL
            filename = url.split('/')[-1].split('?')[0]
            # Get extension
            if '.' in filename:
                return f".{filename.split('.')[-1].lower()}"
            return '.txt'  # Default extension
        except Exception:
            return '.txt'
    
    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp in ISO format.
        
        Returns:
            Current timestamp string
        """
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _determine_overall_status(self, installer_validation: Dict, dependencies: Dict, resource_estimates: Dict) -> str:
        """
        Determine overall analysis status based on component results.
        
        Args:
            installer_validation: Installer validation results
            dependencies: Dependency analysis results
            resource_estimates: Resource estimation results
            
        Returns:
            Overall status string ('ready', 'warning', 'error')
        """
        try:
            # Check for critical errors
            if not installer_validation.get("installer_url_accessible", False):
                return "error"
            
            if "error" in dependencies:
                return "error"
            
            # Check for warnings
            if installer_validation.get("issues"):
                return "warning"
            
            if resource_estimates.get("high_intensity_indicators"):
                return "warning"
            
            # If all checks pass
            return "ready"
            
        except Exception as e:
            logger.error(f"Status determination failed: {str(e)}")
            return "error"