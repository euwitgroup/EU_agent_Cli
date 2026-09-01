"""Utility functions for provider management."""

import logging
from typing import Any, Dict, List, Optional

from myagent.providers.router import ProviderRouter

logger = logging.getLogger(__name__)


async def check_provider_connection(
    provider: str,
    api_key: str,
    model: str,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Test connection to a provider.

    Args:
        provider: Provider name (openai, anthropic, custom)
        api_key: API key
        model: Model name
        base_url: Base URL (for custom provider)

    Returns:
        Dict with connection test results
    """
    try:
        # Create provider config
        config = {
            "api_key": api_key,
            "model": model,
        }
        if base_url and provider == "custom":
            config["base_url"] = base_url

        # Validate configuration
        router = ProviderRouter()
        router.validate_provider_config(provider, config)

        # Create provider instance
        provider_instance = router.create_provider(provider, config)

        # Test with a simple request
        test_messages = [{"role": "user", "content": "Hello, testing connection."}]
        
        response = await provider_instance.generate(
            messages=test_messages,
            tools=[],
            max_tokens=10,
        )

        return {
            "success": True,
            "provider": provider_instance.get_provider_name(),
            "model": model,
            "response_text": response.content[:50] if response.content else "",
            "error": None,
        }

    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return {
            "success": False,
            "provider": provider,
            "model": model,
            "response_text": None,
            "error": str(e),
        }


async def list_models_from_provider(
    provider: str,
    api_key: str,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List available models from a provider.

    Args:
        provider: Provider name
        api_key: API key
        base_url: Base URL (for custom provider)

    Returns:
        Dict with list of models or error
    """
    try:
        if provider == "openai" or provider == "custom":
            import openai

            client = openai.OpenAI(
                api_key=api_key,
                base_url=base_url if provider == "custom" else None,
            )
            
            models_response = client.models.list()
            models = [model.id for model in models_response.data]
            
            return {
                "success": True,
                "provider": provider,
                "models": sorted(models),
                "count": len(models),
                "error": None,
            }

        elif provider == "anthropic":
            # Anthropic doesn't have a models API endpoint
            # Return known models
            known_models = [
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
            ]
            return {
                "success": True,
                "provider": provider,
                "models": known_models,
                "count": len(known_models),
                "error": None,
                "note": "Anthropic doesn't provide a models API. Showing known models.",
            }

        else:
            return {
                "success": False,
                "provider": provider,
                "models": [],
                "count": 0,
                "error": f"Unsupported provider: {provider}",
            }

    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        return {
            "success": False,
            "provider": provider,
            "models": [],
            "count": 0,
            "error": str(e),
        }


def save_provider_config(
    provider: str,
    api_key: str,
    model: str,
    base_url: Optional[str] = None,
    env_file: str = ".env",
) -> bool:
    """
    Save provider configuration to .env file.

    Args:
        provider: Provider name
        api_key: API key
        model: Model name
        base_url: Base URL (for custom provider)
        env_file: Path to .env file

    Returns:
        True if saved successfully
    """
    try:
        from pathlib import Path

        env_path = Path(env_file)
        
        # Read existing content
        existing_lines = []
        if env_path.exists():
            existing_lines = env_path.read_text().splitlines()

        # Remove existing MYAGENT_PROVIDER and all provider-specific configs
        filtered_lines = []
        for line in existing_lines:
            # Skip MYAGENT_PROVIDER line (we'll add the new one)
            if line.startswith("MYAGENT_PROVIDER="):
                continue
            # Skip the provider being configured
            if line.startswith(f"{provider.upper()}_API_KEY="):
                continue
            if line.startswith(f"{provider.upper()}_MODEL="):
                continue
            if line.startswith(f"{provider.upper()}_BASE_URL="):
                continue
            # Keep all other lines
            filtered_lines.append(line)

        # Add new config at the top (after comments if any)
        new_config = [
            f"MYAGENT_PROVIDER={provider}",
            f"{provider.upper()}_API_KEY={api_key}",
            f"{provider.upper()}_MODEL={model}",
        ]

        if base_url and provider == "custom":
            new_config.append(f"CUSTOM_BASE_URL={base_url}")

        # Find where to insert (after initial comments/blank lines)
        insert_index = 0
        for i, line in enumerate(filtered_lines):
            if line.strip() and not line.strip().startswith("#"):
                insert_index = i
                break
        
        # Insert new config
        if insert_index > 0:
            # Insert after comments
            result_lines = filtered_lines[:insert_index] + [""] + new_config + [""] + filtered_lines[insert_index:]
        else:
            # No comments, put at top
            result_lines = new_config + [""] + filtered_lines

        # Write back
        env_path.write_text("\n".join(result_lines) + "\n")

        logger.info(f"Saved provider config to {env_file}")
        return True

    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        return False


def update_env_file(key: str, value: str, env_file: str = ".env") -> bool:
    """
    Update a single environment variable in .env file.

    Args:
        key: Environment variable key
        value: New value
        env_file: Path to .env file

    Returns:
        True if updated successfully
    """
    try:
        from pathlib import Path

        env_path = Path(env_file)
        
        # Read existing content
        existing_lines = []
        if env_path.exists():
            existing_lines = env_path.read_text().splitlines()

        # Update or add the key
        key_found = False
        updated_lines = []
        
        for line in existing_lines:
            if line.startswith(f"{key}="):
                updated_lines.append(f"{key}={value}")
                key_found = True
            else:
                updated_lines.append(line)
        
        # If key wasn't found, add it
        if not key_found:
            updated_lines.append(f"{key}={value}")

        # Write back
        env_path.write_text("\n".join(updated_lines) + "\n")

        logger.info(f"Updated {key} in {env_file}")
        return True

    except Exception as e:
        logger.error(f"Failed to update .env: {e}")
        return False


def list_available_models(provider: str) -> List[str]:
    """
    List available models for a provider.

    Args:
        provider: Provider name

    Returns:
        List of model names
    """
    from myagent.config import get_settings
    import asyncio

    settings = get_settings()
    
    # Get API key for the provider
    api_key_map = {
        "anthropic": settings.anthropic_api_key,
        "openai": settings.openai_api_key,
        "custom": settings.custom_api_key,
    }
    
    api_key = api_key_map.get(provider)
    if not api_key:
        raise ValueError(f"No API key configured for {provider}")
    
    base_url = settings.custom_base_url if provider == "custom" else None
    
    # Call async function
    result = asyncio.run(list_models_from_provider(provider, api_key, base_url))
    
    if not result.get("success"):
        raise Exception(result.get("error", "Failed to list models"))
    
    return result.get("models", [])
