"""Tests for providers module."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from myagent.config import reset_settings, Settings
from myagent.providers import (
    AIProvider,
    Message,
    ToolCall,
    ToolDefinition,
    GenerateResponse,
    OpenAIProvider,
    AnthropicProvider,
    CustomProvider,
    ProviderRouter,
)


@pytest.fixture(autouse=True)
def reset_config():
    """Reset settings before each test."""
    reset_settings()


def test_message_creation():
    """Test Message model creation."""
    msg = Message(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert msg.tool_calls is None


def test_tool_call_creation():
    """Test ToolCall model creation."""
    tool_call = ToolCall(id="call_123", name="test_tool", arguments={"arg": "value"})
    assert tool_call.id == "call_123"
    assert tool_call.name == "test_tool"
    assert tool_call.arguments == {"arg": "value"}


def test_tool_definition_creation():
    """Test ToolDefinition model creation."""
    tool_def = ToolDefinition(
        name="test_tool",
        description="A test tool",
        parameters={"type": "object", "properties": {}},
    )
    assert tool_def.name == "test_tool"
    assert tool_def.description == "A test tool"


def test_generate_response_creation():
    """Test GenerateResponse model creation."""
    response = GenerateResponse(
        content="Response text",
        tool_calls=[],
        finish_reason="stop",
        model="test-model",
    )
    assert response.content == "Response text"
    assert response.finish_reason == "stop"
    assert response.model == "test-model"


class TestOpenAIProvider:
    """Tests for OpenAI provider."""

    def test_initialization(self):
        """Test OpenAI provider initialization."""
        provider = OpenAIProvider(api_key="test-key", model="gpt-4")
        assert provider.api_key == "test-key"
        assert provider.model == "gpt-4"
        assert provider.client is not None

    def test_initialization_with_base_url(self):
        """Test OpenAI provider with custom base URL."""
        provider = OpenAIProvider(
            api_key="test-key", model="gpt-4", base_url="https://custom.api/v1"
        )
        assert provider.base_url == "https://custom.api/v1"

    def test_validate_config_success(self):
        """Test successful configuration validation."""
        provider = OpenAIProvider(api_key="test-key", model="gpt-4")
        assert provider.validate_config() is True

    def test_validate_config_missing_key(self):
        """Test configuration validation with missing API key."""
        # OpenAI client validates on init, so we test our validation separately
        with patch("myagent.providers.openai_provider.OpenAI"):
            provider = OpenAIProvider(api_key="", model="gpt-4")
            with pytest.raises(ValueError, match="API key is required"):
                provider.validate_config()

    def test_validate_config_missing_model(self):
        """Test configuration validation with missing model."""
        provider = OpenAIProvider(api_key="test-key", model="")
        with pytest.raises(ValueError, match="Model name is required"):
            provider.validate_config()

    def test_convert_messages(self):
        """Test message conversion to OpenAI format."""
        provider = OpenAIProvider(api_key="test-key", model="gpt-4")
        messages = [
            Message(role="system", content="You are helpful"),
            Message(role="user", content="Hello"),
        ]
        converted = provider._convert_messages(messages)
        assert len(converted) == 2
        assert converted[0]["role"] == "system"
        assert converted[0]["content"] == "You are helpful"
        assert converted[1]["role"] == "user"
        assert converted[1]["content"] == "Hello"

    def test_convert_tools(self):
        """Test tool conversion to OpenAI format."""
        provider = OpenAIProvider(api_key="test-key", model="gpt-4")
        tools = [
            ToolDefinition(
                name="test_tool",
                description="Test tool",
                parameters={"type": "object"},
            )
        ]
        converted = provider._convert_tools(tools)
        assert len(converted) == 1
        assert converted[0]["type"] == "function"
        assert converted[0]["function"]["name"] == "test_tool"


class TestAnthropicProvider:
    """Tests for Anthropic provider."""

    def test_initialization(self):
        """Test Anthropic provider initialization."""
        provider = AnthropicProvider(api_key="test-key", model="claude-3-sonnet")
        assert provider.api_key == "test-key"
        assert provider.model == "claude-3-sonnet"
        assert provider.client is not None

    def test_validate_config_success(self):
        """Test successful configuration validation."""
        provider = AnthropicProvider(api_key="test-key", model="claude-3-sonnet")
        assert provider.validate_config() is True

    def test_validate_config_missing_key(self):
        """Test configuration validation with missing API key."""
        provider = AnthropicProvider(api_key="", model="claude-3-sonnet")
        with pytest.raises(ValueError, match="API key is required"):
            provider.validate_config()

    def test_convert_messages(self):
        """Test message conversion to Anthropic format."""
        provider = AnthropicProvider(api_key="test-key", model="claude-3-sonnet")
        messages = [
            Message(role="system", content="You are helpful"),
            Message(role="user", content="Hello"),
        ]
        system, converted = provider._convert_messages(messages)
        assert system == "You are helpful"
        assert len(converted) == 1
        assert converted[0]["role"] == "user"
        assert converted[0]["content"] == "Hello"

    def test_convert_tools(self):
        """Test tool conversion to Anthropic format."""
        provider = AnthropicProvider(api_key="test-key", model="claude-3-sonnet")
        tools = [
            ToolDefinition(
                name="test_tool",
                description="Test tool",
                parameters={"type": "object"},
            )
        ]
        converted = provider._convert_tools(tools)
        assert len(converted) == 1
        assert converted[0]["name"] == "test_tool"
        assert converted[0]["description"] == "Test tool"
        assert "input_schema" in converted[0]


class TestCustomProvider:
    """Tests for Custom provider."""

    def test_initialization(self):
        """Test Custom provider initialization."""
        provider = CustomProvider(
            api_key="test-key", model="custom-model", base_url="https://api.custom/v1"
        )
        assert provider.api_key == "test-key"
        assert provider.model == "custom-model"
        assert provider.base_url == "https://api.custom/v1"

    def test_initialization_without_base_url(self):
        """Test Custom provider requires base URL."""
        with pytest.raises(ValueError, match="base_url"):
            CustomProvider(api_key="test-key", model="custom-model", base_url="")

    def test_validate_config(self):
        """Test custom provider configuration validation."""
        provider = CustomProvider(
            api_key="test-key", model="custom-model", base_url="https://api.custom/v1"
        )
        assert provider.validate_config() is True

    def test_get_provider_name(self):
        """Test provider name."""
        provider = CustomProvider(
            api_key="test-key", model="custom-model", base_url="https://api.custom/v1"
        )
        assert provider.get_provider_name() == "custom"


class TestProviderRouter:
    """Tests for ProviderRouter."""

    def test_get_available_providers(self):
        """Test getting available providers."""
        providers = ProviderRouter.get_available_providers()
        assert "openai" in providers
        assert "anthropic" in providers
        assert "custom" in providers

    def test_create_openai_provider(self):
        """Test creating OpenAI provider."""
        reset_settings()
        from myagent.config import get_settings

        settings = get_settings()
        settings.myagent_provider = "openai"
        settings.openai_api_key = "test-key"
        settings.openai_model = "gpt-4"

        provider = ProviderRouter.create_provider()
        assert isinstance(provider, OpenAIProvider)
        assert provider.model == "gpt-4"

    def test_create_anthropic_provider(self):
        """Test creating Anthropic provider."""
        reset_settings()
        from myagent.config import get_settings

        settings = get_settings()
        settings.myagent_provider = "anthropic"
        settings.anthropic_api_key = "test-key"
        settings.anthropic_model = "claude-3-sonnet"

        provider = ProviderRouter.create_provider()
        assert isinstance(provider, AnthropicProvider)
        assert provider.model == "claude-3-sonnet"

    def test_create_custom_provider(self):
        """Test creating Custom provider."""
        reset_settings()
        from myagent.config import get_settings

        settings = get_settings()
        settings.myagent_provider = "custom"
        settings.custom_api_key = "test-key"
        settings.custom_base_url = "https://api.custom/v1"
        settings.custom_model = "custom-model"

        provider = ProviderRouter.create_provider()
        assert isinstance(provider, CustomProvider)
        assert provider.model == "custom-model"

    def test_create_provider_missing_api_key(self):
        """Test creating provider with missing API key."""
        reset_settings()
        from myagent.config import get_settings

        settings = get_settings()
        settings.myagent_provider = "openai"
        settings.openai_api_key = None

        with pytest.raises(ValueError, match="API key not found"):
            ProviderRouter.create_provider()

    def test_create_provider_unsupported(self):
        """Test creating unsupported provider."""
        reset_settings()
        with pytest.raises(ValueError, match="Unsupported provider"):
            ProviderRouter.create_provider(provider_name="unsupported")

    def test_validate_provider_config_openai(self):
        """Test validating OpenAI config."""
        reset_settings()
        from myagent.config import get_settings

        settings = get_settings()
        settings.openai_api_key = "test-key"

        assert ProviderRouter.validate_provider_config("openai") is True

    def test_validate_provider_config_missing_key(self, monkeypatch, tmp_path):
        """Test validating config with missing key."""
        # Change to a temp directory without .env file
        monkeypatch.chdir(tmp_path)
        # Clear API key from environment
        monkeypatch.delenv('OPENAI_API_KEY', raising=False)
        reset_settings()
        
        with pytest.raises(ValueError, match="OpenAI API key is required"):
            ProviderRouter.validate_provider_config("openai")
