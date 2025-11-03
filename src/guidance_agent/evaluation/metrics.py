"""Metrics calculation for advisor evaluation.

This module provides comprehensive metrics for evaluating advisor performance
across multiple quality dimensions: task accuracy, customer outcomes, and
process quality.
"""

from dataclasses import dataclass
from typing import List

from guidance_agent.core.types import OutcomeResult


@dataclass
class AdvisorMetrics:
    """Comprehensive metrics for advisor performance evaluation.

    Attributes:
        Task Accuracy:
            risk_assessment_accuracy: Proportion of correctly identified risks
            guidance_appropriateness: Proportion of appropriate guidance given
            compliance_rate: Proportion of FCA-compliant consultations

        Customer Outcomes:
            satisfaction: Average customer satisfaction score (0-10)
            comprehension: Average customer comprehension score (0-10)
            goal_alignment: Average goal alignment score (0-10)

        Process Quality:
            understanding_verification_rate: Proportion of consultations with understanding checks
            signposting_rate: Proportion of consultations with proper signposting
            db_warning_rate: Proportion of DB pension cases with proper warnings

        Overall:
            overall_quality: Overall success rate
    """

    # Task Accuracy
    risk_assessment_accuracy: float
    guidance_appropriateness: float
    compliance_rate: float

    # Customer Outcomes
    satisfaction: float
    comprehension: float
    goal_alignment: float

    # Process Quality
    understanding_verification_rate: float
    signposting_rate: float
    db_warning_rate: float

    # Overall
    overall_quality: float


def calculate_metrics(outcomes: List[OutcomeResult]) -> AdvisorMetrics:
    """Calculate comprehensive metrics from consultation outcomes.

    Args:
        outcomes: List of consultation outcome results

    Returns:
        AdvisorMetrics with calculated performance metrics

    Example:
        >>> outcomes = [OutcomeResult(...), OutcomeResult(...)]
        >>> metrics = calculate_metrics(outcomes)
        >>> print(f"Success rate: {metrics.overall_quality:.2%}")
    """
    if not outcomes:
        return AdvisorMetrics(
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

    total = len(outcomes)

    # Task Accuracy - proportion of boolean flags that are True
    risk_assessment_accuracy = sum(
        1 for o in outcomes if o.risks_identified
    ) / total

    guidance_appropriateness = sum(
        1 for o in outcomes if o.guidance_appropriate
    ) / total

    compliance_rate = sum(
        1 for o in outcomes if o.fca_compliant
    ) / total

    # Customer Outcomes - average of numeric scores
    satisfaction = sum(o.customer_satisfaction for o in outcomes) / total
    comprehension = sum(o.comprehension for o in outcomes) / total
    goal_alignment = sum(o.goal_alignment for o in outcomes) / total

    # Process Quality
    understanding_verification_rate = sum(
        1 for o in outcomes if o.understanding_checked
    ) / total

    signposting_rate = sum(
        1 for o in outcomes if o.signposted_when_needed
    ) / total

    # DB warning rate - only count cases with DB pensions
    db_pensions = [o for o in outcomes if o.has_db_pension]
    if db_pensions:
        db_warning_rate = sum(1 for o in db_pensions if o.db_warning_given) / len(
            db_pensions
        )
    else:
        db_warning_rate = 0.0

    # Overall quality
    overall_quality = sum(1 for o in outcomes if o.successful) / total

    return AdvisorMetrics(
        risk_assessment_accuracy=risk_assessment_accuracy,
        guidance_appropriateness=guidance_appropriateness,
        compliance_rate=compliance_rate,
        satisfaction=satisfaction,
        comprehension=comprehension,
        goal_alignment=goal_alignment,
        understanding_verification_rate=understanding_verification_rate,
        signposting_rate=signposting_rate,
        db_warning_rate=db_warning_rate,
        overall_quality=overall_quality,
    )
