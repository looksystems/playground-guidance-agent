"""Tests for evaluation pipeline.

Following TDD approach: Write tests FIRST, then implement.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4

from guidance_agent.evaluation.evaluator import evaluate_advisor
from guidance_agent.evaluation.metrics import AdvisorMetrics
from guidance_agent.core.types import OutcomeResult, OutcomeStatus, AdvisorProfile, CustomerProfile
from guidance_agent.advisor.agent import AdvisorAgent
from guidance_agent.customer.agent import CustomerAgent


class TestEvaluateAdvisor:
    """Test evaluate_advisor function."""

    def test_evaluate_advisor_empty_customer_list(self):
        """Test evaluation with no customers."""
        # Setup
        advisor_profile = AdvisorProfile(
            name="Test Advisor",
            description="Test description",
        )
        advisor = AdvisorAgent(profile=advisor_profile)

        # Evaluate with empty list
        metrics = evaluate_advisor(advisor, [])

        # Should return zero metrics
        assert metrics.overall_quality == 0.0
        assert metrics.compliance_rate == 0.0
        assert metrics.satisfaction == 0.0

    @patch("guidance_agent.evaluation.evaluator.run_consultation")
    def test_evaluate_advisor_single_customer(self, mock_run_consultation):
        """Test evaluation with single customer."""
        # Setup advisor
        advisor_profile = AdvisorProfile(
            name="Test Advisor",
            description="Test description",
        )
        advisor = AdvisorAgent(profile=advisor_profile)

        # Setup customer
        customer_profile = CustomerProfile()
        customer = CustomerAgent(profile=customer_profile)

        # Mock consultation outcome
        mock_outcome = OutcomeResult(
            successful=True,
            customer_satisfaction=8.0,
            comprehension=7.5,
            goal_alignment=8.5,
            risks_identified=True,
            guidance_appropriate=True,
            fca_compliant=True,
            understanding_checked=True,
            signposted_when_needed=True,
        )
        mock_run_consultation.return_value = mock_outcome

        # Evaluate
        metrics = evaluate_advisor(advisor, [customer])

        # Verify consultation was run
        mock_run_consultation.assert_called_once_with(advisor, customer, max_turns=20)

        # Verify metrics
        assert metrics.overall_quality == 1.0
        assert metrics.compliance_rate == 1.0
        assert metrics.satisfaction == 8.0
        assert metrics.comprehension == 7.5
        assert metrics.goal_alignment == 8.5

    @patch("guidance_agent.evaluation.evaluator.run_consultation")
    def test_evaluate_advisor_multiple_customers(self, mock_run_consultation):
        """Test evaluation with multiple customers."""
        # Setup advisor
        advisor_profile = AdvisorProfile(
            name="Test Advisor",
            description="Test description",
        )
        advisor = AdvisorAgent(profile=advisor_profile)

        # Setup customers
        customers = [
            CustomerAgent(profile=CustomerProfile()),
            CustomerAgent(profile=CustomerProfile()),
            CustomerAgent(profile=CustomerProfile()),
        ]

        # Mock consultation outcomes with varying results
        outcomes = [
            OutcomeResult(
                successful=True,
                customer_satisfaction=9.0,
                comprehension=8.5,
                goal_alignment=9.0,
                risks_identified=True,
                guidance_appropriate=True,
                fca_compliant=True,
            ),
            OutcomeResult(
                successful=False,
                customer_satisfaction=4.0,
                comprehension=5.0,
                goal_alignment=4.5,
                risks_identified=False,
                guidance_appropriate=False,
                fca_compliant=False,
            ),
            OutcomeResult(
                successful=True,
                customer_satisfaction=8.0,
                comprehension=7.0,
                goal_alignment=8.0,
                risks_identified=True,
                guidance_appropriate=True,
                fca_compliant=True,
            ),
        ]
        mock_run_consultation.side_effect = outcomes

        # Evaluate
        metrics = evaluate_advisor(advisor, customers)

        # Verify consultations were run
        assert mock_run_consultation.call_count == 3

        # Verify metrics (2 out of 3 successful)
        assert metrics.overall_quality == pytest.approx(2 / 3)
        assert metrics.compliance_rate == pytest.approx(2 / 3)
        assert metrics.satisfaction == 7.0  # (9+4+8)/3
        assert metrics.comprehension == pytest.approx(20.5 / 3)  # (8.5+5+7)/3

    @patch("guidance_agent.evaluation.evaluator.run_consultation")
    def test_evaluate_advisor_all_successful(self, mock_run_consultation):
        """Test evaluation with all successful consultations."""
        # Setup
        advisor = AdvisorAgent(
            profile=AdvisorProfile(name="Test", description="Test")
        )
        customers = [CustomerAgent(profile=CustomerProfile()) for _ in range(5)]

        # All successful outcomes
        perfect_outcome = OutcomeResult(
            successful=True,
            customer_satisfaction=9.0,
            comprehension=8.5,
            goal_alignment=9.0,
            risks_identified=True,
            guidance_appropriate=True,
            fca_compliant=True,
            understanding_checked=True,
            signposted_when_needed=True,
        )
        mock_run_consultation.return_value = perfect_outcome

        # Evaluate
        metrics = evaluate_advisor(advisor, customers)

        # All should be perfect
        assert metrics.overall_quality == 1.0
        assert metrics.compliance_rate == 1.0
        assert metrics.risk_assessment_accuracy == 1.0
        assert metrics.guidance_appropriateness == 1.0

    @patch("guidance_agent.evaluation.evaluator.run_consultation")
    def test_evaluate_advisor_all_failed(self, mock_run_consultation):
        """Test evaluation with all failed consultations."""
        # Setup
        advisor = AdvisorAgent(
            profile=AdvisorProfile(name="Test", description="Test")
        )
        customers = [CustomerAgent(profile=CustomerProfile()) for _ in range(3)]

        # All failed outcomes
        failed_outcome = OutcomeResult(
            successful=False,
            customer_satisfaction=3.0,
            comprehension=4.0,
            goal_alignment=3.5,
            risks_identified=False,
            guidance_appropriate=False,
            fca_compliant=False,
            understanding_checked=False,
            signposted_when_needed=False,
        )
        mock_run_consultation.return_value = failed_outcome

        # Evaluate
        metrics = evaluate_advisor(advisor, customers)

        # All should be failed
        assert metrics.overall_quality == 0.0
        assert metrics.compliance_rate == 0.0
        assert metrics.risk_assessment_accuracy == 0.0
        assert metrics.guidance_appropriateness == 0.0

    @patch("guidance_agent.evaluation.evaluator.run_consultation")
    def test_evaluate_advisor_with_db_pensions(self, mock_run_consultation):
        """Test evaluation with DB pension scenarios."""
        # Setup
        advisor = AdvisorAgent(
            profile=AdvisorProfile(name="Test", description="Test")
        )
        customers = [CustomerAgent(profile=CustomerProfile()) for _ in range(4)]

        # Mixed DB pension outcomes
        outcomes = [
            OutcomeResult(has_db_pension=True, db_warning_given=True),
            OutcomeResult(has_db_pension=True, db_warning_given=False),
            OutcomeResult(has_db_pension=False, db_warning_given=False),
            OutcomeResult(has_db_pension=True, db_warning_given=True),
        ]
        mock_run_consultation.side_effect = outcomes

        # Evaluate
        metrics = evaluate_advisor(advisor, customers)

        # 2 out of 3 DB pensions warned correctly
        assert metrics.db_warning_rate == pytest.approx(2 / 3)

    @patch("guidance_agent.evaluation.evaluator.run_consultation")
    def test_evaluate_advisor_preserves_customer_order(self, mock_run_consultation):
        """Test that customers are evaluated in order."""
        # Setup
        advisor = AdvisorAgent(
            profile=AdvisorProfile(name="Test", description="Test")
        )
        customers = [
            CustomerAgent(profile=CustomerProfile()),
            CustomerAgent(profile=CustomerProfile()),
            CustomerAgent(profile=CustomerProfile()),
        ]

        # Different outcomes
        outcomes = [
            OutcomeResult(customer_satisfaction=5.0),
            OutcomeResult(customer_satisfaction=7.0),
            OutcomeResult(customer_satisfaction=9.0),
        ]
        mock_run_consultation.side_effect = outcomes

        # Evaluate
        metrics = evaluate_advisor(advisor, customers)

        # Verify customers called in order
        calls = mock_run_consultation.call_args_list
        assert len(calls) == 3
        for i, call in enumerate(calls):
            assert call[0][0] == advisor  # First arg is advisor
            assert call[0][1] == customers[i]  # Second arg is customer in order

    @patch("guidance_agent.evaluation.evaluator.run_consultation")
    def test_evaluate_advisor_handles_consultation_exceptions(
        self, mock_run_consultation
    ):
        """Test that evaluation handles consultation failures gracefully."""
        # Setup
        advisor = AdvisorAgent(
            profile=AdvisorProfile(name="Test", description="Test")
        )
        customers = [CustomerAgent(profile=CustomerProfile()) for _ in range(3)]

        # First succeeds, second throws exception, third succeeds
        def side_effect(advisor, customer, max_turns=20):
            if customer == customers[1]:
                raise Exception("Consultation failed")
            return OutcomeResult(successful=True, customer_satisfaction=8.0)

        mock_run_consultation.side_effect = side_effect

        # Evaluate - should raise the exception
        with pytest.raises(Exception, match="Consultation failed"):
            evaluate_advisor(advisor, customers)

    @patch("guidance_agent.evaluation.evaluator.run_consultation")
    def test_evaluate_advisor_realistic_scenario(self, mock_run_consultation):
        """Test with realistic mixed outcomes."""
        # Setup
        advisor = AdvisorAgent(
            profile=AdvisorProfile(
                name="Jane Smith",
                description="Experienced pension advisor",
                experience_level="senior",
            )
        )
        customers = [CustomerAgent(profile=CustomerProfile()) for _ in range(10)]

        # Realistic mix: mostly successful with some issues
        outcomes = [
            # 7 successful
            OutcomeResult(
                successful=True,
                customer_satisfaction=8.5,
                comprehension=8.0,
                goal_alignment=8.5,
                risks_identified=True,
                guidance_appropriate=True,
                fca_compliant=True,
                understanding_checked=True,
                signposted_when_needed=True,
            )
            for _ in range(7)
        ] + [
            # 2 partially successful
            OutcomeResult(
                successful=True,
                customer_satisfaction=7.0,
                comprehension=6.5,
                goal_alignment=7.0,
                risks_identified=True,
                guidance_appropriate=True,
                fca_compliant=True,
                understanding_checked=True,
                signposted_when_needed=False,
            )
            for _ in range(2)
        ] + [
            # 1 failed
            OutcomeResult(
                successful=False,
                customer_satisfaction=5.0,
                comprehension=4.5,
                goal_alignment=5.0,
                risks_identified=False,
                guidance_appropriate=False,
                fca_compliant=False,
                understanding_checked=False,
                signposted_when_needed=False,
            )
        ]
        mock_run_consultation.side_effect = outcomes

        # Evaluate
        metrics = evaluate_advisor(advisor, customers)

        # Verify realistic metrics
        assert metrics.overall_quality == 0.9  # 9/10
        assert metrics.compliance_rate == 0.9  # 9/10
        assert metrics.signposting_rate == 0.7  # 7/10
        assert metrics.satisfaction >= 7.0  # Should be decent average
