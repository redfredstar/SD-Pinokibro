"""
P14_WebUIDetector.py - The Web UI Detection Engine

Phase P14 of the PinokioCloud Rebuild Project
Objective: Provide robust pattern matching for detecting web UI startup messages
and extracting local URLs from application logs across diverse web frameworks.

This module implements the core WebUI detection functionality that scans real-time
application output to identify when web interfaces become available and extract
their local URLs for tunneling purposes.
"""

import re
import traceback
from typing import List, Optional, Pattern


class P14_WebUIDetector:
    """
    Specialized utility class for detecting web UI startup patterns in application logs.

    This class maintains a comprehensive library of regex patterns designed to match
    startup messages from various web frameworks and extract local URLs. It provides
    the core functionality for the dual-purpose callback architecture in P13_LaunchManager.

    The detector supports detection of common frameworks including:
    - Gradio (gradio.app, share links)
    - Flask (development server, Werkzeug)
    - FastAPI (uvicorn, hypercorn)
    - ComfyUI (custom startup messages)
    - Streamlit (for future reference)
    - Generic HTTP servers (various formats)

    All patterns are pre-compiled for optimal performance during real-time log processing.
    """

    def __init__(self) -> None:
        """
        Initialize the WebUI detector with comprehensive regex pattern library.

        Creates and compiles a diverse set of regex patterns designed to match
        common web server startup messages across different frameworks. Each
        pattern includes named capture groups for extracting the URL component.

        The patterns are organized by framework and include variations for:
        - Different URL formats (http/https, localhost/127.0.0.1)
        - Various port number formats
        - Framework-specific startup messages
        - IPv4 and IPv6 address formats
        """
        self.url_patterns: List[Pattern[str]] = self._compile_detection_patterns()

    def _compile_detection_patterns(self) -> List[Pattern[str]]:
        """
        Compile comprehensive regex patterns for web UI detection.

        Returns:
            List[Pattern[str]]: List of compiled regex patterns for URL detection

        Raises:
            Exception: If pattern compilation fails with full traceback
        """
        try:
            patterns = [
                # Gradio patterns
                re.compile(
                    r'Running on local URL:\s+(?P<url>https?://(?:localhost|127\.0\.0\.1|\[::\]):(?:\d+))',
                    re.IGNORECASE
                ),
                re.compile(
                    r'gradio\.app.*sharing.*(?P<url>https?://[^\s]+)',
                    re.IGNORECASE
                ),

                # Flask/Werkzeug patterns
                re.compile(
                    r'Running on (?P<url>https?://(?:localhost|127\.0\.0\.1|\[::\]):(?:\d+))',
                    re.IGNORECASE
                ),
                re.compile(
                    r'Werkzeug.*development server.*running.*(?P<url>https?://[^\s]+)',
                    re.IGNORECASE
                ),

                # FastAPI/Uvicorn patterns
                re.compile(
                    r'Uvicorn running on (?P<url>https?://(?:localhost|127\.0\.0\.1|\[::\]):(?:\d+))',
                    re.IGNORECASE
                ),
                re.compile(
                    r'INFO.*Uvicorn.*started server.*url.*(?P<url>https?://[^\s]+)',
                    re.IGNORECASE
                ),

                # ComfyUI patterns
                re.compile(
                    r'Starting server.*(?P<url>https?://(?:localhost|127\.0\.0\.1):(?:\d+))',
                    re.IGNORECASE
                ),
                re.compile(
                    r'To see the GUI go to:\s+(?P<url>https?://[^\s]+)',
                    re.IGNORECASE
                ),

                # Generic HTTP server patterns
                re.compile(
                    r'Server started.*(?P<url>https?://(?:localhost|127\.0\.0\.1|\[::\]):(?:\d+))',
                    re.IGNORECASE
                ),
                re.compile(
                    r'Local server running at.*(?P<url>https?://[^\s]+)',
                    re.IGNORECASE
                ),

                # IPv6 and alternative localhost patterns
                re.compile(
                    r'https?://(?:localhost|127\.0\.0\.1|\[::\]|\[::1\]):(?:\d+)(?:/[^\s]*)?',
                    re.IGNORECASE
                ),

                # Generic URL pattern for various frameworks
                re.compile(
                    r'(?P<url>https?://(?:localhost|127\.0\.0\.1|\[::\]|(?:\d+\.){3}\d+):(?:\d+))',
                    re.IGNORECASE
                ),

                # Streamlit patterns (for future reference)
                re.compile(
                    r'You can now view your Streamlit app.*(?P<url>https?://[^\s]+)',
                    re.IGNORECASE
                ),
                re.compile(
                    r'Local URL:\s+(?P<url>https?://[^\s]+)',
                    re.IGNORECASE
                ),

                # Jupyter server patterns
                re.compile(
                    r'Jupyter Server.*running.*(?P<url>https?://[^\s]+)',
                    re.IGNORECASE
                ),

                # Generic development server patterns
                re.compile(
                    r'Dev server.*listening.*(?P<url>https?://[^\s]+)',
                    re.IGNORECASE
                ),
                re.compile(
                    r'Application startup complete.*(?P<url>https?://[^\s]+)',
                    re.IGNORECASE
                )
            ]

            return patterns

        except Exception as e:
            raise Exception(f"Failed to compile WebUI detection patterns: "
                          f"{str(e)}\n{traceback.format_exc()}")

    def find_url(self, log_line: str) -> Optional[str]:
        """
        Scan a log line for web UI startup URLs using comprehensive pattern matching.

        Iterates through the compiled regex pattern library to detect web UI startup
        messages and extract local URLs. This method is designed for real-time log
        processing and provides robust matching across diverse web frameworks.

        Args:
            log_line: Single line of application log output to analyze

        Returns:
            Optional[str]: Extracted local URL if found, None otherwise

        Raises:
            Exception: If pattern matching fails with full traceback
        """
        try:
            if not isinstance(log_line, str):
                raise ValueError(f"Log line must be a string, got {type(log_line)}")

            # Test each pattern against the log line
            for pattern in self.url_patterns:
                match = pattern.search(log_line)
                if match:
                    url = match.group('url') if 'url' in match.groupdict() else match.group(0)
                    if url:
                        # Validate URL format
                        if self._is_valid_local_url(url):
                            return url.strip()

            return None

        except Exception as e:
            raise Exception(f"Failed to scan log line for URLs: "
                          f"{str(e)}\n{traceback.format_exc()}")

    def _is_valid_local_url(self, url: str) -> bool:
        """
        Validate that a detected URL is a local/private address.

        Ensures the detected URL is safe for tunneling by verifying it's a
        local/private address that won't conflict with public services.

        Args:
            url: URL string to validate

        Returns:
            bool: True if URL is local/private, False otherwise
        """
        try:
            if not url.startswith(('http://', 'https://')):
                return False

            # Extract hostname part
            hostname = url.split('://')[1].split(':')[0].split('/')[0]

            # Check for local/private addresses
            local_patterns = [
                'localhost',
                '127.0.0.1',
                '::1',
                '[::]',
                '0.0.0.0'
            ]

            return hostname.lower() in local_patterns

        except Exception:
            # If parsing fails, err on side of caution
            return False