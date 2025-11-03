"""Unit tests for provider detection and configuration."""

import pytest
import os
from guidance_agent.core.provider_config import (
    LLMProvider,
    detect_provider,
    supports_prompt_caching,
    get_cache_headers,
    get_embedding_dimension,
    get_provider_info,
)


@pytest.fixture(autouse=True)
def clean_embedding_env(monkeypatch):
    """Clean EMBEDDING_DIMENSION env var for each test."""
    monkeypatch.delenv("EMBEDDING_DIMENSION", raising=False)


class TestDetectProvider:
    """Test provider detection logic."""

    def test_detect_openai_by_gpt_prefix(self):
        assert detect_provider("gpt-4-turbo") == LLMProvider.OPENAI
        assert detect_provider("gpt-3.5-turbo") == LLMProvider.OPENAI
        assert detect_provider("gpt-4o") == LLMProvider.OPENAI

    def test_detect_openai_by_embedding_name(self):
        assert detect_provider("text-embedding-3-small") == LLMProvider.OPENAI
        assert detect_provider("text-embedding-ada-002") == LLMProvider.OPENAI

    def test_detect_anthropic_by_claude_name(self):
        assert detect_provider("claude-sonnet-4.5") == LLMProvider.ANTHROPIC
        assert detect_provider("claude-3-opus") == LLMProvider.ANTHROPIC
        assert detect_provider("claude-haiku-4.5") == LLMProvider.ANTHROPIC

    def test_detect_bedrock_by_prefix(self):
        assert detect_provider("bedrock/anthropic.claude-3-5-sonnet-20240229-v1:0") == LLMProvider.BEDROCK
        assert detect_provider("bedrock/amazon.titan-embed-text-v1") == LLMProvider.BEDROCK
        assert detect_provider("bedrock/anthropic.claude-3-haiku-20240307-v1:0") == LLMProvider.BEDROCK

    def test_detect_azure_by_prefix(self):
        assert detect_provider("azure/gpt-4-deployment") == LLMProvider.AZURE
        assert detect_provider("azure/my-custom-deployment") == LLMProvider.AZURE

    def test_detect_ollama_by_prefix(self):
        assert detect_provider("ollama/llama3.1:70b") == LLMProvider.OLLAMA
        assert detect_provider("ollama/nomic-embed-text") == LLMProvider.OLLAMA
        assert detect_provider("ollama/mistral") == LLMProvider.OLLAMA

    def test_detect_lmstudio_by_prefix(self):
        assert detect_provider("lmstudio/llama-3.1-70b") == LLMProvider.LMSTUDIO
        assert detect_provider("lmstudio/mistral-7b") == LLMProvider.LMSTUDIO

    def test_detect_openai_compatible_by_prefix(self):
        # vLLM uses openai/ prefix for OpenAI-compatible API
        assert detect_provider("openai/meta-llama/Llama-3.1-70B") == LLMProvider.VLLM

    def test_detect_localai_by_prefix(self):
        assert detect_provider("localai/llama3") == LLMProvider.LOCALAI

    def test_detect_unknown_model(self):
        assert detect_provider("unknown-model-name") == LLMProvider.UNKNOWN
        assert detect_provider("custom-llm-v1") == LLMProvider.UNKNOWN

    def test_case_insensitive_detection(self):
        # Should work regardless of case
        assert detect_provider("CLAUDE-SONNET-4.5") == LLMProvider.ANTHROPIC
        assert detect_provider("GPT-4-TURBO") == LLMProvider.OPENAI
        assert detect_provider("Bedrock/anthropic.claude-3") == LLMProvider.BEDROCK


class TestSupportsPromptCaching:
    """Test caching support detection."""

    def test_openai_gpt4o_supports_caching(self):
        assert supports_prompt_caching(LLMProvider.OPENAI, "gpt-4o")
        assert supports_prompt_caching(LLMProvider.OPENAI, "gpt-4o-mini")

    def test_openai_gpt4_turbo_supports_caching(self):
        assert supports_prompt_caching(LLMProvider.OPENAI, "gpt-4-turbo-preview")
        assert supports_prompt_caching(LLMProvider.OPENAI, "gpt-4-turbo")

    def test_openai_gpt35_no_caching(self):
        assert not supports_prompt_caching(LLMProvider.OPENAI, "gpt-3.5-turbo")

    def test_openai_gpt4_base_no_caching(self):
        # Base GPT-4 doesn't support caching, only GPT-4 Turbo
        assert not supports_prompt_caching(LLMProvider.OPENAI, "gpt-4")

    def test_anthropic_supports_caching(self):
        assert supports_prompt_caching(LLMProvider.ANTHROPIC, "claude-sonnet-4.5")
        assert supports_prompt_caching(LLMProvider.ANTHROPIC, "claude-3-opus")
        assert supports_prompt_caching(LLMProvider.ANTHROPIC, "claude-haiku-4.5")

    def test_bedrock_claude_supports_caching(self):
        assert supports_prompt_caching(
            LLMProvider.BEDROCK,
            "bedrock/anthropic.claude-3-sonnet"
        )
        assert supports_prompt_caching(
            LLMProvider.BEDROCK,
            "bedrock/anthropic.claude-3-5-sonnet-20240229-v1:0"
        )

    def test_bedrock_non_claude_no_caching(self):
        assert not supports_prompt_caching(
            LLMProvider.BEDROCK,
            "bedrock/amazon.titan-text-v1"
        )

    def test_ollama_no_caching(self):
        assert not supports_prompt_caching(LLMProvider.OLLAMA, "ollama/llama3.1:70b")

    def test_lmstudio_no_caching(self):
        assert not supports_prompt_caching(LLMProvider.LMSTUDIO, "lmstudio/llama-3.1-70b")

    def test_azure_no_caching(self):
        assert not supports_prompt_caching(LLMProvider.AZURE, "azure/gpt-4-deployment")

    def test_vllm_no_caching(self):
        assert not supports_prompt_caching(LLMProvider.VLLM, "openai/llama-3.1")


class TestGetCacheHeaders:
    """Test cache header generation."""

    def test_anthropic_headers(self):
        headers = get_cache_headers(LLMProvider.ANTHROPIC, "claude-sonnet-4.5")
        assert headers == {"anthropic-beta": "prompt-caching-2024-07-31"}

    def test_bedrock_claude_headers(self):
        headers = get_cache_headers(
            LLMProvider.BEDROCK,
            "bedrock/anthropic.claude-3-sonnet"
        )
        assert headers == {"anthropic-beta": "prompt-caching-2024-07-31"}

    def test_bedrock_non_claude_no_headers(self):
        headers = get_cache_headers(
            LLMProvider.BEDROCK,
            "bedrock/amazon.titan-text-v1"
        )
        assert headers == {}

    def test_openai_no_headers(self):
        # OpenAI uses automatic caching, no headers needed
        headers = get_cache_headers(LLMProvider.OPENAI, "gpt-4o")
        assert headers == {}

    def test_ollama_no_headers(self):
        headers = get_cache_headers(LLMProvider.OLLAMA, "ollama/llama3.1:70b")
        assert headers == {}

    def test_lmstudio_no_headers(self):
        headers = get_cache_headers(LLMProvider.LMSTUDIO, "lmstudio/llama-3.1-70b")
        assert headers == {}

    def test_azure_no_headers(self):
        headers = get_cache_headers(LLMProvider.AZURE, "azure/gpt-4-deployment")
        assert headers == {}


class TestGetEmbeddingDimension:
    """Test embedding dimension detection."""

    def test_openai_small(self):
        assert get_embedding_dimension("text-embedding-3-small") == 1536

    def test_openai_large(self):
        assert get_embedding_dimension("text-embedding-3-large") == 3072

    def test_openai_ada(self):
        assert get_embedding_dimension("text-embedding-ada-002") == 1536

    def test_voyage_large(self):
        assert get_embedding_dimension("voyage-large-2") == 1536

    def test_voyage_2(self):
        assert get_embedding_dimension("voyage-2") == 1024

    def test_bedrock_titan(self):
        assert get_embedding_dimension("bedrock/amazon.titan-embed-text-v1") == 1536

    def test_bedrock_cohere_english(self):
        assert get_embedding_dimension("bedrock/cohere.embed-english-v3") == 1024

    def test_bedrock_cohere_multilingual(self):
        assert get_embedding_dimension("bedrock/cohere.embed-multilingual-v3") == 1024

    def test_ollama_nomic(self):
        assert get_embedding_dimension("ollama/nomic-embed-text") == 768

    def test_ollama_bge_large(self):
        assert get_embedding_dimension("ollama/bge-large") == 1024

    def test_ollama_bge_small(self):
        assert get_embedding_dimension("ollama/bge-small") == 384

    def test_ollama_all_minilm(self):
        assert get_embedding_dimension("ollama/all-minilm") == 384

    def test_lmstudio_nomic(self):
        assert get_embedding_dimension("lmstudio/nomic-embed-text") == 768

    def test_unknown_model_uses_default(self):
        assert get_embedding_dimension("unknown-embedding-model") == 1536

    def test_env_var_override(self, monkeypatch):
        monkeypatch.setenv("EMBEDDING_DIMENSION", "2048")
        assert get_embedding_dimension("any-model") == 2048

    def test_env_var_override_with_cleanup(self, monkeypatch):
        # Test that we clean up properly
        monkeypatch.setenv("EMBEDDING_DIMENSION", "999")
        assert get_embedding_dimension("text-embedding-3-small") == 999
        # After monkeypatch context, should return to normal
        monkeypatch.delenv("EMBEDDING_DIMENSION", raising=False)


class TestGetProviderInfo:
    """Test comprehensive provider information."""

    def test_openai_gpt4o_info(self):
        info = get_provider_info("gpt-4o")
        assert info["provider"] == LLMProvider.OPENAI
        assert info["supports_caching"] is True
        assert info["cache_headers"] == {}
        assert info["supports_streaming"] is True
        assert info["is_local"] is False

    def test_anthropic_claude_info(self):
        info = get_provider_info("claude-sonnet-4.5")
        assert info["provider"] == LLMProvider.ANTHROPIC
        assert info["supports_caching"] is True
        assert info["cache_headers"] == {"anthropic-beta": "prompt-caching-2024-07-31"}
        assert info["supports_streaming"] is True
        assert info["is_local"] is False

    def test_bedrock_claude_info(self):
        info = get_provider_info("bedrock/anthropic.claude-3-sonnet")
        assert info["provider"] == LLMProvider.BEDROCK
        assert info["supports_caching"] is True
        assert info["cache_headers"] == {"anthropic-beta": "prompt-caching-2024-07-31"}
        assert info["supports_streaming"] is True
        assert info["is_local"] is False

    def test_ollama_info(self):
        info = get_provider_info("ollama/llama3.1:70b")
        assert info["provider"] == LLMProvider.OLLAMA
        assert info["supports_caching"] is False
        assert info["cache_headers"] == {}
        assert info["supports_streaming"] is True
        assert info["is_local"] is True

    def test_lmstudio_info(self):
        info = get_provider_info("lmstudio/llama-3.1-70b")
        assert info["provider"] == LLMProvider.LMSTUDIO
        assert info["supports_caching"] is False
        assert info["cache_headers"] == {}
        assert info["supports_streaming"] is True
        assert info["is_local"] is True

    def test_azure_info(self):
        info = get_provider_info("azure/gpt-4-deployment")
        assert info["provider"] == LLMProvider.AZURE
        assert info["supports_caching"] is False
        assert info["cache_headers"] == {}
        assert info["supports_streaming"] is True
        assert info["is_local"] is False

    def test_vllm_info(self):
        info = get_provider_info("openai/meta-llama/Llama-3.1-70B")
        assert info["provider"] == LLMProvider.VLLM
        assert info["supports_caching"] is False
        assert info["cache_headers"] == {}
        assert info["supports_streaming"] is True
        assert info["is_local"] is True
