"""Evaluation pipeline for advisor performance.

This module provides the main evaluation function for testing advisor agents
against diverse customer scenarios and computing comprehensive metrics.
"""

from typing import List

from guidance_agent.evaluation.metrics import AdvisorMetrics, calculate_metrics
from guidance_agent.advisor.agent import AdvisorAgent
from guidance_agent.customer.agent import CustomerAgent
from guidance_agent.environment.orchestrator import EventOrchestrator
from guidance_agent.core.types import OutcomeResult


def run_consultation(
    advisor: AdvisorAgent,
    customer: CustomerAgent,
    max_turns: int = 20,
) -> OutcomeResult:
    """Run a single consultation and return the outcome.

    This is a convenience wrapper around EventOrchestrator that returns
    just the outcome (not the full consultation result).

    Args:
        advisor: AdvisorAgent instance
        customer: CustomerAgent instance
        max_turns: Maximum number of conversation turns

    Returns:
        OutcomeResult from the consultation

    Example:
        >>> outcome = run_consultation(advisor, customer)
        >>> print(f"Successful: {outcome.successful}")
        >>> print(f"Satisfaction: {outcome.customer_satisfaction}")
    """
    orchestrator = EventOrchestrator(max_turns=max_turns)
    result = orchestrator.run_consultation(advisor, customer)
    return result.outcome


def evaluate_advisor(
    advisor: AdvisorAgent,
    test_customers: List[CustomerAgent],
    max_turns: int = 20,
) -> AdvisorMetrics:
    """Evaluate advisor performance against diverse customer scenarios.

    Runs consultations with all test customers and computes comprehensive
    quality metrics across task accuracy, customer outcomes, and process quality.

    Args:
        advisor: AdvisorAgent instance to evaluate
        test_customers: List of CustomerAgent instances for testing
        max_turns: Maximum turns per consultation (default 20)

    Returns:
        AdvisorMetrics with comprehensive performance evaluation

    Example:
        >>> # Create test customers
        >>> customers = [generate_customer() for _ in range(100)]
        >>>
        >>> # Evaluate advisor
        >>> metrics = evaluate_advisor(advisor, customers)
        >>>
        >>> # Check performance
        >>> print(f"Success rate: {metrics.overall_quality:.2%}")
        >>> print(f"Compliance: {metrics.compliance_rate:.2%}")
        >>> print(f"Satisfaction: {metrics.satisfaction:.1f}/10")
    """
    outcomes: List[OutcomeResult] = []

    for customer in test_customers:
        # Run consultation
        outcome = run_consultation(advisor, customer, max_turns=max_turns)
        outcomes.append(outcome)

    # Calculate and return metrics
    metrics = calculate_metrics(outcomes)
    return metrics
