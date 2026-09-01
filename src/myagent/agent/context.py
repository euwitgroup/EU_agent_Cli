"""Context manager for building agent context."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# System prompt for the coding agent
SYSTEM_PROMPT = """You are an AI coding agent designed to help developers build and maintain software projects.

Your capabilities:
- Read, write, and edit files in the project
- Search for code and content across files
- Execute terminal commands (tests, build tools, git operations)
- Analyze code and understand project structure
- Plan and implement features
- Debug and fix issues

Core principles:
1. Understand before modifying: Search and read relevant files before making changes
2. Make targeted edits: Use edit_file for precise changes rather than rewriting entire files
3. Verify your work: Run tests after making changes
4. Be transparent: Explain your reasoning and what you're doing
5. Ask for permission: Flag potentially dangerous operations
6. Stay focused: Modify only what's needed for the task
7. Test and iterate: If tests fail, analyze the failure and fix the issue

When working on a task:
1. Understand the project structure
2. Search for relevant code
3. Read necessary files
4. Plan your changes
5. Make modifications
6. Run tests to verify
7. Iterate if needed
8. Summarize what you did

Safety rules:
- Never modify files outside the workspace
- Be cautious with destructive commands (rm, del, git reset --hard)
- Don't expose secrets or credentials
- Preserve existing code conventions and style

You have access to these tools:
- read_file: Read file contents (supports line ranges for large files)
- write_file: Create or completely overwrite a file
- edit_file: Make targeted edits by replacing specific text
- list_files: Browse directory structure
- search_files: Search for content using regex
- find_files: Find files by name pattern
- run_command: Execute shell commands

Always strive to complete the task successfully. If you encounter errors, analyze them and try alternative approaches."""


class ContextManager:
    """Manages context building for the agent."""

    def __init__(self, workspace_dir: Path):
        """
        Initialize context manager.

        Args:
            workspace_dir: Workspace root directory
        """
        self.workspace_dir = workspace_dir
        self.project_info = self._detect_project_info()
        logger.info(f"Context manager initialized: {self.workspace_dir}")

    def _detect_project_info(self) -> Dict[str, Any]:
        """Detect basic project information."""
        info = {
            "name": self.workspace_dir.name,
            "type": "unknown",
            "detected_files": [],
        }

        # Detect project type by looking for common files
        detections = {
            "package.json": "Node.js",
            "pyproject.toml": "Python",
            "requirements.txt": "Python",
            "Cargo.toml": "Rust",
            "go.mod": "Go",
            "pom.xml": "Java/Maven",
            "build.gradle": "Java/Gradle",
            "composer.json": "PHP",
            "Gemfile": "Ruby",
            "*.csproj": ".NET",
        }

        for file_pattern, project_type in detections.items():
            if "*" in file_pattern:
                # Glob pattern
                if list(self.workspace_dir.glob(file_pattern)):
                    info["type"] = project_type
                    info["detected_files"].append(file_pattern)
                    break
            else:
                # Exact match
                if (self.workspace_dir / file_pattern).exists():
                    info["type"] = project_type
                    info["detected_files"].append(file_pattern)
                    break

        return info

    def build_system_context(self) -> str:
        """
        Build the system prompt with context.

        Returns:
            System prompt string
        """
        context_parts = [SYSTEM_PROMPT]

        # Add project information
        context_parts.append(f"\n\nCurrent project: {self.project_info['name']}")
        if self.project_info["type"] != "unknown":
            context_parts.append(f"Project type: {self.project_info['type']}")

        context_parts.append(f"Working directory: {self.workspace_dir}")

        return "\n".join(context_parts)

    def build_user_message(
        self,
        user_input: str,
        include_project_summary: bool = False,
    ) -> str:
        """
        Build a user message with optional context.

        Args:
            user_input: User's input/request
            include_project_summary: Whether to include project summary

        Returns:
            Enhanced user message
        """
        parts = []

        if include_project_summary:
            parts.append(f"Project: {self.project_info['name']}")
            if self.project_info["type"] != "unknown":
                parts.append(f"Type: {self.project_info['type']}")
            parts.append("")

        parts.append(user_input)

        return "\n".join(parts)

    def format_tool_result(self, tool_name: str, result: Any) -> str:
        """
        Format a tool result for inclusion in messages.

        Args:
            tool_name: Name of the tool that was executed
            result: Result from tool execution

        Returns:
            Formatted result string
        """
        if isinstance(result, dict):
            if not result.get("success", True):
                # Error result
                error = result.get("error", "Unknown error")
                return f"Tool '{tool_name}' failed: {error}"

            # Successful result
            if tool_name == "read_file":
                content = result.get("content", "")
                lines = result.get("lines", 0)
                path = result.get("path", "")
                return f"Read file: {path} ({lines} lines)\n\n{content}"

            elif tool_name == "write_file":
                path = result.get("path", "")
                action = result.get("action", "modified")
                return f"File {action}: {path}"

            elif tool_name == "edit_file":
                path = result.get("path", "")
                return f"Edited file: {path}"

            elif tool_name == "list_files":
                items = result.get("items", [])
                count = result.get("count", 0)
                return f"Listed {count} items:\n" + self._format_file_list(items)

            elif tool_name == "search_files":
                results = result.get("results", [])
                count = result.get("count", 0)
                truncated = result.get("truncated", False)
                
                if count == 0:
                    return "No matches found"
                
                output = f"Found {count} matches"
                if truncated:
                    output += " (truncated)"
                output += ":\n\n"
                
                for match in results[:20]:  # Limit display
                    output += f"{match['file']}:{match['line']}: {match['content']}\n"
                
                if len(results) > 20:
                    output += f"\n... and {len(results) - 20} more matches"
                
                return output

            elif tool_name == "find_files":
                files = result.get("files", [])
                count = result.get("count", 0)
                return f"Found {count} files:\n" + "\n".join(f"  {f}" for f in files[:50])

            elif tool_name == "run_command":
                cmd = result.get("command", "")
                exit_code = result.get("exit_code", -1)
                stdout = result.get("stdout", "")
                stderr = result.get("stderr", "")
                duration = result.get("duration", 0)

                output = f"Executed: {cmd}\n"
                output += f"Exit code: {exit_code}\n"
                output += f"Duration: {duration}s\n"

                if stdout:
                    output += f"\nStdout:\n{stdout}"
                if stderr:
                    output += f"\nStderr:\n{stderr}"

                return output

            else:
                # Generic result formatting
                import json
                return json.dumps(result, indent=2)

        return str(result)

    def _format_file_list(self, items: List[Dict[str, Any]], indent: int = 0) -> str:
        """Format file list recursively."""
        output = []
        prefix = "  " * indent

        for item in items:
            name = item.get("name", "")
            item_type = item.get("type", "file")
            
            if item_type == "directory":
                output.append(f"{prefix}📁 {name}/")
                children = item.get("children", [])
                if children:
                    output.append(self._format_file_list(children, indent + 1))
            else:
                size = item.get("size", 0)
                output.append(f"{prefix}📄 {name} ({self._format_size(size)})")

        return "\n".join(output)

    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"

    def summarize_session(self, state: Any) -> str:
        """
        Summarize the current session.

        Args:
            state: AgentState instance

        Returns:
            Session summary string
        """
        summary = []
        summary.append(f"Session Summary:")
        summary.append(f"  Iterations: {state.iteration_count}/{state.max_iterations}")
        summary.append(f"  Tool calls: {len(state.tool_calls)}")

        if state.files_changed:
            summary.append(f"\nFiles modified: {len(state.files_changed)}")
            for file in state.files_changed[:10]:
                summary.append(f"  • {file}")
            if len(state.files_changed) > 10:
                summary.append(f"  ... and {len(state.files_changed) - 10} more")

        if state.files_created:
            summary.append(f"\nFiles created: {len(state.files_created)}")
            for file in state.files_created[:10]:
                summary.append(f"  • {file}")

        if state.commands_executed:
            summary.append(f"\nCommands executed: {len(state.commands_executed)}")
            for cmd in state.commands_executed[-5:]:
                summary.append(f"  • {cmd}")

        return "\n".join(summary)
