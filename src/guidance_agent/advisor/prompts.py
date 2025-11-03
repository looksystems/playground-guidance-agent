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
    prompt = f"""You are {advisor.name}, a pension guidance specialist.

{advisor.description}

Your role is to provide FCA-compliant pension GUIDANCE (not advice). This means:
- Present options without recommending specific choices
- Use language like "you could consider" rather than "you should"
- Explain pros and cons of different options
- Ensure customer understanding throughout
- Signpost to FCA-regulated advisors for complex decisions

CUSTOMER PROFILE:
{format_customer_profile(customer)}

CONVERSATION HISTORY:
{format_conversation(conversation_history)}

RETRIEVED CONTEXT:

Similar Past Cases:
{format_cases(context.cases)}

Learned Guidance Rules:
{format_rules(context.rules)}

Relevant Memories:
{format_memories(context.memories)}

FCA REQUIREMENTS:
{context.fca_requirements if context.fca_requirements else "Stay within guidance boundary, avoid regulated advice"}

CUSTOMER'S CURRENT QUESTION:
"{customer.presenting_question}"

TASK:
Provide appropriate pension guidance that:
1. Addresses the customer's specific question
2. Uses language appropriate for their literacy level ({customer.demographics.financial_literacy if customer.demographics else 'medium'})
3. Presents balanced information (pros and cons)
4. Stays clearly within the FCA guidance boundary
5. Checks customer understanding

Your guidance:"""

    return prompt


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
    # Part 1: System prompt (static, always cached)
    system_prompt = {
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": f"""You are {advisor.name}, a pension guidance specialist.

{advisor.description}

Your role is to provide FCA-compliant pension GUIDANCE (not advice). This means:
- Present options without recommending specific choices
- Use language like "you could consider" rather than "you should"
- Explain pros and cons of different options
- Ensure customer understanding throughout
- Signpost to FCA-regulated advisors for complex decisions""",
                "cache_control": {"type": "ephemeral"},
            }
        ],
    }

    # Part 2: FCA requirements and learned rules (static, always cached)
    fca_context = {
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": f"""FCA Requirements and Guidelines:

{context.fca_requirements if context.fca_requirements else "Stay within guidance boundary, avoid regulated advice"}

Learned Guidance Rules:
{format_rules(context.rules)}""",
                "cache_control": {"type": "ephemeral"},
            }
        ],
    }

    # Part 3: Customer context and similar cases (semi-static, cached within conversation)
    customer_context = {
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": f"""Customer Profile:
{format_customer_profile(customer)}

Similar Past Cases:
{format_cases(context.cases)}

Relevant Memories:
{format_memories(context.memories)}""",
                "cache_control": {"type": "ephemeral"},
            }
        ],
    }

    # Part 4: Conversation and current question (variable, not cached)
    user_message = {
        "role": "user",
        "content": f"""Previous conversation:
{format_conversation(conversation_history)}

Customer's current question: "{customer.presenting_question}"

Please provide appropriate pension guidance that:
1. Addresses the customer's specific question
2. Uses language appropriate for their literacy level ({customer.demographics.financial_literacy if customer.demographics else 'medium'})
3. Presents balanced information (pros and cons)
4. Stays clearly within the FCA guidance boundary
5. Checks customer understanding

Your guidance:""",
    }

    return [system_prompt, fca_context, customer_context, user_message]


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
    prompt = f"""Before providing guidance, think through the situation step-by-step.

CUSTOMER PROFILE:
{format_customer_profile(customer)}

CUSTOMER'S QUESTION:
"{customer.presenting_question}"

RETRIEVED CONTEXT:
Similar Cases:
{format_cases(context.cases)}

Learned Rules:
{format_rules(context.rules)}

FCA REQUIREMENTS:
{context.fca_requirements if context.fca_requirements else "Stay within guidance boundary"}

TASK:
Think through this step-by-step:
1. What is the customer really asking?
2. What are the key considerations for this situation?
3. What similar cases or rules are relevant?
4. What risks or important points must be covered?
5. How should I adapt my language for their literacy level?
6. What checks should I include to ensure understanding?

Your reasoning:"""

    return prompt


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
    prompt = f"""You have analyzed a customer's pension question. Now provide guidance based on your reasoning.

CUSTOMER PROFILE:
{format_customer_profile(customer)}

CUSTOMER'S QUESTION:
"{customer.presenting_question}"

YOUR REASONING:
{reasoning}

FCA REQUIREMENTS:
{context.fca_requirements if context.fca_requirements else "Stay within guidance boundary, avoid regulated advice"}

TASK:
Based on your reasoning above, provide pension guidance that:
1. Addresses the customer's question
2. Uses appropriate language for their literacy level
3. Presents balanced information
4. Stays within FCA guidance boundary
5. Checks customer understanding

Your guidance:"""

    return prompt
