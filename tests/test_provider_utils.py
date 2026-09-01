"""Tests for provider utility functions."""

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from myagent.providers.utils import (
    check_provider_connection,
    list_models_from_provider,
    save_provider_config,
)


class TestProviderConnection:
    """Tests for test_provider_connection."""

    @pytest.mark.asyncio
    async def test_successful_connection(self):
        """Test successful provider connection."""
        with patch("myagent.providers.utils.ProviderRouter") as mock_router_class:
            mock_router = MagicMock()
            mock_router_class.return_value = mock_router

            mock_provider = MagicMock()
            mock_provider.get_provider_name.return_value = "openai"

            # Mock generate response
            mock_response = MagicMock()
            mock_response.content = "Hello! This is a test response."
            mock_provider.generate = AsyncMock(return_value=mock_response)

            mock_router.create_provider.return_value = mock_provider

            result = await check_provider_connection(
                provider="openai",
                api_key="test-key",
                model="gpt-4",
            )

            assert result["success"] is True
            assert result["provider"] == "openai"
            assert result["model"] == "gpt-4"
            assert result["error"] is None
            assert "Hello" in result["response_text"]

    @pytest.mark.asyncio
    async def test_failed_connection(self):
        """Test failed provider connection."""
        with patch("myagent.providers.utils.ProviderRouter") as mock_router_class:
            mock_router = MagicMock()
            mock_router_class.return_value = mock_router
            mock_router.validate_provider_config.side_effect = ValueError("Invalid API key")

            result = await check_provider_connection(
                provider="openai",
                api_key="invalid",
                model="gpt-4",
            )

            assert result["success"] is False
            assert result["provider"] == "openai"
            assert result["error"] == "Invalid API key"

    @pytest.mark.asyncio
    async def test_custom_provider_connection(self):
        """Test custom provider connection with base_url."""
        with patch("myagent.providers.utils.ProviderRouter") as mock_router_class:
            mock_router = MagicMock()
            mock_router_class.return_value = mock_router

            mock_provider = MagicMock()
            mock_provider.get_provider_name.return_value = "custom"

            mock_response = MagicMock()
            mock_response.content = "Custom response"
            mock_provider.generate = AsyncMock(return_value=mock_response)

            mock_router.create_provider.return_value = mock_provider

            result = await check_provider_connection(
                provider="custom",
                api_key="test-key",
                model="custom-model",
                base_url="https://api.custom.com/v1",
            )

            assert result["success"] is True
            assert result["provider"] == "custom"
            assert result["model"] == "custom-model"


class TestListModels:
    """Tests for list_models_from_provider."""

    @pytest.mark.asyncio
    async def test_list_openai_models(self):
        """Test listing OpenAI models."""
        with patch("openai.OpenAI") as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            # Mock models response
            mock_model1 = MagicMock()
            mock_model1.id = "gpt-4"
            mock_model2 = MagicMock()
            mock_model2.id = "gpt-3.5-turbo"

            mock_response = MagicMock()
            mock_response.data = [mock_model1, mock_model2]
            mock_client.models.list.return_value = mock_response

            result = await list_models_from_provider(
                provider="openai",
                api_key="test-key",
            )

            assert result["success"] is True
            assert result["provider"] == "openai"
            assert result["count"] == 2
            assert "gpt-4" in result["models"]
            assert "gpt-3.5-turbo" in result["models"]

    @pytest.mark.asyncio
    async def test_list_anthropic_models(self):
        """Test listing Anthropic models (returns known models)."""
        result = await list_models_from_provider(
            provider="anthropic",
            api_key="test-key",
        )

        assert result["success"] is True
        assert result["provider"] == "anthropic"
        assert result["count"] > 0
        assert "claude-3-5-sonnet-20241022" in result["models"]
        assert result.get("note") is not None

    @pytest.mark.asyncio
    async def test_list_custom_models(self):
        """Test listing custom provider models."""
        with patch("openai.OpenAI") as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            mock_model = MagicMock()
            mock_model.id = "llama-3-70b"

            mock_response = MagicMock()
            mock_response.data = [mock_model]
            mock_client.models.list.return_value = mock_response

            result = await list_models_from_provider(
                provider="custom",
                api_key="test-key",
                base_url="https://custom.com/v1",
            )

            assert result["success"] is True
            assert result["provider"] == "custom"
            assert "llama-3-70b" in result["models"]

    @pytest.mark.asyncio
    async def test_list_models_error(self):
        """Test error handling when listing models."""
        with patch("openai.OpenAI") as mock_openai_class:
            mock_openai_class.side_effect = Exception("API Error")

            result = await list_models_from_provider(
                provider="openai",
                api_key="test-key",
            )

            assert result["success"] is False
            assert result["error"] == "API Error"

    @pytest.mark.asyncio
    async def test_list_models_unsupported_provider(self):
        """Test listing models with unsupported provider."""
        result = await list_models_from_provider(
            provider="unsupported",
            api_key="test-key",
        )

        assert result["success"] is False
        assert "Unsupported provider" in result["error"]


class TestSaveProviderConfig:
    """Tests for save_provider_config."""

    def test_save_new_config(self, tmp_path):
        """Test saving new provider configuration."""
        env_file = tmp_path / ".env"

        success = save_provider_config(
            provider="openai",
            api_key="test-key",
            model="gpt-4",
            env_file=str(env_file),
        )

        assert success is True
        assert env_file.exists()

        content = env_file.read_text()
        assert "MYAGENT_PROVIDER=openai" in content
        assert "OPENAI_API_KEY=test-key" in content
        assert "OPENAI_MODEL=gpt-4" in content

    def test_save_custom_provider_config(self, tmp_path):
        """Test saving custom provider configuration with base_url."""
        env_file = tmp_path / ".env"

        success = save_provider_config(
            provider="custom",
            api_key="test-key",
            model="llama-3",
            base_url="https://custom.com/v1",
            env_file=str(env_file),
        )

        assert success is True

        content = env_file.read_text()
        assert "MYAGENT_PROVIDER=custom" in content
        assert "CUSTOM_API_KEY=test-key" in content
        assert "CUSTOM_MODEL=llama-3" in content
        assert "CUSTOM_BASE_URL=https://custom.com/v1" in content

    def test_update_existing_config(self, tmp_path):
        """Test updating existing configuration."""
        env_file = tmp_path / ".env"

        # Create initial config
        env_file.write_text(
            "MYAGENT_PROVIDER=openai\n"
            "OPENAI_API_KEY=old-key\n"
            "OPENAI_MODEL=gpt-3.5-turbo\n"
            "OTHER_VAR=keep-this\n"
        )

        # Update config
        success = save_provider_config(
            provider="openai",
            api_key="new-key",
            model="gpt-4",
            env_file=str(env_file),
        )

        assert success is True

        content = env_file.read_text()
        assert "OPENAI_API_KEY=new-key" in content
        assert "OPENAI_MODEL=gpt-4" in content
        assert "OTHER_VAR=keep-this" in content
        assert "old-key" not in content

    def test_save_config_error(self):
        """Test error handling when saving config."""
        # Try to save to invalid path
        success = save_provider_config(
            provider="openai",
            api_key="test-key",
            model="gpt-4",
            env_file="/invalid/path/.env",
        )

        assert success is False
