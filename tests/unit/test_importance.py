"""Unit tests for importance scoring."""

import pytest
from unittest.mock import Mock, patch
from guidance_agent.core.memory import rate_importance


class TestImportanceScoring:
    """Tests for LLM-based importance scoring."""

    @patch("guidance_agent.core.memory.completion")
    def test_rate_importance_mundane_observation(self, mock_completion):
        """Test rating a mundane observation returns low importance."""
        # Mock LLM response with rating of 2
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(content="Rating: 2\n\nThis is a routine inquiry.")
                )
            ]
        )

        observation = "Customer asked about their pension balance"
        importance = rate_importance(observation)

        # Should normalize to 0.2 (2/10)
        assert importance == pytest.approx(0.2, abs=0.01)
        assert 0.0 <= importance <= 1.0

        # Verify LLM was called with correct parameters
        mock_completion.assert_called_once()
        call_args = mock_completion.call_args
        assert "pension balance" in str(call_args)
        assert call_args[1]["temperature"] == 0

    @patch("guidance_agent.core.memory.completion")
    def test_rate_importance_critical_observation(self, mock_completion):
        """Test rating a critical observation returns high importance."""
        # Mock LLM response with rating of 10
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content="Rating: 10\n\nThis is an extremely important life-changing decision."
                    )
                )
            ]
        )

        observation = "Customer wants to transfer their defined benefit pension worth £500k"
        importance = rate_importance(observation)

        # Should normalize to 1.0 (10/10)
        assert importance == pytest.approx(1.0, abs=0.01)
        assert 0.0 <= importance <= 1.0

    @patch("guidance_agent.core.memory.completion")
    def test_rate_importance_medium_observation(self, mock_completion):
        """Test rating a medium importance observation."""
        # Mock LLM response with rating of 6
        mock_completion.return_value = Mock(
            choices=[Mock(message=Mock(content="Rating: 6"))]
        )

        observation = "Customer is considering retirement at age 60"
        importance = rate_importance(observation)

        # Should normalize to 0.6 (6/10)
        assert importance == pytest.approx(0.6, abs=0.01)

    @patch("guidance_agent.core.memory.completion")
    def test_rate_importance_parses_various_formats(self, mock_completion):
        """Test that importance scoring handles various response formats."""
        test_cases = [
            ("Rating: 7", 0.7),
            ("The rating is 8 out of 10", 0.8),
            ("I would rate this a 5", 0.5),
            ("Rating: 9/10", 0.9),
            ("Score: 3", 0.3),
        ]

        for response_text, expected_score in test_cases:
            mock_completion.return_value = Mock(
                choices=[Mock(message=Mock(content=response_text))]
            )

            importance = rate_importance("Test observation")
            assert importance == pytest.approx(expected_score, abs=0.01), f"Failed for: {response_text}"

    @patch("guidance_agent.core.memory.completion")
    def test_rate_importance_handles_invalid_rating(self, mock_completion):
        """Test that invalid ratings default to medium importance."""
        # Mock LLM response with no clear rating
        mock_completion.return_value = Mock(
            choices=[Mock(message=Mock(content="This is somewhat important."))]
        )

        observation = "Customer asked a question"
        importance = rate_importance(observation)

        # Should default to medium importance (0.5)
        assert importance == pytest.approx(0.5, abs=0.01)

    @patch("guidance_agent.core.memory.completion")
    def test_rate_importance_clamps_out_of_range(self, mock_completion):
        """Test that ratings outside 1-10 are clamped."""
        # Test rating > 10
        mock_completion.return_value = Mock(
            choices=[Mock(message=Mock(content="Rating: 15"))]
        )
        importance = rate_importance("Test")
        assert importance <= 1.0

        # Test rating < 1
        mock_completion.return_value = Mock(
            choices=[Mock(message=Mock(content="Rating: 0"))]
        )
        importance = rate_importance("Test")
        assert importance >= 0.0

    @patch("guidance_agent.core.memory.completion")
    def test_rate_importance_uses_correct_model(self, mock_completion):
        """Test that importance scoring uses the correct LLM model."""
        mock_completion.return_value = Mock(
            choices=[Mock(message=Mock(content="Rating: 5"))]
        )

        rate_importance("Test observation")

        # Verify model parameter
        call_args = mock_completion.call_args
        assert "model" in call_args[1]

    @patch("guidance_agent.core.memory.completion")
    def test_rate_importance_with_custom_model(self, mock_completion, monkeypatch):
        """Test importance scoring with custom model from environment."""
        monkeypatch.setenv("LITELLM_MODEL_CUSTOMER", "gpt-4")

        mock_completion.return_value = Mock(
            choices=[Mock(message=Mock(content="Rating: 7"))]
        )

        importance = rate_importance("Test observation")

        assert importance == pytest.approx(0.7, abs=0.01)

    @patch("guidance_agent.core.memory.completion")
    def test_rate_importance_prompt_structure(self, mock_completion):
        """Test that the prompt has the correct structure."""
        mock_completion.return_value = Mock(
            choices=[Mock(message=Mock(content="Rating: 5"))]
        )

        observation = "Customer inquired about tax implications"
        rate_importance(observation)

        # Get the actual prompt sent
        call_args = mock_completion.call_args
        messages = call_args[1]["messages"]
        prompt = messages[0]["content"]

        # Verify prompt contains key elements
        assert "1 to 10" in prompt or "1-10" in prompt
        assert observation in prompt
        assert "importance" in prompt.lower() or "important" in prompt.lower()
        assert "mundane" in prompt.lower()

    @patch("guidance_agent.core.memory.completion")
    def test_rate_importance_returns_normalized_float(self, mock_completion):
        """Test that importance always returns a float between 0 and 1."""
        for rating in range(1, 11):
            mock_completion.return_value = Mock(
                choices=[Mock(message=Mock(content=f"Rating: {rating}"))]
            )

            importance = rate_importance(f"Test observation {rating}")

            assert isinstance(importance, float)
            assert 0.0 <= importance <= 1.0
            assert importance == pytest.approx(rating / 10.0, abs=0.01)
