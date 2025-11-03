"""Provider detection and configuration.

This module provides centralized provider detection and configuration
for multi-provider LLM support via LiteLLM.
"""

import os
from enum import Enum
from typing import Optional


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    BEDROCK = "bedrock"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    VLLM = "vllm"
    LOCALAI = "localai"
    UNKNOWN = "unknown"


def detect_provider(model_name: str) -> LLMProvider:
    """Detect provider from model name.

    Args:
        model_name: Model name (e.g., "gpt-4", "claude-3", "bedrock/...")

    Returns:
        Detected provider

    Examples:
        >>> detect_provider("gpt-4-turbo")
        LLMProvider.OPENAI
        >>> detect_provider("claude-sonnet-4.5")
        LLMProvider.ANTHROPIC
        >>> detect_provider("bedrock/anthropic.claude-3")
        LLMProvider.BEDROCK
        >>> detect_provider("ollama/llama3")
        LLMProvider.OLLAMA
        >>> detect_provider("lmstudio/llama-3.1-70b")
        LLMProvider.LMSTUDIO
    """
    model_lower = model_name.lower()

    # Explicit prefixes (most reliable)
    if model_lower.startswith("bedrock/"):
        return LLMProvider.BEDROCK
    if model_lower.startswith("azure/"):
        return LLMProvider.AZURE
    if model_lower.startswith("ollama/"):
        return LLMProvider.OLLAMA
    if model_lower.startswith("lmstudio/"):
        return LLMProvider.LMSTUDIO
    if model_lower.startswith("openai/"):
        return LLMProvider.VLLM  # vLLM uses OpenAI-compatible API
    if model_lower.startswith("localai/"):
        return LLMProvider.LOCALAI

    # Model name patterns (fallback)
    if "claude" in model_lower:
        return LLMProvider.ANTHROPIC
    if any(x in model_lower for x in ["gpt-", "o1-", "text-embedding"]):
        return LLMProvider.OPENAI

    return LLMProvider.UNKNOWN


def supports_prompt_caching(provider: LLMProvider, model_name: str = "") -> bool:
    """Check if provider supports prompt caching.

    Args:
        provider: Detected provider
        model_name: Model name (for provider-specific checks)

    Returns:
        True if caching is supported
    """
    if provider == LLMProvider.OPENAI:
        # Only GPT-4o and GPT-4 Turbo support caching
        return any(x in model_name.lower() for x in ["gpt-4o", "gpt-4-turbo"])

    if provider == LLMProvider.ANTHROPIC:
        # All Claude 3+ models support caching
        return True

    if provider == LLMProvider.BEDROCK:
        # Claude on Bedrock should support caching
        return "claude" in model_name.lower()

    # Azure, local models: no caching
    return False


def get_cache_headers(provider: LLMProvider, model_name: str) -> dict:
    """Get provider-specific cache headers.

    Args:
        provider: Detected provider
        model_name: Model name

    Returns:
        Headers dict for caching
    """
    if provider == LLMProvider.ANTHROPIC:
        return {"anthropic-beta": "prompt-caching-2024-07-31"}

    if provider == LLMProvider.BEDROCK and "claude" in model_name.lower():
        # Bedrock Claude uses Anthropic protocol
        return {"anthropic-beta": "prompt-caching-2024-07-31"}

    # OpenAI, Azure: automatic caching (no headers needed)
    # Local models: no caching support
    return {}


def get_embedding_dimension(model_name: str, default: int = 1536) -> int:
    """Get embedding dimension for model.

    Args:
        model_name: Model name
        default: Default dimension if unknown

    Returns:
        Embedding dimension
    """
    # Check environment variable first (allows override)
    env_dim = os.getenv("EMBEDDING_DIMENSION")
    if env_dim:
        return int(env_dim)

    # Known model dimensions
    dimensions = {
        # OpenAI
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
        # Voyage
        "voyage-large-2": 1536,
        "voyage-2": 1024,
        # Bedrock
        "bedrock/amazon.titan-embed-text-v1": 1536,
        "bedrock/cohere.embed-english-v3": 1024,
        "bedrock/cohere.embed-multilingual-v3": 1024,
        # Local (Ollama)
        "ollama/nomic-embed-text": 768,
        "ollama/bge-large": 1024,
        "ollama/bge-small": 384,
        "ollama/all-minilm": 384,
        # LM Studio
        "lmstudio/nomic-embed-text": 768,
    }

    # Check by full name first
    if model_name in dimensions:
        return dimensions[model_name]

    # Check by partial match - need to check if model_name contains the key pattern
    # Sort by key length (longest first) to match more specific patterns first
    sorted_dimensions = sorted(dimensions.items(), key=lambda x: len(x[0]), reverse=True)
    for key, dim in sorted_dimensions:
        if key in model_name:
            return dim

    return default


def get_provider_info(model_name: str) -> dict:
    """Get comprehensive provider information.

    Args:
        model_name: Model name

    Returns:
        Dict with provider info including:
        - provider: LLMProvider enum
        - supports_caching: bool
        - cache_headers: dict
        - supports_streaming: bool (always True via LiteLLM)
        - is_local: bool
    """
    provider = detect_provider(model_name)

    return {
        "provider": provider,
        "supports_caching": supports_prompt_caching(provider, model_name),
        "cache_headers": get_cache_headers(provider, model_name),
        "supports_streaming": True,  # All providers support streaming via LiteLLM
        "is_local": provider in [LLMProvider.OLLAMA, LLMProvider.LMSTUDIO, LLMProvider.VLLM, LLMProvider.LOCALAI],
    }
