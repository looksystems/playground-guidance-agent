"""Tests for ablation studies.

Following TDD approach: Write tests FIRST, then implement.
"""

import pytest
from unittest.mock import patch, Mock
from dataclasses import dataclass

from guidance_agent.evaluation.ablation import (
    run_ablation_study,
    AblationResults,
    compare_ablation_results,
)
from guidance_agent.evaluation.metrics import AdvisorMetrics
from guidance_agent.core.types import AdvisorProfile, CustomerProfile
from guidance_agent.customer.agent import CustomerAgent


class TestAblationResults:
    """Test AblationResults dataclass."""

    def test_ablation_results_creation(self):
        """Test creating AblationResults instance."""
        baseline_metrics = AdvisorMetrics(
            risk_assessment_accuracy=0.5,
            guidance_appropriateness=0.5,
            compliance_rate=0.5,
            satisfaction=5.0,
            comprehension=5.0,
            goal_alignment=5.0,
            understanding_verification_rate=0.5,
            signposting_rate=0.5,
            db_warning_rate=0.5,
            overall_quality=0.5,
        )

        results = AblationResults(
            baseline=baseline_metrics,
            cases_only=baseline_metrics,
            rules_only=baseline_metrics,
            full=baseline_metrics,
        )

        assert results.baseline == baseline_metrics
        assert results.cases_only == baseline_metrics
        assert results.rules_only == baseline_metrics
        assert results.full == baseline_metrics


class TestRunAblationStudy:
    """Test run_ablation_study function."""

    @patch("guidance_agent.evaluation.ablation.evaluate_advisor")
    @patch("guidance_agent.evaluation.ablation.AdvisorAgent")
    def test_run_ablation_study_empty_customers(
        self, mock_advisor_class, mock_evaluate
    ):
        """Test ablation study with no customers."""
        # Setup mock metrics
        zero_metrics = AdvisorMetrics(
            risk_assessment_accuracy=0.0,
            guidance_appropriateness=0.0,
            compliance_rate=0.0,
            satisfaction=0.0,
            comprehension=0.0,
            goal_alignment=0.0,
            understanding_verification_rate=0.0,
            signposting_rate=0.0,
            db_warning_rate=0.0,
            overall_quality=0.0,
        )
        mock_evaluate.return_value = zero_metrics

        # Run ablation study
        results = run_ablation_study([])

        # Should have 4 evaluations (baseline, cases, rules, full)
        assert mock_evaluate.call_count == 4
        assert results.baseline == zero_metrics
        assert results.cases_only == zero_metrics
        assert results.rules_only == zero_metrics
        assert results.full == zero_metrics

    @patch("guidance_agent.evaluation.ablation.evaluate_advisor")
    @patch("guidance_agent.evaluation.ablation.AdvisorAgent")
    def test_run_ablation_study_creates_four_variants(
        self, mock_advisor_class, mock_evaluate
    ):
        """Test that ablation study creates all four advisor variants."""
        # Setup
        customers = [CustomerAgent(profile=CustomerProfile()) for _ in range(3)]

        mock_metrics = AdvisorMetrics(
            risk_assessment_accuracy=0.8,
            guidance_appropriateness=0.8,
            compliance_rate=0.8,
            satisfaction=7.0,
            comprehension=7.0,
            goal_alignment=7.0,
            understanding_verification_rate=0.8,
            signposting_rate=0.8,
            db_warning_rate=0.8,
            overall_quality=0.8,
        )
        mock_evaluate.return_value = mock_metrics

        # Run ablation study
        results = run_ablation_study(customers)

        # Should create 4 advisor instances
        assert mock_advisor_class.call_count == 4

        # Check that advisors were created with correct configurations
        calls = mock_advisor_class.call_args_list

        # Baseline: no cases, no rules
        assert calls[0][1]["use_case_base"] == False
        assert calls[0][1]["use_rules_base"] == False

        # Cases only: yes cases, no rules
        assert calls[1][1]["use_case_base"] == True
        assert calls[1][1]["use_rules_base"] == False

        # Rules only: no cases, yes rules
        assert calls[2][1]["use_case_base"] == False
        assert calls[2][1]["use_rules_base"] == True

        # Full: yes cases, yes rules
        assert calls[3][1]["use_case_base"] == True
        assert calls[3][1]["use_rules_base"] == True

    @patch("guidance_agent.evaluation.ablation.evaluate_advisor")
    @patch("guidance_agent.evaluation.ablation.AdvisorAgent")
    def test_run_ablation_study_evaluates_all_variants(
        self, mock_advisor_class, mock_evaluate
    ):
        """Test that all variants are evaluated with same customers."""
        # Setup
        customers = [CustomerAgent(profile=CustomerProfile()) for _ in range(5)]

        mock_metrics = AdvisorMetrics(
            risk_assessment_accuracy=0.9,
            guidance_appropriateness=0.9,
            compliance_rate=0.9,
            satisfaction=8.0,
            comprehension=8.0,
            goal_alignment=8.0,
            understanding_verification_rate=0.9,
            signposting_rate=0.9,
            db_warning_rate=0.9,
            overall_quality=0.9,
        )
        mock_evaluate.return_value = mock_metrics

        # Run ablation study
        results = run_ablation_study(customers)

        # Should evaluate 4 times
        assert mock_evaluate.call_count == 4

        # Each evaluation should use the same customer list
        for call in mock_evaluate.call_args_list:
            assert call[0][1] == customers  # Second arg is customers

    @patch("guidance_agent.evaluation.ablation.evaluate_advisor")
    @patch("guidance_agent.evaluation.ablation.AdvisorAgent")
    def test_run_ablation_study_with_different_performance(
        self, mock_advisor_class, mock_evaluate
    ):
        """Test ablation study with different performance levels."""
        # Setup
        customers = [CustomerAgent(profile=CustomerProfile()) for _ in range(10)]

        # Different metrics for each variant
        baseline_metrics = AdvisorMetrics(
            risk_assessment_accuracy=0.6,
            guidance_appropriateness=0.6,
            compliance_rate=0.6,
            satisfaction=6.0,
            comprehension=6.0,
            goal_alignment=6.0,
            understanding_verification_rate=0.6,
            signposting_rate=0.6,
            db_warning_rate=0.6,
            overall_quality=0.6,
        )

        cases_metrics = AdvisorMetrics(
            risk_assessment_accuracy=0.75,
            guidance_appropriateness=0.75,
            compliance_rate=0.75,
            satisfaction=7.5,
            comprehension=7.5,
            goal_alignment=7.5,
            understanding_verification_rate=0.75,
            signposting_rate=0.75,
            db_warning_rate=0.75,
            overall_quality=0.75,
        )

        rules_metrics = AdvisorMetrics(
            risk_assessment_accuracy=0.8,
            guidance_appropriateness=0.8,
            compliance_rate=0.8,
            satisfaction=8.0,
            comprehension=8.0,
            goal_alignment=8.0,
            understanding_verification_rate=0.8,
            signposting_rate=0.8,
            db_warning_rate=0.8,
            overall_quality=0.8,
        )

        full_metrics = AdvisorMetrics(
            risk_assessment_accuracy=0.9,
            guidance_appropriateness=0.9,
            compliance_rate=0.9,
            satisfaction=9.0,
            comprehension=9.0,
            goal_alignment=9.0,
            understanding_verification_rate=0.9,
            signposting_rate=0.9,
            db_warning_rate=0.9,
            overall_quality=0.9,
        )

        mock_evaluate.side_effect = [
            baseline_metrics,
            cases_metrics,
            rules_metrics,
            full_metrics,
        ]

        # Run ablation study
        results = run_ablation_study(customers)

        # Verify each variant got correct metrics
        assert results.baseline.overall_quality == 0.6
        assert results.cases_only.overall_quality == 0.75
        assert results.rules_only.overall_quality == 0.8
        assert results.full.overall_quality == 0.9

        # Full system should be best
        assert results.full.overall_quality > results.baseline.overall_quality

    @patch("guidance_agent.evaluation.ablation.evaluate_advisor")
    @patch("guidance_agent.evaluation.ablation.AdvisorAgent")
    def test_run_ablation_study_with_profile(
        self, mock_advisor_class, mock_evaluate
    ):
        """Test ablation study with custom advisor profile."""
        # Setup
        profile = AdvisorProfile(
            name="Test Advisor",
            description="For testing",
            experience_level="senior",
        )
        customers = [CustomerAgent(profile=CustomerProfile()) for _ in range(3)]

        mock_metrics = AdvisorMetrics(
            risk_assessment_accuracy=0.8,
            guidance_appropriateness=0.8,
            compliance_rate=0.8,
            satisfaction=8.0,
            comprehension=8.0,
            goal_alignment=8.0,
            understanding_verification_rate=0.8,
            signposting_rate=0.8,
            db_warning_rate=0.8,
            overall_quality=0.8,
        )
        mock_evaluate.return_value = mock_metrics

        # Run with custom profile
        results = run_ablation_study(customers, advisor_profile=profile)

        # All 4 advisors should use the custom profile
        for call in mock_advisor_class.call_args_list:
            assert call[1]["profile"] == profile


class TestCompareAblationResults:
    """Test compare_ablation_results function."""

    def test_compare_ablation_results_basic(self):
        """Test basic comparison of ablation results."""
        baseline = AdvisorMetrics(
            risk_assessment_accuracy=0.5,
            guidance_appropriateness=0.5,
            compliance_rate=0.5,
            satisfaction=5.0,
            comprehension=5.0,
            goal_alignment=5.0,
            understanding_verification_rate=0.5,
            signposting_rate=0.5,
            db_warning_rate=0.5,
            overall_quality=0.5,
        )

        full = AdvisorMetrics(
            risk_assessment_accuracy=0.9,
            guidance_appropriateness=0.9,
            compliance_rate=0.9,
            satisfaction=9.0,
            comprehension=9.0,
            goal_alignment=9.0,
            understanding_verification_rate=0.9,
            signposting_rate=0.9,
            db_warning_rate=0.9,
            overall_quality=0.9,
        )

        results = AblationResults(
            baseline=baseline,
            cases_only=baseline,
            rules_only=baseline,
            full=full,
        )

        comparison = compare_ablation_results(results)

        # Should show improvement in all metrics
        assert "overall_quality" in comparison
        assert comparison["overall_quality"]["baseline"] == 0.5
        assert comparison["overall_quality"]["full"] == 0.9
        assert comparison["overall_quality"]["improvement"] == pytest.approx(0.4)

    def test_compare_ablation_results_all_metrics(self):
        """Test comparison includes all key metrics."""
        baseline = AdvisorMetrics(
            risk_assessment_accuracy=0.6,
            guidance_appropriateness=0.6,
            compliance_rate=0.6,
            satisfaction=6.0,
            comprehension=6.0,
            goal_alignment=6.0,
            understanding_verification_rate=0.6,
            signposting_rate=0.6,
            db_warning_rate=0.6,
            overall_quality=0.6,
        )

        full = AdvisorMetrics(
            risk_assessment_accuracy=0.8,
            guidance_appropriateness=0.8,
            compliance_rate=0.8,
            satisfaction=8.0,
            comprehension=8.0,
            goal_alignment=8.0,
            understanding_verification_rate=0.8,
            signposting_rate=0.8,
            db_warning_rate=0.8,
            overall_quality=0.8,
        )

        results = AblationResults(
            baseline=baseline,
            cases_only=baseline,
            rules_only=baseline,
            full=full,
        )

        comparison = compare_ablation_results(results)

        # Should include all key metrics
        expected_metrics = [
            "overall_quality",
            "compliance_rate",
            "satisfaction",
            "risk_assessment_accuracy",
        ]

        for metric in expected_metrics:
            assert metric in comparison
