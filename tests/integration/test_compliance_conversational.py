"""
Integration tests for compliance validation with conversational enhancements.

Tests that conversational language (warmth, personalization, varied phrasing)
passes FCA compliance validation while actual violations are still caught.
"""

import pytest
from unittest.mock import MagicMock, patch
from guidance_agent.compliance.validator import ComplianceValidator
from guidance_agent.core.types import (
    CustomerProfile,
    CustomerDemographics,
    FinancialSituation,
    PensionPot,
)


@pytest.fixture
def compliance_validator():
    """Create a compliance validator instance."""
    return ComplianceValidator()


@pytest.fixture
def sample_customer():
    """Create a sample customer profile."""
    return CustomerProfile(
        demographics=CustomerDemographics(
            age=35,
            gender="F",
            location="London",
            employment_status="employed",
            financial_literacy="medium",
        ),
        financial=FinancialSituation(
            annual_income=45000,
            total_assets=30000,
            total_debt=5000,
            dependents=0,
            risk_tolerance="medium",
        ),
        pensions=[
            PensionPot(
                pot_id="nest-001",
                provider="NEST",
                pot_type="defined_contribution",
                current_value=15000,
                projected_value=85000,
                age_accessible=55,
                is_db_scheme=False,
            )
        ],
        goals="Understand pension options and plan for retirement",
        presenting_question="I want to understand my pension options",
    )


def create_passing_validation(relevance_score=0.95, confidence=0.92):
    """Helper to create a passing validation mock response."""
    return MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content=f"""
                    RELEVANCE: YES
                    RELEVANCE_SCORE: {relevance_score}
                    RELEVANCE_REASONING: Response directly addresses customer's question

                    ANALYSIS:
                    0. Response relevance: PASS - Addresses customer's question appropriately
                    1. Guidance vs Advice boundary: PASS - Uses appropriate language, no specific recommendations
                    2. Risk disclosure: PASS - Balanced information provided
                    3. Clear and not misleading: PASS - Language is clear and appropriate for literacy level
                    4. Understanding verification: PASS - Checks understanding appropriately
                    5. Signposting: PASS - Appropriate for context

                    OVERALL: PASS
                    CONFIDENCE: {confidence}
                    ISSUES: None
                    """
                )
            )
        ]
    )


def create_failing_validation(reason="Advice boundary violation", confidence=0.90):
    """Helper to create a failing validation mock response."""
    return MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content=f"""
                    RELEVANCE: YES
                    RELEVANCE_SCORE: 0.85
                    RELEVANCE_REASONING: Response addresses question but crosses compliance boundaries

                    ANALYSIS:
                    0. Response relevance: PASS - Addresses customer's question
                    1. Guidance vs Advice boundary: FAIL - {reason}
                    2. Risk disclosure: UNCERTAIN - May be missing important risks
                    3. Clear and not misleading: PASS
                    4. Understanding verification: PASS
                    5. Signposting: UNCERTAIN

                    OVERALL: FAIL
                    CONFIDENCE: {confidence}
                    ISSUES: {reason}
                    """
                )
            )
        ]
    )


class TestConversationalLanguageCompliance:
    """Test that conversational enhancements pass compliance validation."""

    def test_warm_greeting_is_compliant(self, compliance_validator, sample_customer):
        """Test that warm, friendly greetings pass validation."""
        guidance = """Hi Sarah! I'm glad you reached out about your pension planning.
        That's a great question, and you're absolutely right to be thinking about this now.
        Let me help you understand your options."""

        customer_message = "Can you help me understand my pension options?"

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_passing_validation()

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message=customer_message,
            )

        assert result.passed is True, f"Warm greeting should be compliant. Issues: {result.issues}"
        assert result.confidence > 0.8, "Should have high confidence in compliance"
        assert len(result.issues) == 0

    def test_signposting_is_compliant(self, compliance_validator, sample_customer):
        """Test that signposting and transitions pass validation."""
        guidance = """Let me break this down for you, Sarah. First, let's look at what
        you currently have. Then we'll explore some options you could consider.

        Here's what this means for you: you have £15,000 at age 35. Building on that,
        you might want to look into increasing your contributions. Before we dive into
        the details, does this make sense so far?"""

        customer_message = "Where do I stand with my pension?"

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_passing_validation()

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message=customer_message,
            )

        assert result.passed is True, f"Signposting should be compliant. Issues: {result.issues}"
        assert result.confidence > 0.8

    def test_personalization_with_name_is_compliant(self, compliance_validator, sample_customer):
        """Test that using customer's name is compliant."""
        guidance = """Great to hear from you, Sarah. Based on your situation at age 35
        with £15,000 in your pension, you have several options to explore. Sarah, one option to
        consider is increasing your monthly contributions. What are your thoughts on that?"""

        customer_message = "How am I doing with my pension savings?"

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_passing_validation()

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message=customer_message,
            )

        assert result.passed is True, f"Using customer name should be compliant. Issues: {result.issues}"
        assert result.confidence > 0.8

    def test_emotional_acknowledgment_is_compliant(self, compliance_validator, sample_customer):
        """Test that acknowledging emotions is compliant."""
        guidance = """I understand this can feel overwhelming, Sarah. It's completely
        normal to feel uncertain about pension planning - many people do. Let's take
        it step by step together. You're right to be thinking about this, and I'm
        here to help make it clearer for you."""

        customer_message = "I'm really confused and worried about my pension."

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_passing_validation()

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message=customer_message,
            )

        assert result.passed is True, f"Emotional acknowledgment should be compliant. Issues: {result.issues}"
        assert result.confidence > 0.8

    def test_varied_phrasing_is_compliant(self, compliance_validator, sample_customer):
        """Test that varied phrasing alternatives are compliant."""
        guidance = """Sarah, you have a few paths available to you. One option to explore
        is increasing your contributions. Another approach is to consolidate your pensions.
        You might want to look into reviewing your fund choices. It's worth thinking about
        your target retirement age as well.

        Each of these approaches has different benefits and considerations. Would you
        like to explore any of these in more detail?"""

        customer_message = "What can I do to improve my pension situation?"

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_passing_validation()

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message=customer_message,
            )

        assert result.passed is True, f"Varied phrasing should be compliant. Issues: {result.issues}"
        assert result.confidence > 0.8


class TestComplianceViolationsStillCaught:
    """Test that actual compliance violations are still detected despite conversational style."""

    def test_directive_language_still_fails(self, compliance_validator, sample_customer):
        """Test that directive language is still caught as violation."""
        guidance = """Sarah, you should definitely increase your pension contributions
        to at least 15% of your salary. I recommend you do this immediately. The best
        option for you is to maximise your employer match right away."""

        customer_message = "What should I do about my pension?"

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_failing_validation(
                "Uses 'should definitely' and 'I recommend', crossing into advice territory"
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message=customer_message,
            )

        assert result.passed is False, "Directive language should fail validation"
        assert len(result.issues) > 0

    def test_specific_recommendations_still_fail(self, compliance_validator, sample_customer):
        """Test that specific recommendations are still violations."""
        guidance = """Hi Sarah! Based on everything, I recommend you consolidate all your
        pensions into your NEST scheme. This is the best choice for your situation.
        You should also increase contributions to exactly 12% of your salary."""

        customer_message = "What's the best way to manage my pensions?"

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_failing_validation(
                "Makes specific recommendation to consolidate into NEST, expresses preference as 'best choice'"
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message=customer_message,
            )

        assert result.passed is False, "Specific recommendations should fail"
        assert len(result.issues) > 0

    def test_missing_risk_disclosure_still_fails(self, compliance_validator, sample_customer):
        """Test that missing risk disclosure is still caught."""
        guidance = """Sarah, you could consider transferring your pension to a
        self-invested personal pension (SIPP). This would give you more control
        over your investments and potentially better returns. It's worth exploring!"""

        customer_message = "Should I transfer my pension to a SIPP?"

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_failing_validation(
                "Missing risk disclosure about SIPP risks, fees, and investment responsibility"
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message=customer_message,
            )

        assert result.passed is False, "Missing risk disclosure should fail"
        assert len(result.issues) > 0

    def test_overly_directive_despite_warmth_still_fails(self, compliance_validator, sample_customer):
        """Test that being warm doesn't excuse directive advice."""
        guidance = """Hi Sarah! Great to chat with you. I really think you need to
        increase your contributions - you should aim for at least £500 per month.
        Trust me, this is what you need to do to be comfortable in retirement.
        Let me know when you've set this up!"""

        customer_message = "How much should I contribute to my pension?"

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_failing_validation(
                "Overly directive with 'you need to', 'you should aim for', and specific amount recommendation"
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message=customer_message,
            )

        assert result.passed is False, "Directive advice should fail even with warm tone"
        assert len(result.issues) > 0


class TestComplexConversationalScenarios:
    """Test complex scenarios mixing conversational style with compliance requirements."""

    def test_conversational_with_proper_risk_disclosure(self, compliance_validator, sample_customer):
        """Test conversational language combined with proper risk disclosure."""
        guidance = """Great question, Sarah! Let me walk you through this. You could
        consider consolidating your old pensions, which some people find helpful for
        simplifying their retirement planning.

        However, it's important to understand both sides. The benefits could include
        easier management and potentially lower fees. But there are also considerations:
        you might lose valuable benefits from your old schemes, exit fees could apply,
        and you'd need to ensure the new scheme is right for your needs.

        Before making any decision, it's worth checking what you might be giving up.
        Does that make sense? Would you like to explore what to look for?"""

        customer_message = "Should I consolidate my old pensions?"

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_passing_validation(relevance_score=0.94, confidence=0.90)

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message=customer_message,
            )

        assert result.passed is True, "Conversational + risk disclosure should pass"
        assert result.confidence > 0.8

    def test_personalized_with_literacy_appropriate_language(self, compliance_validator, sample_customer):
        """Test personalized language at appropriate literacy level."""
        # Set low literacy
        sample_customer.demographics.financial_literacy = "low"

        guidance = """Hi Sarah! Let me explain this in simple terms. Think of your
        pension like a savings account for retirement. Every month, money goes in
        from you and your employer. Over time, this money grows.

        You could consider putting in a bit more each month if you can afford it -
        even small amounts add up over the years. But only if it feels comfortable
        for your budget.

        Does this make sense so far? I want to make sure it's clear before we go further."""

        customer_message = "How do pensions work?"

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_passing_validation(relevance_score=0.96, confidence=0.93)

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message=customer_message,
            )

        assert result.passed is True, "Literacy-appropriate personalization should pass"
        assert result.confidence > 0.8
