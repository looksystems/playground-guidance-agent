"""Integration tests for database operations using SQLAlchemy."""

import pytest
from uuid import uuid4
from datetime import datetime

from guidance_agent.core.database import (
    get_session,
    Memory,
    Case,
    Rule,
    Consultation,
    MemoryTypeEnum,
)


@pytest.mark.integration
class TestDatabaseOperations:
    """Integration tests for database CRUD operations."""

    def test_create_and_retrieve_memory(self):
        """Test creating and retrieving a memory from database."""
        session = get_session()

        try:
            # Create a memory
            memory = Memory(
                id=uuid4(),
                description="Test memory",
                timestamp=datetime.now(),
                last_accessed=datetime.now(),
                importance=0.8,
                memory_type=MemoryTypeEnum.observation,
                embedding=[0.1] * 1536,
                meta={"test": "data"},
            )

            session.add(memory)
            session.commit()

            memory_id = memory.id

            # Retrieve the memory
            retrieved = session.query(Memory).filter(Memory.id == memory_id).first()

            assert retrieved is not None
            assert retrieved.description == "Test memory"
            assert retrieved.importance == 0.8
            assert retrieved.memory_type == MemoryTypeEnum.observation
            assert retrieved.meta == {"test": "data"}
            assert len(retrieved.embedding) == 1536

            # Clean up
            session.delete(retrieved)
            session.commit()

        finally:
            session.close()

    def test_create_case(self):
        """Test creating a case in database."""
        session = get_session()

        try:
            case = Case(
                id=uuid4(),
                task_type="general_inquiry",
                customer_situation="Customer asking about pension options",
                guidance_provided="Explained withdrawal options",
                outcome={"successful": True, "satisfaction": 8.5},
                embedding=[0.2] * 1536,
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

            # Clean up
            session.delete(retrieved)
            session.commit()

        finally:
            session.close()

    def test_create_rule(self):
        """Test creating a guidance rule."""
        session = get_session()

        try:
            rule = Rule(
                id=uuid4(),
                principle="Always check customer understanding",
                domain="general",
                confidence=0.9,
                supporting_evidence=["case-1", "case-2"],
                embedding=[0.3] * 1536,
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

            # Clean up
            session.delete(retrieved)
            session.commit()

        finally:
            session.close()

    def test_create_consultation(self):
        """Test creating a consultation record."""
        session = get_session()

        try:
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

            # Clean up
            session.delete(retrieved)
            session.commit()

        finally:
            session.close()

    def test_query_memories_by_type(self):
        """Test querying memories by type."""
        session = get_session()

        try:
            # Create memories of different types
            obs1 = Memory(
                id=uuid4(),
                description="Observation 1",
                timestamp=datetime.now(),
                last_accessed=datetime.now(),
                importance=0.5,
                memory_type=MemoryTypeEnum.observation,
                embedding=[0.1] * 1536,
            )

            obs2 = Memory(
                id=uuid4(),
                description="Observation 2",
                timestamp=datetime.now(),
                last_accessed=datetime.now(),
                importance=0.6,
                memory_type=MemoryTypeEnum.observation,
                embedding=[0.1] * 1536,
            )

            reflection = Memory(
                id=uuid4(),
                description="Reflection 1",
                timestamp=datetime.now(),
                last_accessed=datetime.now(),
                importance=0.8,
                memory_type=MemoryTypeEnum.reflection,
                embedding=[0.1] * 1536,
            )

            session.add_all([obs1, obs2, reflection])
            session.commit()

            # Query observations only
            observations = (
                session.query(Memory)
                .filter(Memory.memory_type == MemoryTypeEnum.observation)
                .all()
            )

            assert len(observations) >= 2

            # Query reflections only
            reflections = (
                session.query(Memory)
                .filter(Memory.memory_type == MemoryTypeEnum.reflection)
                .all()
            )

            assert len(reflections) >= 1

            # Clean up
            session.delete(obs1)
            session.delete(obs2)
            session.delete(reflection)
            session.commit()

        finally:
            session.close()
