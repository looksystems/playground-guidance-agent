"""Tests for metrics calculation.

Following TDD approach: Write tests FIRST, then implement.
"""

import pytest
from uuid import uuid4
from datetime import datetime

from guidance_agent.evaluation.metrics import AdvisorMetrics, calculate_metrics
from guidance_agent.core.types import OutcomeResult, OutcomeStatus


class TestAdvisorMetrics:
    """Test AdvisorMetrics dataclass."""

    def test_advisor_metrics_creation(self):
        """Test creating AdvisorMetrics instance."""
        metrics = AdvisorMetrics(
            risk_assessment_accuracy=0.95,
            guidance_appropriateness=0.90,
            compliance_rate=0.98,
            satisfaction=8.5,
            comprehension=7.8,
            goal_alignment=8.2,
            understanding_verification_rate=0.85,
            signposting_rate=0.75,
            db_warning_rate=0.95,
            overall_quality=0.92,
        )

        assert metrics.risk_assessment_accuracy == 0.95
        assert metrics.guidance_appropriateness == 0.90
        assert metrics.compliance_rate == 0.98
        assert metrics.satisfaction == 8.5
        assert metrics.comprehension == 7.8
        assert metrics.goal_alignment == 8.2
        assert metrics.understanding_verification_rate == 0.85
        assert metrics.signposting_rate == 0.75
        assert metrics.db_warning_rate == 0.95
        assert metrics.overall_quality == 0.92

    def test_advisor_metrics_default_values(self):
        """Test that all fields are required (no defaults)."""
        # This should fail if fields have defaults
        with pytest.raises(TypeError):
            AdvisorMetrics()


class TestCalculateMetrics:
    """Test calculate_metrics function."""

    def test_calculate_metrics_empty_list(self):
        """Test calculating metrics with empty outcome list."""
        metrics = calculate_metrics([])

        # Empty list should return zeros
        assert metrics.risk_assessment_accuracy == 0.0
        assert metrics.guidance_appropriateness == 0.0
        assert metrics.compliance_rate == 0.0
        assert metrics.satisfaction == 0.0
        assert metrics.comprehension == 0.0
        assert metrics.goal_alignment == 0.0
        assert metrics.understanding_verification_rate == 0.0
        assert metrics.signposting_rate == 0.0
        assert metrics.db_warning_rate == 0.0
        assert metrics.overall_quality == 0.0

    def test_calculate_metrics_single_perfect_outcome(self):
        """Test metrics with single perfect outcome."""
        outcome = OutcomeResult(
            outcome_id=uuid4(),
            status=OutcomeStatus.SUCCESS,
            successful=True,
            customer_satisfaction=10.0,
            comprehension=10.0,
            goal_alignment=10.0,
            risks_identified=True,
            guidance_appropriate=True,
            fca_compliant=True,
            understanding_checked=True,
            signposted_when_needed=True,
            has_db_pension=False,
            db_warning_given=False,
        )

        metrics = calculate_metrics([outcome])

        assert metrics.risk_assessment_accuracy == 1.0
        assert metrics.guidance_appropriateness == 1.0
        assert metrics.compliance_rate == 1.0
        assert metrics.satisfaction == 10.0
        assert metrics.comprehension == 10.0
        assert metrics.goal_alignment == 10.0
        assert metrics.understanding_verification_rate == 1.0
        assert metrics.signposting_rate == 1.0
        assert metrics.db_warning_rate == 0.0  # No DB pensions
        assert metrics.overall_quality == 1.0

    def test_calculate_metrics_single_failed_outcome(self):
        """Test metrics with single failed outcome."""
        outcome = OutcomeResult(
            outcome_id=uuid4(),
            status=OutcomeStatus.FAILURE,
            successful=False,
            customer_satisfaction=3.0,
            comprehension=4.0,
            goal_alignment=2.0,
            risks_identified=False,
            guidance_appropriate=False,
            fca_compliant=False,
            understanding_checked=False,
            signposted_when_needed=False,
            has_db_pension=True,
            db_warning_given=False,  # Should have warned but didn't
        )

        metrics = calculate_metrics([outcome])

        assert metrics.risk_assessment_accuracy == 0.0
        assert metrics.guidance_appropriateness == 0.0
        assert metrics.compliance_rate == 0.0
        assert metrics.satisfaction == 3.0
        assert metrics.comprehension == 4.0
        assert metrics.goal_alignment == 2.0
        assert metrics.understanding_verification_rate == 0.0
        assert metrics.signposting_rate == 0.0
        assert metrics.db_warning_rate == 0.0  # Failed to warn
        assert metrics.overall_quality == 0.0

    def test_calculate_metrics_multiple_outcomes_perfect(self):
        """Test metrics with multiple perfect outcomes."""
        outcomes = [
            OutcomeResult(
                successful=True,
                customer_satisfaction=9.0,
                comprehension=8.5,
                goal_alignment=9.5,
                risks_identified=True,
                guidance_appropriate=True,
                fca_compliant=True,
                understanding_checked=True,
                signposted_when_needed=True,
            )
            for _ in range(5)
        ]

        metrics = calculate_metrics(outcomes)

        assert metrics.risk_assessment_accuracy == 1.0
        assert metrics.guidance_appropriateness == 1.0
        assert metrics.compliance_rate == 1.0
        assert metrics.satisfaction == 9.0
        assert metrics.comprehension == 8.5
        assert metrics.goal_alignment == 9.5
        assert metrics.overall_quality == 1.0

    def test_calculate_metrics_mixed_outcomes(self):
        """Test metrics with mixed success/failure outcomes."""
        outcomes = [
            OutcomeResult(
                successful=True,
                customer_satisfaction=8.0,
                comprehension=7.0,
                goal_alignment=8.5,
                risks_identified=True,
                guidance_appropriate=True,
                fca_compliant=True,
                understanding_checked=True,
                signposted_when_needed=True,
            ),
            OutcomeResult(
                successful=False,
                customer_satisfaction=4.0,
                comprehension=5.0,
                goal_alignment=3.5,
                risks_identified=False,
                guidance_appropriate=False,
                fca_compliant=False,
                understanding_checked=False,
                signposted_when_needed=False,
            ),
            OutcomeResult(
                successful=True,
                customer_satisfaction=9.0,
                comprehension=8.0,
                goal_alignment=9.0,
                risks_identified=True,
                guidance_appropriate=True,
                fca_compliant=True,
                understanding_checked=True,
                signposted_when_needed=True,
            ),
        ]

        metrics = calculate_metrics(outcomes)

        # 2 out of 3 successful
        assert metrics.risk_assessment_accuracy == pytest.approx(2 / 3)
        assert metrics.guidance_appropriateness == pytest.approx(2 / 3)
        assert metrics.compliance_rate == pytest.approx(2 / 3)
        assert metrics.satisfaction == pytest.approx(7.0)  # (8+4+9)/3
        assert metrics.comprehension == pytest.approx(20 / 3)  # (7+5+8)/3
        assert metrics.goal_alignment == pytest.approx(7.0)  # (8.5+3.5+9)/3
        assert metrics.overall_quality == pytest.approx(2 / 3)

    def test_calculate_metrics_db_warning_rate_no_db_pensions(self):
        """Test DB warning rate when no DB pensions present."""
        outcomes = [
            OutcomeResult(
                has_db_pension=False,
                db_warning_given=False,
            )
            for _ in range(3)
        ]

        metrics = calculate_metrics(outcomes)

        # No DB pensions, so rate should be 0
        assert metrics.db_warning_rate == 0.0

    def test_calculate_metrics_db_warning_rate_all_warned(self):
        """Test DB warning rate when all DB pensions properly warned."""
        outcomes = [
            OutcomeResult(
                has_db_pension=True,
                db_warning_given=True,
            )
            for _ in range(4)
        ]

        metrics = calculate_metrics(outcomes)

        # All warned correctly
        assert metrics.db_warning_rate == 1.0

    def test_calculate_metrics_db_warning_rate_partial(self):
        """Test DB warning rate with partial warnings."""
        outcomes = [
            OutcomeResult(has_db_pension=True, db_warning_given=True),
            OutcomeResult(has_db_pension=True, db_warning_given=False),
            OutcomeResult(has_db_pension=True, db_warning_given=True),
            OutcomeResult(has_db_pension=False, db_warning_given=False),  # Ignored
        ]

        metrics = calculate_metrics(outcomes)

        # 2 out of 3 DB pensions warned
        assert metrics.db_warning_rate == pytest.approx(2 / 3)

    def test_calculate_metrics_db_warning_rate_mixed(self):
        """Test DB warning rate with mix of DB and non-DB pensions."""
        outcomes = [
            OutcomeResult(has_db_pension=True, db_warning_given=True),
            OutcomeResult(has_db_pension=False, db_warning_given=False),
            OutcomeResult(has_db_pension=True, db_warning_given=False),
            OutcomeResult(has_db_pension=False, db_warning_given=False),
            OutcomeResult(has_db_pension=True, db_warning_given=True),
        ]

        metrics = calculate_metrics(outcomes)

        # 2 out of 3 DB pensions warned (only count has_db_pension=True)
        assert metrics.db_warning_rate == pytest.approx(2 / 3)

    def test_calculate_metrics_understanding_verification_rate(self):
        """Test understanding verification rate calculation."""
        outcomes = [
            OutcomeResult(understanding_checked=True),
            OutcomeResult(understanding_checked=False),
            OutcomeResult(understanding_checked=True),
            OutcomeResult(understanding_checked=True),
        ]

        metrics = calculate_metrics(outcomes)

        # 3 out of 4 checked
        assert metrics.understanding_verification_rate == 0.75

    def test_calculate_metrics_signposting_rate(self):
        """Test signposting rate calculation."""
        outcomes = [
            OutcomeResult(signposted_when_needed=True),
            OutcomeResult(signposted_when_needed=True),
            OutcomeResult(signposted_when_needed=False),
            OutcomeResult(signposted_when_needed=True),
            OutcomeResult(signposted_when_needed=False),
        ]

        metrics = calculate_metrics(outcomes)

        # 3 out of 5 signposted
        assert metrics.signposting_rate == 0.6

    def test_calculate_metrics_realistic_scenario(self):
        """Test with realistic consultation outcomes."""
        outcomes = [
            # Excellent consultation
            OutcomeResult(
                successful=True,
                customer_satisfaction=9.5,
                comprehension=9.0,
                goal_alignment=9.2,
                risks_identified=True,
                guidance_appropriate=True,
                fca_compliant=True,
                understanding_checked=True,
                signposted_when_needed=True,
                has_db_pension=True,
                db_warning_given=True,
            ),
            # Good consultation
            OutcomeResult(
                successful=True,
                customer_satisfaction=8.0,
                comprehension=7.5,
                goal_alignment=8.0,
                risks_identified=True,
                guidance_appropriate=True,
                fca_compliant=True,
                understanding_checked=True,
                signposted_when_needed=False,
                has_db_pension=False,
            ),
            # Poor consultation
            OutcomeResult(
                successful=False,
                customer_satisfaction=5.0,
                comprehension=4.5,
                goal_alignment=5.5,
                risks_identified=False,
                guidance_appropriate=False,
                fca_compliant=False,
                understanding_checked=False,
                signposted_when_needed=False,
                has_db_pension=True,
                db_warning_given=False,
            ),
            # Average consultation
            OutcomeResult(
                successful=True,
                customer_satisfaction=7.5,
                comprehension=7.0,
                goal_alignment=7.0,
                risks_identified=True,
                guidance_appropriate=True,
                fca_compliant=True,
                understanding_checked=True,
                signposted_when_needed=True,
                has_db_pension=False,
            ),
        ]

        metrics = calculate_metrics(outcomes)

        # Task accuracy
        assert metrics.risk_assessment_accuracy == 0.75  # 3/4
        assert metrics.guidance_appropriateness == 0.75  # 3/4
        assert metrics.compliance_rate == 0.75  # 3/4

        # Customer outcomes
        assert metrics.satisfaction == 7.5  # (9.5+8+5+7.5)/4
        assert metrics.comprehension == 7.0  # (9+7.5+4.5+7)/4
        assert metrics.goal_alignment == 7.425  # (9.2+8+5.5+7)/4

        # Process quality
        assert metrics.understanding_verification_rate == 0.75  # 3/4
        assert metrics.signposting_rate == 0.5  # 2/4
        assert metrics.db_warning_rate == 0.5  # 1/2 (only 2 DB pensions)

        # Overall
        assert metrics.overall_quality == 0.75  # 3/4
