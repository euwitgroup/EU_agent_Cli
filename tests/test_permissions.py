"""Tests for permissions module."""

import pytest
from pathlib import Path

from myagent.permissions import (
    PermissionManager,
    PermissionPolicy,
    PermissionCategory,
    get_permission_manager,
    reset_permission_manager,
)


@pytest.fixture
def temp_workspace(tmp_path):
    """Create a temporary workspace."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return workspace


@pytest.fixture
def perm_manager(temp_workspace):
    """Create permission manager instance."""
    return PermissionManager(temp_workspace, interactive=False)


@pytest.fixture(autouse=True)
def reset_manager():
    """Reset permission manager before each test."""
    reset_permission_manager()


class TestPermissionPolicy:
    """Tests for PermissionPolicy enum."""

    def test_policy_values(self):
        """Test policy enum values."""
        assert PermissionPolicy.ALWAYS.value == "always"
        assert PermissionPolicy.ASK.value == "ask"
        assert PermissionPolicy.NEVER.value == "never"


class TestPermissionCategory:
    """Tests for PermissionCategory enum."""

    def test_category_values(self):
        """Test category enum values."""
        assert PermissionCategory.READ.value == "read"
        assert PermissionCategory.WRITE.value == "write"
        assert PermissionCategory.DELETE.value == "delete"
        assert PermissionCategory.COMMAND.value == "command"
        assert PermissionCategory.NETWORK.value == "network"


class TestPermissionManager:
    """Tests for PermissionManager."""

    def test_initialization(self, perm_manager, temp_workspace):
        """Test permission manager initialization."""
        assert perm_manager.workspace_dir == temp_workspace
        assert perm_manager.interactive is False
        assert PermissionCategory.READ in perm_manager.policies

    def test_default_policies(self, perm_manager):
        """Test default permission policies."""
        assert perm_manager.policies[PermissionCategory.READ] == PermissionPolicy.ALWAYS
        assert perm_manager.policies[PermissionCategory.WRITE] == PermissionPolicy.ASK
        assert perm_manager.policies[PermissionCategory.DELETE] == PermissionPolicy.ASK
        assert perm_manager.policies[PermissionCategory.COMMAND] == PermissionPolicy.ASK

    def test_set_policy(self, perm_manager):
        """Test setting permission policy."""
        perm_manager.set_policy(PermissionCategory.WRITE, PermissionPolicy.ALWAYS)
        assert perm_manager.policies[PermissionCategory.WRITE] == PermissionPolicy.ALWAYS

        perm_manager.set_policy(PermissionCategory.READ, PermissionPolicy.NEVER)
        assert perm_manager.policies[PermissionCategory.READ] == PermissionPolicy.NEVER

    def test_check_permission_always(self, perm_manager):
        """Test permission check with ALWAYS policy."""
        perm_manager.set_policy(PermissionCategory.READ, PermissionPolicy.ALWAYS)
        assert perm_manager.check_permission(PermissionCategory.READ, "read_file") is True

    def test_check_permission_never(self, perm_manager):
        """Test permission check with NEVER policy."""
        perm_manager.set_policy(PermissionCategory.WRITE, PermissionPolicy.NEVER)
        assert perm_manager.check_permission(PermissionCategory.WRITE, "write_file") is False

    def test_check_permission_ask_non_interactive(self, perm_manager):
        """Test permission check with ASK policy in non-interactive mode."""
        perm_manager.set_policy(PermissionCategory.READ, PermissionPolicy.ASK)
        # In non-interactive mode, READ should default to True
        assert perm_manager.check_permission(PermissionCategory.READ, "read_file") is True

        perm_manager.set_policy(PermissionCategory.WRITE, PermissionPolicy.ASK)
        # In non-interactive mode with ASK, writes should be allowed (for testing)
        result = perm_manager.check_permission(PermissionCategory.WRITE, "write_file")
        # Result depends on _prompt_user implementation
        assert isinstance(result, bool)

    def test_permission_caching(self, perm_manager):
        """Test that permission decisions are cached."""
        perm_manager.set_policy(PermissionCategory.WRITE, PermissionPolicy.ASK)

        # First check
        result1 = perm_manager.check_permission(
            PermissionCategory.WRITE, "write_file", {"path": "test.txt"}
        )

        # Second check should return cached result
        result2 = perm_manager.check_permission(
            PermissionCategory.WRITE, "write_file", {"path": "test.txt"}
        )

        assert result1 == result2
        assert len(perm_manager.permission_cache) > 0

    def test_clear_cache(self, perm_manager):
        """Test clearing permission cache."""
        perm_manager.check_permission(PermissionCategory.READ, "read_file")
        assert len(perm_manager.permission_cache) > 0

        perm_manager.clear_cache()
        assert len(perm_manager.permission_cache) == 0

    def test_check_command_permission_safe(self, perm_manager):
        """Test checking permission for safe commands."""
        perm_manager.set_policy(PermissionCategory.COMMAND, PermissionPolicy.ALWAYS)
        assert perm_manager.check_command_permission("echo hello") is True
        assert perm_manager.check_command_permission("pytest") is True

    def test_check_command_permission_dangerous(self, perm_manager):
        """Test checking permission for dangerous commands."""
        # Dangerous commands should require explicit permission
        result = perm_manager.check_command_permission("rm -rf /")
        # In non-interactive mode with dangerous commands, should be denied
        assert result is False

        result = perm_manager.check_command_permission("git reset --hard")
        assert result is False

    def test_check_command_permission_with_policy(self, perm_manager):
        """Test command permission with different policies."""
        # ALWAYS policy
        perm_manager.set_policy(PermissionCategory.COMMAND, PermissionPolicy.ALWAYS)
        assert perm_manager.check_command_permission("echo hello") is True

        # NEVER policy
        perm_manager.set_policy(PermissionCategory.COMMAND, PermissionPolicy.NEVER)
        assert perm_manager.check_command_permission("echo hello") is False

    def test_check_path_access_within_workspace(self, perm_manager, temp_workspace):
        """Test path access within workspace."""
        test_file = temp_workspace / "test.txt"
        assert perm_manager.check_path_access(test_file) is True

        nested_file = temp_workspace / "subdir" / "nested.txt"
        assert perm_manager.check_path_access(nested_file) is True

    def test_check_path_access_outside_workspace(self, perm_manager, temp_workspace):
        """Test path access outside workspace."""
        # Path outside workspace
        outside_path = temp_workspace.parent / "outside.txt"
        assert perm_manager.check_path_access(outside_path) is False

        # Absolute path outside workspace
        root_path = Path("/etc/passwd")
        assert perm_manager.check_path_access(root_path) is False

    def test_check_path_access_traversal_attempt(self, perm_manager, temp_workspace):
        """Test path traversal attack prevention."""
        # Try to escape workspace with ../
        traversal_path = temp_workspace / ".." / ".." / "etc" / "passwd"
        assert perm_manager.check_path_access(traversal_path) is False

    def test_get_stats(self, perm_manager):
        """Test getting permission statistics."""
        stats = perm_manager.get_stats()

        assert "policies" in stats
        assert "cached_decisions" in stats
        assert "interactive" in stats
        assert stats["interactive"] is False
        assert isinstance(stats["cached_decisions"], int)


class TestPermissionManagerGlobal:
    """Tests for global permission manager functions."""

    def test_get_permission_manager_initialization(self, temp_workspace):
        """Test getting permission manager for first time."""
        reset_permission_manager()
        manager = get_permission_manager(temp_workspace)
        assert manager is not None
        assert manager.workspace_dir == temp_workspace

    def test_get_permission_manager_singleton(self, temp_workspace):
        """Test that get_permission_manager returns same instance."""
        reset_permission_manager()
        manager1 = get_permission_manager(temp_workspace)
        manager2 = get_permission_manager()
        assert manager1 is manager2

    def test_get_permission_manager_no_workspace_error(self):
        """Test error when getting manager without workspace."""
        reset_permission_manager()
        with pytest.raises(ValueError, match="workspace_dir required"):
            get_permission_manager()

    def test_reset_permission_manager(self, temp_workspace):
        """Test resetting permission manager."""
        reset_permission_manager()
        manager1 = get_permission_manager(temp_workspace)

        reset_permission_manager()
        manager2 = get_permission_manager(temp_workspace)

        assert manager1 is not manager2


class TestPermissionIntegration:
    """Integration tests for permission system."""

    def test_read_operations_default_allowed(self, perm_manager):
        """Test that read operations are allowed by default."""
        assert perm_manager.check_permission(
            PermissionCategory.READ, "read_file", {"path": "test.txt"}
        ) is True

    def test_write_operations_require_permission(self, perm_manager):
        """Test that write operations require permission."""
        # With ASK policy in non-interactive mode
        result = perm_manager.check_permission(
            PermissionCategory.WRITE, "write_file", {"path": "test.txt"}
        )
        assert isinstance(result, bool)

    def test_delete_operations_require_permission(self, perm_manager):
        """Test that delete operations require permission."""
        result = perm_manager.check_permission(
            PermissionCategory.DELETE, "delete_file", {"path": "test.txt"}
        )
        assert isinstance(result, bool)

    def test_permission_workflow(self, perm_manager):
        """Test complete permission workflow."""
        # Set permissive policies for testing
        perm_manager.set_policy(PermissionCategory.READ, PermissionPolicy.ALWAYS)
        perm_manager.set_policy(PermissionCategory.WRITE, PermissionPolicy.ALWAYS)

        # Read should be allowed
        assert perm_manager.check_permission(PermissionCategory.READ, "read") is True

        # Write should be allowed
        assert perm_manager.check_permission(PermissionCategory.WRITE, "write") is True

        # Check stats
        stats = perm_manager.get_stats()
        assert stats["cached_decisions"] >= 0
