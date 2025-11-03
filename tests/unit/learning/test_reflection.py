"""Unit tests for reflection and learning from failures."""

import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4
from datetime import datetime

from guidance_agent.learning.reflection import (
    reflect_on_failure,
    validate_principle,
    refine_principle,
    judge_rule_value,
    learn_from_failure,
)
from guidance_agent.core.types import (
    OutcomeResult,
    OutcomeStatus,
    CustomerProfile,
    CustomerDemographics,
    FinancialSituation,
    PensionPot,
)
from guidance_agent.retrieval.retriever import RulesBase
from guidance_agent.core.database import Rule, get_session


@pytest.fixture
def db_session():
    """Get a test database session."""
    session = get_session()
    # Cleanup
    session.query(Rule).delete()
    session.commit()

    yield session

    # Cleanup
    session.query(Rule).delete()
    session.commit()
    session.close()


@pytest.fixture
def rules_base(db_session):
    """Create a rules base for testing."""
    return RulesBase(session=db_session)


@pytest.fixture
def failed_outcome():
    """Create a failed outcome for testing."""
    return OutcomeResult(
        outcome_id=uuid4(),
        status=OutcomeStatus.FAILURE,
        successful=False,
        customer_satisfaction=3.0,
        comprehension=4.0,
        goal_alignment=2.0,
        risks_identified=False,
        guidance_appropriate=False,
        fca_compliant=True,
        understanding_checked=False,
        signposted_when_needed=False,
        reasoning="Customer left confused about risks",
        issues=[
            "Did not adequately explain pension transfer risks",
            "Failed to check customer understanding",
            "Did not use appropriate language for low financial literacy",
        ],
        timestamp=datetime.now(),
    )


@pytest.fixture
def sample_customer_profile():
    """Create a sample customer profile."""
    demographics = CustomerDemographics(
        age=58,
        gender="female",
        location="Manchester",
        employment_status="employed",
        financial_literacy="low",
    )

    financial = FinancialSituation(
        annual_income=35000.0,
        total_assets=100000.0,
        total_debt=20000.0,
        dependents=0,
        risk_tolerance="low",
    )

    pension = PensionPot(
        pot_id="pot-456",
        provider="XYZ Pensions",
        pot_type="defined_benefit",
        current_value=300000.0,
        projected_value=350000.0,
        age_accessible=60,
        is_db_scheme=True,
        db_guaranteed_amount=18000.0,
    )

    return CustomerProfile(
        customer_id=uuid4(),
        demographics=demographics,
        financial=financial,
        pensions=[pension],
        goals="Understand pension transfer options",
        presenting_question="Should I transfer my DB pension to access it early?",
    )


@pytest.fixture
def sample_guidance():
    """Sample guidance text that failed."""
    return """You could transfer your DB pension to a DC scheme to access it at 55.
This would give you more flexibility. The transfer value is £300,000."""


class TestReflectOnFailure:
    """Tests for reflect_on_failure function."""

    @patch("guidance_agent.learning.reflection.completion")
    def test_reflect_on_failure_basic(
        self, mock_completion, sample_customer_profile, sample_guidance, failed_outcome
    ):
        """Test basic reflection on failure."""
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="""Principle: When customers have low financial literacy,
                    always explain complex concepts in simple terms and check understanding.

                    Domain: communication"""
                )
            )
        ]
        mock_completion.return_value = mock_response

        reflection = reflect_on_failure(
            customer_profile=sample_customer_profile,
            guidance_provided=sample_guidance,
            outcome=failed_outcome,
        )

        assert "principle" in reflection
        assert "domain" in reflection
        assert len(reflection["principle"]) > 0
        assert len(reflection["domain"]) > 0

    @patch("guidance_agent.learning.reflection.completion")
    def test_reflect_identifies_communication_issue(
        self, mock_completion, sample_customer_profile, sample_guidance, failed_outcome
    ):
        """Test that reflection identifies communication issues."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="""Principle: Adapt language complexity to customer's financial literacy level.

                    Domain: communication"""
                )
            )
        ]
        mock_completion.return_value = mock_response

        reflection = reflect_on_failure(
            customer_profile=sample_customer_profile,
            guidance_provided=sample_guidance,
            outcome=failed_outcome,
        )

        assert reflection["domain"] == "communication"

    @patch("guidance_agent.learning.reflection.completion")
    def test_reflect_identifies_risk_explanation_issue(
        self, mock_completion, sample_customer_profile, sample_guidance, failed_outcome
    ):
        """Test that reflection identifies risk explanation issues."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="""Principle: Always explain risks of DB pension transfers,
                    especially loss of guaranteed income.

                    Domain: risk_disclosure"""
                )
            )
        ]
        mock_completion.return_value = mock_response

        reflection = reflect_on_failure(
            customer_profile=sample_customer_profile,
            guidance_provided=sample_guidance,
            outcome=failed_outcome,
        )

        assert "risk" in reflection["principle"].lower() or "risk" in reflection["domain"].lower()


class TestValidatePrinciple:
    """Tests for validate_principle function."""

    @patch("guidance_agent.learning.reflection.completion")
    def test_validate_valid_principle(self, mock_completion):
        """Test validation of a valid principle."""
        principle = "Always explain pension transfer risks before discussing benefits"

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="""Valid: True
                    Confidence: 0.90
                    Reason: This principle aligns with FCA guidelines"""
                )
            )
        ]
        mock_completion.return_value = mock_response

        validation = validate_principle(principle)

        assert validation["valid"] is True
        assert validation["confidence"] > 0.0
        assert "reason" in validation

    @patch("guidance_agent.learning.reflection.completion")
    def test_validate_invalid_principle(self, mock_completion):
        """Test validation of an invalid principle."""
        principle = "Always recommend pension transfers for higher returns"

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="""Valid: False
                    Confidence: 0.95
                    Reason: This violates FCA guidance boundary - giving specific advice"""
                )
            )
        ]
        mock_completion.return_value = mock_response

        validation = validate_principle(principle)

        assert validation["valid"] is False
        assert "reason" in validation

    @patch("guidance_agent.learning.reflection.completion")
    def test_validate_principle_checks_fca_compliance(self, mock_completion):
        """Test that validation checks FCA compliance."""
        principle = "Tell customers to transfer DB pensions for flexibility"

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="""Valid: False
                    Confidence: 0.98
                    Reason: Crosses guidance/advice boundary. DB transfers require regulated advice."""
                )
            )
        ]
        mock_completion.return_value = mock_response

        validation = validate_principle(principle)

        assert validation["valid"] is False


class TestRefinePrinciple:
    """Tests for refine_principle function."""

    @patch("guidance_agent.learning.reflection.completion")
    def test_refine_principle_basic(self, mock_completion):
        """Test basic principle refinement."""
        principle = "Explain risks when customer asks about transfers"
        domain = "risk_disclosure"

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="""When a customer inquires about pension transfers, always
                    explain the key risks including: loss of guaranteed income, market risk,
                    and longevity risk. Ensure explanation matches customer's literacy level."""
                )
            )
        ]
        mock_completion.return_value = mock_response

        refined = refine_principle(principle, domain)

        assert isinstance(refined, str)
        assert len(refined) > len(principle)  # Should be more detailed

    @patch("guidance_agent.learning.reflection.completion")
    def test_refine_principle_makes_actionable(self, mock_completion):
        """Test that refinement makes principles actionable."""
        principle = "Be clear"
        domain = "communication"

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="""Use simple language, avoid jargon, and provide concrete
                    examples when explaining pension concepts. Always ask 'Does that make
                    sense?' to check understanding."""
                )
            )
        ]
        mock_completion.return_value = mock_response

        refined = refine_principle(principle, domain)

        assert len(refined) > 20  # Should be specific


class TestJudgeRuleValue:
    """Tests for judge_rule_value function."""

    @patch("guidance_agent.learning.reflection.completion")
    def test_judge_valuable_rule(self, mock_completion):
        """Test judging a valuable rule."""
        rule_principle = "Always warn about DB pension transfer risks before age 55"
        domain = "defined_benefit_transfers"

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Valuable: True\nScore: 0.92"))
        ]
        mock_completion.return_value = mock_response

        is_valuable = judge_rule_value(rule_principle, domain)

        assert is_valuable is True

    @patch("guidance_agent.learning.reflection.completion")
    def test_judge_not_valuable_rule(self, mock_completion):
        """Test judging a non-valuable rule."""
        rule_principle = "Always greet customer politely"
        domain = "general"

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Valuable: False\nScore: 0.30"))
        ]
        mock_completion.return_value = mock_response

        is_valuable = judge_rule_value(rule_principle, domain)

        assert is_valuable is False


class TestLearnFromFailure:
    """Tests for learn_from_failure function (integration)."""

    @patch("guidance_agent.learning.reflection.embed")
    @patch("guidance_agent.learning.reflection.judge_rule_value")
    @patch("guidance_agent.learning.reflection.refine_principle")
    @patch("guidance_agent.learning.reflection.validate_principle")
    @patch("guidance_agent.learning.reflection.reflect_on_failure")
    def test_learn_from_failure_adds_rule(
        self,
        mock_reflect,
        mock_validate,
        mock_refine,
        mock_judge,
        mock_embed,
        rules_base,
        sample_customer_profile,
        sample_guidance,
        failed_outcome,
        db_session,
    ):
        """Test that learning from failure adds a rule."""
        # Mock the learning pipeline
        mock_reflect.return_value = {
            "principle": "Explain risks clearly to low literacy customers",
            "domain": "risk_disclosure",
        }
        mock_validate.return_value = {"valid": True, "confidence": 0.85, "reason": "Good"}
        mock_refine.return_value = "When explaining pension risks to customers with low financial literacy, use simple language and concrete examples."
        mock_judge.return_value = True
        mock_embed.return_value = [0.1] * 1536

        initial_count = db_session.query(Rule).count()

        learn_from_failure(
            rules_base=rules_base,
            customer_profile=sample_customer_profile,
            guidance_provided=sample_guidance,
            outcome=failed_outcome,
        )

        # Should have added one rule
        final_count = db_session.query(Rule).count()
        assert final_count == initial_count + 1

    @patch("guidance_agent.learning.reflection.embed")
    @patch("guidance_agent.learning.reflection.judge_rule_value")
    @patch("guidance_agent.learning.reflection.refine_principle")
    @patch("guidance_agent.learning.reflection.validate_principle")
    @patch("guidance_agent.learning.reflection.reflect_on_failure")
    def test_learn_from_failure_rejects_invalid_principle(
        self,
        mock_reflect,
        mock_validate,
        mock_refine,
        mock_judge,
        mock_embed,
        rules_base,
        sample_customer_profile,
        sample_guidance,
        failed_outcome,
        db_session,
    ):
        """Test that invalid principles are rejected."""
        # Mock invalid principle
        mock_reflect.return_value = {
            "principle": "Always recommend transfers",
            "domain": "advice",
        }
        mock_validate.return_value = {
            "valid": False,
            "confidence": 0.95,
            "reason": "Crosses advice boundary",
        }

        initial_count = db_session.query(Rule).count()

        learn_from_failure(
            rules_base=rules_base,
            customer_profile=sample_customer_profile,
            guidance_provided=sample_guidance,
            outcome=failed_outcome,
        )

        # Should not have added any rules
        final_count = db_session.query(Rule).count()
        assert final_count == initial_count

    @patch("guidance_agent.learning.reflection.embed")
    @patch("guidance_agent.learning.reflection.judge_rule_value")
    @patch("guidance_agent.learning.reflection.refine_principle")
    @patch("guidance_agent.learning.reflection.validate_principle")
    @patch("guidance_agent.learning.reflection.reflect_on_failure")
    def test_learn_from_failure_rejects_low_value_rule(
        self,
        mock_reflect,
        mock_validate,
        mock_refine,
        mock_judge,
        mock_embed,
        rules_base,
        sample_customer_profile,
        sample_guidance,
        failed_outcome,
        db_session,
    ):
        """Test that low-value rules are rejected."""
        # Mock low-value rule
        mock_reflect.return_value = {"principle": "Be nice", "domain": "general"}
        mock_validate.return_value = {"valid": True, "confidence": 0.70, "reason": "OK"}
        mock_refine.return_value = "Be polite and friendly"
        mock_judge.return_value = False  # Low value

        initial_count = db_session.query(Rule).count()

        learn_from_failure(
            rules_base=rules_base,
            customer_profile=sample_customer_profile,
            guidance_provided=sample_guidance,
            outcome=failed_outcome,
        )

        # Should not have added any rules
        final_count = db_session.query(Rule).count()
        assert final_count == initial_count

    @patch("guidance_agent.learning.reflection.embed")
    @patch("guidance_agent.learning.reflection.judge_rule_value")
    @patch("guidance_agent.learning.reflection.refine_principle")
    @patch("guidance_agent.learning.reflection.validate_principle")
    @patch("guidance_agent.learning.reflection.reflect_on_failure")
    def test_learn_from_failure_stores_correct_confidence(
        self,
        mock_reflect,
        mock_validate,
        mock_refine,
        mock_judge,
        mock_embed,
        rules_base,
        sample_customer_profile,
        sample_guidance,
        failed_outcome,
        db_session,
    ):
        """Test that stored rule has correct confidence from validation."""
        mock_reflect.return_value = {
            "principle": "Check understanding",
            "domain": "communication",
        }
        mock_validate.return_value = {"valid": True, "confidence": 0.78, "reason": "Good"}
        mock_refine.return_value = "Always ask customer if explanation makes sense"
        mock_judge.return_value = True
        mock_embed.return_value = [0.1] * 1536

        learn_from_failure(
            rules_base=rules_base,
            customer_profile=sample_customer_profile,
            guidance_provided=sample_guidance,
            outcome=failed_outcome,
        )

        # Check stored rule
        rule = db_session.query(Rule).first()
        assert rule is not None
        assert rule.confidence == 0.78

    def test_learn_from_success_ignored(
        self, rules_base, sample_customer_profile, sample_guidance, db_session
    ):
        """Test that successful outcomes don't trigger reflection."""
        successful_outcome = OutcomeResult(
            status=OutcomeStatus.SUCCESS,
            successful=True,
            customer_satisfaction=9.0,
        )

        initial_count = db_session.query(Rule).count()

        learn_from_failure(
            rules_base=rules_base,
            customer_profile=sample_customer_profile,
            guidance_provided=sample_guidance,
            outcome=successful_outcome,
        )

        # Should not add rules for successful outcomes
        final_count = db_session.query(Rule).count()
        assert final_count == initial_count
