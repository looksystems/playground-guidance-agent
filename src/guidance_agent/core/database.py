"""Database models and session management using SQLAlchemy."""

import os
from typing import Generator
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, TIMESTAMP, CheckConstraint, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from datetime import datetime
import enum

from dotenv import load_dotenv

load_dotenv()

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/guidance_agent")

# Create engine
engine = create_engine(DATABASE_URL, echo=False, future=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Enums for database
class MemoryTypeEnum(str, enum.Enum):
    """Memory types."""
    observation = "observation"
    reflection = "reflection"
    plan = "plan"


# Models
class Memory(Base):
    """Memory table - stores agent memories with vector embeddings."""

    __tablename__ = "memories"

    id = Column(UUID(as_uuid=True), primary_key=True)
    description = Column(String, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    last_accessed = Column(TIMESTAMP(timezone=True), nullable=False)
    importance = Column(Float, nullable=False)
    memory_type = Column(SQLEnum(MemoryTypeEnum, name="memory_type_enum"), nullable=False)
    embedding = Column(Vector(1536))  # pgvector column
    meta = Column(JSONB, default={}, name="metadata")  # 'metadata' is reserved, use 'meta' as attribute
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("importance >= 0 AND importance <= 1", name="memories_importance_check"),
    )


class Case(Base):
    """Case table - stores successful consultation cases."""

    __tablename__ = "cases"

    id = Column(UUID(as_uuid=True), primary_key=True)
    task_type = Column(String(100), nullable=False)
    customer_situation = Column(String, nullable=False)
    guidance_provided = Column(String, nullable=False)
    outcome = Column(JSONB, nullable=False)
    embedding = Column(Vector(1536))  # pgvector column
    meta = Column(JSONB, default={}, name="metadata")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Rule(Base):
    """Rule table - stores learned guidance rules."""

    __tablename__ = "rules"

    id = Column(UUID(as_uuid=True), primary_key=True)
    principle = Column(String, nullable=False)
    domain = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    supporting_evidence = Column(JSONB, default=[])
    embedding = Column(Vector(1536))  # pgvector column
    meta = Column(JSONB, default={}, name="metadata")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="rules_confidence_check"),
    )


class Consultation(Base):
    """Consultation table - tracks full consultation sessions."""

    __tablename__ = "consultations"

    id = Column(UUID(as_uuid=True), primary_key=True)
    customer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    advisor_id = Column(UUID(as_uuid=True), nullable=False)
    conversation = Column(JSONB, nullable=False)
    outcome = Column(JSONB)
    start_time = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    end_time = Column(TIMESTAMP(timezone=True))
    duration_seconds = Column(Integer)
    meta = Column(JSONB, default={}, name="metadata")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class FCAKnowledge(Base):
    """FCA compliance knowledge for retrieval."""

    __tablename__ = "fca_knowledge"

    id = Column(UUID(as_uuid=True), primary_key=True)
    content = Column(String, nullable=False)
    source = Column(String(255))
    category = Column(String(100), nullable=False, index=True)
    embedding = Column(Vector(1536))
    meta = Column(JSONB, default={}, name="metadata")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class PensionKnowledge(Base):
    """Pension domain knowledge for retrieval."""

    __tablename__ = "pension_knowledge"

    id = Column(UUID(as_uuid=True), primary_key=True)
    content = Column(String, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    subcategory = Column(String(100))
    embedding = Column(Vector(1536))
    meta = Column(JSONB, default={}, name="metadata")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


# Database session management
def get_db() -> Generator[Session, None, None]:
    """Get database session.

    Yields:
        SQLAlchemy session

    Example:
        >>> with next(get_db()) as db:
        ...     memories = db.query(Memory).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables.

    This creates all tables if they don't exist.
    For migrations, use Alembic instead.
    """
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    """Get a new database session.

    Returns:
        SQLAlchemy session

    Example:
        >>> session = get_session()
        >>> memories = session.query(Memory).all()
        >>> session.close()
    """
    return SessionLocal()
