"""Vector store implementation using PostgreSQL with pgvector extension."""

from typing import Any, Optional, Type, Union
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import func, cast, String
from sqlalchemy.dialects.postgresql import JSONB

from guidance_agent.core.database import Memory, Case, Rule, MemoryTypeEnum


class PgVectorStore:
    """Vector store using PostgreSQL with pgvector extension and SQLAlchemy.

    This class provides a generic interface for storing and retrieving vectors
    with metadata using pgvector's similarity search capabilities.

    Args:
        session: SQLAlchemy database session
        model: SQLAlchemy model class (Memory, Case, or Rule)

    Example:
        >>> session = get_session()
        >>> store = PgVectorStore(session, Memory)
        >>> store.add(uuid4(), embedding=[0.1]*1536, metadata={...})
        >>> results = store.search(query_embedding, top_k=10)
    """

    def __init__(self, session: Session, model: Type[Union[Memory, Case, Rule]]):
        """Initialize vector store with database session and model."""
        self.session = session
        self.model = model

    def add(
        self,
        id: UUID,
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> None:
        """Add or update a vector with metadata.

        If a record with the given ID already exists, it will be updated.
        Otherwise, a new record is created.

        Args:
            id: Unique identifier for the vector
            embedding: Vector embedding (must match model's dimension)
            metadata: Dictionary containing model-specific fields

        Example:
            >>> store.add(
            ...     id=uuid4(),
            ...     embedding=[0.1] * 1536,
            ...     metadata={
            ...         "description": "Customer asked about pension",
            ...         "importance": 0.8,
            ...         "memory_type": "observation",
            ...         "timestamp": "2024-01-01T12:00:00",
            ...         "last_accessed": "2024-01-01T12:00:00",
            ...     }
            ... )
        """
        # Check if record exists
        existing = self.session.query(self.model).filter(self.model.id == id).first()

        if existing:
            # Update existing record
            self._update_record(existing, embedding, metadata)
        else:
            # Create new record
            record = self._create_record(id, embedding, metadata)
            self.session.add(record)

        self.session.commit()

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        filter_dict: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors using cosine similarity.

        Args:
            query_embedding: Query vector for similarity search
            top_k: Maximum number of results to return
            filter_dict: Optional metadata filters (e.g., {"memory_type": "observation"})

        Returns:
            List of dictionaries containing:
                - id: Record UUID
                - metadata: Record metadata as dictionary
                - similarity: Cosine similarity score (0-1, higher is more similar)

        Example:
            >>> results = store.search(
            ...     query_embedding=[0.1] * 1536,
            ...     top_k=5,
            ...     filter_dict={"memory_type": "observation"}
            ... )
            >>> for result in results:
            ...     print(f"{result['similarity']:.3f}: {result['metadata']['description']}")
        """
        # Start with base query
        query = self.session.query(
            self.model.id,
            self.model,
            # Calculate cosine similarity: 1 - (vector <=> query)
            (1 - self.model.embedding.cosine_distance(query_embedding)).label(
                "similarity"
            ),
        )

        # Apply metadata filters if provided
        if filter_dict:
            query = self._apply_filters(query, filter_dict)

        # Order by similarity (closest first) and limit results
        query = query.order_by(
            self.model.embedding.cosine_distance(query_embedding)
        ).limit(top_k)

        # Execute query and format results
        results = []
        for record_id, record, similarity in query.all():
            results.append(
                {
                    "id": str(record_id),
                    "metadata": self._record_to_metadata(record),
                    "similarity": float(similarity),
                }
            )

        return results

    def delete(self, id: UUID) -> None:
        """Delete a vector by ID.

        Args:
            id: UUID of the record to delete

        Example:
            >>> store.delete(memory_id)
        """
        self.session.query(self.model).filter(self.model.id == id).delete()
        self.session.commit()

    def _create_record(
        self, id: UUID, embedding: list[float], metadata: dict[str, Any]
    ) -> Union[Memory, Case, Rule]:
        """Create a new database record from embedding and metadata.

        Args:
            id: Record UUID
            embedding: Vector embedding
            metadata: Model-specific metadata

        Returns:
            New SQLAlchemy model instance
        """
        if self.model == Memory:
            return Memory(
                id=id,
                embedding=embedding,
                description=metadata.get("description", ""),
                timestamp=self._parse_datetime(metadata.get("timestamp")),
                last_accessed=self._parse_datetime(metadata.get("last_accessed")),
                importance=metadata.get("importance", 0.5),
                memory_type=MemoryTypeEnum(metadata.get("memory_type", "observation")),
                meta=metadata.get("meta", {}),
            )
        elif self.model == Case:
            return Case(
                id=id,
                embedding=embedding,
                task_type=metadata.get("task_type", ""),
                customer_situation=metadata.get("customer_situation", ""),
                guidance_provided=metadata.get("guidance_provided", ""),
                outcome=metadata.get("outcome", {}),
                meta=metadata.get("meta", {}),
            )
        elif self.model == Rule:
            return Rule(
                id=id,
                embedding=embedding,
                principle=metadata.get("principle", ""),
                domain=metadata.get("domain", ""),
                confidence=metadata.get("confidence", 0.5),
                supporting_evidence=metadata.get("supporting_evidence", []),
                meta=metadata.get("meta", {}),
            )
        else:
            raise ValueError(f"Unsupported model type: {self.model}")

    def _update_record(
        self,
        record: Union[Memory, Case, Rule],
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> None:
        """Update an existing database record.

        Args:
            record: Existing SQLAlchemy model instance
            embedding: New vector embedding
            metadata: New metadata
        """
        record.embedding = embedding

        if isinstance(record, Memory):
            record.description = metadata.get("description", record.description)
            record.timestamp = self._parse_datetime(
                metadata.get("timestamp"), record.timestamp
            )
            record.last_accessed = self._parse_datetime(
                metadata.get("last_accessed"), record.last_accessed
            )
            record.importance = metadata.get("importance", record.importance)
            record.memory_type = MemoryTypeEnum(
                metadata.get("memory_type", record.memory_type.value)
            )
            record.meta = metadata.get("meta", record.meta)

        elif isinstance(record, Case):
            record.task_type = metadata.get("task_type", record.task_type)
            record.customer_situation = metadata.get(
                "customer_situation", record.customer_situation
            )
            record.guidance_provided = metadata.get(
                "guidance_provided", record.guidance_provided
            )
            record.outcome = metadata.get("outcome", record.outcome)
            record.meta = metadata.get("meta", record.meta)

        elif isinstance(record, Rule):
            record.principle = metadata.get("principle", record.principle)
            record.domain = metadata.get("domain", record.domain)
            record.confidence = metadata.get("confidence", record.confidence)
            record.supporting_evidence = metadata.get(
                "supporting_evidence", record.supporting_evidence
            )
            record.meta = metadata.get("meta", record.meta)

    def _record_to_metadata(self, record: Union[Memory, Case, Rule]) -> dict[str, Any]:
        """Convert a database record to metadata dictionary.

        Args:
            record: SQLAlchemy model instance

        Returns:
            Dictionary with record fields
        """
        if isinstance(record, Memory):
            return {
                "description": record.description,
                "timestamp": record.timestamp.isoformat() if record.timestamp else None,
                "last_accessed": (
                    record.last_accessed.isoformat() if record.last_accessed else None
                ),
                "importance": record.importance,
                "memory_type": record.memory_type.value,
                "meta": record.meta or {},
            }
        elif isinstance(record, Case):
            return {
                "task_type": record.task_type,
                "customer_situation": record.customer_situation,
                "guidance_provided": record.guidance_provided,
                "outcome": record.outcome,
                "meta": record.meta or {},
            }
        elif isinstance(record, Rule):
            return {
                "principle": record.principle,
                "domain": record.domain,
                "confidence": record.confidence,
                "supporting_evidence": record.supporting_evidence,
                "meta": record.meta or {},
            }
        else:
            return {}

    def _apply_filters(self, query, filter_dict: dict[str, Any]):
        """Apply metadata filters to query.

        Args:
            query: SQLAlchemy query object
            filter_dict: Dictionary of filters to apply

        Returns:
            Modified query with filters applied
        """
        for key, value in filter_dict.items():
            if isinstance(self.model, type) and issubclass(self.model, Memory):
                # Direct column filters for Memory model
                if key == "memory_type" and hasattr(self.model, "memory_type"):
                    query = query.filter(
                        self.model.memory_type == MemoryTypeEnum(value)
                    )
                elif key == "importance" and hasattr(self.model, "importance"):
                    query = query.filter(self.model.importance == value)
                # Add more direct column filters as needed

            # For Case and Rule models, use similar direct filtering
            elif isinstance(self.model, type) and issubclass(self.model, Case):
                if key == "task_type" and hasattr(self.model, "task_type"):
                    query = query.filter(self.model.task_type == value)

            elif isinstance(self.model, type) and issubclass(self.model, Rule):
                if key == "domain" and hasattr(self.model, "domain"):
                    query = query.filter(self.model.domain == value)

        return query

    @staticmethod
    def _parse_datetime(
        value: Optional[Union[str, datetime]], default: Optional[datetime] = None
    ) -> datetime:
        """Parse datetime from string or return existing datetime.

        Args:
            value: Datetime string or datetime object
            default: Default value if parsing fails

        Returns:
            Datetime object
        """
        if isinstance(value, datetime):
            return value
        elif isinstance(value, str):
            # Handle ISO format datetime strings
            if "T" in value:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            else:
                return datetime.fromisoformat(value)
        elif default is not None:
            return default
        else:
            return datetime.now()
