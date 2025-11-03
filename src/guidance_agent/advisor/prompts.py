"""Prompt templates for advisor agent guidance generation.

This module provides functions to format various inputs into prompts
for the advisor agent to generate FCA-compliant pension guidance.
"""

from typing import List
from guidance_agent.core.types import (
    Case,
    CustomerProfile,
    AdvisorProfile,
    GuidanceRule,
    RetrievedContext,
)
from guidance_agent.core.memory import MemoryNode
from guidance_agent.core.template_engine import render_template, get_template_engine


def format_customer_profile(customer: CustomerProfile) -> str:
    """Format customer profile for inclusion in prompts.

    Args:
        customer: Customer profile to format

    Returns:
        Formatted customer profile string
    """
    parts = []

    # Demographics
    if customer.demographics:
        demo = customer.demographics
        parts.append(f"Age: {demo.age}")
        parts.append(f"Location: {demo.location}")
        parts.append(f"Employment: {demo.employment_status}")
        parts.append(f"Financial Literacy: {demo.financial_literacy}")

    # Financial situation
    if customer.financial:
        fin = customer.financial
        parts.append(f"\nFinancial Situation:")
        parts.append(f"- Annual Income: £{fin.annual_income:,.0f}")
        parts.append(f"- Total Assets: £{fin.total_assets:,.0f}")
        parts.append(f"- Total Debt: £{fin.total_debt:,.0f}")
        parts.append(f"- Dependents: {fin.dependents}")
        parts.append(f"- Risk Tolerance: {fin.risk_tolerance}")

    # Pensions
    if customer.pensions:
        parts.append(f"\nPension Pots ({len(customer.pensions)}):")
        for i, pension in enumerate(customer.pensions, 1):
            parts.append(f"\nPot {i}:")
            parts.append(f"- Provider: {pension.provider}")
            parts.append(f"- Type: {pension.pot_type.replace('_', ' ')}")
            parts.append(f"- Current Value: £{pension.current_value:,.0f}")
            parts.append(f"- Accessible from age: {pension.age_accessible}")

            # Highlight DB pensions
            if pension.is_db_scheme:
                parts.append(
                    f"- ⚠️ DEFINED BENEFIT SCHEME - Guaranteed income: £{pension.db_guaranteed_amount:,.0f}/year"
                )

    # Goals
    if customer.goals:
        parts.append(f"\nCustomer Goals: {customer.goals}")

    return "\n".join(parts)


def format_conversation(conversation: List[dict]) -> str:
    """Format conversation history for inclusion in prompts.

    Args:
        conversation: List of conversation messages with role and content

    Returns:
        Formatted conversation string
    """
    if not conversation:
        return "(No prior conversation)"

    formatted = []
    for msg in conversation:
        role = msg["role"].capitalize()
        content = msg["content"]
        formatted.append(f"{role}: {content}")

    return "\n".join(formatted)


def format_cases(cases: List[Case]) -> str:
    """Format similar cases for inclusion in prompts.

    Args:
        cases: List of similar cases

    Returns:
        Formatted cases string
    """
    if not cases:
        return "(No similar cases found)"

    formatted = []
    for i, case in enumerate(cases, 1):
        formatted.append(f"\nCase {i} (similarity: {case.similarity_score:.2f}):")
        formatted.append(f"Customer Situation: {case.customer_situation}")
        formatted.append(f"Guidance Provided: {case.guidance_provided}")
        formatted.append(f"Outcome: {case.outcome_summary}")

    return "\n".join(formatted)


def format_rules(rules: List[GuidanceRule]) -> str:
    """Format guidance rules for inclusion in prompts.

    Args:
        rules: List of guidance rules

    Returns:
        Formatted rules string
    """
    if not rules:
        return "(No relevant rules found)"

    formatted = []
    for i, rule in enumerate(rules, 1):
        formatted.append(
            f"\n{i}. {rule.principle} (confidence: {rule.confidence:.2f}, domain: {rule.domain})"
        )

    return "\n".join(formatted)


def format_memories(memories: List[MemoryNode]) -> str:
    """Format memories for inclusion in prompts.

    Args:
        memories: List of memory nodes

    Returns:
        Formatted memories string
    """
    if not memories:
        return "(No relevant memories)"

    formatted = []
    for i, memory in enumerate(memories, 1):
        formatted.append(
            f"\n{i}. [{memory.memory_type.value}] {memory.description} (importance: {memory.importance:.2f})"
        )

    return "\n".join(formatted)


def build_guidance_prompt(
    advisor: AdvisorProfile,
    customer: CustomerProfile,
    context: RetrievedContext,
    conversation_history: List[dict],
) -> str:
    """Build complete prompt for guidance generation.

    Args:
        advisor: Advisor profile
        customer: Customer profile
        context: Retrieved context (cases, rules, memories)
        conversation_history: Prior conversation

    Returns:
        Complete guidance generation prompt
    """
    return render_template(
        "advisor/guidance_main.jinja",
        advisor=advisor,
        customer=customer,
        context=context,
        conversation_history=conversation_history,
    )


def build_guidance_prompt_cached(
    advisor: AdvisorProfile,
    customer: CustomerProfile,
    context: RetrievedContext,
    conversation_history: List[dict],
) -> List[dict]:
    """Build cache-optimized prompt for guidance generation.

    This function structures the prompt to maximize cache hit rates:
    - Static content (system prompt, FCA requirements) goes first and is cached
    - Semi-static content (customer context) is cached within conversations
    - Variable content (current question) is not cached

    Args:
        advisor: Advisor profile
        customer: Customer profile
        context: Retrieved context (cases, rules, memories)
        conversation_history: Prior conversation

    Returns:
        List of message dictionaries with cache control markers
    """
    return get_template_engine().render_messages(
        "advisor/guidance_cached.jinja",
        advisor=advisor,
        customer=customer,
        context=context,
        conversation_history=conversation_history,
    )


def build_reasoning_prompt(
    customer: CustomerProfile,
    context: RetrievedContext,
) -> str:
    """Build prompt for chain-of-thought reasoning.

    Args:
        customer: Customer profile
        context: Retrieved context

    Returns:
        Reasoning prompt
    """
    return render_template(
        "advisor/reasoning.jinja",
        customer=customer,
        context=context,
    )


def build_guidance_prompt_with_reasoning(
    customer: CustomerProfile,
    context: RetrievedContext,
    reasoning: str,
) -> str:
    """Build prompt for guidance generation given reasoning.

    Args:
        customer: Customer profile
        context: Retrieved context
        reasoning: Chain-of-thought reasoning

    Returns:
        Guidance prompt with reasoning
    """
    return render_template(
        "advisor/guidance_with_reasoning.jinja",
        customer=customer,
        context=context,
        reasoning=reasoning,
    )
