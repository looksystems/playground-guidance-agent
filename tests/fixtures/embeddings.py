"""Embedding-related fixtures for tests."""

import os
from pathlib import Path
from dotenv import load_dotenv
import pytest

# Load .env file from project root to get EMBEDDING_DIMENSION
# This ensures tests use the same configuration as the application
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Get embedding dimension from environment (loaded from .env)
# Default to 1536 only if not set in .env
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))


@pytest.fixture
def embedding_dimension():
    """Get the configured embedding dimension."""
    return EMBEDDING_DIMENSION


@pytest.fixture
def sample_embedding(embedding_dimension):
    """Generate a sample embedding vector with the configured dimensions."""
    return [0.1] * embedding_dimension


@pytest.fixture
def sample_embedding_batch(embedding_dimension):
    """Generate a batch of sample embedding vectors."""
    return [[float(i) * 0.1] * embedding_dimension for i in range(5)]
