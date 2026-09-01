"""Base provider interface for AI providers."""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional

from pydantic import BaseModel


class ToolDefinition(BaseModel):
    """Tool definition for function calling."""

    name: str
    description: str
    parameters: Dict[str, Any]


class ToolCall(BaseModel):
    """Represents a tool call from the model."""

    id: str
    name: str
    arguments: Dict[str, Any]


class Message(BaseModel):
    """Represents a message in the conversation."""

    role: str  # "user", "assistant", "system"
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None  # For tool results


class GenerateResponse(BaseModel):
    """Response from a generation request."""

    content: Optional[str] = None
    tool_calls: List[ToolCall] = []
    finish_reason: str  # "stop", "tool_calls", "length", etc.
    model: str
    usage: Optional[Dict[str, int]] = None


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, api_key: str, model: str, **kwargs):
        """
        Initialize the provider.

        Args:
            api_key: API key for authentication
            model: Model name to use
            **kwargs: Additional provider-specific parameters
        """
        self.api_key = api_key
        self.model = model
        self.config = kwargs

    @abstractmethod
    def generate(
        self,
        messages: List[Message],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> GenerateResponse:
        """
        Generate a response from the model.

        Args:
            messages: Conversation messages
            tools: Available tools for function calling
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            GenerateResponse with content and/or tool calls
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Message],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """
        Generate a streaming response from the model.

        Args:
            messages: Conversation messages
            tools: Available tools for function calling
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Content chunks as they arrive
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate provider configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        pass

    def get_provider_name(self) -> str:
        """Get the provider name."""
        return self.__class__.__name__.replace("Provider", "").lower()
