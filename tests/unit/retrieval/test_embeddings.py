"""Tests for embedding utilities."""

import os
import pytest
from unittest.mock import patch, MagicMock
from guidance_agent.retrieval.embeddings import embed, embed_batch


class TestEmbeddings:
    """Test embedding generation."""

    @patch("guidance_agent.retrieval.embeddings.embedding")
    def test_embed_single_text_without_dimensions_when_drop_params_enabled(self, mock_embedding):
        """Test that dimensions parameter is not passed when LITELLM_DROP_PARAMS is true."""
        # Arrange
        mock_response = MagicMock()
        mock_response.data = [{"embedding": [0.1, 0.2, 0.3]}]
        mock_embedding.return_value = mock_response

        # Set environment variable to enable drop_params
        with patch.dict(os.environ, {"LITELLM_DROP_PARAMS": "true"}):
            # Act
            result = embed("test text")

            # Assert
            assert result == [0.1, 0.2, 0.3]
            # Verify that embedding was called without dimensions parameter
            call_kwargs = mock_embedding.call_args[1]
            assert "dimensions" not in call_kwargs, "dimensions parameter should not be passed when LITELLM_DROP_PARAMS is true"

    @patch("guidance_agent.retrieval.embeddings.embedding")
    def test_embed_batch_without_dimensions_when_drop_params_enabled(self, mock_embedding):
        """Test that dimensions parameter is not passed for batch when LITELLM_DROP_PARAMS is true."""
        # Arrange
        mock_response = MagicMock()
        mock_response.data = [
            {"embedding": [0.1, 0.2]},
            {"embedding": [0.3, 0.4]},
        ]
        mock_embedding.return_value = mock_response

        # Set environment variable to enable drop_params
        with patch.dict(os.environ, {"LITELLM_DROP_PARAMS": "true"}):
            # Act
            result = embed_batch(["text1", "text2"])

            # Assert
            assert len(result) == 2
            # Verify that embedding was called without dimensions parameter
            call_kwargs = mock_embedding.call_args[1]
            assert "dimensions" not in call_kwargs, "dimensions parameter should not be passed when LITELLM_DROP_PARAMS is true"

    @patch("guidance_agent.retrieval.embeddings.embedding")
    def test_embed_with_dimensions_when_drop_params_disabled(self, mock_embedding):
        """Test that dimensions parameter IS passed when LITELLM_DROP_PARAMS is false or not set."""
        # Arrange
        mock_response = MagicMock()
        mock_response.data = [{"embedding": [0.1] * 1536}]
        mock_embedding.return_value = mock_response

        # Set environment variable to disable drop_params
        with patch.dict(os.environ, {"LITELLM_DROP_PARAMS": "false", "EMBEDDING_DIMENSION": "1536"}):
            # Act
            result = embed("test text")

            # Assert
            assert len(result) == 1536
            # Verify that embedding was called WITH dimensions parameter
            call_kwargs = mock_embedding.call_args[1]
            assert "dimensions" in call_kwargs, "dimensions parameter should be passed when LITELLM_DROP_PARAMS is false"
            assert call_kwargs["dimensions"] == 1536

    @patch("guidance_agent.retrieval.embeddings.embedding")
    def test_embed_multiple_texts(self, mock_embedding):
        """Test embedding multiple texts at once."""
        # Arrange
        mock_response = MagicMock()
        mock_response.data = [
            {"embedding": [0.1, 0.2]},
            {"embedding": [0.3, 0.4]},
            {"embedding": [0.5, 0.6]},
        ]
        mock_embedding.return_value = mock_response

        with patch.dict(os.environ, {"LITELLM_DROP_PARAMS": "true"}):
            # Act
            result = embed(["text1", "text2", "text3"])

            # Assert
            assert len(result) == 3
            assert result[0] == [0.1, 0.2]
            assert result[1] == [0.3, 0.4]
            assert result[2] == [0.5, 0.6]
