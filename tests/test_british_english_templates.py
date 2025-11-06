"""TDD tests for British English spelling in Jinja templates.

This test suite verifies that all templates use British English spelling conventions
as documented in specs/british-english-conversational-improvements.md.

These tests will FAIL initially (since code still uses American English) and should
pass after implementing the fixes.

British English conventions tested:
- -ise endings: optimise, analyse, summarise (not -ize)
- -our endings: behaviour (not -or)
- -ed participles: analysed (not analyzed)
"""

import pytest

from guidance_agent.core.template_engine import get_template_engine


class TestBritishEnglishInTemplates:
    """Test that all Jinja templates use British English spelling."""

    def test_guidance_with_reasoning_uses_analysed(
        self, sample_advisor, sample_customer, empty_context, empty_conversation_history
    ):
        """Test guidance_with_reasoning.jinja uses 'analysed' not 'analyzed'.

        Line 15: "analyzed" → "analysed"

        This test will FAIL initially until the template is updated.
        """
        engine = get_template_engine()

        result = engine.render(
            "advisor/guidance_with_reasoning.jinja",
            advisor=sample_advisor,
            customer=sample_customer,
            conversation_history=empty_conversation_history,
            context=empty_context,
        )

        # Check for British spelling
        assert "analysed" in result.lower(), (
            "Template should use British spelling 'analysed' (not 'analyzed')"
        )

        # Ensure American spelling is NOT present
        assert "analyzed" not in result.lower(), (
            "Template should NOT use American spelling 'analyzed'"
        )

    def test_guidance_cached_uses_optimised(self):
        """Test guidance_cached.jinja uses 'optimised/optimises' not 'optimized/optimizes'.

        Line 2: "optimized" → "optimised"
        Line 8: "optimizes" → "optimises"

        These changes are in template comments, so we check the raw template file.
        """
        from pathlib import Path

        template_path = Path(__file__).parent.parent / "src" / "guidance_agent" / "templates" / "advisor" / "guidance_cached.jinja"
        template_content = template_path.read_text().lower()

        # Check for British spelling variants in comments
        has_british_spelling = "optimised" in template_content or "optimises" in template_content
        assert has_british_spelling, (
            "Template should use British spelling 'optimised' or 'optimises' "
            "(not 'optimized' or 'optimizes')"
        )

        # Ensure American spelling variants are NOT present
        assert "optimized" not in template_content, (
            "Template should NOT use American spelling 'optimized'"
        )
        assert "optimizes" not in template_content, (
            "Template should NOT use American spelling 'optimizes'"
        )

    def test_compliance_validation_uses_behaviour(self, sample_customer, sample_guidance):
        """Test compliance/validation.jinja uses 'behaviour' not 'behavior'.

        Line 69: "behavior" → "behaviour"

        This test will FAIL initially until the template is updated.
        """
        engine = get_template_engine()

        # Validation template requires customer (CustomerProfile) and guidance parameters
        result = engine.render(
            "compliance/validation.jinja",
            guidance=sample_guidance,
            customer=sample_customer,
            reasoning="Test reasoning",
            customer_message="Test message",
        )

        # Check for British spelling
        assert "behaviour" in result.lower(), (
            "Template should use British spelling 'behaviour' (not 'behavior')"
        )

        # Ensure American spelling is NOT present
        assert "behavior" not in result.lower(), (
            "Template should NOT use American spelling 'behavior'"
        )

    def test_customer_response_uses_behaviour(self, sample_customer):
        """Test customer/response.jinja uses 'behaviour' not 'behavior'.

        Line 48: "behavior" → "behaviour"

        This test will FAIL initially until the template is updated.
        """
        engine = get_template_engine()

        result = engine.render(
            "customer/response.jinja",
            customer=sample_customer,
            advisor_message="Let me explain pension options to you.",
            comprehension={
                'understanding_level': 'good',
                'confusion_points': [],
                'customer_feeling': 'confident'
            },
        )

        # Check for British spelling
        assert "behaviour" in result.lower(), (
            "Template should use British spelling 'behaviour' (not 'behavior')"
        )

        # Ensure American spelling is NOT present
        assert "behavior" not in result.lower(), (
            "Template should NOT use American spelling 'behavior'"
        )

    def test_learning_reflection_uses_analyses(self):
        """Test learning/reflection.jinja uses 'analyses' not 'analyzes'.

        Line 4: "analyzes" → "analyses"

        This change is in template comment, so we check the raw template file.
        """
        from pathlib import Path

        template_path = Path(__file__).parent.parent / "src" / "guidance_agent" / "templates" / "learning" / "reflection.jinja"
        template_content = template_path.read_text().lower()

        # Check for British spelling in comments
        # Note: "analyses" could be noun (plural) or verb (third person singular)
        # We're looking for the verb form that replaced "analyzes"
        assert "analyses" in template_content, (
            "Template should use British spelling 'analyses' (verb: third person singular)"
        )

        # Ensure American spelling is NOT present
        assert "analyzes" not in template_content, (
            "Template should NOT use American spelling 'analyzes'"
        )

    def test_all_templates_avoid_american_spelling(
        self, sample_advisor, sample_customer, empty_context, empty_conversation_history
    ):
        """Comprehensive test that NO templates use American spelling variants.

        This is a catch-all test to ensure no American spellings slip through.
        Tests all advisor templates that can be easily rendered.
        """
        engine = get_template_engine()

        # American spellings that should NOT appear anywhere
        american_spellings = [
            "analyzed",
            "analyzes",
            "analyzing",
            "optimized",
            "optimizes",
            "optimizing",
            "behavior",
            "behaviors",
            "maximize",
            "maximizes",
            "maximizing",
            "favor",
            "favored",
            "favoring",
        ]

        # Test guidance_main template
        result = engine.render(
            "advisor/guidance_main.jinja",
            advisor=sample_advisor,
            customer=sample_customer,
            conversation_history=empty_conversation_history,
            context=empty_context,
        )

        result_lower = result.lower()
        for american in american_spellings:
            assert american not in result_lower, (
                f"guidance_main.jinja should NOT contain American spelling '{american}'"
            )

        # Test guidance_with_reasoning template
        result = engine.render(
            "advisor/guidance_with_reasoning.jinja",
            advisor=sample_advisor,
            customer=sample_customer,
            conversation_history=empty_conversation_history,
            context=empty_context,
        )

        result_lower = result.lower()
        for american in american_spellings:
            assert american not in result_lower, (
                f"guidance_with_reasoning.jinja should NOT contain American spelling '{american}'"
            )

    def test_templates_use_british_spelling_variants(
        self, sample_advisor, sample_customer, empty_context, empty_conversation_history
    ):
        """Positive test: verify templates DO use British spelling variants.

        This complements the negative tests by checking for presence of
        British spellings (not just absence of American ones).
        """
        engine = get_template_engine()

        # British spellings that SHOULD appear in various templates
        british_spellings = [
            "analysed",  # guidance_with_reasoning.jinja
            "optimised",  # guidance_cached.jinja
            "behaviour",  # compliance/validation.jinja, customer/response.jinja
            "analyses",   # learning/reflection.jinja
        ]

        # Collect all template outputs
        all_outputs = []

        # Guidance templates
        for template_name in [
            "advisor/guidance_main.jinja",
            "advisor/guidance_with_reasoning.jinja",
            "advisor/guidance_cached.jinja",
        ]:
            result = engine.render(
                template_name,
                advisor=sample_advisor,
                customer=sample_customer,
                conversation_history=empty_conversation_history,
                context=empty_context,
            )
            all_outputs.append((template_name, result))

        # Combine all outputs for checking
        combined_output = " ".join(output for _, output in all_outputs).lower()

        # At least some British spellings should be present across all templates
        british_found = [spelling for spelling in british_spellings
                        if spelling in combined_output]

        assert len(british_found) > 0, (
            f"Templates should use British spellings. Expected to find some of: "
            f"{british_spellings}, but found none in combined template outputs"
        )


@pytest.fixture
def sample_consultation():
    """Create a sample consultation for testing reflection template."""
    from uuid import uuid4
    from datetime import datetime

    return {
        "id": uuid4(),
        "customer_id": uuid4(),
        "advisor_id": uuid4(),
        "conversation_history": [
            {"role": "user", "content": "How much should I save for retirement?"},
            {"role": "assistant", "content": "That depends on several factors..."}
        ],
        "outcome": "successful",
        "created_at": datetime.now(),
    }
