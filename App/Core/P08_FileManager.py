"""
P08_FileManager.py - The File Operations Engine

Phase P08 of the PinokioCloud Rebuild Project
Objective: Provide robust, production-grade implementations of all fs.* 
file operations from the Pinokio API with comprehensive error handling.

This module implements all file system operations required by Pinokio applications
including downloads with progress tracking, atomic file operations, and 
comprehensive error handling with full traceback reporting.
"""

import os
import shutil
import traceback
import tempfile
from pathlib import Path
from typing import Callable, Optional
import requests
from urllib.parse import urlparse


class P08_FileManager:
    """
    Production-grade file operations manager for the PinokioCloud project.
    
    This class provides complete implementations of all file system operations
    required by the Pinokio API (fs.*). All operations include robust error
    handling with full traceback reporting and atomic operation guarantees
    where appropriate.
    
    The manager handles:
    - Downloads with progress tracking and error handling
    - Atomic file write operations with directory creation
    - File and directory copying with preservation of metadata
    - Safe file and directory deletion
    - Symbolic link creation with error handling
    """

    def __init__(self, path_mapper):
        """
        Initialize the P08_FileManager with path resolution capability.
        
        Args:
            path_mapper: P01_PathMapper instance for platform-agnostic path resolution
            
        The constructor uses dependency injection to ensure path operations
        are portable across different cloud environments.
        """
        self.path_mapper = path_mapper

    def download(self, uri: str, dest_dir: Path, 
                callback: Callable[[str], None]) -> Path:
        """
        Download a file from a URI to a destination directory with progress tracking.
        
        This method downloads files using the requests library with streaming
        enabled for memory efficiency. Progress is reported via callback and
        all HTTP errors are handled gracefully with full error reporting.
        
        Args:
            uri: URL of the file to download
            dest_dir: Destination directory for the downloaded file
            callback: Function to receive progress and status updates
            
        Returns:
            Path: The full path to the downloaded file
            
        Raises:
            Exception: Re-raises all exceptions with full tracebacks for debugging
        """
        callback(f"[P08_FileManager] Starting download from: {uri}")
        
        try:
            # Parse filename from URI
            parsed_uri = urlparse(uri)
            filename = Path(parsed_uri.path).name
            if not filename:
                filename = "downloaded_file"
                
            dest_path = Path(dest_dir) / filename
            callback(f"[P08_FileManager] Download destination: {dest_path}")
            
            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Perform download with streaming
            response = requests.get(uri, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get file size for progress tracking
            total_size = int(response.headers.get('content-length', 0))
            callback(f"[P08_FileManager] File size: {total_size} bytes")
            
            # Download with progress reporting
            downloaded_size = 0
            with open(dest_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            callback(f"[P08_FileManager] Progress: {progress:.1f}% "
                                   f"({downloaded_size}/{total_size} bytes)")
            
            callback(f"[P08_FileManager] Download completed successfully: {dest_path}")
            return dest_path
            
        except requests.exceptions.RequestException as e:
            callback(f"[P08_FileManager] HTTP/Network error during download:")
            callback(f"[P08_FileManager] {traceback.format_exc()}")
            raise
        except Exception as e:
            callback(f"[P08_FileManager] Download operation FAILED:")
            callback(f"[P08_FileManager] {traceback.format_exc()}")
            raise

    def write(self, path: Path, content: str) -> None:
        """
        Write string content to a file with atomic operation guarantees.
        
        This method ensures atomic file writes by writing to a temporary file
        first and then moving it to the final destination. Parent directories
        are created as needed and all filesystem errors are handled with
        full error reporting.
        
        Args:
            path: Target file path for writing content
            content: String content to write to the file
            
        Raises:
            Exception: Re-raises all exceptions with full tracebacks for debugging
        """
        try:
            target_path = Path(path)
            
            # Ensure parent directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Atomic write using temporary file
            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode='w', 
                    dir=target_path.parent,
                    delete=False,
                    encoding='utf-8'
                ) as temp_file:
                    temp_path = Path(temp_file.name)
                    temp_file.write(content)
                    temp_file.flush()
                    os.fsync(temp_file.fileno())
                
                # Atomic move to final destination
                temp_path.replace(target_path)
                
            except Exception as e:
                # Clean up temporary file on error
                if temp_path and temp_path.exists():
                    temp_path.unlink()
                raise
                
        except Exception as e:
            raise Exception(f"File write operation failed for {path}: "
                          f"{str(e)}\n{traceback.format_exc()}")

    def copy(self, src: Path, dest: Path) -> None:
        """
        Copy a file or recursively copy a directory with metadata preservation.
        
        This method handles both file and directory copying using the appropriate
        shutil functions. Metadata (timestamps, permissions) is preserved and
        all filesystem errors are handled with comprehensive error reporting.
        
        Args:
            src: Source file or directory path
            dest: Destination file or directory path
            
        Raises:
            Exception: Re-raises all exceptions with full tracebacks for debugging
        """
        try:
            src_path = Path(src)
            dest_path = Path(dest)
            
            if not src_path.exists():
                raise FileNotFoundError(f"Source path does not exist: {src_path}")
            
            # Ensure destination parent directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if src_path.is_file():
                # Copy file with metadata preservation
                shutil.copy2(src_path, dest_path)
            elif src_path.is_dir():
                # Recursive directory copy
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.copytree(src_path, dest_path)
            else:
                raise ValueError(f"Source is neither file nor directory: {src_path}")
                
        except Exception as e:
            raise Exception(f"Copy operation failed from {src} to {dest}: "
                          f"{str(e)}\n{traceback.format_exc()}")

    def rm(self, path: Path) -> None:
        """
        Delete a file or recursively delete a directory.
        
        This method safely removes files using os.remove and directories
        using shutil.rmtree. Non-existent paths are handled gracefully
        and all filesystem errors include full error reporting.
        
        Args:
            path: Path to file or directory to delete
            
        Raises:
            Exception: Re-raises all exceptions with full tracebacks for debugging
        """
        try:
            target_path = Path(path)
            
            if not target_path.exists():
                # Silently succeed if path doesn't exist (idempotent operation)
                return
            
            if target_path.is_file() or target_path.is_symlink():
                # Remove file or symbolic link
                os.remove(target_path)
            elif target_path.is_dir():
                # Recursively remove directory
                shutil.rmtree(target_path)
            else:
                raise ValueError(f"Path is neither file nor directory: {target_path}")
                
        except Exception as e:
            raise Exception(f"Remove operation failed for {path}: "
                          f"{str(e)}\n{traceback.format_exc()}")

    def link(self, src: Path, dest: Path) -> None:
        """
        Create a symbolic link from dest pointing to src.
        
        This method creates symbolic links using os.symlink with proper
        error handling for platform compatibility and permission issues.
        Parent directories are created as needed.
        
        Args:
            src: Source path that the link will point to
            dest: Destination path where the link will be created
            
        Raises:
            Exception: Re-raises all exceptions with full tracebacks for debugging
        """
        try:
            src_path = Path(src)
            dest_path = Path(dest)
            
            # Ensure destination parent directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Remove existing link/file at destination if it exists
            if dest_path.exists() or dest_path.is_symlink():
                dest_path.unlink()
            
            # Create symbolic link
            os.symlink(src_path, dest_path)
            
        except Exception as e:
            raise Exception(f"Link creation failed from {src} to {dest}: "
                          f"{str(e)}\n{traceback.format_exc()}")

    def mkdir(self, path: Path, parents: bool = True) -> None:
        """
        Create a directory with optional parent directory creation.
        
        This method creates directories using pathlib with robust error
        handling. The parents parameter controls whether parent directories
        are created automatically.
        
        Args:
            path: Directory path to create
            parents: Whether to create parent directories if they don't exist
            
        Raises:
            Exception: Re-raises all exceptions with full tracebacks for debugging
        """
        try:
            target_path = Path(path)
            target_path.mkdir(parents=parents, exist_ok=True)
            
        except Exception as e:
            raise Exception(f"Directory creation failed for {path}: "
                          f"{str(e)}\n{traceback.format_exc()}")

    def exists(self, path: Path) -> bool:
        """
        Check if a file or directory exists at the given path.
        
        This method provides a simple existence check with error handling
        for permission and filesystem access issues.
        
        Args:
            path: Path to check for existence
            
        Returns:
            bool: True if path exists, False otherwise
            
        Raises:
            Exception: Re-raises all exceptions with full tracebacks for debugging
        """
        try:
            return Path(path).exists()
            
        except Exception as e:
            raise Exception(f"Existence check failed for {path}: "
                          f"{str(e)}\n{traceback.format_exc()}")