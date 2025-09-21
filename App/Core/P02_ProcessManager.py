"""
app/core/P02_ProcessManager.py
Real-Time Process Execution Engine

Implements the "Maximum Debug" philosophy through non-blocking process execution
with real-time callback streaming. Built on asyncio for concurrency with thread-safe
PID management.
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass, field
import threading
import signal
import os


@dataclass
class ProcessInfo:
    """Container for process metadata and state."""

    pid: int
    command: str
    start_time: datetime
    process_obj: asyncio.subprocess.Process
    status: str = "running"  # "running", "completed", "failed", "killed"
    exit_code: Optional[int] = None
    cwd: Optional[str] = None


class P02_ProcessManager:
    """
    Manages asynchronous subprocess execution with real-time output streaming.

    Core features:
    - Non-blocking command execution using asyncio
    - Real-time stdout/stderr streaming via callbacks
    - Thread-safe PID tracking and management
    - Graceful and forced process termination
    """

    def __init__(self):
        """Initialize the ProcessManager with empty state tracking."""
        self._active_processes: Dict[str, ProcessInfo] = {}
        self._process_lock = threading.Lock()
        self._pid_counter = 0
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._executor_thread: Optional[threading.Thread] = None
        self._initialize_event_loop()

    def _initialize_event_loop(self):
        """Set up the asyncio event loop in a dedicated thread."""

        def run_loop():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_forever()

        self._executor_thread = threading.Thread(target=run_loop, daemon=True)
        self._executor_thread.start()

        # Wait for loop initialization
        while self._loop is None:
            asyncio.sleep(0.01)

    def shell_run(
        self,
        command: str,
        callback: Callable[[str], None],
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> int:
        """
        Execute a shell command with real-time output streaming.

        Args:
            command: Shell command to execute
            callback: Function called for each line of output
            cwd: Working directory for command execution
            env: Environment variables for the process

        Returns:
            Exit code of the process (0 for success, non-zero for failure)
        """
        # Run the async method in the dedicated event loop
        future = asyncio.run_coroutine_threadsafe(
            self._async_shell_run(command, callback, cwd, env), self._loop
        )
        return future.result()

    async def _async_shell_run(
        self,
        command: str,
        callback: Callable[[str], None],
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> int:
        """Async implementation of shell_run."""
        # Generate unique process identifier
        with self._process_lock:
            process_id = f"process_{self._pid_counter:03d}"
            self._pid_counter += 1

        # Prepare environment
        if env is not None:
            process_env = os.environ.copy()
            process_env.update(env)
        else:
            process_env = None

        try:
            # Create subprocess
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=process_env,
            )

            # Store process info
            process_info = ProcessInfo(
                pid=process.pid,
                command=command,
                start_time=datetime.now(),
                process_obj=process,
                status="running",
                cwd=cwd,
            )

            with self._process_lock:
                self._active_processes[process_id] = process_info

            # Stream output
            streaming_task = asyncio.create_task(self._stream_output(process, callback))

            # Wait for completion
            exit_code = await process.wait()
            await streaming_task

            # Update process status
            with self._process_lock:
                self._active_processes[process_id].status = (
                    "completed" if exit_code == 0 else "failed"
                )
                self._active_processes[process_id].exit_code = exit_code

            return exit_code

        except FileNotFoundError as e:
            callback(f"[ERROR] Command not found: {command}")
            callback(f"[ERROR] {str(e)}")
            with self._process_lock:
                if process_id in self._active_processes:
                    self._active_processes[process_id].status = "failed"
                    self._active_processes[process_id].exit_code = -1
            return -1

        except PermissionError as e:
            callback(f"[ERROR] Permission denied: {command}")
            callback(f"[ERROR] {str(e)}")
            with self._process_lock:
                if process_id in self._active_processes:
                    self._active_processes[process_id].status = "failed"
                    self._active_processes[process_id].exit_code = -1
            return -1

        except Exception as e:
            callback(f"[ERROR] Unexpected error executing command: {command}")
            callback(f"[ERROR] {type(e).__name__}: {str(e)}")
            with self._process_lock:
                if process_id in self._active_processes:
                    self._active_processes[process_id].status = "failed"
                    self._active_processes[process_id].exit_code = -1
            return -1

    async def _stream_output(
        self, process: asyncio.subprocess.Process, callback: Callable[[str], None]
    ):
        """
        Stream output from both stdout and stderr concurrently.

        Args:
            process: The subprocess to stream from
            callback: Function to call with each line of output
        """

        async def read_stream(stream, stream_name: str):
            """Read from a single stream and callback each line."""
            if stream is None:
                return

            try:
                while True:
                    line = await stream.readline()
                    if not line:
                        break

                    # Decode and clean the line
                    decoded_line = line.decode("utf-8", errors="replace").rstrip("\n\r")

                    # Prefix with stream type
                    prefixed_line = f"[{stream_name}] {decoded_line}"

                    # Invoke callback immediately
                    callback(prefixed_line)

            except Exception as e:
                callback(f"[{stream_name}] Stream error: {str(e)}")

        # Launch both stream readers concurrently
        await asyncio.gather(
            read_stream(process.stdout, "stdout"),
            read_stream(process.stderr, "stderr"),
            return_exceptions=True,
        )

    def get_active_processes(self) -> Dict[str, int]:
        """
        Get a snapshot of currently running processes.

        Returns:
            Dictionary mapping process IDs to PIDs
        """
        with self._process_lock:
            return {
                proc_id: proc_info.pid
                for proc_id, proc_info in self._active_processes.items()
                if proc_info.status == "running"
            }

    def get_all_processes(self) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed information about all tracked processes.

        Returns:
            Dictionary with full process information
        """
        with self._process_lock:
            result = {}
            for proc_id, proc_info in self._active_processes.items():
                result[proc_id] = {
                    "pid": proc_info.pid,
                    "command": proc_info.command,
                    "status": proc_info.status,
                    "start_time": proc_info.start_time.isoformat(),
                    "exit_code": proc_info.exit_code,
                    "cwd": proc_info.cwd,
                }
            return result

    def kill_process(self, pid: int) -> bool:
        """
        Terminate a process by PID.

        Args:
            pid: Process ID to terminate

        Returns:
            True if process was successfully terminated, False otherwise
        """
        future = asyncio.run_coroutine_threadsafe(
            self._async_kill_process(pid), self._loop
        )
        return future.result()

    async def _async_kill_process(self, pid: int) -> bool:
        """Async implementation of kill_process."""
        target_process = None
        target_id = None

        with self._process_lock:
            for proc_id, proc_info in self._active_processes.items():
                if proc_info.pid == pid and proc_info.status == "running":
                    target_process = proc_info.process_obj
                    target_id = proc_id
                    break

        if not target_process:
            return False

        try:
            # Graceful termination
            target_process.terminate()

            # Wait up to 5 seconds for graceful shutdown
            try:
                await asyncio.wait_for(target_process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                # Force kill if graceful termination failed
                target_process.kill()
                await target_process.wait()

            # Update status
            with self._process_lock:
                if target_id in self._active_processes:
                    self._active_processes[target_id].status = "killed"

            return True

        except ProcessLookupError:
            # Process already dead
            with self._process_lock:
                if target_id in self._active_processes:
                    self._active_processes[target_id].status = "killed"
            return True

        except Exception:
            return False

    def cleanup_completed_processes(self):
        """Remove completed/failed/killed processes from tracking."""
        with self._process_lock:
            to_remove = [
                proc_id
                for proc_id, proc_info in self._active_processes.items()
                if proc_info.status in ["completed", "failed", "killed"]
            ]
            for proc_id in to_remove:
                del self._active_processes[proc_id]

    def shutdown(self):
        """Clean shutdown of the ProcessManager."""
        if self._loop and self._loop.is_running():
            # Kill all active processes
            active_pids = list(self.get_active_processes().values())
            for pid in active_pids:
                self.kill_process(pid)

            # Stop the event loop
            self._loop.call_soon_threadsafe(self._loop.stop)
            if self._executor_thread:
                self._executor_thread.join(timeout=5)

    def __del__(self):
        """Ensure cleanup on deletion."""
        self.shutdown()
