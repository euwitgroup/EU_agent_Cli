"""Permission manager for controlling tool access."""

import logging
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from myagent.tools.terminal import is_dangerous_command

logger = logging.getLogger(__name__)


class PermissionPolicy(str, Enum):
    """Permission policy options."""

    ALWAYS = "always"  # Always allow without asking
    ASK = "ask"  # Ask user for permission
    NEVER = "never"  # Never allow


class PermissionCategory(str, Enum):
    """Permission categories for different operations."""

    READ = "read"  # File reading operations
    WRITE = "write"  # File writing/editing operations
    DELETE = "delete"  # File deletion operations
    COMMAND = "command"  # Command execution
    NETWORK = "network"  # Network operations (future)


class PermissionManager:
    """Manages permissions for tool execution."""

    def __init__(self, workspace_dir: Path, interactive: bool = True):
        """
        Initialize permission manager.

        Args:
            workspace_dir: Workspace root directory
            interactive: Whether to prompt for permissions interactively
        """
        self.workspace_dir = workspace_dir.resolve()
        self.interactive = interactive

        # Default policies
        self.policies: Dict[PermissionCategory, PermissionPolicy] = {
            PermissionCategory.READ: PermissionPolicy.ALWAYS,
            PermissionCategory.WRITE: PermissionPolicy.ASK,
            PermissionCategory.DELETE: PermissionPolicy.ASK,
            PermissionCategory.COMMAND: PermissionPolicy.ASK,
            PermissionCategory.NETWORK: PermissionPolicy.ASK,
        }

        # Session-based permission cache: (category, identifier) -> decision
        self.permission_cache: Dict[tuple, bool] = {}

        logger.info(f"Permission manager initialized: interactive={interactive}")

    def set_policy(self, category: PermissionCategory, policy: PermissionPolicy) -> None:
        """
        Set permission policy for a category.

        Args:
            category: Permission category
            policy: Policy to apply
        """
        self.policies[category] = policy
        logger.info(f"Set policy: {category.value} -> {policy.value}")

    def check_permission(
        self,
        category: PermissionCategory,
        operation: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Check if an operation is permitted.

        Args:
            category: Permission category
            operation: Operation description
            details: Additional details about the operation

        Returns:
            True if operation is permitted, False otherwise
        """
        details = details or {}
        policy = self.policies.get(category, PermissionPolicy.ASK)

        # Check cache first
        cache_key = (category, operation, str(details))
        if cache_key in self.permission_cache:
            cached_decision = self.permission_cache[cache_key]
            logger.debug(f"Using cached permission: {cached_decision}")
            return cached_decision

        # Apply policy
        if policy == PermissionPolicy.ALWAYS:
            decision = True
        elif policy == PermissionPolicy.NEVER:
            decision = False
        elif policy == PermissionPolicy.ASK:
            # In non-interactive mode, default to safe choice
            if not self.interactive:
                decision = category == PermissionCategory.READ
            else:
                decision = self._prompt_user(category, operation, details)
        else:
            decision = False

        # Cache decision
        self.permission_cache[cache_key] = decision
        return decision

    def check_command_permission(self, command: str) -> bool:
        """
        Check if a command is permitted to execute.

        Args:
            command: Command string to check

        Returns:
            True if command is permitted, False otherwise
        """
        # Check if command is dangerous
        if is_dangerous_command(command):
            logger.warning(f"Dangerous command detected: {command[:100]}")
            return self.check_permission(
                PermissionCategory.COMMAND,
                f"dangerous_command",
                {"command": command[:200], "reason": "Potentially destructive operation"},
            )

        # Regular commands follow command policy
        policy = self.policies.get(PermissionCategory.COMMAND, PermissionPolicy.ASK)

        if policy == PermissionPolicy.ALWAYS:
            return True
        elif policy == PermissionPolicy.NEVER:
            return False
        else:
            # For ASK policy, check cache or prompt
            cache_key = (PermissionCategory.COMMAND, "execute", command[:100])
            if cache_key in self.permission_cache:
                return self.permission_cache[cache_key]

            if not self.interactive:
                # In non-interactive mode, allow safe commands
                return not is_dangerous_command(command)

            decision = self._prompt_user(
                PermissionCategory.COMMAND, "execute command", {"command": command}
            )
            self.permission_cache[cache_key] = decision
            return decision

    def check_path_access(self, path: Path, operation: str = "access") -> bool:
        """
        Check if a path is accessible (within workspace).

        Args:
            path: Path to check
            operation: Operation description

        Returns:
            True if path is accessible, False otherwise
        """
        try:
            resolved = path.resolve()
            workspace_resolved = self.workspace_dir.resolve()

            # Check if path is within workspace
            is_within = str(resolved).startswith(str(workspace_resolved))

            if not is_within:
                logger.warning(f"Path outside workspace blocked: {path}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking path access: {e}")
            return False

    def _prompt_user(
        self, category: PermissionCategory, operation: str, details: Dict[str, Any]
    ) -> bool:
        """
        Prompt user for permission (placeholder for Phase 7).

        Args:
            category: Permission category
            operation: Operation description
            details: Operation details

        Returns:
            User's decision (True = allow, False = deny)
        """
        # This will be properly implemented in Phase 7 with interactive prompts
        # For now, default to safe choices for testing

        if category == PermissionCategory.READ:
            return True  # Reading is generally safe

        # For other operations, check if it's clearly safe
        if category == PermissionCategory.WRITE:
            # Allow writes by default in testing
            return True

        if category == PermissionCategory.COMMAND:
            command = details.get("command", "")
            # Deny dangerous commands by default in non-interactive
            return not is_dangerous_command(command)

        # Default to deny for other categories
        return False

    def clear_cache(self) -> None:
        """Clear the permission cache."""
        self.permission_cache.clear()
        logger.debug("Permission cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get permission statistics.

        Returns:
            Dict with permission stats
        """
        return {
            "policies": {k.value: v.value for k, v in self.policies.items()},
            "cached_decisions": len(self.permission_cache),
            "interactive": self.interactive,
        }


# Global permission manager instance
_manager: Optional[PermissionManager] = None


def get_permission_manager(
    workspace_dir: Optional[Path] = None, interactive: bool = True
) -> PermissionManager:
    """
    Get or create the global permission manager.

    Args:
        workspace_dir: Workspace directory (required for first initialization)
        interactive: Whether to enable interactive prompts

    Returns:
        PermissionManager instance
    """
    global _manager

    if _manager is None:
        if workspace_dir is None:
            raise ValueError("workspace_dir required for first initialization")
        _manager = PermissionManager(workspace_dir, interactive)

    return _manager


def reset_permission_manager() -> None:
    """Reset the global permission manager (useful for testing)."""
    global _manager
    _manager = None
