"""Tool implementations."""

from pathlib import Path
from typing import Optional

from myagent.providers.base import ToolDefinition
from myagent.tools.filesystem import FilesystemTools
from myagent.tools.git import GitTools
from myagent.tools.registry import Tool, ToolRegistry, get_registry, reset_registry
from myagent.tools.search import SearchTools
from myagent.tools.terminal import TerminalTools, is_dangerous_command
from myagent.tools.tests import TestRunner

__all__ = [
    "Tool",
    "ToolRegistry",
    "ToolDefinition",
    "get_registry",
    "reset_registry",
    "FilesystemTools",
    "SearchTools",
    "TerminalTools",
    "GitTools",
    "TestRunner",
    "is_dangerous_command",
    "register_all_tools",
]


def register_all_tools(workspace_dir: Path) -> ToolRegistry:
    """
    Register all available tools for the agent.

    Args:
        workspace_dir: Workspace root directory

    Returns:
        Configured ToolRegistry
    """
    registry = get_registry()

    # Initialize tool collections
    fs_tools = FilesystemTools(workspace_dir)
    search_tools = SearchTools(workspace_dir)
    terminal_tools = TerminalTools(workspace_dir)
    git_tools = GitTools(workspace_dir)
    test_runner = TestRunner(workspace_dir)

    # Register read_file
    registry.register(
        name="read_file",
        description="Read the contents of a file. Use start_line and end_line to read specific sections of large files.",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path relative to workspace or absolute path",
                },
                "start_line": {
                    "type": "integer",
                    "description": "Optional starting line number (1-indexed)",
                },
                "end_line": {
                    "type": "integer",
                    "description": "Optional ending line number (1-indexed, inclusive)",
                },
            },
            "required": ["path"],
        },
        handler=fs_tools.read_file,
        permission_category="read",
    )

    # Register write_file
    registry.register(
        name="write_file",
        description="Create a new file or completely overwrite an existing file with new content.",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path relative to workspace or absolute path",
                },
                "content": {"type": "string", "description": "Content to write to the file"},
            },
            "required": ["path", "content"],
        },
        handler=fs_tools.write_file,
        permission_category="write",
    )

    # Register edit_file
    registry.register(
        name="edit_file",
        description="Edit a file by replacing old_text with new_text. The old_text must match exactly (including whitespace) and must be unique in the file.",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path relative to workspace or absolute path",
                },
                "old_text": {
                    "type": "string",
                    "description": "Text to find and replace (must match exactly)",
                },
                "new_text": {"type": "string", "description": "Replacement text"},
            },
            "required": ["path", "old_text", "new_text"],
        },
        handler=fs_tools.edit_file,
        permission_category="write",
    )

    # Register list_files
    registry.register(
        name="list_files",
        description="List files and directories in a given path. Automatically ignores common directories like .git, node_modules, etc.",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path to list (default: current directory)",
                    "default": ".",
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum depth to traverse (default: 2)",
                    "default": 2,
                },
            },
        },
        handler=fs_tools.list_files,
        permission_category="read",
    )

    # Register search_files
    registry.register(
        name="search_files",
        description="Search for text content within files using regex patterns. Returns matching lines with file paths and line numbers.",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query (regex pattern)"},
                "path": {
                    "type": "string",
                    "description": "Directory to search in (default: current directory)",
                    "default": ".",
                },
                "case_sensitive": {
                    "type": "boolean",
                    "description": "Whether search is case sensitive (default: false)",
                    "default": False,
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 100)",
                    "default": 100,
                },
            },
            "required": ["query"],
        },
        handler=search_tools.search_files,
        permission_category="read",
    )

    # Register find_files
    registry.register(
        name="find_files",
        description="Find files by name pattern using glob syntax (e.g., '*.py', 'test_*.py').",
        parameters={
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Glob pattern for file names"},
                "path": {
                    "type": "string",
                    "description": "Directory to search in (default: current directory)",
                    "default": ".",
                },
            },
            "required": ["pattern"],
        },
        handler=search_tools.find_files,
        permission_category="read",
    )

    # Register run_command
    registry.register(
        name="run_command",
        description="Execute a shell command and return the output. Use this to run tests, build commands, git operations, etc.",
        parameters={
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to execute"},
                "cwd": {
                    "type": "string",
                    "description": "Working directory (relative to workspace or absolute)",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default from config)",
                },
            },
            "required": ["command"],
        },
        handler=terminal_tools.run_command,
        permission_category="command",
    )

    # Register git_status
    registry.register(
        name="git_status",
        description="Get the current Git status showing modified, added, and untracked files.",
        parameters={
            "type": "object",
            "properties": {
                "short": {
                    "type": "boolean",
                    "description": "Use short format (default: false)",
                    "default": False,
                },
            },
        },
        handler=git_tools.git_status,
        permission_category="read",
    )

    # Register git_diff
    registry.register(
        name="git_diff",
        description="Show differences between working directory and the last commit. Useful for reviewing changes before committing.",
        parameters={
            "type": "object",
            "properties": {
                "staged": {
                    "type": "boolean",
                    "description": "Show staged changes (default: false)",
                    "default": False,
                },
                "file_path": {
                    "type": "string",
                    "description": "Optional specific file to diff",
                },
            },
        },
        handler=git_tools.git_diff,
        permission_category="read",
    )

    # Register git_log
    registry.register(
        name="git_log",
        description="Show recent commit history.",
        parameters={
            "type": "object",
            "properties": {
                "max_count": {
                    "type": "integer",
                    "description": "Maximum number of commits to show (default: 10)",
                    "default": 10,
                },
                "oneline": {
                    "type": "boolean",
                    "description": "Use oneline format (default: true)",
                    "default": True,
                },
            },
        },
        handler=git_tools.git_log,
        permission_category="read",
    )

    return registry
