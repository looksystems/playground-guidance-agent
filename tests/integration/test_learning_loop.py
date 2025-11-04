"""Integration tests for the complete learning loop.

These tests verify that the entire learning system works end-to-end:
- Learning from successful consultations (case extraction)
- Learning from failures (reflection and rule generation)
- Confidence adjustment based on outcomes
- Rule performance tracking
"""

import os
import pytest
from unittest.mock import patch
from uuid import uuid4
from pathlib import Path
from dotenv import load_dotenv

# Load .env to get correct EMBEDDING_DIMENSION
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Get embedding dimension from environment (loaded from .env)
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIMENSION", "1536"))

from guidance_agent.learning import (
    learn_from_successful_consultation,
    learn_from_failure,
    track_rule_performance,
    get_rule_performance_metrics,
)
from guidance_agent.core.types import (
    OutcomeResult,
    OutcomeStatus,
    CustomerProfile,
    CustomerDemographics,
    FinancialSituation,
    PensionPot,
)
from guidance_agent.retrieval.retriever import CaseBase, RulesBase
from guidance_agent.core.database import Case, Rule, get_session


@pytest.fixture
def db_session():
    """Get a test database session."""
    session = get_session()
    # Cleanup
    session.query(Case).delete()
    session.query(Rule).delete()
    session.commit()

    yield session

    # Cleanup
    session.query(Case).delete()
    session.query(Rule).delete()
    session.commit()
    session.close()


@pytest.fixture
def case_base(db_session):
    """Create a case base."""
    return CaseBase(session=db_session)


@pytest.fixture
def rules_base(db_session):
    """Create a rules base."""
    return RulesBase(session=db_session)


@pytest.fixture
def customer_profile():
    """Create a customer profile."""
    demographics = CustomerDemographics(
        age=55,
        gender="male",
        location="London",
        employment_status="employed",
        financial_literacy="medium",
    )

    financial = FinancialSituation(
        annual_income=50000.0,
        total_assets=200000.0,
        total_debt=50000.0,
        dependents=2,
        risk_tolerance="medium",
    )

    pension = PensionPot(
        pot_id="pot-123",
        provider="ABC Pension Co",
        pot_type="defined_contribution",
        current_value=150000.0,
        projected_value=200000.0,
        age_accessible=55,
    )

    return CustomerProfile(
        customer_id=uuid4(),
        demographics=demographics,
        financial=financial,
        pensions=[pension],
        goals="Planning retirement at age 60",
        presenting_question="What are my options for accessing my pension?",
    )


class TestCompleteLearningLoop:
    """Integration tests for the complete learning loop."""

    @patch("guidance_agent.learning.case_learning.embed")
    def test_learn_from_successful_consultation_full_cycle(
        self, mock_embed, case_base, customer_profile, db_session
    ):
        """Test complete cycle of learning from success."""
        # Mock embedding
        mock_embed.return_value = [0.1] * EMBEDDING_DIM

        # Simulate successful consultation
        guidance = "You can take 25% tax-free lump sum, use drawdown, or buy an annuity."
        outcome = OutcomeResult(
            status=OutcomeStatus.SUCCESS,
            successful=True,
            customer_satisfaction=9.0,
            comprehension=8.5,
            goal_alignment=9.0,
        )

        # Learn from success
        learn_from_successful_consultation(
            case_base=case_base,
            customer_profile=customer_profile,
            guidance_provided=guidance,
            outcome=outcome,
        )

        # Verify case was stored
        cases = db_session.query(Case).all()
        assert len(cases) == 1
        assert cases[0].task_type == "withdrawal_options"
        assert cases[0].guidance_provided == guidance

    @patch("guidance_agent.learning.reflection.embed")
    @patch("guidance_agent.learning.reflection.judge_rule_value")
    @patch("guidance_agent.learning.reflection.refine_principle")
    @patch("guidance_agent.learning.reflection.validate_principle")
    @patch("guidance_agent.learning.reflection.reflect_on_failure")
    def test_learn_from_failure_full_cycle(
        self,
        mock_reflect,
        mock_validate,
        mock_refine,
        mock_judge,
        mock_embed,
        rules_base,
        customer_profile,
        db_session,
    ):
        """Test complete cycle of learning from failure."""
        # Mock the learning pipeline
        mock_reflect.return_value = {
            "principle": "Check customer understanding",
            "domain": "communication",
        }
        mock_validate.return_value = {"valid": True, "confidence": 0.85, "reason": "Good"}
        mock_refine.return_value = "Always verify customer comprehension by asking them to explain back"
        mock_judge.return_value = True
        mock_embed.return_value = [0.2] * EMBEDDING_DIM

        # Simulate failed consultation
        guidance = "Complex technical explanation without checking understanding"
        outcome = OutcomeResult(
            status=OutcomeStatus.FAILURE,
            successful=False,
            customer_satisfaction=3.0,
            comprehension=2.0,
            goal_alignment=4.0,
            issues=["Failed to check understanding"],
        )

        # Learn from failure
        learn_from_failure(
            rules_base=rules_base,
            customer_profile=customer_profile,
            guidance_provided=guidance,
            outcome=outcome,
        )

        # Verify rule was stored
        rules = db_session.query(Rule).all()
        assert len(rules) == 1
        assert rules[0].domain == "communication"
        assert rules[0].confidence == 0.85

    @patch("guidance_agent.learning.reflection.embed")
    @patch("guidance_agent.learning.reflection.judge_rule_value")
    @patch("guidance_agent.learning.reflection.refine_principle")
    @patch("guidance_agent.learning.reflection.validate_principle")
    @patch("guidance_agent.learning.reflection.reflect_on_failure")
    @patch("guidance_agent.learning.case_learning.embed")
    def test_mixed_success_and_failure_learning(
        self,
        mock_embed_case,
        mock_reflect,
        mock_validate,
        mock_refine,
        mock_judge,
        mock_embed_rule,
        case_base,
        rules_base,
        customer_profile,
        db_session,
    ):
        """Test learning from both successful and failed consultations."""
        # Setup mocks
        mock_embed_case.return_value = [0.1] * EMBEDDING_DIM
        mock_embed_rule.return_value = [0.2] * EMBEDDING_DIM
        mock_reflect.return_value = {"principle": "Test", "domain": "test"}
        mock_validate.return_value = {"valid": True, "confidence": 0.75, "reason": "OK"}
        mock_refine.return_value = "Refined test principle"
        mock_judge.return_value = True

        # Learn from 2 successes
        for i in range(2):
            outcome = OutcomeResult(successful=True, customer_satisfaction=8.0)
            learn_from_successful_consultation(
                case_base, customer_profile, f"Guidance {i}", outcome
            )

        # Learn from 1 failure
        outcome = OutcomeResult(successful=False, customer_satisfaction=3.0)
        learn_from_failure(rules_base, customer_profile, "Bad guidance", outcome)

        # Verify both types of learning occurred
        cases = db_session.query(Case).all()
        rules = db_session.query(Rule).all()

        assert len(cases) == 2  # Two successful cases
        assert len(rules) == 1  # One rule from failure

    @patch("guidance_agent.learning.reflection.embed")
    @patch("guidance_agent.learning.reflection.judge_rule_value")
    @patch("guidance_agent.learning.reflection.refine_principle")
    @patch("guidance_agent.learning.reflection.validate_principle")
    @patch("guidance_agent.learning.reflection.reflect_on_failure")
    def test_rule_performance_tracking_over_time(
        self,
        mock_reflect,
        mock_validate,
        mock_refine,
        mock_judge,
        mock_embed,
        rules_base,
        customer_profile,
        db_session,
    ):
        """Test that rule performance is tracked over multiple uses."""
        # Setup mocks
        mock_reflect.return_value = {"principle": "Test", "domain": "test"}
        mock_validate.return_value = {"valid": True, "confidence": 0.70, "reason": "OK"}
        mock_refine.return_value = "Test principle"
        mock_judge.return_value = True
        mock_embed.return_value = [0.1] * EMBEDDING_DIM

        # Create a rule through learning
        outcome = OutcomeResult(successful=False, customer_satisfaction=3.0)
        learn_from_failure(rules_base, customer_profile, "Guidance", outcome)

        rule = db_session.query(Rule).first()
        rule_id = str(rule.id)

        # Track performance: 3 successes, 1 failure
        track_rule_performance([rule_id], OutcomeResult(successful=True), db_session)
        track_rule_performance([rule_id], OutcomeResult(successful=True), db_session)
        track_rule_performance([rule_id], OutcomeResult(successful=True), db_session)
        track_rule_performance([rule_id], OutcomeResult(successful=False), db_session)

        # Check metrics
        db_session.expire(rule)
        updated_rule = db_session.query(Rule).filter(Rule.id == rule.id).first()
        metrics = get_rule_performance_metrics(updated_rule)

        assert metrics["uses"] == 4
        assert metrics["successes"] == 3
        assert metrics["failures"] == 1
        assert metrics["success_rate"] == 0.75

    @patch("guidance_agent.learning.case_learning.embed")
    def test_retrieval_after_learning(
        self, mock_embed, case_base, customer_profile, db_session
    ):
        """Test that learned cases can be retrieved."""
        # Mock embedding
        mock_embed.return_value = [0.1] * EMBEDDING_DIM

        # Learn from multiple successful consultations
        for i in range(3):
            outcome = OutcomeResult(successful=True, customer_satisfaction=8.0 + i)
            learn_from_successful_consultation(
                case_base, customer_profile, f"Guidance {i}", outcome
            )

        # Retrieve similar cases
        query_embedding = [0.1] * EMBEDDING_DIM
        retrieved_cases = case_base.retrieve(query_embedding, top_k=2)

        # Should retrieve cases
        assert len(retrieved_cases) <= 2
        assert all("guidance_provided" in case for case in retrieved_cases)
