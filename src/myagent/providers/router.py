"""Provider router for selecting and instantiating providers."""

import logging
from typing import Optional

from myagent.config import get_settings
from myagent.providers.anthropic_provider import AnthropicProvider
from myagent.providers.base import AIProvider
from myagent.providers.custom import CustomProvider
from myagent.providers.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class ProviderRouter:
    """Router for managing AI provider selection and instantiation."""

    @staticmethod
    def create_provider(
        provider_name: Optional[str] = None, model_name: Optional[str] = None
    ) -> AIProvider:
        """
        Create and return an AI provider instance.

        Args:
            provider_name: Provider to use (openai, anthropic, custom). If None, uses config.
            model_name: Model name to use. If None, uses config.

        Returns:
            Configured AIProvider instance

        Raises:
            ValueError: If provider is not supported or configuration is invalid
        """
        settings = get_settings()

        # Determine provider and model
        provider = provider_name or settings.get_provider()
        model = model_name or settings.get_model()

        logger.info(f"Creating provider: {provider}, model: {model}")

        # Prepare common kwargs with retry settings
        provider_kwargs = {
            "max_retries": settings.myagent_max_retries,
            "initial_retry_delay": settings.myagent_initial_retry_delay,
            "max_retry_delay": settings.myagent_max_retry_delay,
        }

        # Create appropriate provider
        if provider == "openai":
            api_key = settings.openai_api_key
            base_url = settings.openai_base_url

            if not api_key:
                raise ValueError(
                    "OpenAI API key not found. Set OPENAI_API_KEY environment variable."
                )

            return OpenAIProvider(
                api_key=api_key, model=model, base_url=base_url, **provider_kwargs
            )

        elif provider == "anthropic":
            api_key = settings.anthropic_api_key

            if not api_key:
                raise ValueError(
                    "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable."
                )

            return AnthropicProvider(api_key=api_key, model=model, **provider_kwargs)

        elif provider == "custom":
            api_key = settings.custom_api_key
            base_url = settings.custom_base_url

            if not api_key:
                raise ValueError(
                    "Custom API key not found. Set CUSTOM_API_KEY environment variable."
                )

            if not base_url:
                raise ValueError(
                    "Custom base URL not found. Set CUSTOM_BASE_URL environment variable."
                )

            return CustomProvider(
                api_key=api_key, model=model, base_url=base_url, **provider_kwargs
            )

        else:
            raise ValueError(
                f"Unsupported provider: {provider}. Supported: openai, anthropic, custom"
            )

    @staticmethod
    def get_available_providers() -> list[str]:
        """Get list of available provider names."""
        return ["openai", "anthropic", "custom"]

    @staticmethod
    def validate_provider_config(provider_name: str) -> bool:
        """
        Validate that a provider has required configuration.

        Args:
            provider_name: Provider to validate

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is missing or invalid
        """
        settings = get_settings()

        if provider_name == "openai":
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key is required")
            return True

        elif provider_name == "anthropic":
            if not settings.anthropic_api_key:
                raise ValueError("Anthropic API key is required")
            return True

        elif provider_name == "custom":
            if not settings.custom_api_key:
                raise ValueError("Custom API key is required")
            if not settings.custom_base_url:
                raise ValueError("Custom base URL is required")
            if not settings.custom_model:
                raise ValueError("Custom model name is required")
            return True

        else:
            raise ValueError(f"Unknown provider: {provider_name}")
