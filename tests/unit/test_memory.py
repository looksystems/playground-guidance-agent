"""Unit tests for memory module."""

import pytest
from datetime import datetime, timedelta
from uuid import UUID

from guidance_agent.core.memory import MemoryNode, MemoryStream
from guidance_agent.core.types import MemoryType
from tests.fixtures.embeddings import EMBEDDING_DIMENSION as EMBEDDING_DIM


class TestMemoryNode:
    """Tests for MemoryNode class."""

    def test_create_memory_node(self):
        """Test creating a basic memory node."""
        memory = MemoryNode(
            description="Test memory",
            importance=0.8,
            memory_type=MemoryType.OBSERVATION,
        )

        assert memory.description == "Test memory"
        assert memory.importance == 0.8
        assert memory.memory_type == MemoryType.OBSERVATION
        assert isinstance(memory.memory_id, UUID)
        assert isinstance(memory.timestamp, datetime)

    def test_memory_access_updates_last_accessed(self):
        """Test that accessing a memory updates last_accessed timestamp."""
        memory = MemoryNode(description="Test")
        original_time = memory.last_accessed

        # Wait a tiny bit
        import time

        time.sleep(0.01)

        memory.access()
        assert memory.last_accessed > original_time

    def test_recency_score_decreases_over_time(self):
        """Test that recency score decreases with time."""
        memory = MemoryNode(description="Test")

        # Score right now should be close to 1
        score_now = memory.recency_score()
        assert score_now > 0.99

        # Score 24 hours ago should be less
        past_time = datetime.now() - timedelta(hours=24)
        memory.last_accessed = past_time
        score_past = memory.recency_score()
        assert score_past < score_now
        assert 0 < score_past < 1

    def test_memory_to_dict(self):
        """Test converting memory to dictionary."""
        memory = MemoryNode(
            description="Test memory",
            importance=0.7,
            memory_type=MemoryType.REFLECTION,
            embedding=[0.1, 0.2, 0.3],
            citations=["citation-1"],
        )

        data = memory.to_dict()

        assert data["description"] == "Test memory"
        assert data["importance"] == 0.7
        assert data["memory_type"] == "reflection"
        assert data["embedding"] == [0.1, 0.2, 0.3]
        assert data["citations"] == ["citation-1"]
        assert isinstance(data["id"], str)

    def test_memory_from_dict(self):
        """Test creating memory from dictionary."""
        data = {
            "id": "12345678-1234-5678-1234-567812345678",
            "description": "Test memory",
            "timestamp": "2024-01-01T12:00:00",
            "last_accessed": "2024-01-01T12:00:00",
            "importance": 0.7,
            "memory_type": "observation",
            "embedding": [0.1, 0.2],
            "citations": ["test"],
            "metadata": {"key": "value"},
        }

        memory = MemoryNode.from_dict(data)

        assert str(memory.memory_id) == data["id"]
        assert memory.description == "Test memory"
        assert memory.importance == 0.7
        assert memory.memory_type == MemoryType.OBSERVATION


class TestMemoryStream:
    """Tests for MemoryStream class."""

    def test_create_empty_stream(self, memory_stream):
        """Test creating an empty memory stream."""
        assert memory_stream.get_memory_count() == 0
        assert memory_stream.memories == []

    def test_add_memory_to_stream(self, memory_stream, sample_memory_node):
        """Test adding a memory to the stream."""
        memory_stream.add(sample_memory_node)

        assert memory_stream.get_memory_count() == 1
        assert memory_stream.memories[0] == sample_memory_node

    def test_retrieve_from_empty_stream(self, memory_stream):
        """Test retrieving from an empty stream returns empty list."""
        query_embedding = [0.1] * EMBEDDING_DIM
        results = memory_stream.retrieve(query_embedding, top_k=5)

        assert results == []

    def test_retrieve_memories_by_relevance(self, populated_memory_stream):
        """Test retrieving memories with relevance scoring."""
        # Query embedding similar to memory at index 3
        query_embedding = [3.0] * EMBEDDING_DIM

        results = populated_memory_stream.retrieve(
            query_embedding, top_k=3, recency_weight=0.0, importance_weight=0.0, relevance_weight=1.0
        )

        assert len(results) <= 3
        assert len(results) > 0

    def test_retrieve_memories_by_importance(self, populated_memory_stream):
        """Test retrieving memories prioritizing importance."""
        query_embedding = [0.0] * EMBEDDING_DIM

        results = populated_memory_stream.retrieve(
            query_embedding,
            top_k=3,
            recency_weight=0.0,
            importance_weight=1.0,
            relevance_weight=0.0,
        )

        assert len(results) <= 3
        # Highest importance should be first (0.8 from reflection or 0.9 from observation)
        if len(results) > 1:
            assert results[0].importance >= results[1].importance

    def test_retrieve_by_type(self, populated_memory_stream):
        """Test retrieving memories filtered by type."""
        observations = populated_memory_stream.retrieve_by_type(MemoryType.OBSERVATION, limit=10)
        reflections = populated_memory_stream.retrieve_by_type(MemoryType.REFLECTION, limit=10)

        assert len(observations) == 5
        assert len(reflections) == 1
        assert all(m.memory_type == MemoryType.OBSERVATION for m in observations)
        assert all(m.memory_type == MemoryType.REFLECTION for m in reflections)

    def test_retrieve_recent_memories(self, memory_stream):
        """Test retrieving memories within time window."""
        # Add memory from 2 hours ago
        old_memory = MemoryNode(description="Old memory", importance=0.5)
        old_memory.timestamp = datetime.now() - timedelta(hours=2)
        memory_stream.add(old_memory)

        # Add memory from now
        new_memory = MemoryNode(description="New memory", importance=0.5)
        memory_stream.add(new_memory)

        # Retrieve memories from last 1 hour
        recent = memory_stream.retrieve_recent(hours=1, limit=10)

        assert len(recent) == 1
        assert recent[0].description == "New memory"

    def test_clear_stream(self, populated_memory_stream):
        """Test clearing all memories from stream."""
        assert populated_memory_stream.get_memory_count() > 0

        populated_memory_stream.clear()

        assert populated_memory_stream.get_memory_count() == 0
        assert populated_memory_stream.memories == []

    def test_memory_retrieval_by_similarity(self, memory_stream):
        """Test that memory retrieval returns most similar memories.

        This test verifies the similarity algorithm behavior by ensuring
        that memories with similar embeddings are retrieved over dissimilar ones.
        """
        # Create memories with different embeddings
        # Memory 1: embedding along x-axis
        similar_memory = MemoryNode(
            description="Pension consolidation advice",
            importance=0.5,
            embedding=[1.0] + [0.0] * (EMBEDDING_DIM - 1)  # [1, 0, 0, ...]
        )

        # Memory 2: embedding along y-axis (orthogonal to query)
        different_memory = MemoryNode(
            description="Mortgage advice",
            importance=0.5,
            embedding=[0.0, 1.0] + [0.0] * (EMBEDDING_DIM - 2)  # [0, 1, 0, ...]
        )

        # Add both memories
        memory_stream.add(similar_memory)
        memory_stream.add(different_memory)

        # Query with embedding similar to first memory (along x-axis)
        query_embedding = [1.0] + [0.0] * (EMBEDDING_DIM - 1)

        # Retrieve with pure relevance weighting
        results = memory_stream.retrieve(
            query_embedding,
            top_k=2,
            relevance_weight=1.0,
            importance_weight=0.0,
            recency_weight=0.0
        )

        # Should return similar memory first (tests cosine similarity behavior)
        assert len(results) == 2
        assert results[0].description == "Pension consolidation advice"
        assert results[1].description == "Mortgage advice"
