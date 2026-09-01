"""Agent state management."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class AgentState:
    """Represents the state of an agent session."""

    # Session metadata
    workspace_dir: Path
    provider: str
    model: str

    # Conversation
    messages: List[Dict[str, Any]] = field(default_factory=list)

    # Execution tracking
    iteration_count: int = 0
    max_iterations: int = 50
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    files_changed: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    files_deleted: List[str] = field(default_factory=list)
    commands_executed: List[str] = field(default_factory=list)

    # Test results
    last_test_result: Optional[Dict[str, Any]] = None

    # Permission decisions
    permission_cache: Dict[str, str] = field(default_factory=dict)

    def add_message(self, role: str, content: Any) -> None:
        """Add a message to the conversation."""
        if isinstance(content, dict):
            # Store entire dict as-is (for tool calls, tool results, etc.)
            self.messages.append({"role": role, **content})
        else:
            # Simple string content
            self.messages.append({"role": role, "content": content})

    def add_tool_call(self, tool_name: str, args: Dict[str, Any], result: Any) -> None:
        """Record a tool call."""
        self.tool_calls.append({"tool": tool_name, "args": args, "result": result})

    def record_file_change(self, path: str, action: str = "modified") -> None:
        """Record a file change."""
        if action == "created":
            self.files_created.append(path)
        elif action == "deleted":
            self.files_deleted.append(path)
        elif action == "modified":
            if path not in self.files_changed:
                self.files_changed.append(path)

    def record_command(self, command: str) -> None:
        """Record a command execution."""
        self.commands_executed.append(command)

    def increment_iteration(self) -> None:
        """Increment the iteration counter."""
        self.iteration_count += 1

    def has_reached_limit(self) -> bool:
        """Check if iteration limit has been reached."""
        return self.iteration_count >= self.max_iterations

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the session."""
        return {
            "iterations": self.iteration_count,
            "tool_calls": len(self.tool_calls),
            "files_changed": len(self.files_changed),
            "files_created": len(self.files_created),
            "files_deleted": len(self.files_deleted),
            "commands_executed": len(self.commands_executed),
        }
