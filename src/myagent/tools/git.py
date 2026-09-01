"""Git integration tools."""

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class GitTools:
    """Git operations for the agent."""

    def __init__(self, workspace_dir: Path):
        """
        Initialize Git tools.

        Args:
            workspace_dir: Root directory for Git operations
        """
        self.workspace_dir = workspace_dir.resolve()
        self._has_git = self._check_git_available()
        self._is_git_repo = self._check_git_repo()
        logger.info(f"Git tools initialized: available={self._has_git}, repo={self._is_git_repo}")

    def _check_git_available(self) -> bool:
        """Check if git is available."""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _check_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        if not self._has_git:
            return False

        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=self.workspace_dir,
            )
            return result.returncode == 0
        except subprocess.SubprocessError:
            return False

    def _run_git_command(self, args: list, timeout: int = 30) -> Dict[str, Any]:
        """
        Run a git command.

        Args:
            args: Git command arguments
            timeout: Command timeout in seconds

        Returns:
            Dict with command results
        """
        if not self._has_git:
            return {
                "success": False,
                "error": "Git is not available on this system",
            }

        try:
            result = subprocess.run(
                ["git"] + args,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.workspace_dir,
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Git command timed out after {timeout} seconds",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Git command failed: {e}",
            }

    def git_status(self, short: bool = False) -> Dict[str, Any]:
        """
        Get git status.

        Args:
            short: Whether to use short format

        Returns:
            Dict with status information
        """
        if not self._has_git:
            return {
                "success": False,
                "error": "Git is not available on this system",
            }

        if not self._is_git_repo:
            return {
                "success": False,
                "error": "Not a git repository",
            }

        args = ["status"]
        if short:
            args.append("--short")

        result = self._run_git_command(args)

        if result["success"]:
            return {
                "success": True,
                "status": result["stdout"],
                "is_clean": len(result["stdout"].strip()) == 0 or "nothing to commit" in result["stdout"],
            }

        return result

    def git_diff(self, staged: bool = False, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Get git diff.

        Args:
            staged: Whether to show staged changes
            file_path: Optional specific file to diff

        Returns:
            Dict with diff information
        """
        if not self._has_git:
            return {
                "success": False,
                "error": "Git is not available on this system",
            }

        if not self._is_git_repo:
            return {
                "success": False,
                "error": "Not a git repository",
            }

        args = ["diff"]
        if staged:
            args.append("--cached")

        if file_path:
            args.append(file_path)

        result = self._run_git_command(args)

        if result["success"]:
            return {
                "success": True,
                "diff": result["stdout"],
                "has_changes": len(result["stdout"].strip()) > 0,
            }

        return result

    def git_log(self, max_count: int = 10, oneline: bool = True) -> Dict[str, Any]:
        """
        Get git log.

        Args:
            max_count: Maximum number of commits to show
            oneline: Whether to use oneline format

        Returns:
            Dict with log information
        """
        if not self._has_git:
            return {
                "success": False,
                "error": "Git is not available on this system",
            }

        if not self._is_git_repo:
            return {
                "success": False,
                "error": "Not a git repository",
            }

        args = ["log", f"--max-count={max_count}"]
        if oneline:
            args.append("--oneline")

        result = self._run_git_command(args)

        if result["success"]:
            commits = []
            for line in result["stdout"].strip().split("\n"):
                if line:
                    commits.append(line)

            return {
                "success": True,
                "commits": commits,
                "count": len(commits),
            }

        return result

    def git_branch(self, list_all: bool = False) -> Dict[str, Any]:
        """
        Get git branches.

        Args:
            list_all: Whether to list all branches (including remote)

        Returns:
            Dict with branch information
        """
        if not self._has_git:
            return {
                "success": False,
                "error": "Git is not available on this system",
            }

        if not self._is_git_repo:
            return {
                "success": False,
                "error": "Not a git repository",
            }

        args = ["branch"]
        if list_all:
            args.append("--all")

        result = self._run_git_command(args)

        if result["success"]:
            branches = []
            current_branch = None

            for line in result["stdout"].strip().split("\n"):
                if line.startswith("*"):
                    current_branch = line[2:].strip()
                    branches.append(current_branch)
                elif line.strip():
                    branches.append(line.strip())

            return {
                "success": True,
                "branches": branches,
                "current_branch": current_branch,
            }

        return result

    def is_git_available(self) -> bool:
        """Check if git is available."""
        return self._has_git

    def is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        return self._is_git_repo
