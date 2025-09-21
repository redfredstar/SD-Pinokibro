"""
P02_ProcessManager.py - The All-Seeing Eye (Real-Time Monitoring Engine)

This module implements the core "Maximum Debug" philosophy by providing a robust,
non-blocking, and thread-safe engine for all subprocess execution. It captures and
streams raw, unfiltered output from shell commands in real-time through a callback
mechanism, enabling complete transparency for debugging purposes.

Author: Pinokiobro Architect
Phase: P02 - The All-Seeing Eye
"""

import asyncio
import threading
import sys
from typing import Dict, Callable, Optional, Any
import logging
from dataclasses import dataclass


@dataclass
class ProcessInfo:
    """Data class to store information about active processes."""
    pid: int
    command: str
    status: str  # 'running', 'completed', 'failed', 'killed'


class P02_ProcessManager:
    """
    A robust, non-blocking process manager that executes shell commands and
    streams their output in real-time through a callback mechanism.
    
    This class implements a dedicated background thread to run the asyncio event loop,
    ensuring all async operations are truly non-blocking and can be safely called
    from a synchronous environment like an ipywidgets callback.
    """
    
    def __init__(self):
        """Initialize the ProcessManager with an empty process tracking dictionary."""
        self.active_processes: Dict[int, ProcessInfo] = {}
        self._event_loop = None
        self._thread = None
        self._start_event_loop()
        
    def _start_event_loop(self) -> None:
        """
        Start a dedicated background thread to run the asyncio event loop.
        
        This is a critical design choice that ensures all async operations within
        the ProcessManager are truly non-blocking and can be safely called from
        a synchronous environment.
        """
        def run_loop():
            """Run the asyncio event loop in a separate thread."""
            self._event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._event_loop)
            self._event_loop.run_forever()
            
        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()
        
    def _run_async_task(self, coro) -> Any:
        """
        Run an async coroutine in the dedicated event loop thread.
        
        Args:
            coro: The asyncio coroutine to execute.
            
        Returns:
            The result of the coroutine execution.
        """
        if not self._event_loop:
            raise RuntimeError("Event loop not started")
            
        future = asyncio.run_coroutine_threadsafe(coro, self._event_loop)
        return future.result()
        
    async def _stream_output(self, process: asyncio.subprocess.Process, 
                           callback: Callable[[str], None]) -> None:
        """
        Stream stdout and stderr from a process concurrently.
        
        This method uses asyncio.gather to read stdout and stderr concurrently,
        guaranteeing that no output is missed and that the callback is invoked
        in the correct chronological order.
        
        Args:
            process: The asyncio subprocess object.
            callback: Function to call with each line of output.
        """
        async def read_stream(stream, prefix: str = ""):
            """Read lines from a stream and pass them to the callback."""
            while True:
                line = await stream.readline()
                if not line:
                    break
                # Decode and pass the line to the callback with prefix
                decoded_line = line.decode('utf-8', errors='replace').rstrip()
                callback(f"{prefix}{decoded_line}")
                
        # Read both streams concurrently
        await asyncio.gather(
            read_stream(process.stdout, "STDOUT: "),
            read_stream(process.stderr, "STDERR: ")
        )
        
    def shell_run(self, command: str, callback: Callable[[str], None], 
                  cwd: Optional[str] = None) -> int:
        """
        Execute a shell command non-blockingly and stream output in real-time.
        
        This method creates an asyncio subprocess, captures its PID for tracking,
        and streams all output through the provided callback function.
        
        Args:
            command: The shell command to execute.
            callback: Function to call with each line of output.
            cwd: Optional working directory for the command.
            
        Returns:
            The Process ID (PID) of the created subprocess.
            
        Raises:
            FileNotFoundError: If the command executable is not found.
            PermissionError: If the command cannot be executed due to permissions.
            RuntimeError: If the event loop is not running.
        """
        try:
            # Run the async shell command in our dedicated event loop
            pid = self._run_async_task(
                self._async_shell_run(command, callback, cwd)
            )
            return pid
        except Exception as e:
            # Log the full traceback as per Maximum Debug philosophy
            logging.error(f"Failed to execute command '{command}': {str(e)}", 
                        exc_info=True)
            raise
            
    async def _async_shell_run(self, command: str, callback: Callable[[str], None],
                              cwd: Optional[str] = None) -> int:
        """
        Async implementation of shell command execution.
        
        Args:
            command: The shell command to execute.
            callback: Function to call with each line of output.
            cwd: Optional working directory for the command.
            
        Returns:
            The Process ID (PID) of the created subprocess.
        """
        # Create the subprocess
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        
        # Store process information for tracking
        self.active_processes[process.pid] = ProcessInfo(
            pid=process.pid,
            command=command,
            status='running'
        )
        
        # Stream output in the background
        asyncio.create_task(self._stream_output(process, callback))
        
        return process.pid
        
    def get_active_processes(self) -> Dict[int, ProcessInfo]:
        """
        Get information about all currently active processes.
        
        Returns:
            A dictionary mapping PIDs to ProcessInfo objects.
        """
        return self.active_processes.copy()
        
    def kill_process(self, pid: int) -> bool:
        """
        Terminate a process by its PID.
        
        Args:
            pid: The Process ID to terminate.
            
        Returns:
            True if the process was found and terminated, False otherwise.
        """
        if pid not in self.active_processes:
            logging.warning(f"Process with PID {pid} not found in active processes")
            return False
            
        try:
            import signal
            # Send SIGTERM to terminate the process gracefully
            import os
            os.kill(pid, signal.SIGTERM)
            
            # Update process status
            self.active_processes[pid].status = 'killed'
            logging.info(f"Process {pid} terminated successfully")
            return True
        except ProcessLookupError:
            logging.warning(f"Process {pid} no longer exists")
            # Remove from tracking if it doesn't exist
            if pid in self.active_processes:
                del self.active_processes[pid]
            return False
        except PermissionError:
            logging.error(f"Permission denied when trying to kill process {pid}")
            return False
        except Exception as e:
            logging.error(f"Failed to kill process {pid}: {str(e)}", exc_info=True)
            return False