"""Terminal tools for executing commands."""

import logging
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from myagent.config import get_settings

logger = logging.getLogger(__name__)

# Dangerous commands that should require confirmation
DANGEROUS_COMMANDS = {
    # Deletion
    "rm",
    "rmdir",
    "del",
    "rd",
    "Remove-Item",
    # Disk operations
    "format",
    "mkfs",
    "dd",
    # System
    "shutdown",
    "reboot",
    "poweroff",
    "halt",
    # Git destructive
    "git reset --hard",
    "git clean",
    "git push --force",
    # Database
    "DROP DATABASE",
    "DROP TABLE",
    "TRUNCATE",
}


def is_dangerous_command(command: str) -> bool:
    """
    Check if a command is potentially dangerous.

    Args:
        command: Command string to check

    Returns:
        True if command is considered dangerous
    """
    command_lower = command.lower()

    # Check for exact matches and substrings
    for dangerous in DANGEROUS_COMMANDS:
        if dangerous.lower() in command_lower:
            return True

    # Check for force flags
    if any(flag in command_lower for flag in ["-f ", "--force", "/f"]):
        if any(cmd in command_lower for cmd in ["rm", "del", "remove"]):
            return True

    return False


class TerminalTools:
    """Terminal command execution tools."""

    def __init__(self, workspace_dir: Path):
        """
        Initialize terminal tools.

        Args:
            workspace_dir: Root directory for command execution
        """
        self.workspace_dir = workspace_dir.resolve()
        settings = get_settings()
        self.default_timeout = settings.myagent_command_timeout
        logger.info(f"Terminal tools initialized: timeout={self.default_timeout}s")

    def run_command(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: Optional[int] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a shell command.

        Args:
            command: Command to execute
            cwd: Working directory (relative to workspace or absolute)
            timeout: Timeout in seconds (uses default if not specified)
            env: Environment variables to set

        Returns:
            Dict with stdout, stderr, exit_code, duration
        """
        try:
            # Determine working directory
            if cwd:
                if Path(cwd).is_absolute():
                    work_dir = Path(cwd).resolve()
                else:
                    work_dir = (self.workspace_dir / cwd).resolve()

                # Validate within workspace
                if not str(work_dir).startswith(str(self.workspace_dir)):
                    return {"error": "Working directory outside workspace", "success": False}
            else:
                work_dir = self.workspace_dir

            if not work_dir.exists():
                return {"error": f"Working directory not found: {cwd}", "success": False}

            # Use configured timeout if not specified
            cmd_timeout = timeout if timeout is not None else self.default_timeout

            # Prepare environment
            import os

            cmd_env = os.environ.copy()
            if env:
                cmd_env.update(env)

            logger.info(f"Executing command: {command[:100]}...")
            start_time = time.time()

            # Execute command using PowerShell on Windows
            import platform

            if platform.system() == "Windows":
                # Use PowerShell for better Windows compatibility
                result = subprocess.run(
                    ["powershell", "-Command", command],
                    capture_output=True,
                    text=True,
                    timeout=cmd_timeout,
                    cwd=work_dir,
                    env=cmd_env,
                )
            else:
                # Use shell on Unix-like systems
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=cmd_timeout,
                    cwd=work_dir,
                    env=cmd_env,
                )

            duration = time.time() - start_time

            # Truncate very long output
            max_output_length = 10000
            stdout = result.stdout
            stderr = result.stderr

            if len(stdout) > max_output_length:
                stdout = stdout[:max_output_length] + f"\n\n[truncated: {len(stdout)} total chars]"
            if len(stderr) > max_output_length:
                stderr = stderr[:max_output_length] + f"\n\n[truncated: {len(stderr)} total chars]"

            return {
                "success": result.returncode == 0,
                "command": command,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": result.returncode,
                "duration": round(duration, 2),
            }

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            logger.warning(f"Command timed out after {cmd_timeout}s: {command[:100]}")
            return {
                "success": False,
                "error": f"Command timed out after {cmd_timeout} seconds",
                "command": command,
                "duration": round(duration, 2),
            }

        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return {
                "success": False,
                "error": f"Command execution failed: {e}",
                "command": command,
            }

    def get_shell_info(self) -> Dict[str, str]:
        """
        Get information about the shell environment.

        Returns:
            Dict with shell type and platform info
        """
        import platform

        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
            "shell": "powershell" if platform.system() == "Windows" else "bash",
        }
