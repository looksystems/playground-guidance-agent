"""Memory stream implementation for the guidance agent."""

import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4

from litellm import completion

from guidance_agent.core.types import MemoryType
from guidance_agent.core.template_engine import render_template

logger = logging.getLogger(__name__)


@dataclass
class MemoryNode:
    """A single memory in the memory stream."""

    memory_id: UUID = field(default_factory=uuid4)
    description: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    importance: float = 0.5  # 0-1 scale
    memory_type: MemoryType = MemoryType.OBSERVATION
    embedding: Optional[list[float]] = None
    citations: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def access(self) -> None:
        """Update last accessed time when memory is retrieved."""
        self.last_accessed = datetime.now(timezone.utc)

    def recency_score(self, current_time: Optional[datetime] = None) -> float:
        """Calculate recency score using exponential decay.

        Score decreases exponentially with time elapsed since last access.
        Uses decay factor from Simulacra paper.

        Args:
            current_time: Current timestamp, defaults to now

        Returns:
            Recency score between 0 and 1
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        hours_since_access = (current_time - self.last_accessed).total_seconds() / 3600
        decay_factor = 0.99  # From Simulacra paper
        return decay_factor ** hours_since_access

    def to_dict(self) -> dict:
        """Convert memory to dictionary for storage."""
        return {
            "id": str(self.memory_id),
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "importance": self.importance,
            "memory_type": self.memory_type.value,
            "embedding": self.embedding,
            "citations": self.citations,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryNode":
        """Create memory from dictionary."""
        return cls(
            memory_id=UUID(data["id"]),
            description=data["description"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
            importance=data["importance"],
            memory_type=MemoryType(data["memory_type"]),
            embedding=data.get("embedding"),
            citations=data.get("citations", []),
            metadata=data.get("metadata", {}),
        )


class MemoryStream:
    """Memory stream with retrieval based on recency, importance, and relevance.

    Supports optional database persistence using SQLAlchemy.

    Args:
        session: Optional SQLAlchemy session for database persistence
        load_existing: If True and session provided, load existing memories from database
    """

    def __init__(self, session=None, load_existing: bool = False):
        """Initialize memory stream with optional database persistence.

        Args:
            session: SQLAlchemy database session for persistence (optional)
            load_existing: If True, load existing memories from database
        """
        self.memories: list[MemoryNode] = []
        self.session = session

        # Load existing memories from database if requested
        if session and load_existing:
            self._load_from_database()

    def add(self, memory: MemoryNode) -> None:
        """Add a memory to the stream and optionally persist to database.

        Args:
            memory: Memory node to add
        """
        self.memories.append(memory)

        # Persist to database if session is available
        if self.session:
            self._persist_memory(memory)

    def retrieve(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        recency_weight: float = 0.5,
        importance_weight: float = 0.3,
        relevance_weight: float = 0.2,
        current_time: Optional[datetime] = None,
    ) -> list[MemoryNode]:
        """Retrieve memories using weighted combination of recency, importance, and relevance.

        Uses retrieval function from Simulacra paper:
        score = α*recency + β*importance + γ*relevance

        Args:
            query_embedding: Query vector for semantic similarity
            top_k: Number of memories to retrieve
            recency_weight: Weight for recency score (α)
            importance_weight: Weight for importance score (β)
            relevance_weight: Weight for relevance score (γ)
            current_time: Current timestamp for recency calculation

        Returns:
            List of top-k memories sorted by score
        """
        if not self.memories:
            return []

        if current_time is None:
            current_time = datetime.now(timezone.utc)

        # Calculate scores for each memory
        scored_memories = []
        for memory in self.memories:
            # Recency score
            recency = memory.recency_score(current_time)

            # Importance score (already normalized 0-1)
            importance = memory.importance

            # Relevance score (cosine similarity)
            if memory.embedding and query_embedding:
                relevance = self._cosine_similarity(memory.embedding, query_embedding)
            else:
                relevance = 0.0

            # Weighted combination
            score = (
                recency_weight * recency
                + importance_weight * importance
                + relevance_weight * relevance
            )

            scored_memories.append((memory, score))

        # Sort by score and return top-k
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        top_memories = [memory for memory, _ in scored_memories[:top_k]]

        # Update last accessed time
        for memory in top_memories:
            memory.access()
            # Update in database if session available
            if self.session:
                self._update_last_accessed(memory)

        return top_memories

    def retrieve_by_type(
        self, memory_type: MemoryType, limit: int = 10
    ) -> list[MemoryNode]:
        """Retrieve memories filtered by type.

        Args:
            memory_type: Type of memory to retrieve
            limit: Maximum number of memories to return

        Returns:
            List of memories of the specified type
        """
        filtered = [m for m in self.memories if m.memory_type == memory_type]
        return sorted(filtered, key=lambda m: m.timestamp, reverse=True)[:limit]

    def retrieve_recent(
        self, hours: int = 24, limit: int = 100
    ) -> list[MemoryNode]:
        """Retrieve recent memories within time window.

        Args:
            hours: Time window in hours
            limit: Maximum number of memories to return

        Returns:
            List of recent memories
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        recent = [m for m in self.memories if m.timestamp >= cutoff_time]
        return sorted(recent, key=lambda m: m.timestamp, reverse=True)[:limit]

    def get_memory_count(self) -> int:
        """Get total number of memories in stream."""
        return len(self.memories)

    def clear(self) -> None:
        """Clear all memories from stream and database."""
        # Clear from database if session available
        if self.session:
            from guidance_agent.core.database import Memory
            self.session.query(Memory).delete()
            self.session.commit()

        self.memories.clear()

    def get_by_id(self, memory_id: UUID) -> Optional[MemoryNode]:
        """Retrieve a specific memory by ID.

        Args:
            memory_id: UUID of the memory to retrieve

        Returns:
            MemoryNode if found, None otherwise
        """
        for memory in self.memories:
            if memory.memory_id == memory_id:
                return memory
        return None

    def delete(self, memory_id: UUID) -> None:
        """Delete a memory by ID from stream and database.

        Args:
            memory_id: UUID of the memory to delete
        """
        # Remove from in-memory list
        self.memories = [m for m in self.memories if m.memory_id != memory_id]

        # Remove from database if session available
        if self.session:
            from guidance_agent.core.database import Memory
            self.session.query(Memory).filter(Memory.id == memory_id).delete()
            self.session.commit()

    def update(self, memory: MemoryNode) -> None:
        """Update a memory in the stream and database.

        Args:
            memory: Updated memory node
        """
        # Update in-memory (already done by reference)
        # Just persist to database if session available
        if self.session:
            self._update_memory_in_db(memory)

    @staticmethod
    def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score between -1 and 1
        """
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def _load_from_database(self) -> None:
        """Load existing memories from database into stream."""
        from guidance_agent.core.database import Memory, MemoryTypeEnum

        db_memories = self.session.query(Memory).all()

        for db_memory in db_memories:
            # Convert embedding to list if it exists
            embedding = None
            if db_memory.embedding is not None:
                embedding = list(db_memory.embedding)

            memory_node = MemoryNode(
                memory_id=db_memory.id,
                description=db_memory.description,
                timestamp=db_memory.timestamp,
                last_accessed=db_memory.last_accessed,
                importance=db_memory.importance,
                memory_type=MemoryType(db_memory.memory_type.value),
                embedding=embedding,
                metadata=db_memory.meta or {},
            )
            self.memories.append(memory_node)

    def _persist_memory(self, memory: MemoryNode) -> None:
        """Persist a memory to the database.

        Args:
            memory: Memory node to persist
        """
        try:
            from guidance_agent.core.database import Memory, MemoryTypeEnum

            db_memory = Memory(
                id=memory.memory_id,
                description=memory.description,
                timestamp=memory.timestamp,
                last_accessed=memory.last_accessed,
                importance=memory.importance,
                memory_type=MemoryTypeEnum(memory.memory_type.value),
                embedding=memory.embedding,
                meta=memory.metadata,
            )

            self.session.add(db_memory)
            self.session.commit()

            # Log successful persistence with truncated description
            truncated_desc = memory.description[:50] + "..." if len(memory.description) > 50 else memory.description
            logger.info(f"Persisted memory {memory.memory_id}: {truncated_desc}")

        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to persist memory: {e}", exc_info=True)
            raise

    def _update_last_accessed(self, memory: MemoryNode) -> None:
        """Update last_accessed timestamp in database.

        Args:
            memory: Memory node with updated last_accessed
        """
        from guidance_agent.core.database import Memory

        db_memory = self.session.query(Memory).filter(Memory.id == memory.memory_id).first()
        if db_memory:
            db_memory.last_accessed = memory.last_accessed
            self.session.commit()

    def _update_memory_in_db(self, memory: MemoryNode) -> None:
        """Update all fields of a memory in database.

        Args:
            memory: Memory node with updated fields
        """
        from guidance_agent.core.database import Memory, MemoryTypeEnum

        db_memory = self.session.query(Memory).filter(Memory.id == memory.memory_id).first()
        if db_memory:
            db_memory.description = memory.description
            db_memory.timestamp = memory.timestamp
            db_memory.last_accessed = memory.last_accessed
            db_memory.importance = memory.importance
            db_memory.memory_type = MemoryTypeEnum(memory.memory_type.value)
            db_memory.embedding = memory.embedding
            db_memory.meta = memory.metadata
            self.session.commit()


def rate_importance(observation: str) -> float:
    """Rate the importance of an observation using LLM.

    Uses LiteLLM to call an LLM that rates the observation on a 1-10 scale.
    The rating is then normalized to a 0-1 range.

    Args:
        observation: The observation text to rate

    Returns:
        Importance score between 0.0 and 1.0

    Example:
        >>> importance = rate_importance("Customer asked about pension balance")
        >>> print(f"Importance: {importance:.2f}")
        Importance: 0.20
    """
    prompt = render_template(
        "memory/importance_rating.jinja",
        observation=observation,
    )

    try:
        # Use LiteLLM for provider flexibility
        model = os.getenv("LITELLM_MODEL_CUSTOMER", "gpt-3.5-turbo")
        response = completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        # Parse rating from response
        content = response.choices[0].message.content
        rating = parse_rating(content)

        # Normalize to [0, 1] and clamp
        normalized = rating / 10.0
        return max(0.0, min(1.0, normalized))

    except Exception as e:
        # If LLM call fails, return medium importance
        print(f"Warning: Failed to rate importance: {e}")
        return 0.5


def parse_rating(text: str) -> float:
    """Parse a rating from LLM response text.

    Looks for patterns like:
    - "Rating: 7"
    - "I would rate this a 8"
    - "Score: 5"
    - "Rating: 9/10"

    Args:
        text: Response text from LLM

    Returns:
        Rating as a float (1-10), or 5.0 if no rating found
    """
    # Common patterns for ratings
    patterns = [
        r"rating:?\s*(\d+)",
        r"rate\s+this\s+a?\s*(\d+)",
        r"score:?\s*(\d+)",
        r"(\d+)\s*/\s*10",
        r"(\d+)\s+out\s+of\s+10",
    ]

    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            try:
                rating = float(match.group(1))
                # Clamp to valid range
                return max(1.0, min(10.0, rating))
            except ValueError:
                continue

    # If no pattern matched, try to find any standalone number 1-10
    numbers = re.findall(r"\b([1-9]|10)\b", text)
    if numbers:
        return float(numbers[0])

    # Default to medium importance
    return 5.0
