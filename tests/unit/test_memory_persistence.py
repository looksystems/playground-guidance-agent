"""Unit tests for memory persistence with database."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from guidance_agent.core.memory import MemoryNode, MemoryStream
from guidance_agent.core.types import MemoryType
from guidance_agent.core.database import Memory, get_session


@pytest.fixture
def db_session():
    """Get a test database session."""
    session = get_session()
    # Cleanup BEFORE test
    session.query(Memory).delete()
    session.commit()

    yield session

    # Cleanup AFTER test
    session.query(Memory).delete()
    session.commit()
    session.close()


@pytest.fixture
def persistent_memory_stream(db_session):
    """Create a memory stream with database persistence."""
    return MemoryStream(session=db_session)


class TestMemoryPersistence:
    """Tests for memory stream database persistence."""

    def test_create_memory_stream_with_session(self, db_session):
        """Test creating a memory stream with database session."""
        stream = MemoryStream(session=db_session)
        assert stream.session is not None
        assert stream.get_memory_count() == 0

    def test_create_memory_stream_without_session(self):
        """Test creating a memory stream without database (in-memory only)."""
        stream = MemoryStream()
        assert stream.session is None
        assert stream.get_memory_count() == 0

    def test_add_memory_persists_to_database(self, persistent_memory_stream, db_session):
        """Test that adding a memory persists it to the database."""
        memory = MemoryNode(
            description="Customer asked about pension withdrawal",
            importance=0.8,
            memory_type=MemoryType.OBSERVATION,
            embedding=[0.1] * 1536,
        )

        persistent_memory_stream.add(memory)

        # Verify it's in the stream
        assert persistent_memory_stream.get_memory_count() == 1

        # Verify it's in the database
        db_memory = db_session.query(Memory).filter(Memory.id == memory.memory_id).first()
        assert db_memory is not None
        assert db_memory.description == "Customer asked about pension withdrawal"
        assert db_memory.importance == 0.8

    def test_load_memories_from_database(self, db_session):
        """Test loading existing memories from database on initialization."""
        # Add memories directly to database
        memory1_id = uuid4()
        memory2_id = uuid4()

        db_memory1 = Memory(
            id=memory1_id,
            description="Memory 1",
            timestamp=datetime.now(),
            last_accessed=datetime.now(),
            importance=0.7,
            memory_type="observation",
            embedding=[0.1] * 1536,
        )
        db_memory2 = Memory(
            id=memory2_id,
            description="Memory 2",
            timestamp=datetime.now(),
            last_accessed=datetime.now(),
            importance=0.6,
            memory_type="reflection",
            embedding=[0.2] * 1536,
        )

        db_session.add(db_memory1)
        db_session.add(db_memory2)
        db_session.commit()

        # Create new stream - should load existing memories
        stream = MemoryStream(session=db_session, load_existing=True)

        assert stream.get_memory_count() == 2
        memory_ids = [m.memory_id for m in stream.memories]
        assert memory1_id in memory_ids
        assert memory2_id in memory_ids

    def test_retrieve_updates_last_accessed_in_database(self, persistent_memory_stream, db_session):
        """Test that retrieving memories updates last_accessed in database."""
        from datetime import timezone

        memory = MemoryNode(
            description="Test memory",
            importance=0.7,
            memory_type=MemoryType.OBSERVATION,
            embedding=[0.5] * 1536,
        )
        # Get original access time from database after persisting
        persistent_memory_stream.add(memory)
        db_memory_orig = db_session.query(Memory).filter(Memory.id == memory.memory_id).first()
        original_access_time = db_memory_orig.last_accessed

        # Wait a moment
        import time
        time.sleep(0.01)

        # Retrieve the memory
        query_embedding = [0.5] * 1536
        retrieved = persistent_memory_stream.retrieve(query_embedding, top_k=1)

        assert len(retrieved) == 1

        # Check that last_accessed was updated in database
        db_session.expire_all()  # Clear session cache
        db_memory = db_session.query(Memory).filter(Memory.id == memory.memory_id).first()
        assert db_memory.last_accessed > original_access_time

    def test_add_without_session_does_not_persist(self):
        """Test that adding memory without session doesn't persist to database."""
        stream = MemoryStream()  # No session
        memory = MemoryNode(
            description="In-memory only",
            importance=0.5,
            memory_type=MemoryType.OBSERVATION,
            embedding=[0.1] * 1536,
        )

        stream.add(memory)

        # Should be in stream
        assert stream.get_memory_count() == 1

        # But not in database (verify by checking with fresh session)
        session = get_session()
        try:
            db_memory = session.query(Memory).filter(Memory.id == memory.memory_id).first()
            assert db_memory is None
        finally:
            session.close()

    def test_retrieve_from_database_by_id(self, persistent_memory_stream, db_session):
        """Test retrieving a specific memory from database by ID."""
        memory = MemoryNode(
            description="Specific memory",
            importance=0.8,
            memory_type=MemoryType.REFLECTION,
            embedding=[0.3] * 1536,
        )

        persistent_memory_stream.add(memory)

        # Retrieve by ID
        retrieved = persistent_memory_stream.get_by_id(memory.memory_id)

        assert retrieved is not None
        assert retrieved.memory_id == memory.memory_id
        assert retrieved.description == "Specific memory"

    def test_delete_memory_from_database(self, persistent_memory_stream, db_session):
        """Test deleting a memory removes it from database."""
        memory = MemoryNode(
            description="To be deleted",
            importance=0.5,
            memory_type=MemoryType.OBSERVATION,
            embedding=[0.2] * 1536,
        )

        persistent_memory_stream.add(memory)
        assert persistent_memory_stream.get_memory_count() == 1

        # Delete the memory
        persistent_memory_stream.delete(memory.memory_id)

        # Should be removed from stream
        assert persistent_memory_stream.get_memory_count() == 0

        # Should be removed from database
        db_memory = db_session.query(Memory).filter(Memory.id == memory.memory_id).first()
        assert db_memory is None

    def test_batch_add_memories(self, persistent_memory_stream, db_session):
        """Test adding multiple memories at once."""
        memories = [
            MemoryNode(
                description=f"Memory {i}",
                importance=0.5 + (i * 0.1),
                memory_type=MemoryType.OBSERVATION,
                embedding=[float(i) * 0.1] * 1536,
            )
            for i in range(5)
        ]

        for memory in memories:
            persistent_memory_stream.add(memory)

        # All should be in stream
        assert persistent_memory_stream.get_memory_count() == 5

        # All should be in database
        db_count = db_session.query(Memory).count()
        assert db_count == 5

    def test_clear_removes_from_database(self, persistent_memory_stream, db_session):
        """Test that clearing stream also clears database."""
        # Add some memories
        for i in range(3):
            memory = MemoryNode(
                description=f"Memory {i}",
                importance=0.5,
                memory_type=MemoryType.OBSERVATION,
                embedding=[0.1] * 1536,
            )
            persistent_memory_stream.add(memory)

        assert persistent_memory_stream.get_memory_count() == 3

        # Clear the stream
        persistent_memory_stream.clear()

        # Should be empty
        assert persistent_memory_stream.get_memory_count() == 0

        # Database should also be empty
        db_count = db_session.query(Memory).count()
        assert db_count == 0

    def test_update_memory_in_database(self, persistent_memory_stream, db_session):
        """Test updating a memory's importance updates the database."""
        memory = MemoryNode(
            description="Original",
            importance=0.5,
            memory_type=MemoryType.OBSERVATION,
            embedding=[0.1] * 1536,
        )

        persistent_memory_stream.add(memory)

        # Update importance
        memory.importance = 0.9
        persistent_memory_stream.update(memory)

        # Verify in database
        db_memory = db_session.query(Memory).filter(Memory.id == memory.memory_id).first()
        assert db_memory.importance == 0.9

    def test_retrieve_with_database_filter(self, persistent_memory_stream, db_session):
        """Test retrieving memories with database-level filtering."""
        # Add memories of different types
        obs_memory = MemoryNode(
            description="Observation",
            importance=0.7,
            memory_type=MemoryType.OBSERVATION,
            embedding=[0.1] * 1536,
        )
        ref_memory = MemoryNode(
            description="Reflection",
            importance=0.8,
            memory_type=MemoryType.REFLECTION,
            embedding=[0.2] * 1536,
        )

        persistent_memory_stream.add(obs_memory)
        persistent_memory_stream.add(ref_memory)

        # Retrieve only observations using database filter
        results = persistent_memory_stream.retrieve_by_type(MemoryType.OBSERVATION)

        assert len(results) == 1
        assert results[0].memory_type == MemoryType.OBSERVATION
