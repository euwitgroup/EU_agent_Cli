"""Tool registry for managing available tools."""

import logging
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Tool(BaseModel):
    """Represents a tool that can be called by the agent."""

    model_config = {"arbitrary_types_allowed": True}

    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Any = None  # Actual function, not serialized
    permission_category: str = "general"


class ToolRegistry:
    """Registry for managing and executing tools."""

    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, Tool] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable,
        permission_category: str = "general",
    ) -> None:
        """
        Register a new tool.

        Args:
            name: Tool name
            description: Tool description
            parameters: JSON schema for tool parameters
            handler: Function to execute the tool
            permission_category: Permission category for safety checks
        """
        if name in self._tools:
            logger.warning(f"Tool '{name}' already registered, overwriting")

        tool = Tool(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler,
            permission_category=permission_category,
        )

        self._tools[name] = tool
        logger.debug(f"Registered tool: {name}")

    def unregister(self, name: str) -> bool:
        """
        Unregister a tool.

        Args:
            name: Tool name to unregister

        Returns:
            True if tool was unregistered, False if not found
        """
        if name in self._tools:
            del self._tools[name]
            logger.debug(f"Unregistered tool: {name}")
            return True
        return False

    def get(self, name: str) -> Optional[Tool]:
        """
        Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(name)

    def list(self) -> List[Tool]:
        """
        Get all registered tools.

        Returns:
            List of all tools
        """
        return list(self._tools.values())

    def list_names(self) -> List[str]:
        """
        Get names of all registered tools.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def get_definitions(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions for AI providers.

        Returns:
            List of tool definitions (name, description, parameters)
        """
        return [
            {"name": tool.name, "description": tool.description, "parameters": tool.parameters}
            for tool in self._tools.values()
        ]

    def execute(self, name: str, **kwargs) -> Any:
        """
        Execute a tool by name.

        Args:
            name: Tool name
            **kwargs: Tool arguments

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found
            Exception: If tool execution fails
        """
        tool = self.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")

        logger.debug(f"Executing tool: {name} with args: {list(kwargs.keys())}")

        try:
            result = tool.handler(**kwargs)
            logger.debug(f"Tool '{name}' executed successfully")
            return result
        except Exception as e:
            logger.error(f"Tool '{name}' execution failed: {e}")
            raise

    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()
        logger.debug("Cleared all tools from registry")


# Global registry instance
_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    """Get or create the global tool registry."""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry


def reset_registry() -> None:
    """Reset the global registry (useful for testing)."""
    global _registry
    _registry = None
