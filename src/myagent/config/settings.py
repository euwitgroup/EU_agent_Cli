"""Configuration settings for MyAgent."""

import logging
from pathlib import Path
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """MyAgent configuration settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Provider Configuration
    myagent_provider: Literal["openai", "anthropic", "custom"] = Field(
        default="anthropic", description="AI provider to use"
    )

    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1", description="OpenAI API base URL"
    )
    openai_model: str = Field(default="gpt-4-turbo-preview", description="OpenAI model name")

    # Anthropic
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    anthropic_model: str = Field(
        default="claude-3-5-sonnet-20241022", description="Anthropic model name"
    )

    # Custom Provider
    custom_api_key: Optional[str] = Field(default=None, description="Custom provider API key")
    custom_base_url: Optional[str] = Field(
        default=None, description="Custom provider base URL"
    )
    custom_model: Optional[str] = Field(default=None, description="Custom provider model name")

    # Agent Configuration
    myagent_max_iterations: int = Field(
        default=50, description="Maximum agent loop iterations", ge=1, le=200
    )
    myagent_command_timeout: int = Field(
        default=120, description="Command execution timeout in seconds", ge=1
    )
    myagent_auto_approve_reads: bool = Field(
        default=True, description="Auto-approve read operations"
    )

    # API Retry Configuration
    myagent_max_retries: int = Field(
        default=3, description="Maximum API retry attempts on rate limits", ge=0, le=10
    )
    myagent_initial_retry_delay: float = Field(
        default=1.0, description="Initial retry delay in seconds", ge=0.1, le=10.0
    )
    myagent_max_retry_delay: float = Field(
        default=60.0, description="Maximum retry delay in seconds", ge=1.0, le=300.0
    )

    # Logging
    myagent_log_level: str = Field(default="INFO", description="Logging level")

    # Runtime overrides (set via CLI)
    provider_override: Optional[str] = None
    model_override: Optional[str] = None
    cwd_override: Optional[Path] = None
    verbose: bool = False
    no_color: bool = False

    def get_provider(self) -> str:
        """Get the active provider considering CLI overrides."""
        return self.provider_override or self.myagent_provider

    def get_model(self) -> str:
        """Get the active model considering CLI overrides."""
        if self.model_override:
            return self.model_override

        provider = self.get_provider()
        if provider == "openai":
            return self.openai_model
        elif provider == "anthropic":
            return self.anthropic_model
        elif provider == "custom":
            return self.custom_model or "unknown"
        return "unknown"

    def get_api_key(self) -> Optional[str]:
        """Get the API key for the active provider."""
        provider = self.get_provider()
        if provider == "openai":
            return self.openai_api_key
        elif provider == "anthropic":
            return self.anthropic_api_key
        elif provider == "custom":
            return self.custom_api_key
        return None

    def get_base_url(self) -> Optional[str]:
        """Get the base URL for the active provider."""
        provider = self.get_provider()
        if provider == "openai":
            return self.openai_base_url
        elif provider == "custom":
            return self.custom_base_url
        return None

    def get_log_level(self) -> int:
        """Get the logging level as an integer."""
        if self.verbose:
            return logging.DEBUG
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return level_map.get(self.myagent_log_level.upper(), logging.INFO)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Reset the global settings instance (useful for testing)."""
    global _settings
    _settings = None
