"""Custom OpenAI-compatible provider implementation."""

import logging
from typing import AsyncIterator, List, Optional

from myagent.providers.base import GenerateResponse, Message, ToolDefinition
from myagent.providers.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class CustomProvider(OpenAIProvider):
    """
    Custom provider for OpenAI-compatible APIs.

    This provider extends OpenAIProvider and can work with any
    OpenAI-compatible endpoint by specifying a custom base_url.
    """

    def __init__(self, api_key: str, model: str, base_url: str, **kwargs):
        """
        Initialize custom provider.

        Args:
            api_key: API key for the custom provider
            model: Model name to use
            base_url: Base URL for the API endpoint
            **kwargs: Additional configuration
        """
        if not base_url:
            raise ValueError("Custom provider requires a base_url")

        super().__init__(api_key=api_key, model=model, base_url=base_url, **kwargs)
        logger.info(f"Custom provider initialized: {base_url}")

    def validate_config(self) -> bool:
        """Validate custom provider configuration."""
        if not self.api_key:
            raise ValueError("API key is required")
        if not self.model:
            raise ValueError("Model name is required")
        if not self.base_url:
            raise ValueError("Base URL is required for custom provider")
        return True

    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "custom"
