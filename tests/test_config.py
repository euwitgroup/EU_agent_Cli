"""Tests for configuration module."""

import pytest
import os
from myagent.config import Settings, get_settings, reset_settings


@pytest.fixture
def clean_env(monkeypatch):
    """Clean environment fixture that removes provider-related env vars."""
    monkeypatch.delenv('MYAGENT_PROVIDER', raising=False)
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    monkeypatch.delenv('ANTHROPIC_API_KEY', raising=False)
    monkeypatch.delenv('CUSTOM_API_KEY', raising=False)
    reset_settings()


def test_settings_defaults(clean_env, monkeypatch):
    """Test default configuration values."""
    #Prevent loading .env file
    monkeypatch.setenv('MYAGENT_PROVIDER', 'anthropic')
    reset_settings()
    settings = Settings()

    assert settings.myagent_provider == "anthropic"
    assert settings.myagent_max_iterations == 50
    assert settings.myagent_command_timeout == 120
    assert settings.myagent_auto_approve_reads is True


def test_settings_provider_override(clean_env, monkeypatch):
    """Test provider override functionality."""
    monkeypatch.setenv('MYAGENT_PROVIDER', 'anthropic')
    reset_settings()
    settings = Settings()

    assert settings.get_provider() == "anthropic"

    settings.provider_override = "openai"
    assert settings.get_provider() == "openai"


def test_settings_model_selection():
    """Test model selection based on provider."""
    reset_settings()
    settings = Settings()

    settings.myagent_provider = "openai"
    assert settings.get_model() == settings.openai_model

    settings.myagent_provider = "anthropic"
    assert settings.get_model() == settings.anthropic_model


def test_settings_model_override():
    """Test model override functionality."""
    reset_settings()
    settings = Settings()

    settings.model_override = "custom-model"
    assert settings.get_model() == "custom-model"


def test_settings_api_key_retrieval():
    """Test API key retrieval for different providers."""
    reset_settings()
    settings = Settings()

    settings.openai_api_key = "test-openai-key"
    settings.anthropic_api_key = "test-anthropic-key"
    settings.custom_api_key = "test-custom-key"

    settings.myagent_provider = "openai"
    assert settings.get_api_key() == "test-openai-key"

    settings.myagent_provider = "anthropic"
    assert settings.get_api_key() == "test-anthropic-key"

    settings.myagent_provider = "custom"
    assert settings.get_api_key() == "test-custom-key"


def test_get_settings_singleton():
    """Test that get_settings returns the same instance."""
    reset_settings()
    settings1 = get_settings()
    settings2 = get_settings()

    assert settings1 is settings2


def test_reset_settings():
    """Test settings reset functionality."""
    reset_settings()
    settings1 = get_settings()
    settings1.provider_override = "test"

    reset_settings()
    settings2 = get_settings()

    assert settings2.provider_override is None
