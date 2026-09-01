"""Anthropic provider implementation."""

import json
import logging
import time
from typing import Any, AsyncIterator, Dict, List, Optional

from anthropic import Anthropic, RateLimitError

from myagent.providers.base import (
    AIProvider,
    GenerateResponse,
    Message,
    ToolCall,
    ToolDefinition,
)

logger = logging.getLogger(__name__)


class AnthropicProvider(AIProvider):
    """Anthropic (Claude) API provider."""

    def __init__(self, api_key: str, model: str, **kwargs):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key
            model: Model name (e.g., "claude-3-5-sonnet-20241022")
            **kwargs: Additional configuration
        """
        super().__init__(api_key, model, **kwargs)
        
        # Retry configuration
        self.max_retries = kwargs.get("max_retries", 3)
        self.initial_retry_delay = kwargs.get("initial_retry_delay", 1.0)
        self.max_retry_delay = kwargs.get("max_retry_delay", 60.0)
        
        self.client = Anthropic(api_key=api_key)

    def validate_config(self) -> bool:
        """Validate Anthropic configuration."""
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        if not self.model:
            raise ValueError("Model name is required")
        return True

    def _convert_messages(self, messages: List[Message]) -> tuple[Optional[str], List[Dict[str, Any]]]:
        """
        Convert internal messages to Anthropic format.

        Returns:
            Tuple of (system_prompt, messages_list)
        """
        system_prompt = None
        anthropic_messages = []

        for msg in messages:
            # Extract system message separately
            if msg.role == "system":
                system_prompt = msg.content
                continue

            anthropic_msg = {"role": msg.role}

            # Handle content
            if msg.content:
                anthropic_msg["content"] = msg.content

            # Handle tool calls (assistant messages with tool use)
            if msg.tool_calls:
                content_blocks = []
                if msg.content:
                    content_blocks.append({"type": "text", "text": msg.content})

                for tc in msg.tool_calls:
                    content_blocks.append(
                        {
                            "type": "tool_use",
                            "id": tc.id,
                            "name": tc.name,
                            "input": tc.arguments,
                        }
                    )
                anthropic_msg["content"] = content_blocks

            # Handle tool results (user messages with tool results)
            if msg.tool_call_id:
                anthropic_msg["role"] = "user"
                anthropic_msg["content"] = [
                    {
                        "type": "tool_result",
                        "tool_use_id": msg.tool_call_id,
                        "content": msg.content or "",
                    }
                ]

            anthropic_messages.append(anthropic_msg)

        return system_prompt, anthropic_messages

    def _convert_tools(self, tools: List[ToolDefinition]) -> List[Dict[str, Any]]:
        """Convert internal tool definitions to Anthropic format."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.parameters,
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
                response = self.client.messages.create(**params)
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
                logger.error(f"Anthropic API error: {e}")
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
        """Generate a response using Anthropic API with automatic retry on rate limits."""
        self.validate_config()

        try:
            # Convert messages
            system_prompt, anthropic_messages = self._convert_messages(messages)

            # Build request parameters
            params = {
                "model": self.model,
                "messages": anthropic_messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 4096,  # Anthropic requires max_tokens
            }

            if system_prompt:
                params["system"] = system_prompt

            if tools:
                params["tools"] = self._convert_tools(tools)

            logger.debug(f"Anthropic request: {params['model']}, messages={len(anthropic_messages)}")

            # Make API call with retry logic
            response = self._make_request_with_retry(params)

            # Parse response
            content_text = None
            tool_calls = []

            for block in response.content:
                if block.type == "text":
                    content_text = block.text
                elif block.type == "tool_use":
                    tool_calls.append(
                        ToolCall(id=block.id, name=block.name, arguments=block.input)
                    )

            # Extract usage
            usage = None
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                }

            # Map stop reason
            finish_reason = "stop"
            if response.stop_reason == "tool_use":
                finish_reason = "tool_calls"
            elif response.stop_reason == "max_tokens":
                finish_reason = "length"
            elif response.stop_reason:
                finish_reason = response.stop_reason

            return GenerateResponse(
                content=content_text,
                tool_calls=tool_calls,
                finish_reason=finish_reason,
                model=response.model,
                usage=usage,
            )

        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            raise

    async def generate_stream(
        self,
        messages: List[Message],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Generate a streaming response using Anthropic API."""
        self.validate_config()

        try:
            # Convert messages
            system_prompt, anthropic_messages = self._convert_messages(messages)

            # Build request parameters
            params = {
                "model": self.model,
                "messages": anthropic_messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 4096,
                "stream": True,
            }

            if system_prompt:
                params["system"] = system_prompt

            if tools:
                params["tools"] = self._convert_tools(tools)

            logger.debug(f"Anthropic streaming request: {params['model']}")

            # Make streaming API call
            with self.client.messages.stream(**params) as stream:
                for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            raise
