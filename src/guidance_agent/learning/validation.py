"""Rule validation and confidence adjustment based on outcomes.

This module implements mechanisms for:
- Updating rule confidence based on consultation outcomes
- Tracking rule performance over time
- Adjusting confidence scores dynamically based on success/failure
"""

from typing import Optional
from sqlalchemy.orm import Session

from guidance_agent.core.types import OutcomeResult
from guidance_agent.core.database import Rule


def update_rule_confidence(
    rule: Rule,
    new_confidence: float,
    session: Session,
) -> float:
    """Update a rule's confidence score.

    Args:
        rule: The rule to update
        new_confidence: New confidence value
        session: Database session

    Returns:
        The updated confidence value (bounded to [0, 1])

    Example:
        >>> new_conf = update_rule_confidence(rule, 0.85, session)
        >>> assert 0.0 <= new_conf <= 1.0
    """
    # Ensure confidence is bounded
    bounded_confidence = max(0.0, min(1.0, new_confidence))

    # Update rule
    rule.confidence = bounded_confidence
    session.commit()

    return bounded_confidence


def adjust_confidence_on_success(
    rule: Rule,
    outcome: OutcomeResult,
    session: Session,
    learning_rate: float = 0.05,
) -> float:
    """Adjust rule confidence upward based on successful outcome.

    The adjustment magnitude depends on:
    1. The quality of the outcome (customer satisfaction, comprehension, goal alignment)
    2. The learning rate parameter

    Args:
        rule: The rule that was applied
        outcome: Successful outcome result
        session: Database session
        learning_rate: How quickly to adjust confidence (default: 0.05)

    Returns:
        New confidence value

    Example:
        >>> new_conf = adjust_confidence_on_success(rule, success_outcome, session)
        >>> assert new_conf > rule.confidence
    """
    # Calculate outcome quality score (0-1)
    quality_score = (
        outcome.customer_satisfaction / 10.0 +
        outcome.comprehension / 10.0 +
        outcome.goal_alignment / 10.0
    ) / 3.0

    # Adjust confidence based on quality
    # Higher quality outcomes lead to larger confidence increases
    confidence_delta = learning_rate * quality_score

    new_confidence = rule.confidence + confidence_delta

    return update_rule_confidence(rule, new_confidence, session)


def adjust_confidence_on_failure(
    rule: Rule,
    outcome: OutcomeResult,
    session: Session,
    learning_rate: float = 0.05,
) -> float:
    """Adjust rule confidence downward based on failed outcome.

    The adjustment magnitude depends on the learning rate parameter.

    Args:
        rule: The rule that was applied
        outcome: Failed outcome result
        session: Database session
        learning_rate: How quickly to adjust confidence (default: 0.05)

    Returns:
        New confidence value

    Example:
        >>> new_conf = adjust_confidence_on_failure(rule, failed_outcome, session)
        >>> assert new_conf < rule.confidence
    """
    # Decrease confidence on failure
    confidence_delta = learning_rate

    new_confidence = rule.confidence - confidence_delta

    return update_rule_confidence(rule, new_confidence, session)


def track_rule_performance(
    rule_ids: list[str],
    outcome: OutcomeResult,
    session: Session,
) -> None:
    """Track performance statistics for rules used in a consultation.

    Updates the metadata for each rule to track:
    - Total uses
    - Successful uses
    - Failed uses

    Args:
        rule_ids: List of rule IDs that were applied
        outcome: Consultation outcome
        session: Database session

    Example:
        >>> track_rule_performance(
        ...     rule_ids=['rule-1', 'rule-2'],
        ...     outcome=outcome,
        ...     session=session,
        ... )
    """
    from sqlalchemy import update
    from uuid import UUID

    for rule_id in rule_ids:
        # Find rule
        if isinstance(rule_id, str):
            rule_id = UUID(rule_id)

        rule = session.query(Rule).filter(Rule.id == rule_id).first()
        if not rule:
            continue

        # Get current metadata or initialize
        current_meta = rule.meta if rule.meta else {}

        # Initialize performance tracking if needed
        if "performance" not in current_meta:
            current_meta["performance"] = {
                "uses": 0,
                "successes": 0,
                "failures": 0,
            }

        # Update statistics
        performance = current_meta["performance"]
        performance["uses"] += 1

        if outcome.successful:
            performance["successes"] += 1
        else:
            performance["failures"] += 1

        # Update using direct SQL to ensure JSONB update is detected
        stmt = (
            update(Rule)
            .where(Rule.id == rule_id)
            .values(meta=current_meta)
        )
        session.execute(stmt)
        session.commit()

        # Refresh the rule object
        session.expire(rule)


def get_rule_performance_metrics(rule: Rule) -> dict:
    """Get performance metrics for a rule.

    Args:
        rule: The rule to get metrics for

    Returns:
        Dictionary with:
            - uses: Total number of times rule was used
            - successes: Number of successful outcomes
            - failures: Number of failed outcomes
            - success_rate: Ratio of successes to total uses

    Example:
        >>> metrics = get_rule_performance_metrics(rule)
        >>> print(f"Success rate: {metrics['success_rate']:.1%}")
    """
    if not rule.meta or "performance" not in rule.meta:
        return {
            "uses": 0,
            "successes": 0,
            "failures": 0,
            "success_rate": 0.0,
        }

    performance = rule.meta["performance"]
    uses = performance.get("uses", 0)
    successes = performance.get("successes", 0)
    failures = performance.get("failures", 0)

    success_rate = successes / uses if uses > 0 else 0.0

    return {
        "uses": uses,
        "successes": successes,
        "failures": failures,
        "success_rate": success_rate,
    }
