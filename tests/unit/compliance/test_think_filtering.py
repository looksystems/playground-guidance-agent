"""Tests for <think> tag filtering in compliance validator.

The compliance validator needs to filter out reasoning model <think> tags
before validation, since customers don't see these internal reasoning blocks.
"""

import pytest
from guidance_agent.compliance.validator import ComplianceValidator


class TestThinkTagFiltering:
    """Test <think> tag filtering functionality."""

    def test_filter_simple_think_tag(self):
        """Test filtering a simple <think> block."""
        text = "<think>Internal reasoning here</think>Customer-facing content"
        result = ComplianceValidator._filter_think_tags(text)
        assert result == "Customer-facing content"
        assert "<think>" not in result

    def test_filter_multiline_think_tag(self):
        """Test filtering multiline <think> blocks."""
        text = """<think>
Okay, I need to help the customer.
Let's break this down:
1. First point
2. Second point
</think>

Thank you for your question. Here's my guidance..."""
        result = ComplianceValidator._filter_think_tags(text)
        assert "Thank you for your question" in result
        assert "<think>" not in result
        assert "Okay, I need to help" not in result

    def test_filter_case_insensitive(self):
        """Test filtering with different cases."""
        test_cases = [
            "<think>reasoning</think>content",
            "<THINK>reasoning</THINK>content",
            "<Think>reasoning</Think>content",
            "<tHiNk>reasoning</tHiNk>content",
        ]
        for text in test_cases:
            result = ComplianceValidator._filter_think_tags(text)
            assert result == "content"
            assert "reasoning" not in result

    def test_filter_multiple_think_tags(self):
        """Test filtering multiple <think> blocks."""
        text = "<think>First reasoning</think>Content 1<think>Second reasoning</think>Content 2"
        result = ComplianceValidator._filter_think_tags(text)
        assert result == "Content 1Content 2"
        assert "reasoning" not in result

    def test_no_think_tags_unchanged(self):
        """Test that text without <think> tags is unchanged."""
        text = "This is regular guidance content without any think tags."
        result = ComplianceValidator._filter_think_tags(text)
        assert result == text

    def test_filter_preserves_newlines(self):
        """Test that filtering preserves newlines in content."""
        text = "<think>reasoning</think>\n\nParagraph 1\n\nParagraph 2"
        result = ComplianceValidator._filter_think_tags(text)
        assert "Paragraph 1" in result
        assert "Paragraph 2" in result
        # Note: strip() is called, so leading/trailing whitespace is removed

    def test_filter_with_special_characters(self):
        """Test filtering with special regex characters in content."""
        text = "<think>reasoning</think>Price: £100, (example) [test] *note*"
        result = ComplianceValidator._filter_think_tags(text)
        assert "Price: £100" in result
        assert "(example)" in result
        assert "reasoning" not in result

    def test_empty_think_tag(self):
        """Test filtering empty <think> tags."""
        text = "<think></think>Content after empty tag"
        result = ComplianceValidator._filter_think_tags(text)
        assert result == "Content after empty tag"

    def test_nested_angle_brackets(self):
        """Test content with angle brackets that aren't think tags."""
        text = "For x < 10 and y > 5, the result is <output>."
        result = ComplianceValidator._filter_think_tags(text)
        assert result == text  # Should be unchanged
        assert "< 10" in result
        assert "> 5" in result
