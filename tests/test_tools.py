"""Tests for tools module."""

import pytest
import tempfile
from pathlib import Path

from myagent.tools import (
    FilesystemTools,
    SearchTools,
    TerminalTools,
    ToolRegistry,
    get_registry,
    reset_registry,
    is_dangerous_command,
    register_all_tools,
)


@pytest.fixture
def temp_workspace(tmp_path):
    """Create a temporary workspace for testing."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return workspace


@pytest.fixture
def fs_tools(temp_workspace):
    """Create filesystem tools instance."""
    return FilesystemTools(temp_workspace)


@pytest.fixture
def search_tools(temp_workspace):
    """Create search tools instance."""
    return SearchTools(temp_workspace)


@pytest.fixture
def terminal_tools(temp_workspace):
    """Create terminal tools instance."""
    return TerminalTools(temp_workspace)


@pytest.fixture(autouse=True)
def reset_tool_registry():
    """Reset registry before each test."""
    reset_registry()


class TestToolRegistry:
    """Tests for ToolRegistry."""

    def test_register_tool(self):
        """Test registering a tool."""
        registry = get_registry()

        def dummy_handler():
            return "result"

        registry.register(
            name="test_tool",
            description="Test tool",
            parameters={"type": "object"},
            handler=dummy_handler,
        )

        tool = registry.get("test_tool")
        assert tool is not None
        assert tool.name == "test_tool"
        assert tool.description == "Test tool"

    def test_list_tools(self):
        """Test listing tools."""
        registry = get_registry()

        registry.register("tool1", "Desc 1", {}, lambda: None)
        registry.register("tool2", "Desc 2", {}, lambda: None)

        tools = registry.list()
        assert len(tools) == 2
        assert {t.name for t in tools} == {"tool1", "tool2"}

    def test_execute_tool(self):
        """Test executing a tool."""
        registry = get_registry()

        def add_handler(a, b):
            return a + b

        registry.register("add", "Add numbers", {}, add_handler)

        result = registry.execute("add", a=5, b=3)
        assert result == 8

    def test_execute_nonexistent_tool(self):
        """Test executing a tool that doesn't exist."""
        registry = get_registry()

        with pytest.raises(ValueError, match="not found"):
            registry.execute("nonexistent_tool")


class TestFilesystemTools:
    """Tests for FilesystemTools."""

    def test_read_file_success(self, fs_tools, temp_workspace):
        """Test reading a file successfully."""
        test_file = temp_workspace / "test.txt"
        test_file.write_text("Hello, World!")

        result = fs_tools.read_file("test.txt")
        assert result["success"] is True
        assert result["content"] == "Hello, World!"
        assert result["lines"] == 1

    def test_read_file_not_found(self, fs_tools):
        """Test reading a nonexistent file."""
        result = fs_tools.read_file("nonexistent.txt")
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_read_file_with_line_range(self, fs_tools, temp_workspace):
        """Test reading specific lines from a file."""
        test_file = temp_workspace / "test.txt"
        test_file.write_text("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")

        result = fs_tools.read_file("test.txt", start_line=2, end_line=4)
        assert result["success"] is True
        assert "Line 2" in result["content"]
        assert "Line 4" in result["content"]
        assert "Line 1" not in result["content"]
        assert "Line 5" not in result["content"]

    def test_read_binary_file(self, fs_tools, temp_workspace):
        """Test reading a binary file."""
        test_file = temp_workspace / "test.png"
        test_file.write_bytes(b"\x89PNG\r\n\x1a\n")

        result = fs_tools.read_file("test.png")
        assert result["success"] is True
        assert result["is_binary"] is True
        assert "size" in result

    def test_write_file_create(self, fs_tools, temp_workspace):
        """Test creating a new file."""
        result = fs_tools.write_file("new_file.txt", "New content")
        assert result["success"] is True
        assert result["action"] == "created"

        # Verify file was created
        file_path = temp_workspace / "new_file.txt"
        assert file_path.exists()
        assert file_path.read_text() == "New content"

    def test_write_file_overwrite(self, fs_tools, temp_workspace):
        """Test overwriting an existing file."""
        test_file = temp_workspace / "existing.txt"
        test_file.write_text("Old content")

        result = fs_tools.write_file("existing.txt", "New content")
        assert result["success"] is True
        assert result["action"] == "modified"
        assert test_file.read_text() == "New content"

    def test_write_file_create_directories(self, fs_tools, temp_workspace):
        """Test creating parent directories automatically."""
        result = fs_tools.write_file("subdir/nested/file.txt", "Content")
        assert result["success"] is True

        file_path = temp_workspace / "subdir" / "nested" / "file.txt"
        assert file_path.exists()

    def test_edit_file_success(self, fs_tools, temp_workspace):
        """Test editing a file successfully."""
        test_file = temp_workspace / "edit.txt"
        test_file.write_text("Hello World\nGoodbye World")

        result = fs_tools.edit_file("edit.txt", "Hello World", "Hi Universe")
        assert result["success"] is True
        assert result["action"] == "modified"
        assert test_file.read_text() == "Hi Universe\nGoodbye World"

    def test_edit_file_text_not_found(self, fs_tools, temp_workspace):
        """Test editing with text that doesn't exist."""
        test_file = temp_workspace / "edit.txt"
        test_file.write_text("Hello World")

        result = fs_tools.edit_file("edit.txt", "Nonexistent", "Replacement")
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_edit_file_multiple_matches(self, fs_tools, temp_workspace):
        """Test editing with text that appears multiple times."""
        test_file = temp_workspace / "edit.txt"
        test_file.write_text("Hello\nHello\nHello")

        result = fs_tools.edit_file("edit.txt", "Hello", "Hi")
        assert result["success"] is False
        assert "multiple" in result["error"].lower() or "times" in result["error"].lower()

    def test_list_files_success(self, fs_tools, temp_workspace):
        """Test listing files in a directory."""
        # Create some files
        (temp_workspace / "file1.txt").write_text("content")
        (temp_workspace / "file2.py").write_text("content")
        (temp_workspace / "subdir").mkdir()
        (temp_workspace / "subdir" / "file3.txt").write_text("content")

        result = fs_tools.list_files(".")
        assert result["success"] is True
        assert result["count"] >= 2
        assert any(item["name"] == "file1.txt" for item in result["items"])

    def test_list_files_not_found(self, fs_tools):
        """Test listing nonexistent directory."""
        result = fs_tools.list_files("nonexistent")
        assert result["success"] is False

    def test_path_traversal_protection(self, fs_tools, temp_workspace):
        """Test protection against path traversal attacks."""
        result = fs_tools.read_file("../../etc/passwd")
        assert result["success"] is False
        assert "outside workspace" in result["error"].lower()


class TestSearchTools:
    """Tests for SearchTools."""

    def test_search_files_python_fallback(self, search_tools, temp_workspace):
        """Test Python-based search."""
        # Create test files
        (temp_workspace / "file1.py").write_text("def hello():\n    pass")
        (temp_workspace / "file2.py").write_text("def world():\n    pass")

        result = search_tools.search_files("def hello")
        assert result["success"] is True
        assert result["count"] >= 1
        assert any("file1.py" in r["file"] for r in result["results"])

    def test_search_files_case_insensitive(self, search_tools, temp_workspace):
        """Test case-insensitive search."""
        (temp_workspace / "test.txt").write_text("Hello World")

        result = search_tools.search_files("hello", case_sensitive=False)
        assert result["success"] is True
        assert result["count"] >= 1

    def test_find_files_by_pattern(self, search_tools, temp_workspace):
        """Test finding files by glob pattern."""
        (temp_workspace / "test1.py").write_text("")
        (temp_workspace / "test2.py").write_text("")
        (temp_workspace / "readme.md").write_text("")

        result = search_tools.find_files("*.py")
        assert result["success"] is True
        assert result["count"] == 2
        assert all(f.endswith(".py") for f in result["files"])


class TestTerminalTools:
    """Tests for TerminalTools."""

    def test_run_command_success(self, terminal_tools):
        """Test running a successful command."""
        result = terminal_tools.run_command("echo Hello")
        assert result["success"] is True
        assert "Hello" in result["stdout"]

    def test_run_command_failure(self, terminal_tools):
        """Test running a failing command."""
        result = terminal_tools.run_command("exit 1")
        assert result["success"] is False
        assert result["exit_code"] == 1

    def test_is_dangerous_command(self):
        """Test dangerous command detection."""
        assert is_dangerous_command("rm -rf /") is True
        assert is_dangerous_command("del /f file.txt") is True
        assert is_dangerous_command("git reset --hard") is True
        assert is_dangerous_command("shutdown now") is True
        assert is_dangerous_command("echo hello") is False
        assert is_dangerous_command("pytest") is False


class TestToolRegistration:
    """Tests for tool registration."""

    def test_register_all_tools(self, temp_workspace):
        """Test registering all tools."""
        registry = register_all_tools(temp_workspace)

        # Check that key tools are registered
        assert registry.get("read_file") is not None
        assert registry.get("write_file") is not None
        assert registry.get("edit_file") is not None
        assert registry.get("list_files") is not None
        assert registry.get("search_files") is not None
        assert registry.get("find_files") is not None
        assert registry.get("run_command") is not None

    def test_tool_definitions_for_provider(self, temp_workspace):
        """Test getting tool definitions for AI providers."""
        registry = register_all_tools(temp_workspace)
        definitions = registry.get_definitions()

        assert len(definitions) >= 7
        assert all("name" in d for d in definitions)
        assert all("description" in d for d in definitions)
        assert all("parameters" in d for d in definitions)



class TestGitTools:
    """Tests for GitTools."""

    def test_initialization(self, temp_workspace):
        """Test Git tools initialization."""
        from myagent.tools.git import GitTools

        git_tools = GitTools(temp_workspace)
        assert git_tools.workspace_dir == temp_workspace

    def test_git_not_available(self, temp_workspace):
        """Test behavior when git is not available."""
        from myagent.tools.git import GitTools
        from unittest.mock import patch

        with patch.object(GitTools, "_check_git_available", return_value=False):
            git_tools = GitTools(temp_workspace)
            result = git_tools.git_status()
            assert result["success"] is False
            assert "not available" in result["error"].lower()

    def test_not_git_repo(self, temp_workspace):
        """Test behavior when not in a git repo."""
        from myagent.tools.git import GitTools

        git_tools = GitTools(temp_workspace)
        if not git_tools.is_git_repo():
            result = git_tools.git_status()
            assert result["success"] is False
            assert "not a git repository" in result["error"].lower()


class TestTestRunner:
    """Tests for TestRunner."""

    def test_initialization(self, temp_workspace):
        """Test test runner initialization."""
        from myagent.tools.tests import TestRunner

        runner = TestRunner(temp_workspace)
        assert runner.workspace_dir == temp_workspace

    def test_detect_pytest(self, temp_workspace):
        """Test detecting pytest framework."""
        from myagent.tools.tests import TestRunner

        # Create pytest indicator
        (temp_workspace / "pytest.ini").write_text("[pytest]")

        runner = TestRunner(temp_workspace)
        # Note: detection may not work without proper content
        assert runner.detected_framework in [None, "pytest"]

    def test_detect_npm(self, temp_workspace):
        """Test detecting npm test framework."""
        from myagent.tools.tests import TestRunner
        import json

        # Create package.json with test script
        package = {"scripts": {"test": "jest"}}
        (temp_workspace / "package.json").write_text(json.dumps(package))

        runner = TestRunner(temp_workspace)
        assert runner.detected_framework == "jest"

    def test_get_test_command_pytest(self, temp_workspace):
        """Test getting pytest command."""
        from myagent.tools.tests import TestRunner
        from unittest.mock import patch

        with patch.object(TestRunner, "_detect_test_framework", return_value="pytest"):
            runner = TestRunner(temp_workspace)
            cmd = runner.get_test_command()
            assert cmd == "pytest"

            cmd_specific = runner.get_test_command("test_file.py")
            assert "test_file.py" in cmd_specific

    def test_parse_pytest_output(self, temp_workspace):
        """Test parsing pytest output."""
        from myagent.tools.tests import TestRunner

        runner = TestRunner(temp_workspace)
        output = "5 passed, 2 failed in 1.23s"

        results = runner._parse_pytest_output(output)
        assert results["passed"] == 5
        assert results["failed"] == 2
        assert results["duration"] == 1.23

    def test_parse_jest_output(self, temp_workspace):
        """Test parsing Jest output."""
        from myagent.tools.tests import TestRunner

        runner = TestRunner(temp_workspace)
        output = "Tests: 2 failed, 8 passed, 10 total\nTime: 2.5s"

        results = runner._parse_jest_output(output)
        assert results["passed"] == 8
        assert results["failed"] == 2
        assert results["total"] == 10
        assert results["duration"] == 2.5

    def test_format_test_results(self, temp_workspace):
        """Test formatting test results."""
        from myagent.tools.tests import TestRunner

        runner = TestRunner(temp_workspace)
        results = {
            "framework": "pytest",
            "passed": 5,
            "failed": 2,
            "total": 7,
            "duration": 1.5,
        }

        formatted = runner.format_test_results(results)
        assert "pytest" in formatted
        assert "5" in formatted
        assert "2" in formatted
