"""Shared pytest fixtures for tests."""

import os
import pytest
from datetime import datetime
from uuid import uuid4
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root to get EMBEDDING_DIMENSION
# This ensures tests use the same configuration as the application
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from guidance_agent.core import (
    AgentConfig,
    MemoryNode,
    MemoryStream,
    MemoryType,
    CustomerProfile,
    CustomerDemographics,
    FinancialSituation,
    PensionPot,
)

# Get embedding dimension from environment (loaded from .env)
# Default to 1536 only if not set in .env
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIMENSION", "1536"))


@pytest.fixture
def sample_memory_node():
    """Create a sample memory node for testing."""
    return MemoryNode(
        memory_id=uuid4(),
        description="Customer asked about pension withdrawal options",
        timestamp=datetime.now(),
        importance=0.7,
        memory_type=MemoryType.OBSERVATION,
        embedding=[0.1] * EMBEDDING_DIM,  # Mock embedding
    )


@pytest.fixture
def memory_stream():
    """Create an empty memory stream."""
    return MemoryStream()


@pytest.fixture
def populated_memory_stream(sample_memory_node):
    """Create a memory stream with some test memories."""
    stream = MemoryStream()

    # Add various types of memories
    for i in range(5):
        memory = MemoryNode(
            description=f"Test observation {i}",
            importance=0.5 + (i * 0.1),
            memory_type=MemoryType.OBSERVATION,
            embedding=[float(i)] * EMBEDDING_DIM,
        )
        stream.add(memory)

    # Add a reflection
    reflection = MemoryNode(
        description="Customer seems uncertain about risk tolerance",
        importance=0.8,
        memory_type=MemoryType.REFLECTION,
        embedding=[0.5] * EMBEDDING_DIM,
    )
    stream.add(reflection)

    return stream


@pytest.fixture
def agent_config():
    """Create a sample agent configuration."""
    return AgentConfig(
        name="Test Agent",
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=1000,
    )


@pytest.fixture
def sample_customer_profile():
    """Create a sample customer profile for testing."""
    demographics = CustomerDemographics(
        age=55,
        gender="male",
        location="London",
        employment_status="employed",
        financial_literacy="medium",
    )

    financial = FinancialSituation(
        annual_income=50000.0,
        total_assets=200000.0,
        total_debt=50000.0,
        dependents=2,
        risk_tolerance="medium",
    )

    pension = PensionPot(
        pot_id="pot-123",
        provider="ABC Pension Co",
        pot_type="defined_contribution",
        current_value=150000.0,
        projected_value=200000.0,
        age_accessible=55,
    )

    return CustomerProfile(
        demographics=demographics,
        financial=financial,
        pensions=[pension],
        goals="Planning retirement at age 60",
        presenting_question="What are my options for accessing my pension?",
    )


@pytest.fixture
def mock_embedding():
    """Create a mock embedding vector."""
    return [0.1] * EMBEDDING_DIM


@pytest.fixture
def mock_embedding_batch():
    """Create a batch of mock embedding vectors."""
    return [[float(i) * 0.1] * EMBEDDING_DIM for i in range(5)]


@pytest.fixture(autouse=True)
def disable_phoenix_tracing(monkeypatch):
    """Disable Phoenix tracing for tests to avoid external dependencies."""
    monkeypatch.setenv("PHOENIX_AUTO_SETUP", "false")


# Import template fixtures
pytest_plugins = ["tests.fixtures.template_data"]
