"""OpenAI provider implementation."""

import json
import logging
import time
from typing import Any, AsyncIterator, Dict, List, Optional

from openai import OpenAI, RateLimitError

from myagent.providers.base import (
    AIProvider,
    GenerateResponse,
    Message,
    ToolCall,
    ToolDefinition,
)

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: str, model: str, base_url: Optional[str] = None, **kwargs):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model name (e.g., "gpt-4-turbo-preview")
            base_url: Optional base URL for API (for OpenAI-compatible endpoints)
            **kwargs: Additional configuration
        """
        super().__init__(api_key, model, **kwargs)
        self.base_url = base_url

        # Retry configuration
        self.max_retries = kwargs.get("max_retries", 3)
        self.initial_retry_delay = kwargs.get("initial_retry_delay", 1.0)
        self.max_retry_delay = kwargs.get("max_retry_delay", 60.0)

        # Initialize client
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        self.client = OpenAI(**client_kwargs)

    def validate_config(self) -> bool:
        """Validate OpenAI configuration."""
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        if not self.model:
            raise ValueError("Model name is required")
        return True

    def _convert_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert internal messages to OpenAI format."""
        openai_messages = []

        for msg in messages:
            openai_msg = {"role": msg.role}

            if msg.content:
                openai_msg["content"] = msg.content

            # Handle tool calls in assistant messages
            if msg.tool_calls:
                openai_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)},
                    }
                    for tc in msg.tool_calls
                ]

            # Handle tool results
            if msg.tool_call_id:
                openai_msg["tool_call_id"] = msg.tool_call_id
                openai_msg["role"] = "tool"

            openai_messages.append(openai_msg)

        return openai_messages

    def _convert_tools(self, tools: List[ToolDefinition]) -> List[Dict[str, Any]]:
        """Convert internal tool definitions to OpenAI format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in tools
        ]

    def _make_request_with_retry(self, params: Dict[str, Any]) -> Any:
        """
        Make API request with exponential backoff retry logic.
        
        Args:
            params: Request parameters
            
        Returns:
            API response
            
        Raises:
            Exception: If all retries fail
        """
        last_exception = None
        retry_delay = self.initial_retry_delay
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(**params)
                return response
                
            except RateLimitError as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    logger.warning(
                        f"Rate limit hit (attempt {attempt + 1}/{self.max_retries + 1}). "
                        f"Retrying in {retry_delay:.1f}s..."
                    )
                    time.sleep(retry_delay)
                    
                    # Exponential backoff with jitter
                    retry_delay = min(retry_delay * 2, self.max_retry_delay)
                else:
                    logger.error(f"Rate limit exceeded after {self.max_retries + 1} attempts")
                    raise
                    
            except Exception as e:
                # Don't retry on other errors
                logger.error(f"OpenAI API error: {e}")
                raise
        
        # Should never reach here, but just in case
        if last_exception:
            raise last_exception

    def generate(
        self,
        messages: List[Message],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> GenerateResponse:
        """Generate a response using OpenAI API with automatic retry on rate limits."""
        self.validate_config()

        try:
            # Convert messages and tools
            openai_messages = self._convert_messages(messages)

            # Build request parameters
            params = {
                "model": self.model,
                "messages": openai_messages,
                "temperature": temperature,
            }

            if max_tokens:
                params["max_tokens"] = max_tokens

            if tools:
                params["tools"] = self._convert_tools(tools)

            logger.debug(f"OpenAI request: {params['model']}, messages={len(openai_messages)}")

            # Make API call with retry logic
            response = self._make_request_with_retry(params)

            # Parse response
            message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason

            # Extract content
            content = message.content if message.content else None

            # Extract tool calls
            tool_calls = []
            if message.tool_calls:
                for tc in message.tool_calls:
                    try:
                        arguments = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse tool arguments: {tc.function.arguments}")
                        arguments = {}

                    tool_calls.append(
                        ToolCall(id=tc.id, name=tc.function.name, arguments=arguments)
                    )

            # Extract usage
            usage = None
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            return GenerateResponse(
                content=content,
                tool_calls=tool_calls,
                finish_reason=finish_reason,
                model=response.model,
                usage=usage,
            )

        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise

    async def generate_stream(
        self,
        messages: List[Message],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Generate a streaming response using OpenAI API."""
        self.validate_config()

        try:
            # Convert messages and tools
            openai_messages = self._convert_messages(messages)

            # Build request parameters
            params = {
                "model": self.model,
                "messages": openai_messages,
                "temperature": temperature,
                "stream": True,
            }

            if max_tokens:
                params["max_tokens"] = max_tokens

            if tools:
                params["tools"] = self._convert_tools(tools)

            logger.debug(f"OpenAI streaming request: {params['model']}")

            # Make streaming API call
            stream = self.client.chat.completions.create(**params)

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise
