"""Learning from successful consultations (case-based learning).

This module implements case extraction and storage for successful consultations.
When a consultation succeeds, we extract a case that can be used as a template
for similar future situations.
"""

from typing import Any
from uuid import uuid4

from guidance_agent.core.types import OutcomeResult, CustomerProfile, TaskType
from guidance_agent.retrieval.retriever import CaseBase
from guidance_agent.retrieval.embeddings import embed


def classify_task_type(question: str) -> TaskType:
    """Classify the task type based on customer's question.

    Uses simple keyword matching to classify the question into one of the
    predefined task types. In production, this could be replaced with an
    LLM-based classifier.

    Args:
        question: Customer's presenting question

    Returns:
        TaskType enum value

    Example:
        >>> task_type = classify_task_type("What are my pension withdrawal options?")
        >>> assert task_type == TaskType.WITHDRAWAL_OPTIONS
    """
    question_lower = question.lower()

    # Keyword-based classification (order matters - check specific before general)

    # Check for DB transfer specifically first
    if "defined benefit" in question_lower or "db pension" in question_lower:
        if "transfer" in question_lower:
            return TaskType.DEFINED_BENEFIT_TRANSFER

    # Check for tax first (very specific)
    if any(keyword in question_lower for keyword in ["tax", "taxation"]):
        return TaskType.TAX_IMPLICATIONS

    # Check for retirement planning
    if any(keyword in question_lower for keyword in ["how much", "need for retirement", "retirement planning"]):
        return TaskType.RETIREMENT_PLANNING

    # Check for transfer (not DB)
    if any(
        keyword in question_lower
        for keyword in ["transfer", "move pension", "consolidate"]
    ):
        return TaskType.PENSION_TRANSFER

    # Check for withdrawal/access
    if any(
        keyword in question_lower
        for keyword in ["withdrawal", "access", "take out", "take money", "options"]
    ):
        return TaskType.WITHDRAWAL_OPTIONS

    # Check for annuity
    if any(keyword in question_lower for keyword in ["annuity", "guaranteed income"]):
        return TaskType.ANNUITY_OPTIONS

    # Check for drawdown
    if any(keyword in question_lower for keyword in ["drawdown", "flexible"]):
        return TaskType.DRAWDOWN_STRATEGY

    # Default to general inquiry
    return TaskType.GENERAL_INQUIRY


def summarize_customer_situation(customer_profile: CustomerProfile) -> str:
    """Summarize customer's situation in a concise format.

    Creates a text summary of the customer's key characteristics that will
    be embedded and used for similarity matching.

    Args:
        customer_profile: Customer profile to summarize

    Returns:
        String summary of customer situation

    Example:
        >>> summary = summarize_customer_situation(profile)
        >>> print(summary)
        '55 year old employed male from London with medium financial literacy...'
    """
    parts = []

    # Demographics
    if customer_profile.demographics:
        demo = customer_profile.demographics
        parts.append(
            f"{demo.age} year old {demo.employment_status} {demo.gender} "
            f"from {demo.location} with {demo.financial_literacy} financial literacy"
        )

    # Financial situation
    if customer_profile.financial:
        fin = customer_profile.financial
        parts.append(
            f"Annual income £{fin.annual_income:,.0f}, "
            f"total assets £{fin.total_assets:,.0f}, "
            f"{fin.dependents} dependents, "
            f"{fin.risk_tolerance} risk tolerance"
        )

    # Pension details
    if customer_profile.pensions:
        total_pension_value = sum(p.current_value for p in customer_profile.pensions)
        pension_count = len(customer_profile.pensions)
        parts.append(
            f"{pension_count} pension pot(s) worth £{total_pension_value:,.0f} total"
        )

        # Check for DB pensions
        db_pensions = [p for p in customer_profile.pensions if p.is_db_scheme]
        if db_pensions:
            parts.append(f"Includes {len(db_pensions)} defined benefit pension(s)")

    # Goals
    if customer_profile.goals:
        parts.append(f"Goals: {customer_profile.goals}")

    return ". ".join(parts)


def extract_case_from_consultation(
    customer_profile: CustomerProfile,
    guidance_provided: str,
    outcome: OutcomeResult,
    conversational_quality: float = None,
    conversation_history: list = None,
) -> dict[str, Any]:
    """Extract a case from a successful consultation.

    Creates a case record that includes the customer situation, guidance provided,
    and outcome. The case is embedded for semantic similarity search.

    For high-quality consultations (quality > 0.7), also captures successful
    dialogue techniques used.

    Args:
        customer_profile: Customer profile from the consultation
        guidance_provided: Guidance that was provided to customer
        outcome: Result of the consultation
        conversational_quality: Optional quality score (0-1)
        conversation_history: Optional full conversation for technique analysis

    Returns:
        Dictionary containing case data ready for storage

    Example:
        >>> case_data = extract_case_from_consultation(profile, guidance, outcome)
        >>> assert "embedding" in case_data
        >>> assert "task_type" in case_data
    """
    # Classify the task type
    task_type = classify_task_type(customer_profile.presenting_question)

    # Summarize customer situation
    customer_situation = summarize_customer_situation(customer_profile)

    # Create embedding for similarity search
    # Embed the customer situation for matching similar cases
    embedding = embed(customer_situation)

    # Create case data
    case_data = {
        "id": uuid4(),
        "task_type": task_type.value,
        "customer_situation": customer_situation,
        "guidance_provided": guidance_provided,
        "outcome": outcome.to_dict(),
        "embedding": embedding,
    }

    # Capture dialogue techniques for high-quality consultations (Phase 2)
    if conversational_quality is not None and conversational_quality > 0.7 and conversation_history:
        dialogue_techniques = _extract_dialogue_techniques(conversation_history, conversational_quality)
        case_data["dialogue_techniques"] = dialogue_techniques

    return case_data


def _extract_dialogue_techniques(conversation_history: list, quality_score: float) -> dict[str, Any]:
    """Extract successful dialogue techniques from a high-quality consultation.

    Args:
        conversation_history: List of conversation turns
        quality_score: Overall conversational quality score

    Returns:
        Dictionary of successful techniques used

    Example:
        >>> techniques = _extract_dialogue_techniques(history, 0.85)
        >>> assert "signposting_examples" in techniques
    """
    # Extract advisor messages only
    advisor_messages = [
        msg["content"]
        for msg in conversation_history
        if msg.get("role") == "advisor"
    ]

    if not advisor_messages:
        return {}

    # Signposting phrases used
    signpost_phrases = [
        "let me break this down", "let me explain", "let me help",
        "here's what this means", "here's what", "building on",
        "before we", "first,", "let's explore", "let's look",
        "here's how", "one option", "one approach",
        "some people find", "it's worth", "it depends"
    ]

    signposting_examples = []
    for msg in advisor_messages:
        for phrase in signpost_phrases:
            if phrase in msg.lower():
                # Extract sentence containing the phrase
                sentences = msg.split(". ")
                for sentence in sentences:
                    if phrase in sentence.lower():
                        signposting_examples.append(sentence.strip())
                        break

    # Engagement questions (examples)
    engagement_questions = []
    for msg in advisor_messages:
        sentences = msg.split(". ")
        for sentence in sentences:
            if "?" in sentence:
                engagement_questions.append(sentence.strip())

    # Personalization examples (name usage)
    personalization_examples = []
    for msg in advisor_messages:
        # Look for patterns like "Hi [Name]" or addressing customer by name
        if any(greeting in msg for greeting in ["Hi ", "Hello ", "Thank you "]):
            sentences = msg.split(". ")
            for sentence in sentences:
                if any(greeting in sentence for greeting in ["Hi ", "Hello ", "Thank you "]):
                    personalization_examples.append(sentence.strip())
                    break

    techniques = {
        "quality_score": quality_score,
        "signposting_examples": signposting_examples[:3],  # Top 3 examples
        "engagement_questions": engagement_questions[:3],  # Top 3 examples
        "personalization_examples": personalization_examples[:2],  # Top 2 examples
        "total_advisor_messages": len(advisor_messages),
        "avg_message_length": sum(len(msg) for msg in advisor_messages) // len(advisor_messages) if advisor_messages else 0,
    }

    return techniques


def learn_from_successful_consultation(
    case_base: CaseBase,
    customer_profile: CustomerProfile,
    guidance_provided: str,
    outcome: OutcomeResult,
    conversational_quality: float = None,
    conversation_history: list = None,
) -> None:
    """Learn from a successful consultation by extracting and storing a case.

    This function is called after a consultation completes successfully.
    It extracts a case from the consultation and adds it to the case base
    for future retrieval.

    Only successful consultations are added to the case base. Failed or
    partially successful consultations may still be used for learning,
    but through the reflection mechanism instead.

    Args:
        case_base: Case base to add the case to
        customer_profile: Customer profile from the consultation
        guidance_provided: Guidance that was provided to customer
        outcome: Result of the consultation
        conversational_quality: Optional quality score (0-1)
        conversation_history: Optional full conversation for technique analysis

    Example:
        >>> learn_from_successful_consultation(
        ...     case_base=case_base,
        ...     customer_profile=profile,
        ...     guidance_provided=guidance,
        ...     outcome=outcome,
        ... )
    """
    # Only learn from successful consultations
    if not outcome.successful:
        return

    # Extract case from consultation
    case_data = extract_case_from_consultation(
        customer_profile=customer_profile,
        guidance_provided=guidance_provided,
        outcome=outcome,
        conversational_quality=conversational_quality,
        conversation_history=conversation_history,
    )

    # Add to case base
    metadata = {
        "task_type": case_data["task_type"],
        "customer_situation": case_data["customer_situation"],
        "guidance_provided": case_data["guidance_provided"],
        "outcome": case_data["outcome"],
    }

    # Include dialogue techniques if available
    if "dialogue_techniques" in case_data:
        metadata["dialogue_techniques"] = case_data["dialogue_techniques"]

    case_base.add(
        id=case_data["id"],
        embedding=case_data["embedding"],
        metadata=metadata,
    )
