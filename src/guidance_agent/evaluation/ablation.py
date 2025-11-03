"""Ablation studies for advisor evaluation.

This module provides functionality to compare advisor performance with
different configurations: baseline (no learning), cases only, rules only,
and full system (both cases and rules).
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from guidance_agent.evaluation.evaluator import evaluate_advisor
from guidance_agent.evaluation.metrics import AdvisorMetrics
from guidance_agent.advisor.agent import AdvisorAgent
from guidance_agent.customer.agent import CustomerAgent
from guidance_agent.core.types import AdvisorProfile


@dataclass
class AblationResults:
    """Results from ablation study comparing different advisor configurations.

    Attributes:
        baseline: Metrics from advisor with no case base or rules base
        cases_only: Metrics from advisor with only case base
        rules_only: Metrics from advisor with only rules base
        full: Metrics from advisor with both case base and rules base
    """

    baseline: AdvisorMetrics
    cases_only: AdvisorMetrics
    rules_only: AdvisorMetrics
    full: AdvisorMetrics


def run_ablation_study(
    test_customers: List[CustomerAgent],
    advisor_profile: Optional[AdvisorProfile] = None,
    max_turns: int = 20,
) -> AblationResults:
    """Run ablation study comparing different advisor configurations.

    Tests four configurations:
    1. Baseline: No case base, no rules base (pure LLM)
    2. Cases only: Case base enabled, rules base disabled
    3. Rules only: Rules base enabled, case base disabled
    4. Full system: Both case base and rules base enabled

    Each configuration is evaluated on the same set of test customers
    to enable fair comparison.

    Args:
        test_customers: List of CustomerAgent instances for testing
        advisor_profile: Optional custom advisor profile (uses default if None)
        max_turns: Maximum turns per consultation (default 20)

    Returns:
        AblationResults with metrics for all four configurations

    Example:
        >>> # Generate test customers
        >>> customers = [generate_customer() for _ in range(100)]
        >>>
        >>> # Run ablation study
        >>> results = run_ablation_study(customers)
        >>>
        >>> # Compare performance
        >>> print(f"Baseline: {results.baseline.overall_quality:.2%}")
        >>> print(f"Cases only: {results.cases_only.overall_quality:.2%}")
        >>> print(f"Rules only: {results.rules_only.overall_quality:.2%}")
        >>> print(f"Full system: {results.full.overall_quality:.2%}")
        >>>
        >>> # Show improvement
        >>> improvement = results.full.overall_quality - results.baseline.overall_quality
        >>> print(f"Improvement: {improvement:.2%}")
    """
    # Use default profile if not provided
    if advisor_profile is None:
        advisor_profile = AdvisorProfile(
            name="Ablation Test Advisor",
            description="Advisor for ablation study",
        )

    # 1. Baseline: No case base, no rules base
    advisor_baseline = AdvisorAgent(
        profile=advisor_profile,
        use_case_base=False,
        use_rules_base=False,
    )

    # 2. Cases only: Case base enabled
    advisor_cases = AdvisorAgent(
        profile=advisor_profile,
        use_case_base=True,
        use_rules_base=False,
    )

    # 3. Rules only: Rules base enabled
    advisor_rules = AdvisorAgent(
        profile=advisor_profile,
        use_case_base=False,
        use_rules_base=True,
    )

    # 4. Full system: Both enabled
    advisor_full = AdvisorAgent(
        profile=advisor_profile,
        use_case_base=True,
        use_rules_base=True,
    )

    # Evaluate all configurations
    baseline_metrics = evaluate_advisor(advisor_baseline, test_customers, max_turns)
    cases_metrics = evaluate_advisor(advisor_cases, test_customers, max_turns)
    rules_metrics = evaluate_advisor(advisor_rules, test_customers, max_turns)
    full_metrics = evaluate_advisor(advisor_full, test_customers, max_turns)

    return AblationResults(
        baseline=baseline_metrics,
        cases_only=cases_metrics,
        rules_only=rules_metrics,
        full=full_metrics,
    )


def compare_ablation_results(results: AblationResults) -> Dict[str, Dict[str, float]]:
    """Compare ablation results across key metrics.

    Args:
        results: AblationResults from ablation study

    Returns:
        Dictionary mapping metric names to comparison data with keys:
        - baseline: Baseline metric value
        - cases_only: Cases-only metric value
        - rules_only: Rules-only metric value
        - full: Full system metric value
        - improvement: Difference between full and baseline

    Example:
        >>> comparison = compare_ablation_results(results)
        >>> print(comparison["overall_quality"])
        {
            "baseline": 0.65,
            "cases_only": 0.75,
            "rules_only": 0.78,
            "full": 0.88,
            "improvement": 0.23
        }
    """
    # Key metrics to compare
    metrics_to_compare = [
        "overall_quality",
        "compliance_rate",
        "satisfaction",
        "comprehension",
        "risk_assessment_accuracy",
        "guidance_appropriateness",
        "understanding_verification_rate",
        "signposting_rate",
    ]

    comparison: Dict[str, Dict[str, float]] = {}

    for metric_name in metrics_to_compare:
        baseline_value = getattr(results.baseline, metric_name)
        cases_value = getattr(results.cases_only, metric_name)
        rules_value = getattr(results.rules_only, metric_name)
        full_value = getattr(results.full, metric_name)

        comparison[metric_name] = {
            "baseline": baseline_value,
            "cases_only": cases_value,
            "rules_only": rules_value,
            "full": full_value,
            "improvement": full_value - baseline_value,
        }

    return comparison
