"""Reflection and learning from failures.

This module implements the reflection mechanism for learning from failed consultations.
When a consultation fails, the agent reflects on what went wrong, generates a principle,
validates it, refines it, and potentially adds it as a rule to the rules base.
"""

import re
import os
from typing import Any
from uuid import uuid4

from litellm import completion

from guidance_agent.core.types import OutcomeResult, CustomerProfile
from guidance_agent.retrieval.retriever import RulesBase
from guidance_agent.retrieval.embeddings import embed
from guidance_agent.core.template_engine import render_template


def reflect_on_failure(
    customer_profile: CustomerProfile,
    guidance_provided: str,
    outcome: OutcomeResult,
) -> dict[str, str]:
    """Reflect on a failed consultation to extract a learning principle.

    Uses an LLM to analyse the failure and extract a principle that could
    prevent similar failures in the future.

    Args:
        customer_profile: Customer profile from the failed consultation
        guidance_provided: Guidance that was provided
        outcome: Failed outcome with reasoning and issues

    Returns:
        Dictionary with:
            - principle: The extracted principle
            - domain: The domain this principle applies to

    Example:
        >>> reflection = reflect_on_failure(profile, guidance, failed_outcome)
        >>> print(reflection["principle"])
        'Always check customer understanding when explaining complex concepts'
    """
    # Build reflection prompt
    prompt = render_template(
        "learning/reflection.jinja",
        customer_profile=customer_profile,
        guidance_provided=guidance_provided,
        outcome=outcome,
    )

    # Call LLM
    model = os.getenv("LITELLM_MODEL_ADVISOR", "gpt-4-turbo-preview")
    response = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    content = response.choices[0].message.content

    # Parse response
    principle_match = re.search(r"Principle:\s*(.+?)(?=\n\n|Domain:|$)", content, re.DOTALL)
    domain_match = re.search(r"Domain:\s*(.+?)(?=\n|$)", content)

    principle = principle_match.group(1).strip() if principle_match else "Unknown principle"
    domain = domain_match.group(1).strip() if domain_match else "general"

    return {"principle": principle, "domain": domain}


def validate_principle(principle: str) -> dict[str, Any]:
    """Validate a principle against FCA guidelines and best practices.

    Uses an LLM to check if the principle is valid, doesn't cross the
    guidance/advice boundary, and aligns with FCA requirements.

    Args:
        principle: The principle to validate

    Returns:
        Dictionary with:
            - valid: Boolean indicating if principle is valid
            - confidence: Confidence score (0-1)
            - reason: Explanation of the decision

    Example:
        >>> validation = validate_principle("Always give investment advice")
        >>> assert validation["valid"] is False  # Crosses advice boundary
    """
    prompt = render_template(
        "learning/principle_validation.jinja",
        principle=principle,
    )

    model = os.getenv("LITELLM_MODEL_ADVISOR", "gpt-4-turbo-preview")
    response = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,  # Deterministic for validation
    )

    content = response.choices[0].message.content

    # Parse response
    valid_match = re.search(r"Valid:\s*(True|False)", content, re.IGNORECASE)
    confidence_match = re.search(r"Confidence:\s*(0\.\d+|1\.0|\d+)", content)
    reason_match = re.search(r"Reason:\s*(.+?)(?=\n\n|$)", content, re.DOTALL)

    valid = valid_match.group(1).lower() == "true" if valid_match else False
    confidence = float(confidence_match.group(1)) if confidence_match else 0.5
    reason = reason_match.group(1).strip() if reason_match else "No reason provided"

    return {"valid": valid, "confidence": confidence, "reason": reason}


def refine_principle(principle: str, domain: str) -> str:
    """Refine a principle to make it more specific and actionable.

    Uses an LLM to expand and refine the principle with concrete details.

    Args:
        principle: The principle to refine
        domain: The domain this principle applies to

    Returns:
        Refined principle string

    Example:
        >>> refined = refine_principle("Explain risks", "risk_disclosure")
        >>> print(refined)
        'When explaining pension risks, cover market risk, longevity risk...'
    """
    prompt = render_template(
        "learning/principle_refinement.jinja",
        principle=principle,
        domain=domain,
    )

    model = os.getenv("LITELLM_MODEL_ADVISOR", "gpt-4-turbo-preview")
    response = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    refined = response.choices[0].message.content.strip()

    # Remove any "Refined principle:" prefix
    refined = re.sub(r"^Refined [Pp]rinciple:\s*", "", refined)

    return refined


def judge_rule_value(rule_principle: str, domain: str) -> bool:
    """Judge whether a rule is valuable enough to add to the rules base.

    Uses an LLM to assess if the rule provides significant value beyond
    common sense or obvious guidance.

    Args:
        rule_principle: The rule principle to judge
        domain: The domain this rule applies to

    Returns:
        True if rule is valuable, False otherwise

    Example:
        >>> is_valuable = judge_rule_value("Always be polite", "general")
        >>> assert is_valuable is False  # Too generic
    """
    prompt = render_template(
        "learning/rule_judgment.jinja",
        rule_principle=rule_principle,
        domain=domain,
    )

    model = os.getenv("LITELLM_MODEL_ADVISOR", "gpt-4-turbo-preview")
    response = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )

    content = response.choices[0].message.content

    # Parse response
    valuable_match = re.search(r"Valuable:\s*(True|False)", content, re.IGNORECASE)
    score_match = re.search(r"Score:\s*(0\.\d+|1\.0|\d+)", content)

    is_valuable = valuable_match.group(1).lower() == "true" if valuable_match else False
    score = float(score_match.group(1)) if score_match else 0.0

    # Require both "valuable" flag and score above threshold
    return is_valuable and score >= 0.6


def learn_from_failure(
    rules_base: RulesBase,
    customer_profile: CustomerProfile,
    guidance_provided: str,
    outcome: OutcomeResult,
) -> None:
    """Learn from a failed consultation through reflection and rule generation.

    This is the main learning function for failures. It orchestrates the full
    learning pipeline:
    1. Reflect on failure to extract principle
    2. Validate principle against FCA guidelines
    3. Refine principle to make it actionable
    4. Judge if principle is valuable enough to store
    5. Add to rules base if it passes all checks

    Only failures trigger learning through this mechanism.

    Args:
        rules_base: Rules base to add the rule to
        customer_profile: Customer profile from the consultation
        guidance_provided: Guidance that was provided
        outcome: Result of the consultation (must be a failure)

    Example:
        >>> learn_from_failure(
        ...     rules_base=rules_base,
        ...     customer_profile=profile,
        ...     guidance_provided=guidance,
        ...     outcome=failed_outcome,
        ... )
    """
    # Only learn from failures
    if outcome.successful:
        return

    # Step 1: Reflect on failure to extract principle
    reflection = reflect_on_failure(
        customer_profile=customer_profile,
        guidance_provided=guidance_provided,
        outcome=outcome,
    )

    principle = reflection["principle"]
    domain = reflection["domain"]

    # Step 2: Validate principle
    validation = validate_principle(principle)

    if not validation["valid"]:
        # Principle rejected - doesn't align with FCA guidelines
        return

    # Step 3: Refine principle
    refined_principle = refine_principle(principle, domain)

    # Step 4: Judge if rule is valuable
    if not judge_rule_value(refined_principle, domain):
        # Rule not valuable enough to store
        return

    # Step 5: Add to rules base
    # Create embedding for similarity search
    embedding = embed(refined_principle)

    # Add rule with confidence from validation
    rules_base.add(
        id=uuid4(),
        embedding=embedding,
        metadata={
            "principle": refined_principle,
            "domain": domain,
            "confidence": validation["confidence"],
            "supporting_evidence": [],  # Start with empty evidence
        },
    )
