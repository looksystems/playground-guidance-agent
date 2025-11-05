"""Memory-related fixtures for tests."""

import pytest
from datetime import datetime
from uuid import uuid4

from guidance_agent.core.memory import MemoryNode, MemoryStream
from guidance_agent.core.types import MemoryType
from tests.fixtures.embeddings import EMBEDDING_DIMENSION


@pytest.fixture
def sample_memory_node():
    """Create a sample memory node for testing."""
    return MemoryNode(
        memory_id=uuid4(),
        description="Customer asked about pension withdrawal options",
        timestamp=datetime.now(),
        importance=0.7,
        memory_type=MemoryType.OBSERVATION,
        embedding=[0.1] * EMBEDDING_DIMENSION,
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
            embedding=[float(i)] * EMBEDDING_DIMENSION,
        )
        stream.add(memory)

    # Add a reflection
    reflection = MemoryNode(
        description="Customer seems uncertain about risk tolerance",
        importance=0.8,
        memory_type=MemoryType.REFLECTION,
        embedding=[0.5] * EMBEDDING_DIMENSION,
    )
    stream.add(reflection)

    return stream
