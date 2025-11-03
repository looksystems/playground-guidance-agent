"""Embedding utilities using LiteLLM for provider flexibility."""

import os
from typing import Optional

from litellm import embedding
from dotenv import load_dotenv

from guidance_agent.core.provider_config import get_embedding_dimension as get_dimension_from_config

# Load environment variables
load_dotenv()


def embed(
    text: str | list[str],
    model: Optional[str] = None,
    dimensions: Optional[int] = None,
) -> list[float] | list[list[float]]:
    """Generate embeddings using LiteLLM (supports multiple providers).

    Args:
        text: Single text string or list of texts to embed
        model: Model to use, defaults to LITELLM_MODEL_EMBEDDINGS env var
        dimensions: Embedding dimensions, defaults to EMBEDDING_DIMENSION env var

    Returns:
        Single embedding vector or list of embedding vectors

    Examples:
        >>> embed("Hello world")
        [0.1, 0.2, ..., 0.9]

        >>> embed(["Hello", "World"])
        [[0.1, 0.2, ...], [0.3, 0.4, ...]]
    """
    if model is None:
        model = os.getenv("LITELLM_MODEL_EMBEDDINGS", "text-embedding-3-small")

    if dimensions is None:
        dimensions = int(os.getenv("EMBEDDING_DIMENSION", "1536"))

    # Ensure text is a list for the API
    is_single = isinstance(text, str)
    texts = [text] if is_single else text

    # Generate embeddings
    response = embedding(model=model, input=texts, dimensions=dimensions)

    # Extract embeddings from response
    embeddings = [data["embedding"] for data in response.data]

    # Return single embedding if input was single string
    return embeddings[0] if is_single else embeddings


def embed_batch(
    texts: list[str],
    model: Optional[str] = None,
    dimensions: Optional[int] = None,
    batch_size: int = 100,
) -> list[list[float]]:
    """Generate embeddings for a batch of texts with batching support.

    Useful for processing large numbers of texts efficiently.

    Args:
        texts: List of texts to embed
        model: Model to use, defaults to LITELLM_MODEL_EMBEDDINGS env var
        dimensions: Embedding dimensions
        batch_size: Number of texts to process per API call

    Returns:
        List of embedding vectors
    """
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        batch_embeddings = embed(batch, model=model, dimensions=dimensions)
        all_embeddings.extend(batch_embeddings)

    return all_embeddings


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculate cosine similarity between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Cosine similarity score between -1 and 1
    """
    if len(vec1) != len(vec2):
        raise ValueError(f"Vectors must have same length: {len(vec1)} != {len(vec2)}")

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sum(a * a for a in vec1) ** 0.5
    magnitude2 = sum(b * b for b in vec2) ** 0.5

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def get_embedding_dimension(model: Optional[str] = None) -> int:
    """Get the embedding dimension for a model.

    Args:
        model: Model name, defaults to LITELLM_MODEL_EMBEDDINGS env var

    Returns:
        Embedding dimension
    """
    if model is None:
        model = os.getenv("LITELLM_MODEL_EMBEDDINGS", "text-embedding-3-small")

    # Use centralized provider_config for dimension lookup
    return get_dimension_from_config(model)
