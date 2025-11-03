"""Multi-faceted retrieval system combining memories, cases, and rules."""

from typing import Optional, Any
from uuid import UUID

from sqlalchemy.orm import Session

from guidance_agent.core.memory import MemoryStream
from guidance_agent.core.types import RetrievedContext
from guidance_agent.retrieval.vector_store import PgVectorStore
from guidance_agent.core.database import Case, Rule


class CaseBase:
    """Case base for storing and retrieving successful consultation cases.

    Uses vector similarity search to find relevant past cases that can
    inform current guidance.

    Args:
        session: SQLAlchemy database session
    """

    def __init__(self, session: Session):
        """Initialize case base with database session."""
        self.session = session
        self.vector_store = PgVectorStore(session, Case)

    def add(
        self,
        id: UUID,
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> None:
        """Add a case to the case base.

        Args:
            id: Unique identifier for the case
            embedding: Vector embedding of the case
            metadata: Case metadata including:
                - task_type: Type of task
                - customer_situation: Description of customer's situation
                - guidance_provided: Guidance that was given
                - outcome: Result of the consultation
        """
        self.vector_store.add(id, embedding, metadata)

    def retrieve(
        self,
        query_embedding: list[float],
        top_k: int = 3,
        task_type: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Retrieve similar cases by semantic similarity.

        Args:
            query_embedding: Query vector for similarity search
            top_k: Number of cases to retrieve
            task_type: Optional filter by task type

        Returns:
            List of case dictionaries with metadata and similarity scores
        """
        filter_dict = {"task_type": task_type} if task_type else None
        results = self.vector_store.search(
            query_embedding, top_k=top_k, filter_dict=filter_dict
        )

        # Convert to more usable format
        cases = []
        for result in results:
            case = {
                "id": result["id"],
                "task_type": result["metadata"]["task_type"],
                "customer_situation": result["metadata"]["customer_situation"],
                "guidance_provided": result["metadata"]["guidance_provided"],
                "outcome": result["metadata"]["outcome"],
                "similarity": result["similarity"],
            }
            cases.append(case)

        return cases


class RulesBase:
    """Rules base for storing and retrieving learned guidance rules.

    Uses vector similarity search combined with confidence weighting to find
    relevant rules that should be applied.

    Args:
        session: SQLAlchemy database session
    """

    def __init__(self, session: Session):
        """Initialize rules base with database session."""
        self.session = session
        self.vector_store = PgVectorStore(session, Rule)

    def add(
        self,
        id: UUID,
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> None:
        """Add a rule to the rules base.

        Args:
            id: Unique identifier for the rule
            embedding: Vector embedding of the rule
            metadata: Rule metadata including:
                - principle: The rule principle/guideline
                - domain: Domain the rule applies to
                - confidence: Confidence score (0-1)
                - supporting_evidence: List of supporting case IDs
        """
        self.vector_store.add(id, embedding, metadata)

    def retrieve(
        self,
        query_embedding: list[float],
        top_k: int = 4,
        domain: Optional[str] = None,
        min_confidence: float = 0.0,
    ) -> list[dict[str, Any]]:
        """Retrieve similar rules by semantic similarity weighted by confidence.

        Args:
            query_embedding: Query vector for similarity search
            top_k: Number of rules to retrieve
            domain: Optional filter by domain
            min_confidence: Minimum confidence threshold

        Returns:
            List of rule dictionaries with metadata and weighted scores
        """
        # Get more rules than needed for confidence filtering/weighting
        filter_dict = {"domain": domain} if domain else None
        results = self.vector_store.search(
            query_embedding, top_k=top_k * 2, filter_dict=filter_dict
        )

        # Apply confidence weighting and filtering
        weighted_rules = []
        for result in results:
            confidence = result["metadata"]["confidence"]

            # Filter by minimum confidence
            if confidence < min_confidence:
                continue

            # Weight similarity by confidence
            weighted_score = result["similarity"] * confidence

            rule = {
                "id": result["id"],
                "principle": result["metadata"]["principle"],
                "domain": result["metadata"]["domain"],
                "confidence": confidence,
                "supporting_evidence": result["metadata"]["supporting_evidence"],
                "similarity": result["similarity"],
                "weighted_score": weighted_score,
            }
            weighted_rules.append(rule)

        # Sort by weighted score and return top_k
        weighted_rules.sort(key=lambda x: x["weighted_score"], reverse=True)
        return weighted_rules[:top_k]


def retrieve_context(
    query: str,
    query_embedding: list[float],
    memory_stream: MemoryStream,
    case_base: CaseBase,
    rules_base: RulesBase,
    memory_top_k: int = 10,
    case_top_k: int = 3,
    rule_top_k: int = 4,
    fca_requirements: Optional[str] = None,
) -> RetrievedContext:
    """Multi-faceted retrieval combining memories, cases, and rules.

    Retrieves relevant context from three sources:
    1. Memory stream: Recent observations and reflections (recency + importance + relevance)
    2. Case base: Similar past cases (semantic similarity)
    3. Rules base: Applicable guidance rules (semantic similarity + confidence)

    Args:
        query: Natural language query describing the situation
        query_embedding: Vector embedding of the query
        memory_stream: Memory stream to retrieve from
        case_base: Case base to retrieve from
        rules_base: Rules base to retrieve from
        memory_top_k: Number of memories to retrieve
        case_top_k: Number of cases to retrieve
        rule_top_k: Number of rules to retrieve
        fca_requirements: Optional FCA requirements string

    Returns:
        RetrievedContext containing memories, cases, rules, and reasoning

    Example:
        >>> context = retrieve_context(
        ...     query="Customer wants pension withdrawal advice",
        ...     query_embedding=embed("Customer wants pension withdrawal advice"),
        ...     memory_stream=stream,
        ...     case_base=cases,
        ...     rules_base=rules,
        ... )
        >>> print(f"Found {len(context.memories)} memories, {len(context.cases)} cases")
    """
    # Retrieve from memory stream (recency + importance + relevance)
    memories = memory_stream.retrieve(query_embedding, top_k=memory_top_k)

    # Retrieve from case base (semantic similarity)
    cases = case_base.retrieve(query_embedding, top_k=case_top_k)

    # Retrieve from rules base (semantic similarity + confidence weighting)
    rules = rules_base.retrieve(query_embedding, top_k=rule_top_k)

    # Generate reasoning about what was retrieved
    reasoning = _generate_retrieval_reasoning(query, memories, cases, rules)

    return RetrievedContext(
        memories=memories,
        cases=cases,
        rules=rules,
        fca_requirements=fca_requirements,
        reasoning=reasoning,
    )


def _generate_retrieval_reasoning(
    query: str,
    memories: list,
    cases: list,
    rules: list,
) -> str:
    """Generate reasoning about what was retrieved and why.

    Args:
        query: Original query
        memories: Retrieved memories
        cases: Retrieved cases
        rules: Retrieved rules

    Returns:
        Reasoning string explaining the retrieval
    """
    parts = [f"Retrieved context for query: '{query}'"]

    if memories:
        parts.append(
            f"- Found {len(memories)} relevant memories including "
            f"{sum(1 for m in memories if m.memory_type.value == 'observation')} observations and "
            f"{sum(1 for m in memories if m.memory_type.value == 'reflection')} reflections"
        )

    if cases:
        task_types = set(c["task_type"] for c in cases)
        parts.append(
            f"- Found {len(cases)} similar past cases covering: {', '.join(task_types)}"
        )

    if rules:
        avg_confidence = sum(r["confidence"] for r in rules) / len(rules)
        parts.append(
            f"- Found {len(rules)} applicable rules with average confidence {avg_confidence:.2f}"
        )

    if not memories and not cases and not rules:
        parts.append("- No relevant context found in any source")

    return "\n".join(parts)
