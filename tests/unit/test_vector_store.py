"""Unit tests for vector store."""

import pytest
from uuid import uuid4
from sqlalchemy.orm import Session

from guidance_agent.retrieval.vector_store import PgVectorStore
from guidance_agent.core.database import Memory, Case, Rule, MemoryTypeEnum, get_session


@pytest.fixture
def db_session():
    """Get a test database session."""
    session = get_session()
    # Cleanup BEFORE test: Delete all test data
    session.query(Memory).delete()
    session.query(Case).delete()
    session.query(Rule).delete()
    session.commit()

    yield session

    # Cleanup AFTER test: Delete all test data
    session.query(Memory).delete()
    session.query(Case).delete()
    session.query(Rule).delete()
    session.commit()
    session.close()


@pytest.fixture
def memory_vector_store(db_session):
    """Create a vector store for Memory table."""
    return PgVectorStore(db_session, Memory)


@pytest.fixture
def sample_embedding():
    """Create a sample 1536-dimensional embedding."""
    return [0.1] * 1536


class TestPgVectorStore:
    """Tests for PgVectorStore class."""

    def test_create_vector_store(self, memory_vector_store):
        """Test creating a vector store instance."""
        assert memory_vector_store is not None
        assert memory_vector_store.model == Memory

    def test_add_memory_vector(self, memory_vector_store, sample_embedding, db_session):
        """Test adding a vector with metadata to the store."""
        memory_id = uuid4()
        metadata = {
            "description": "Test memory",
            "timestamp": "2024-01-01T12:00:00",
            "last_accessed": "2024-01-01T12:00:00",
            "importance": 0.8,
            "memory_type": "observation",
        }

        memory_vector_store.add(
            id=memory_id,
            embedding=sample_embedding,
            metadata=metadata,
        )

        # Verify the memory was added
        memory = db_session.query(Memory).filter(Memory.id == memory_id).first()
        assert memory is not None
        assert memory.description == "Test memory"
        assert memory.importance == 0.8
        assert memory.memory_type == MemoryTypeEnum.observation
        assert len(memory.embedding) == 1536

    def test_add_updates_existing_vector(self, memory_vector_store, sample_embedding, db_session):
        """Test that adding with same ID updates existing record."""
        memory_id = uuid4()
        metadata_v1 = {
            "description": "Original description",
            "timestamp": "2024-01-01T12:00:00",
            "last_accessed": "2024-01-01T12:00:00",
            "importance": 0.5,
            "memory_type": "observation",
        }

        # Add first version
        memory_vector_store.add(memory_id, sample_embedding, metadata_v1)

        # Update with new metadata
        metadata_v2 = {
            "description": "Updated description",
            "timestamp": "2024-01-01T12:00:00",
            "last_accessed": "2024-01-01T13:00:00",
            "importance": 0.9,
            "memory_type": "reflection",
        }
        new_embedding = [0.2] * 1536
        memory_vector_store.add(memory_id, new_embedding, metadata_v2)

        # Should only have one record
        count = db_session.query(Memory).filter(Memory.id == memory_id).count()
        assert count == 1

        # Verify it was updated
        memory = db_session.query(Memory).filter(Memory.id == memory_id).first()
        assert memory.description == "Updated description"
        assert memory.importance == 0.9
        assert memory.memory_type == MemoryTypeEnum.reflection

    def test_search_by_similarity(self, memory_vector_store, db_session):
        """Test searching for similar vectors."""
        # Add multiple memories with different embeddings
        memories_data = [
            (uuid4(), [1.0] + [0.0] * 1535, "Memory about pensions", 0.7),
            (uuid4(), [0.0] * 1535 + [1.0], "Memory about retirement", 0.6),
            (uuid4(), [0.9] + [0.0] * 1535, "Memory about pension transfer", 0.8),
        ]

        for mem_id, embedding, description, importance in memories_data:
            metadata = {
                "description": description,
                "timestamp": "2024-01-01T12:00:00",
                "last_accessed": "2024-01-01T12:00:00",
                "importance": importance,
                "memory_type": "observation",
            }
            memory_vector_store.add(mem_id, embedding, metadata)

        # Search with query similar to first and third memories
        query_embedding = [0.95] + [0.0] * 1535
        results = memory_vector_store.search(query_embedding, top_k=2)

        # Should return 2 results
        assert len(results) == 2

        # Most similar should be "pension transfer" (0.9) or "pensions" (1.0)
        top_result = results[0]
        assert "pension" in top_result["metadata"]["description"].lower()
        assert top_result["similarity"] > 0.9

    def test_search_with_empty_store(self, memory_vector_store):
        """Test searching in an empty store returns empty list."""
        query_embedding = [0.1] * 1536
        results = memory_vector_store.search(query_embedding, top_k=5)

        assert results == []

    def test_search_with_metadata_filter(self, memory_vector_store, db_session):
        """Test searching with JSONB metadata filtering."""
        # Add memories with different types
        for i in range(3):
            mem_id = uuid4()
            metadata = {
                "description": f"Test memory {i}",
                "timestamp": "2024-01-01T12:00:00",
                "last_accessed": "2024-01-01T12:00:00",
                "importance": 0.5 + (i * 0.1),
                "memory_type": "observation" if i < 2 else "reflection",
            }
            embedding = [float(i)] * 1536
            memory_vector_store.add(mem_id, embedding, metadata)

        # Search only for observations
        query_embedding = [0.0] * 1536
        results = memory_vector_store.search(
            query_embedding,
            top_k=10,
            filter_dict={"memory_type": "observation"},
        )

        # Should only return observations
        assert len(results) == 2
        for result in results:
            assert result["metadata"]["memory_type"] == "observation"

    def test_search_respects_top_k(self, memory_vector_store, db_session):
        """Test that search respects top_k parameter."""
        # Add 10 memories (use embeddings 1-10 to avoid zero vector issues)
        for i in range(1, 11):
            mem_id = uuid4()
            metadata = {
                "description": f"Memory {i}",
                "timestamp": "2024-01-01T12:00:00",
                "last_accessed": "2024-01-01T12:00:00",
                "importance": 0.5,
                "memory_type": "observation",
            }
            embedding = [float(i) * 0.1] * 1536  # Scale to avoid numerical issues
            memory_vector_store.add(mem_id, embedding, metadata)

        query_embedding = [0.5] * 1536

        # Request only 3 results
        results = memory_vector_store.search(query_embedding, top_k=3)
        assert len(results) == 3

        # Request 20 results (more than available)
        results = memory_vector_store.search(query_embedding, top_k=20)
        assert len(results) == 10

    def test_delete_vector(self, memory_vector_store, sample_embedding, db_session):
        """Test deleting a vector from the store."""
        memory_id = uuid4()
        metadata = {
            "description": "Test memory",
            "timestamp": "2024-01-01T12:00:00",
            "last_accessed": "2024-01-01T12:00:00",
            "importance": 0.7,
            "memory_type": "observation",
        }

        # Add memory
        memory_vector_store.add(memory_id, sample_embedding, metadata)

        # Verify it exists
        memory = db_session.query(Memory).filter(Memory.id == memory_id).first()
        assert memory is not None

        # Delete it
        memory_vector_store.delete(memory_id)

        # Verify it's gone
        memory = db_session.query(Memory).filter(Memory.id == memory_id).first()
        assert memory is None

    def test_delete_nonexistent_vector(self, memory_vector_store):
        """Test deleting a non-existent vector doesn't raise error."""
        non_existent_id = uuid4()
        # Should not raise any error
        memory_vector_store.delete(non_existent_id)

    def test_case_vector_store(self, db_session):
        """Test vector store works with Case model."""
        case_store = PgVectorStore(db_session, Case)

        case_id = uuid4()
        embedding = [0.5] * 1536
        metadata = {
            "task_type": "pension_transfer",
            "customer_situation": "Customer wants to transfer DB pension",
            "guidance_provided": "Explained risks and recommended Pension Wise",
            "outcome": {"successful": True},
        }

        case_store.add(case_id, embedding, metadata)

        # Verify case was added
        case = db_session.query(Case).filter(Case.id == case_id).first()
        assert case is not None
        assert case.task_type == "pension_transfer"

    def test_rule_vector_store(self, db_session):
        """Test vector store works with Rule model."""
        rule_store = PgVectorStore(db_session, Rule)

        rule_id = uuid4()
        embedding = [0.3] * 1536
        metadata = {
            "principle": "Always warn about DB pension transfer risks",
            "domain": "pension_transfers",
            "confidence": 0.95,
            "supporting_evidence": ["case-1", "case-2"],
        }

        rule_store.add(rule_id, embedding, metadata)

        # Verify rule was added
        rule = db_session.query(Rule).filter(Rule.id == rule_id).first()
        assert rule is not None
        assert rule.principle == "Always warn about DB pension transfer risks"
        assert rule.confidence == 0.95

    def test_search_returns_sorted_by_similarity(self, memory_vector_store, db_session):
        """Test that search results are sorted by similarity score."""
        # Add memories with embeddings at different distances (avoid zero vectors)
        memories_data = [
            (uuid4(), [1.0] + [0.1] * 1535, "Exact match"),
            (uuid4(), [0.5] + [0.1] * 1535, "Partial match"),
            (uuid4(), [0.1] * 1536, "Distant match"),
        ]

        for mem_id, embedding, description in memories_data:
            metadata = {
                "description": description,
                "timestamp": "2024-01-01T12:00:00",
                "last_accessed": "2024-01-01T12:00:00",
                "importance": 0.5,
                "memory_type": "observation",
            }
            memory_vector_store.add(mem_id, embedding, metadata)

        # Search with query matching first embedding
        query_embedding = [1.0] + [0.1] * 1535
        results = memory_vector_store.search(query_embedding, top_k=3)

        # Results should be ordered by similarity
        assert len(results) == 3
        assert results[0]["similarity"] >= results[1]["similarity"]
        assert results[1]["similarity"] >= results[2]["similarity"]
        assert results[0]["metadata"]["description"] == "Exact match"
