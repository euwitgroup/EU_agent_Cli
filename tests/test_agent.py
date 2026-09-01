"""Tests for agent module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from myagent.agent import AgentLoop, AgentState, ContextManager
from myagent.providers import GenerateResponse, ToolCall


@pytest.fixture
def temp_workspace(tmp_path):
    """Create a temporary workspace."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return workspace


@pytest.fixture
def agent_state(temp_workspace):
    """Create agent state instance."""
    return AgentState(
        workspace_dir=temp_workspace,
        provider="test",
        model="test-model",
    )


class TestAgentState:
    """Tests for AgentState."""

    def test_initialization(self, agent_state, temp_workspace):
        """Test state initialization."""
        assert agent_state.workspace_dir == temp_workspace
        assert agent_state.provider == "test"
        assert agent_state.model == "test-model"
        assert agent_state.iteration_count == 0
        assert agent_state.max_iterations == 50

    def test_add_message(self, agent_state):
        """Test adding messages."""
        agent_state.add_message("user", "Hello")
        agent_state.add_message("assistant", "Hi there")

        assert len(agent_state.messages) == 2
        assert agent_state.messages[0]["role"] == "user"
        assert agent_state.messages[0]["content"] == "Hello"

    def test_add_tool_call(self, agent_state):
        """Test recording tool calls."""
        agent_state.add_tool_call("test_tool", {"arg": "value"}, {"result": "success"})

        assert len(agent_state.tool_calls) == 1
        assert agent_state.tool_calls[0]["tool"] == "test_tool"

    def test_record_file_change(self, agent_state):
        """Test recording file changes."""
        agent_state.record_file_change("file1.py", "modified")
        agent_state.record_file_change("file2.py", "created")
        agent_state.record_file_change("file3.py", "deleted")

        assert "file1.py" in agent_state.files_changed
        assert "file2.py" in agent_state.files_created
        assert "file3.py" in agent_state.files_deleted

    def test_record_command(self, agent_state):
        """Test recording commands."""
        agent_state.record_command("pytest")
        agent_state.record_command("git status")

        assert len(agent_state.commands_executed) == 2
        assert "pytest" in agent_state.commands_executed

    def test_iteration_management(self, agent_state):
        """Test iteration counting and limits."""
        assert not agent_state.has_reached_limit()

        for i in range(50):
            agent_state.increment_iteration()

        assert agent_state.iteration_count == 50
        assert agent_state.has_reached_limit()

    def test_get_summary(self, agent_state):
        """Test getting session summary."""
        agent_state.increment_iteration()
        agent_state.add_tool_call("test", {}, {})
        agent_state.record_file_change("test.py", "modified")

        summary = agent_state.get_summary()
        assert summary["iterations"] == 1
        assert summary["tool_calls"] == 1
        assert summary["files_changed"] == 1


class TestContextManager:
    """Tests for ContextManager."""

    def test_initialization(self, temp_workspace):
        """Test context manager initialization."""
        ctx = ContextManager(temp_workspace)
        assert ctx.workspace_dir == temp_workspace
        assert ctx.project_info["name"] == "workspace"

    def test_project_detection_python(self, temp_workspace):
        """Test Python project detection."""
        (temp_workspace / "pyproject.toml").write_text("")
        ctx = ContextManager(temp_workspace)
        assert ctx.project_info["type"] == "Python"

    def test_project_detection_nodejs(self, temp_workspace):
        """Test Node.js project detection."""
        (temp_workspace / "package.json").write_text("{}")
        ctx = ContextManager(temp_workspace)
        assert ctx.project_info["type"] == "Node.js"

    def test_build_system_context(self, temp_workspace):
        """Test building system context."""
        ctx = ContextManager(temp_workspace)
        system_prompt = ctx.build_system_context()

        assert "coding agent" in system_prompt.lower()
        assert "workspace" in system_prompt
        assert len(system_prompt) > 100

    def test_build_user_message(self, temp_workspace):
        """Test building user message."""
        ctx = ContextManager(temp_workspace)
        
        msg = ctx.build_user_message("Fix the bug")
        assert "Fix the bug" in msg

        msg_with_summary = ctx.build_user_message("Fix the bug", include_project_summary=True)
        assert "Project:" in msg_with_summary
        assert "Fix the bug" in msg_with_summary

    def test_format_tool_result_read_file(self, temp_workspace):
        """Test formatting read_file result."""
        ctx = ContextManager(temp_workspace)
        result = {
            "success": True,
            "path": "test.py",
            "content": "def hello():\n    pass",
            "lines": 2,
        }

        formatted = ctx.format_tool_result("read_file", result)
        assert "test.py" in formatted
        assert "def hello()" in formatted

    def test_format_tool_result_error(self, temp_workspace):
        """Test formatting error result."""
        ctx = ContextManager(temp_workspace)
        result = {"success": False, "error": "File not found"}

        formatted = ctx.format_tool_result("read_file", result)
        assert "failed" in formatted.lower()
        assert "not found" in formatted.lower()

    def test_format_tool_result_search(self, temp_workspace):
        """Test formatting search results."""
        ctx = ContextManager(temp_workspace)
        result = {
            "success": True,
            "count": 2,
            "results": [
                {"file": "test.py", "line": 5, "content": "def hello():"},
                {"file": "main.py", "line": 10, "content": "hello()"},
            ],
        }

        formatted = ctx.format_tool_result("search_files", result)
        assert "2 matches" in formatted
        assert "test.py" in formatted

    def test_format_tool_result_command(self, temp_workspace):
        """Test formatting command result."""
        ctx = ContextManager(temp_workspace)
        result = {
            "success": True,
            "command": "pytest",
            "exit_code": 0,
            "stdout": "All tests passed",
            "stderr": "",
            "duration": 1.5,
        }

        formatted = ctx.format_tool_result("run_command", result)
        assert "pytest" in formatted
        assert "Exit code: 0" in formatted
        assert "All tests passed" in formatted


class TestAgentLoop:
    """Tests for AgentLoop."""

    def test_initialization(self, temp_workspace):
        """Test agent loop initialization."""
        with patch("myagent.agent.loop.ProviderRouter.create_provider") as mock_provider:
            mock_provider.return_value = Mock()
            loop = AgentLoop(temp_workspace)
            
            assert loop.workspace_dir == temp_workspace
            assert loop.state is not None
            assert loop.context_manager is not None
            assert loop.tool_registry is not None

    def test_execute_tools(self, temp_workspace):
        """Test tool execution."""
        with patch("myagent.agent.loop.ProviderRouter.create_provider") as mock_provider:
            mock_provider.return_value = Mock()
            loop = AgentLoop(temp_workspace)

            # Mock tool registry
            loop.tool_registry.execute = Mock(return_value={"success": True, "result": "ok"})

            tool_calls = [
                ToolCall(id="call_1", name="test_tool", arguments={"arg": "value"})
            ]

            results = loop._execute_tools(tool_calls)
            
            assert len(results) == 1
            assert results[0]["success"] is True
            loop.tool_registry.execute.assert_called_once_with("test_tool", arg="value")

    def test_run_simple_task(self, temp_workspace):
        """Test running a simple task that completes."""
        with patch("myagent.agent.loop.ProviderRouter.create_provider") as mock_provider:
            # Mock provider
            mock_provider_instance = Mock()
            mock_provider_instance.generate.return_value = GenerateResponse(
                content="Task completed successfully",
                tool_calls=[],
                finish_reason="stop",
                model="test-model",
            )
            mock_provider.return_value = mock_provider_instance

            loop = AgentLoop(temp_workspace)
            result = loop.run("Test task")

            assert result["success"] is True
            assert "Task completed" in result["message"]
            assert mock_provider_instance.generate.called

    def test_run_with_tool_calls(self, temp_workspace):
        """Test running a task with tool calls."""
        with patch("myagent.agent.loop.ProviderRouter.create_provider") as mock_provider:
            # Mock provider with tool call then completion
            mock_provider_instance = Mock()
            mock_provider_instance.generate.side_effect = [
                GenerateResponse(
                    content="I'll read the file",
                    tool_calls=[
                        ToolCall(id="call_1", name="read_file", arguments={"path": "test.txt"})
                    ],
                    finish_reason="tool_calls",
                    model="test-model",
                ),
                GenerateResponse(
                    content="File read successfully",
                    tool_calls=[],
                    finish_reason="stop",
                    model="test-model",
                ),
            ]
            mock_provider.return_value = mock_provider_instance

            loop = AgentLoop(temp_workspace)
            
            # Create test file
            (temp_workspace / "test.txt").write_text("content")

            result = loop.run("Read test.txt")

            assert result["success"] is True
            assert mock_provider_instance.generate.call_count == 2

    def test_run_iteration_limit(self, temp_workspace):
        """Test iteration limit handling."""
        with patch("myagent.agent.loop.ProviderRouter.create_provider") as mock_provider:
            # Mock provider that always returns tool calls (infinite loop)
            mock_provider_instance = Mock()
            mock_provider_instance.generate.return_value = GenerateResponse(
                content="Using tool",
                tool_calls=[
                    ToolCall(id="call_1", name="list_files", arguments={"path": "."})
                ],
                finish_reason="tool_calls",
                model="test-model",
            )
            mock_provider.return_value = mock_provider_instance

            loop = AgentLoop(temp_workspace)
            loop.state.max_iterations = 3  # Set low limit for test

            result = loop.run("Infinite task")

            assert result["success"] is False
            assert "limit" in result["error"].lower()
            assert loop.state.iteration_count == 3
