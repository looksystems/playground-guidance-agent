"""Outcome simulation for pension guidance consultations.

This module simulates consultation outcomes based on the conversation between
advisor and customer, providing feedback for the learning system.
"""

import os
import json
from typing import List, Dict
from litellm import completion

from guidance_agent.customer.agent import CustomerAgent
from guidance_agent.core.types import OutcomeResult, OutcomeStatus
from guidance_agent.core.template_engine import render_template


def simulate_outcome(
    customer: CustomerAgent, conversation_history: List[dict]
) -> OutcomeResult:
    """Simulate the outcome of a pension guidance consultation.

    Uses LLM to evaluate the quality of guidance provided and customer
    satisfaction based on the conversation.

    Args:
        customer: CustomerAgent with profile and conversation memory
        conversation_history: List of conversation messages

    Returns:
        OutcomeResult with metrics and success determination
    """
    model = os.getenv("LITELLM_MODEL_CUSTOMER", "gpt-4o-mini")

    # Check if customer has DB pension
    has_db_pension = any(
        pension.is_db_scheme for pension in customer.profile.pensions
    ) if customer.profile.pensions else False

    prompt = render_template(
        "customer/outcome.jinja",
        customer=customer,
        conversation_history=conversation_history,
        has_db_pension=has_db_pension
    )

    try:
        response = completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,  # Lower temperature for more consistent evaluation
        )

        data = json.loads(response.choices[0].message.content)

        # Determine success based on criteria
        successful = (
            data.get("customer_satisfaction", 0) >= 7.0
            and data.get("comprehension", 0) >= 7.0
            and data.get("goal_alignment", 0) >= 7.0
            and data.get("fca_compliant", False) is True  # Compliance must be perfect
        )

        # Determine status
        if successful:
            status = OutcomeStatus.SUCCESS
        elif (
            data.get("customer_satisfaction", 0) >= 5.0
            and data.get("comprehension", 0) >= 5.0
        ):
            status = OutcomeStatus.PARTIAL_SUCCESS
        else:
            status = OutcomeStatus.FAILURE

        # Build outcome result
        outcome = OutcomeResult(
            status=status,
            successful=successful,
            customer_satisfaction=float(data.get("customer_satisfaction", 5.0)),
            comprehension=float(data.get("comprehension", 5.0)),
            goal_alignment=float(data.get("goal_alignment", 5.0)),
            risks_identified=bool(data.get("risks_identified", False)),
            guidance_appropriate=bool(data.get("guidance_appropriate", True)),
            fca_compliant=bool(data.get("fca_compliant", True)),
            understanding_checked=bool(data.get("understanding_checked", False)),
            signposted_when_needed=bool(data.get("signposted_when_needed", False)),
            has_db_pension=has_db_pension,
            db_warning_given=bool(data.get("db_warning_given", False)),
            reasoning=data.get("reasoning", ""),
        )

        return outcome

    except Exception as e:
        # Fallback to simple evaluation based on comprehension level
        # Higher comprehension = better outcome
        satisfaction = min(10.0, customer.comprehension_level * 10)
        comprehension_score = min(10.0, customer.comprehension_level * 10)

        successful = satisfaction >= 7.0 and comprehension_score >= 7.0

        return OutcomeResult(
            status=OutcomeStatus.SUCCESS if successful else OutcomeStatus.PARTIAL_SUCCESS,
            successful=successful,
            customer_satisfaction=satisfaction,
            comprehension=comprehension_score,
            goal_alignment=satisfaction,  # Approximate
            risks_identified=True,
            guidance_appropriate=True,
            fca_compliant=True,
            understanding_checked=len(conversation_history) > 2,
            signposted_when_needed=False,
            has_db_pension=has_db_pension,
            db_warning_given=False,
            reasoning="Outcome evaluation based on comprehension level (LLM error fallback)",
        )
