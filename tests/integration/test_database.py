"""Integration tests for database operations using SQLAlchemy."""

import pytest
from uuid import uuid4
from datetime import datetime

from guidance_agent.core.database import (
    Memory,
    Case,
    Rule,
    Consultation,
    MemoryTypeEnum,
)
from tests.fixtures.embeddings import EMBEDDING_DIMENSION as EMBEDDING_DIM


@pytest.mark.integration
class TestDatabaseOperations:
    """Integration tests for database CRUD operations.

    Uses transactional fixtures for complete test isolation.
    All database changes are automatically rolled back after each test.
    """

    def test_create_memory_in_database(self, transactional_db_session):
        """Verify memory can be created and persisted to database."""
        session = transactional_db_session

        # Create a memory
        memory = Memory(
            id=uuid4(),
            description="Test memory",
            timestamp=datetime.now(),
            last_accessed=datetime.now(),
            importance=0.8,
            memory_type=MemoryTypeEnum.observation,
            embedding=[0.1] * EMBEDDING_DIM,
            meta={"test": "data"},
        )

        session.add(memory)
        session.commit()

        # Verify it was persisted
        count = session.query(Memory).filter(Memory.id == memory.id).count()
        assert count == 1

        # No cleanup needed - transaction will be rolled back automatically

    def test_retrieve_memory_by_id(self, transactional_db_session):
        """Verify memory can be retrieved by ID with all fields intact."""
        session = transactional_db_session

        # Create and persist a memory
        memory_id = uuid4()
        memory = Memory(
            id=memory_id,
            description="Test memory",
            timestamp=datetime.now(),
            last_accessed=datetime.now(),
            importance=0.8,
            memory_type=MemoryTypeEnum.observation,
            embedding=[0.1] * EMBEDDING_DIM,
            meta={"test": "data"},
        )
        session.add(memory)
        session.commit()

        # Retrieve the memory
        retrieved = session.query(Memory).filter(Memory.id == memory_id).first()

        assert retrieved is not None
        assert retrieved.description == "Test memory"
        assert retrieved.importance == 0.8
        assert retrieved.memory_type == MemoryTypeEnum.observation
        assert retrieved.meta == {"test": "data"}
        assert len(retrieved.embedding) == EMBEDDING_DIM

        # No cleanup needed - transaction will be rolled back automatically

    def test_create_case(self, transactional_db_session):
        """Test creating a case in database."""
        session = transactional_db_session

        case = Case(
            id=uuid4(),
            task_type="general_inquiry",
            customer_situation="Customer asking about pension options",
            guidance_provided="Explained withdrawal options",
            outcome={"successful": True, "satisfaction": 8.5},
            embedding=[0.2] * EMBEDDING_DIM,
            meta={"advisor_id": str(uuid4())},
        )

        session.add(case)
        session.commit()

        case_id = case.id

        # Retrieve
        retrieved = session.query(Case).filter(Case.id == case_id).first()

        assert retrieved is not None
        assert retrieved.task_type == "general_inquiry"
        assert retrieved.outcome["successful"] is True
        assert retrieved.outcome["satisfaction"] == 8.5

        # No cleanup needed - transaction will be rolled back automatically

    def test_create_rule(self, transactional_db_session):
        """Test creating a guidance rule."""
        session = transactional_db_session

        rule = Rule(
            id=uuid4(),
            principle="Always check customer understanding",
            domain="general",
            confidence=0.9,
            supporting_evidence=["case-1", "case-2"],
            embedding=[0.3] * EMBEDDING_DIM,
        )

        session.add(rule)
        session.commit()

        rule_id = rule.id

        # Retrieve
        retrieved = session.query(Rule).filter(Rule.id == rule_id).first()

        assert retrieved is not None
        assert retrieved.principle == "Always check customer understanding"
        assert retrieved.confidence == 0.9
        assert retrieved.supporting_evidence == ["case-1", "case-2"]

        # No cleanup needed - transaction will be rolled back automatically

    def test_create_consultation(self, transactional_db_session):
        """Test creating a consultation record."""
        session = transactional_db_session

        consultation = Consultation(
            id=uuid4(),
            customer_id=uuid4(),
            advisor_id=uuid4(),
            conversation=[
                {"role": "customer", "content": "I want to access my pension"},
                {"role": "advisor", "content": "Let me explain your options"},
            ],
            outcome={"successful": True},
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=300,
        )

        session.add(consultation)
        session.commit()

        consultation_id = consultation.id

        # Retrieve
        retrieved = (
            session.query(Consultation)
            .filter(Consultation.id == consultation_id)
            .first()
        )

        assert retrieved is not None
        assert len(retrieved.conversation) == 2
        assert retrieved.conversation[0]["role"] == "customer"
        assert retrieved.duration_seconds == 300

        # No cleanup needed - transaction will be rolled back automatically

    def test_query_memories_by_type(self, transactional_db_session):
        """Test querying memories by type."""
        session = transactional_db_session

        # Create memories of different types
        obs1 = Memory(
            id=uuid4(),
            description="Observation 1",
            timestamp=datetime.now(),
            last_accessed=datetime.now(),
            importance=0.5,
            memory_type=MemoryTypeEnum.observation,
            embedding=[0.1] * EMBEDDING_DIM,
        )

        obs2 = Memory(
            id=uuid4(),
            description="Observation 2",
            timestamp=datetime.now(),
            last_accessed=datetime.now(),
            importance=0.6,
            memory_type=MemoryTypeEnum.observation,
            embedding=[0.1] * EMBEDDING_DIM,
        )

        reflection = Memory(
            id=uuid4(),
            description="Reflection 1",
            timestamp=datetime.now(),
            last_accessed=datetime.now(),
            importance=0.8,
            memory_type=MemoryTypeEnum.reflection,
            embedding=[0.1] * EMBEDDING_DIM,
        )

        session.add_all([obs1, obs2, reflection])
        session.commit()

        # Query observations only
        observations = (
            session.query(Memory)
            .filter(Memory.memory_type == MemoryTypeEnum.observation)
            .all()
        )

        assert len(observations) == 2

        # Query reflections only
        reflections = (
            session.query(Memory)
            .filter(Memory.memory_type == MemoryTypeEnum.reflection)
            .all()
        )

        assert len(reflections) == 1

        # No cleanup needed - transaction will be rolled back automatically
