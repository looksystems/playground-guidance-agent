"""Experiment tracking with Phoenix observability.

This module provides experiment tracking for training runs, with automatic
tracing via Phoenix/OpenTelemetry and database storage for results.
"""

import os
from typing import List, Optional
from datetime import datetime
from uuid import uuid4
from opentelemetry import trace

from guidance_agent.evaluation.evaluator import run_consultation
from guidance_agent.evaluation.metrics import calculate_metrics, AdvisorMetrics
from guidance_agent.advisor.agent import AdvisorAgent
from guidance_agent.customer.agent import CustomerAgent
from guidance_agent.customer.generator import generate_customer_profile
from guidance_agent.core.types import OutcomeResult
from guidance_agent.core.database import get_session, Consultation


def store_experiment_outcomes(
    experiment_name: str, outcomes: List[OutcomeResult]
) -> None:
    """Store experiment outcomes in database for future analysis.

    Args:
        experiment_name: Name of the experiment
        outcomes: List of consultation outcomes to store

    Example:
        >>> outcomes = [OutcomeResult(...), ...]
        >>> store_experiment_outcomes("baseline_v1", outcomes)
    """
    session = get_session()
    try:
        for outcome in outcomes:
            # Create consultation record
            consultation = Consultation(
                id=uuid4(),
                customer_id=uuid4(),  # Placeholder
                advisor_id=uuid4(),  # Placeholder
                conversation=[],  # Not storing full conversation here
                outcome=outcome.to_dict(),
                start_time=outcome.timestamp,
                end_time=outcome.timestamp,
                duration_seconds=0,
                meta={"experiment": experiment_name},
            )
            session.add(consultation)

        session.commit()
    finally:
        session.close()


def load_experiment_outcomes(experiment_name: str) -> List[OutcomeResult]:
    """Load previously stored experiment outcomes from database.

    Args:
        experiment_name: Name of the experiment to load

    Returns:
        List of OutcomeResult instances from the experiment

    Example:
        >>> outcomes = load_experiment_outcomes("baseline_v1")
        >>> metrics = calculate_metrics(outcomes)
    """
    session = get_session()
    try:
        # Query consultations for this experiment
        consultations = (
            session.query(Consultation)
            .filter(Consultation.meta["experiment"].astext == experiment_name)
            .all()
        )

        # Convert to OutcomeResult instances
        outcomes = []
        for consultation in consultations:
            # Note: This is a simplified conversion
            # In production, you'd properly reconstruct OutcomeResult from dict
            outcome_dict = consultation.outcome
            # For now, just return empty list if no outcomes
            # Real implementation would deserialize properly
            pass

        return outcomes
    finally:
        session.close()


def run_training_experiment(
    experiment_name: str,
    advisor: AdvisorAgent,
    test_customers: List[CustomerAgent],
    num_customers: int = 100,
    progress_interval: int = 100,
    max_turns: int = 20,
) -> AdvisorMetrics:
    """Run training experiment with Phoenix tracing and metrics tracking.

    Automatically traces all LLM calls via Phoenix/OpenTelemetry and logs
    progress at regular intervals. Stores final outcomes in database.

    Args:
        experiment_name: Name for the experiment (used in traces and storage)
        advisor: AdvisorAgent instance to evaluate
        test_customers: Pre-generated customers to use (if provided)
        num_customers: Number of customers to generate if test_customers empty
        progress_interval: Log progress every N consultations (default 100)
        max_turns: Maximum turns per consultation (default 20)

    Returns:
        AdvisorMetrics with final performance metrics

    Example:
        >>> advisor = AdvisorAgent(profile=my_profile)
        >>> metrics = run_training_experiment(
        ...     "baseline_v1",
        ...     advisor,
        ...     [],
        ...     num_customers=1000,
        ... )
        >>> print(f"Success rate: {metrics.overall_quality:.2%}")
        >>> # View traces at http://localhost:6006
    """
    # Get tracer for OpenTelemetry
    tracer = trace.get_tracer(__name__)

    # Create experiment span (automatically captured in Phoenix)
    with tracer.start_as_current_span(
        experiment_name,
        attributes={
            "experiment.name": experiment_name,
            "experiment.num_customers": num_customers,
            "experiment.model": os.getenv("LITELLM_MODEL_ADVISOR", "unknown"),
            "experiment.start_time": datetime.now().isoformat(),
        },
    ) as span:
        outcomes: List[OutcomeResult] = []

        # Use provided customers or generate new ones
        if test_customers:
            customers = test_customers[:num_customers]
        else:
            # Generate customers on the fly
            customers = []
            for i in range(num_customers):
                profile = generate_customer_profile()
                customer = CustomerAgent(profile=profile)
                customers.append(customer)

        # Run consultations
        for i, customer in enumerate(customers):
            # Run consultation (automatically traced by LiteLLM instrumentation!)
            outcome = run_consultation(advisor, customer, max_turns=max_turns)
            outcomes.append(outcome)

            # Add evaluations as span attributes for each consultation
            span.set_attribute(
                f"consultation.{i}.satisfaction", outcome.customer_satisfaction
            )
            span.set_attribute(
                f"consultation.{i}.compliance", float(outcome.fca_compliant)
            )

            # Log progress at intervals
            if i > 0 and i % progress_interval == 0:
                current_metrics = calculate_metrics(outcomes)
                span.add_event(
                    "progress_checkpoint",
                    attributes={
                        "progress": i,
                        "avg_satisfaction": current_metrics.satisfaction,
                        "compliance_rate": current_metrics.compliance_rate,
                        "overall_quality": current_metrics.overall_quality,
                    },
                )

        # Calculate final metrics
        final_metrics = calculate_metrics(outcomes)

        # Add final results to span
        span.set_attribute("experiment.completed", True)
        span.set_attribute("results.satisfaction", final_metrics.satisfaction)
        span.set_attribute("results.comprehension", final_metrics.comprehension)
        span.set_attribute("results.compliance_rate", final_metrics.compliance_rate)
        span.set_attribute("results.overall_quality", final_metrics.overall_quality)
        span.set_attribute(
            "results.risk_assessment_accuracy", final_metrics.risk_assessment_accuracy
        )

        # Store outcomes in database for future evaluation
        store_experiment_outcomes(experiment_name, outcomes)

        return final_metrics
