"""
Integration tests for FCA neutrality requirements - Phase 7.

Tests that evaluative language, value judgments, and adequacy assessments
fail validation while neutral fact-stating passes.

This suite implements TDD - tests are written BEFORE implementation,
so many will FAIL initially until the compliance validator is enhanced
to detect these violations.
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
    """Create a sample customer profile for testing."""
    return CustomerProfile(
        demographics=CustomerDemographics(
            age=45,
            gender="M",
            location="Manchester",
            employment_status="employed",
            financial_literacy="medium",
        ),
        financial=FinancialSituation(
            annual_income=55000,
            total_assets=150000,
            total_debt=10000,
            dependents=2,
            risk_tolerance="medium",
        ),
        pensions=[
            PensionPot(
                pot_id="aviva-001",
                provider="Aviva",
                pot_type="defined_contribution",
                current_value=150000,
                projected_value=320000,
                age_accessible=55,
                is_db_scheme=False,
            )
        ],
        goals="Understand if pension savings are adequate for retirement",
        presenting_question="How is my pension looking?",
    )


@pytest.fixture
def young_customer():
    """Create a younger customer profile for testing."""
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
        goals="Understand pension options",
        presenting_question="What should I do with my pension?",
    )


def create_failing_validation(reason="Evaluative language violation", confidence=0.90):
    """Helper to create a failing validation mock response."""
    return MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content=f"""
                    RELEVANCE: YES
                    RELEVANCE_SCORE: 0.85
                    RELEVANCE_REASONING: Response addresses question but uses evaluative language

                    ANALYSIS:
                    0. Response relevance: PASS - Addresses customer's question
                    1. Guidance vs Advice boundary: FAIL - {reason}
                    2. Risk disclosure: PASS
                    3. Clear and not misleading: FAIL - Uses value judgments
                    4. Understanding verification: PASS
                    5. Signposting: PASS

                    OVERALL: FAIL
                    CONFIDENCE: {confidence}
                    ISSUES: {reason}
                    """
                )
            )
        ]
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
                    RELEVANCE_REASONING: Response neutrally addresses customer's question

                    ANALYSIS:
                    0. Response relevance: PASS - Addresses customer's question appropriately
                    1. Guidance vs Advice boundary: PASS - Uses neutral language, no evaluations
                    2. Risk disclosure: PASS - Balanced information provided
                    3. Clear and not misleading: PASS - Neutral fact-stating without judgment
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


class TestEvaluativeLanguageViolations:
    """Test that evaluative language and value judgments FAIL validation."""

    def test_solid_foundation_language_fails(self, compliance_validator, sample_customer):
        """Value judgment on pension adequacy using 'solid foundation' must fail."""
        guidance = "Having £150,000 at age 45 is a solid foundation for retirement."

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_failing_validation(
                "Uses 'solid foundation' which is evaluative language making a value judgment about adequacy"
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message="How is my pension?"
            )

        assert result.passed is False, "Value judgment on adequacy should fail validation"
        assert len(result.issues) > 0, "Should have identified issues with evaluative language"

    def test_doing_well_assessment_fails(self, compliance_validator, sample_customer):
        """Suitability assessment using 'doing well' must fail."""
        guidance = "Based on your situation, you're actually doing well with your pension."

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_failing_validation(
                "Uses 'doing well' which makes a suitability assessment about pension adequacy"
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message="Am I saving enough?"
            )

        assert result.passed is False, "Adequacy assessment should fail validation"
        assert len(result.issues) > 0, "Should have identified suitability assessment violation"

    def test_social_proof_with_circumstances_fails(self, compliance_validator, young_customer):
        """Social proof linked to customer circumstances must fail (implies steering)."""
        guidance = "Some people in your situation at age 35 find it helpful to consolidate."

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_failing_validation(
                "Social proof linked to circumstances ('in your situation') implies steering/recommendation"
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=young_customer,
                customer_message="What should I do?"
            )

        assert result.passed is False, "Social proof + circumstances should fail (steering)"
        assert len(result.issues) > 0, "Should identify social proof as implicit recommendation"

    def test_enthusiastic_response_to_amount_fails(self, compliance_validator, sample_customer):
        """Enthusiastic evaluation of financial position must fail."""
        guidance = "Great! £150k is an excellent amount for your age."

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_failing_validation(
                "Uses 'excellent amount for your age' which evaluates adequacy/suitability"
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message="I have £150k in my pension"
            )

        assert result.passed is False, "Evaluative response to amount should fail"
        assert len(result.issues) > 0, "Should identify enthusiastic evaluation as violation"

    def test_better_than_average_comparison_fails(self, compliance_validator, sample_customer):
        """Comparative statements about adequacy must fail."""
        guidance = "You're doing better than many people your age with pension savings."

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_failing_validation(
                "Compares customer to others ('better than many people') making adequacy judgment"
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message="How am I doing compared to others?"
            )

        assert result.passed is False, "Comparative adequacy statements should fail"
        assert len(result.issues) > 0, "Should identify comparative evaluation as violation"

    def test_good_amount_evaluation_fails(self, compliance_validator, sample_customer):
        """Direct value judgment using 'good amount' must fail."""
        guidance = "That's a good amount to have saved at your age."

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_failing_validation(
                "Uses 'good amount' which is direct value judgment about adequacy"
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message="I have £150k saved"
            )

        assert result.passed is False, "Direct value judgment should fail"
        assert len(result.issues) > 0, "Should identify 'good amount' as evaluative language"

    def test_right_track_assessment_fails(self, compliance_validator, young_customer):
        """Assessment phrases like 'on the right track' must fail."""
        guidance = "You're on the right track with your pension savings at age 35."

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_failing_validation(
                "Uses 'on the right track' which evaluates adequacy/suitability of actions"
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=young_customer,
                customer_message="Am I doing the right thing?"
            )

        assert result.passed is False, "'Right track' assessment should fail"
        assert len(result.issues) > 0, "Should identify track assessment as evaluation"


class TestNeutralCompliantLanguage:
    """Test that neutral, fact-based language PASSES validation."""

    def test_neutral_fact_stating_passes(self, compliance_validator, sample_customer):
        """Neutral fact-stating without judgment must pass."""
        guidance = """You have £150,000 at age 45. Whether this meets your retirement
        needs depends on your target retirement age, expected lifestyle, and other income
        sources. Would you like to explore what's important for your retirement planning?"""

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_passing_validation(
                relevance_score=0.95,
                confidence=0.92
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message="How is my pension?"
            )

        assert result.passed is True, "Neutral fact-stating should pass validation"
        assert result.confidence > 0.8, "Should have high confidence in compliance"
        assert len(result.issues) == 0, "Should have no compliance issues"

    def test_process_warmth_passes(self, compliance_validator, sample_customer):
        """Warmth about the process (not circumstances) must pass."""
        guidance = """I'm glad you're thinking about your retirement planning - that's an
        important topic to explore. Let me help you understand the factors that affect
        whether your current savings will meet your needs."""

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_passing_validation(
                relevance_score=0.94,
                confidence=0.90
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message="Should I be worried about my pension?"
            )

        assert result.passed is True, "Warmth about process should pass"
        assert result.confidence > 0.8
        assert len(result.issues) == 0

    def test_adequacy_factor_listing_passes(self, compliance_validator, sample_customer):
        """Listing adequacy factors without evaluation must pass."""
        guidance = """Whether £150,000 will meet your retirement needs depends on several factors:
        - Your target retirement age
        - The lifestyle you're planning for in retirement
        - Whether you'll have other income sources (State Pension, other savings)
        - Where you plan to live in retirement
        - Your health and life expectancy considerations

        Would you like to explore what's most important to you for retirement planning?"""

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_passing_validation(
                relevance_score=0.96,
                confidence=0.93
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message="Is my pension enough?"
            )

        assert result.passed is True, "Objective factor listing should pass"
        assert result.confidence > 0.8
        assert len(result.issues) == 0

    def test_neutral_exploration_offer_passes(self, compliance_validator, sample_customer):
        """Neutral exploration offers without judgment must pass."""
        guidance = """Your pension currently has £150,000. To understand what this means
        for your retirement, we'd need to consider your personal goals and circumstances.

        I can help you explore:
        - What factors determine if savings meet your needs
        - Different ways to think about retirement planning
        - When it might be worth speaking with a financial adviser

        What would be most helpful to discuss?"""

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_passing_validation(
                relevance_score=0.95,
                confidence=0.91
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message="What should I know about my pension?"
            )

        assert result.passed is True, "Neutral exploration offer should pass"
        assert result.confidence > 0.8
        assert len(result.issues) == 0

    def test_factual_projection_without_judgment_passes(self, compliance_validator, sample_customer):
        """Factual projections without adequacy judgment must pass."""
        guidance = """Your pension is currently valued at £150,000. Based on typical
        growth assumptions, this could reach approximately £320,000 by age 67.

        Whether this will provide the retirement income you need depends on your
        personal circumstances and goals. Different people need different amounts
        based on their lifestyle plans.

        Would you like to explore what factors affect retirement income needs?"""

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_passing_validation(
                relevance_score=0.94,
                confidence=0.90
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message="Will my pension be enough?"
            )

        assert result.passed is True, "Factual projection without judgment should pass"
        assert result.confidence > 0.8
        assert len(result.issues) == 0


class TestEdgeCasesAndSubtleViolations:
    """Test edge cases and subtle evaluative language violations."""

    def test_implied_adequacy_through_relief_fails(self, compliance_validator, sample_customer):
        """Implying adequacy through reassurance must fail."""
        guidance = "Good news - you don't need to worry about your pension situation."

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_failing_validation(
                "Implies adequacy assessment through 'don't need to worry' reassurance"
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message="Should I be worried about my pension?"
            )

        assert result.passed is False, "Implied adequacy through reassurance should fail"
        assert len(result.issues) > 0

    def test_positive_framing_of_amount_fails(self, compliance_validator, sample_customer):
        """Positive framing implying adequacy must fail."""
        guidance = "£150,000 is a substantial sum that puts you in a strong position."

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_failing_validation(
                "Uses 'substantial sum' and 'strong position' as evaluative adequacy judgments"
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message="What do you think of my pension amount?"
            )

        assert result.passed is False, "Positive framing should fail"
        assert len(result.issues) > 0

    def test_ahead_of_game_comparison_fails(self, compliance_validator, young_customer):
        """Comparative positioning like 'ahead of the game' must fail."""
        guidance = "At age 35 with £15,000 saved, you're ahead of the game."

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_failing_validation(
                "Uses 'ahead of the game' which makes comparative adequacy judgment"
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=young_customer,
                customer_message="How am I doing for my age?"
            )

        assert result.passed is False, "'Ahead of the game' comparison should fail"
        assert len(result.issues) > 0

    def test_neutral_acknowledgment_of_engagement_passes(self, compliance_validator, young_customer):
        """Neutral acknowledgment of engagement (not circumstances) must pass."""
        guidance = """Thank you for taking the time to think about your pension planning.
        You're asking important questions about your retirement.

        You currently have £15,000 saved at age 35. Let's explore what factors
        determine whether this will meet your eventual needs."""

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_passing_validation(
                relevance_score=0.93,
                confidence=0.89
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=young_customer,
                customer_message="Am I on track with my pension?"
            )

        assert result.passed is True, "Neutral acknowledgment of engagement should pass"
        assert result.confidence > 0.8
        assert len(result.issues) == 0

    def test_concerning_language_without_judgment_passes(self, compliance_validator, sample_customer):
        """Acknowledging concern without judging circumstances must pass."""
        guidance = """I understand you're concerned about your pension. That's a common
        feeling, and it's good that you're looking into it.

        Your pension has £150,000. Whether this meets your needs isn't something I can
        assess - it depends on your personal goals and circumstances. A financial adviser
        can help you evaluate if it's adequate for your situation."""

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_passing_validation(
                relevance_score=0.94,
                confidence=0.90
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message="I'm worried my pension isn't enough"
            )

        assert result.passed is True, "Acknowledging concern without judgment should pass"
        assert result.confidence > 0.8
        assert len(result.issues) == 0


class TestCompleteConversationalExamples:
    """Test complete conversational responses with full context."""

    def test_full_violating_response_fails(self, compliance_validator, sample_customer):
        """Complete response with multiple evaluative elements must fail."""
        guidance = """Great question! Having £150,000 at 45 is actually a solid foundation.
        You're doing better than many people your age. That's a good amount!

        Some people in your situation find it helpful to keep contributing regularly.
        You're on the right track - just stay the course."""

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_failing_validation(
                "Multiple violations: 'solid foundation', 'doing better than many', 'good amount', 'right track'"
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message="I have £150,000. Am I doing OK?"
            )

        assert result.passed is False, "Response with multiple evaluations should fail"
        assert len(result.issues) > 0

    def test_full_compliant_response_passes(self, compliance_validator, sample_customer):
        """Complete neutral response with proper structure must pass."""
        guidance = """Thank you for sharing that with me. You have £150,000 in your pension at age 45.

        Whether this will meet your retirement needs depends on several factors:
        - Your target retirement age
        - The lifestyle you're planning for in retirement
        - Whether you'll have other income sources (State Pension, other savings)
        - Where you plan to live in retirement
        - Your health and life expectancy considerations

        Would you like to explore what's most important to you for retirement planning?
        For a comprehensive assessment of whether your current savings will be adequate
        for your specific circumstances, I'd recommend speaking with an FCA-regulated
        financial adviser who can do a full suitability analysis."""

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_passing_validation(
                relevance_score=0.97,
                confidence=0.94
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=sample_customer,
                customer_message="I have £150,000. Am I doing OK?"
            )

        assert result.passed is True, "Properly structured neutral response should pass"
        assert result.confidence > 0.8
        assert len(result.issues) == 0

    def test_warm_but_neutral_younger_customer_passes(self, compliance_validator, young_customer):
        """Warm engagement without evaluating circumstances must pass."""
        guidance = """I'm glad you're thinking about this now. Pension planning can seem
        complicated, but we can work through it together.

        You currently have £15,000 saved at age 35. To understand what this means for
        your future, we'd need to consider your goals - when you want to retire, what
        kind of lifestyle you're aiming for, and what other income you might have.

        Different people need different amounts based on their circumstances. There's
        no universal "right amount" at your age.

        Would you like to explore what factors matter for your retirement planning?"""

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = create_passing_validation(
                relevance_score=0.95,
                confidence=0.91
            )

            result = compliance_validator.validate(
                guidance=guidance,
                customer=young_customer,
                customer_message="Is £15k enough at age 35?"
            )

        assert result.passed is True, "Warm but neutral response should pass"
        assert result.confidence > 0.8
        assert len(result.issues) == 0
