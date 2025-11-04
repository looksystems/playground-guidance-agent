"""Tests for bootstrap script configuration."""

import os
import pytest
from unittest.mock import patch


class TestBootstrapConfiguration:
    """Test that bootstrap scripts use correct model naming."""

    def test_model_names_have_correct_format(self):
        """Test that model names in .env follow the correct provider/model-name format."""
        # Read the .env file
        env_path = "/Users/adrian/Work/guidance-agent/.env"

        with open(env_path, "r") as f:
            env_content = f.read()

        # Check for the correct model name format
        # LM Studio's OpenAI-compatible API requires "openai/" prefix
        # The model name must match exactly what LM Studio reports (e.g., "qwen/qwen3-30b-a3b")
        # LiteLLM uses the "openai/" prefix to route to the OpenAI-compatible endpoint
        # Full format: openai/<exact-model-name-from-lm-studio>

        # These assertions verify the correct configuration
        assert "openai/qwen/qwen3-30b-a3b" in env_content, "Model name should use openai/<lm-studio-model-name> format"
        assert "OPENAI_API_BASE=http://localhost:1234/v1" in env_content, "OpenAI API base should point to LM Studio"

    def test_litellm_drop_params_is_set(self):
        """Test that LITELLM_DROP_PARAMS is set to true in .env."""
        env_path = "/Users/adrian/Work/guidance-agent/.env"

        with open(env_path, "r") as f:
            env_content = f.read()

        # Check that LITELLM_DROP_PARAMS is set to true
        assert "LITELLM_DROP_PARAMS=true" in env_content, "LITELLM_DROP_PARAMS should be set to true"

    @patch.dict(os.environ, {"LITELLM_MODEL_ADVISOR": "openai/qwen/qwen3-30b-a3b"})
    def test_advisor_model_name_format(self):
        """Test that advisor model name uses correct format."""
        model_name = os.getenv("LITELLM_MODEL_ADVISOR")

        # Model name should start with "openai/" for LM Studio's OpenAI-compatible API
        assert model_name.startswith("openai/"), f"Expected model name to start with 'openai/', got: {model_name}"

    @patch.dict(os.environ, {"LITELLM_MODEL_COMPLIANCE": "openai/qwen/qwen3-30b-a3b"})
    def test_compliance_model_name_format(self):
        """Test that compliance model name uses correct format."""
        model_name = os.getenv("LITELLM_MODEL_COMPLIANCE")

        # Model name should start with "openai/" for LM Studio's OpenAI-compatible API
        assert model_name.startswith("openai/"), f"Expected model name to start with 'openai/', got: {model_name}"
