"""Tests for admin memories API endpoints."""

import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock
from datetime import datetime, timezone, timedelta
from uuid import uuid4


@pytest.fixture
def admin_headers():
    """Admin authorization headers."""
    return {"Authorization": "Bearer admin-token"}


@pytest.fixture
def sample_memory_observation():
    """Sample observation memory."""
    memory = MagicMock()
    memory.id = uuid4()
    memory.description = "Customer expressed concern about pension consolidation costs"
    memory.timestamp = datetime.now(timezone.utc) - timedelta(hours=2)
    memory.last_accessed = datetime.now(timezone.utc) - timedelta(minutes=30)
    memory.importance = 0.85
    memory.memory_type = "observation"
    memory.embedding = [0.1] * 1536  # Mock embedding vector
    memory.meta = {"consultation_id": str(uuid4()), "topic": "consolidation"}
    memory.created_at = datetime.now(timezone.utc) - timedelta(hours=2)
    return memory


@pytest.fixture
def sample_memory_reflection():
    """Sample reflection memory."""
    memory = MagicMock()
    memory.id = uuid4()
    memory.description = "Customers often need reassurance about consolidation benefits"
    memory.timestamp = datetime.now(timezone.utc) - timedelta(days=1)
    memory.last_accessed = datetime.now(timezone.utc) - timedelta(hours=5)
    memory.importance = 0.65
    memory.memory_type = "reflection"
    memory.embedding = [0.2] * 1536
    memory.meta = {"pattern_count": 5}
    memory.created_at = datetime.now(timezone.utc) - timedelta(days=1)
    return memory


@pytest.fixture
def sample_memory_plan():
    """Sample plan memory."""
    memory = MagicMock()
    memory.id = uuid4()
    memory.description = "Review consolidation guidance for customers over 55"
    memory.timestamp = datetime.now(timezone.utc) - timedelta(hours=12)
    memory.last_accessed = datetime.now(timezone.utc) - timedelta(hours=12)
    memory.importance = 0.35
    memory.memory_type = "plan"
    memory.embedding = None  # No embedding
    memory.meta = {"priority": "low"}
    memory.created_at = datetime.now(timezone.utc) - timedelta(hours=12)
    return memory


@pytest.mark.asyncio
async def test_list_memories_success(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_memory_observation,
    sample_memory_reflection,
    sample_memory_plan
):
    """Test listing memories successfully."""
    # Setup mock database response
    mock_db_session.all.return_value = [
        sample_memory_observation,
        sample_memory_reflection,
        sample_memory_plan
    ]
    mock_db_session.count.return_value = 3

    response = await client.get("/api/admin/memories", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()

    # Check pagination structure
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "pages" in data

    # Check data
    assert data["total"] == 3
    assert len(data["items"]) == 3
    assert data["page"] == 1
    assert data["page_size"] == 20

    # Check first memory structure
    first_memory = data["items"][0]
    assert "id" in first_memory
    assert "description" in first_memory
    assert "timestamp" in first_memory
    assert "last_accessed" in first_memory
    assert "importance" in first_memory
    assert "memory_type" in first_memory
    assert "has_embedding" in first_memory
    assert "meta" in first_memory
    assert "created_at" in first_memory

    # Check memory types
    memory_types = [m["memory_type"] for m in data["items"]]
    assert "observation" in memory_types
    assert "reflection" in memory_types
    assert "plan" in memory_types


@pytest.mark.asyncio
async def test_list_memories_no_auth(client: AsyncClient):
    """Test listing memories without admin auth."""
    response = await client.get("/api/admin/memories")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_memories_with_pagination(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_memory_observation
):
    """Test listing memories with pagination parameters."""
    # Setup mock for 25 memories
    memories = [sample_memory_observation] * 25
    mock_db_session.all.return_value = memories[:10]  # Second page
    mock_db_session.count.return_value = 25

    response = await client.get(
        "/api/admin/memories?page=2&page_size=10",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 25
    assert data["page"] == 2
    assert data["page_size"] == 10
    assert data["pages"] == 3
    assert len(data["items"]) == 10


@pytest.mark.asyncio
async def test_list_memories_filter_by_memory_type(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_memory_observation
):
    """Test filtering memories by memory_type."""
    mock_db_session.all.return_value = [sample_memory_observation]
    mock_db_session.count.return_value = 1

    response = await client.get(
        "/api/admin/memories?memory_type=observation",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["memory_type"] == "observation"

    # Verify filter was applied to database query
    mock_db_session.filter.assert_called()


@pytest.mark.asyncio
async def test_list_memories_filter_by_importance_range(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_memory_observation
):
    """Test filtering memories by importance range."""
    mock_db_session.all.return_value = [sample_memory_observation]
    mock_db_session.count.return_value = 1

    response = await client.get(
        "/api/admin/memories?min_importance=0.7&max_importance=0.9",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    first_memory = data["items"][0]
    assert first_memory["importance"] >= 0.7
    assert first_memory["importance"] <= 0.9

    # Verify filter was applied
    mock_db_session.filter.assert_called()


@pytest.mark.asyncio
async def test_list_memories_sort_by_importance(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_memory_observation,
    sample_memory_reflection,
    sample_memory_plan
):
    """Test sorting memories by importance."""
    # Return memories sorted by importance descending
    mock_db_session.all.return_value = [
        sample_memory_observation,  # 0.85
        sample_memory_reflection,   # 0.65
        sample_memory_plan          # 0.35
    ]
    mock_db_session.count.return_value = 3

    response = await client.get(
        "/api/admin/memories?sort_by=importance&sort_order=desc",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Verify order is descending by importance
    importances = [m["importance"] for m in data["items"]]
    assert importances == sorted(importances, reverse=True)

    # Verify order_by was called on database
    mock_db_session.order_by.assert_called()


@pytest.mark.asyncio
async def test_list_memories_sort_by_timestamp(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_memory_observation
):
    """Test sorting memories by timestamp."""
    mock_db_session.all.return_value = [sample_memory_observation]
    mock_db_session.count.return_value = 1

    response = await client.get(
        "/api/admin/memories?sort_by=timestamp&sort_order=asc",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    mock_db_session.order_by.assert_called()


@pytest.mark.asyncio
async def test_list_memories_sort_by_last_accessed(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_memory_observation
):
    """Test sorting memories by last_accessed."""
    mock_db_session.all.return_value = [sample_memory_observation]
    mock_db_session.count.return_value = 1

    response = await client.get(
        "/api/admin/memories?sort_by=last_accessed&sort_order=desc",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    mock_db_session.order_by.assert_called()


@pytest.mark.asyncio
async def test_list_memories_date_range_filter(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_memory_observation
):
    """Test filtering memories by date range."""
    mock_db_session.all.return_value = [sample_memory_observation]
    mock_db_session.count.return_value = 1

    from_date = (datetime.now(timezone.utc) - timedelta(days=7)).date().isoformat()
    to_date = datetime.now(timezone.utc).date().isoformat()

    response = await client.get(
        f"/api/admin/memories?from_date={from_date}&to_date={to_date}",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    mock_db_session.filter.assert_called()


@pytest.mark.asyncio
async def test_list_memories_empty_result(
    client: AsyncClient,
    admin_headers,
    mock_db_session
):
    """Test listing memories with no results."""
    mock_db_session.all.return_value = []
    mock_db_session.count.return_value = 0

    response = await client.get("/api/admin/memories", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 0
    assert len(data["items"]) == 0
    assert data["pages"] == 0


@pytest.mark.asyncio
async def test_list_memories_invalid_memory_type(
    client: AsyncClient,
    admin_headers
):
    """Test filtering with invalid memory_type."""
    response = await client.get(
        "/api/admin/memories?memory_type=invalid_type",
        headers=admin_headers
    )

    # Should return validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_memories_invalid_importance_range(
    client: AsyncClient,
    admin_headers
):
    """Test filtering with invalid importance range."""
    response = await client.get(
        "/api/admin/memories?min_importance=1.5",  # Max is 1.0
        headers=admin_headers
    )

    # Should return validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_memories_invalid_sort_by(
    client: AsyncClient,
    admin_headers
):
    """Test sorting with invalid sort_by field."""
    response = await client.get(
        "/api/admin/memories?sort_by=invalid_field",
        headers=admin_headers
    )

    # Should return validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_memories_max_page_size(
    client: AsyncClient,
    admin_headers,
    mock_db_session
):
    """Test that page_size over 100 returns validation error."""
    mock_db_session.all.return_value = []
    mock_db_session.count.return_value = 0

    response = await client.get(
        "/api/admin/memories?page_size=500",  # Over max
        headers=admin_headers
    )

    # Should return validation error for page_size > 100
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_memory_by_id_success(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_memory_observation
):
    """Test getting a specific memory by ID."""
    mock_db_session.first.return_value = sample_memory_observation

    memory_id = str(sample_memory_observation.id)
    response = await client.get(
        f"/api/admin/memories/{memory_id}",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Check all fields are present
    assert data["id"] == memory_id
    assert data["description"] == sample_memory_observation.description
    assert data["importance"] == sample_memory_observation.importance
    assert data["memory_type"] == "observation"
    assert data["has_embedding"] is True
    assert isinstance(data["meta"], dict)
    assert "timestamp" in data
    assert "last_accessed" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_memory_by_id_not_found(
    client: AsyncClient,
    admin_headers,
    mock_db_session
):
    """Test getting a non-existent memory."""
    mock_db_session.first.return_value = None

    fake_id = str(uuid4())
    response = await client.get(
        f"/api/admin/memories/{fake_id}",
        headers=admin_headers
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_memory_by_id_no_auth(client: AsyncClient):
    """Test getting memory without admin auth."""
    fake_id = str(uuid4())
    response = await client.get(f"/api/admin/memories/{fake_id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_memory_by_id_invalid_uuid(
    client: AsyncClient,
    admin_headers
):
    """Test getting memory with invalid UUID."""
    response = await client.get(
        "/api/admin/memories/not-a-uuid",
        headers=admin_headers
    )

    # Should return validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_memories_has_embedding_indicator(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_memory_observation,
    sample_memory_plan
):
    """Test that has_embedding field correctly indicates embedding presence."""
    mock_db_session.all.return_value = [
        sample_memory_observation,  # Has embedding
        sample_memory_plan          # No embedding
    ]
    mock_db_session.count.return_value = 2

    response = await client.get("/api/admin/memories", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()

    # First memory should have embedding
    assert data["items"][0]["has_embedding"] is True

    # Second memory should not have embedding
    assert data["items"][1]["has_embedding"] is False


@pytest.mark.asyncio
async def test_list_memories_multiple_filters(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_memory_observation
):
    """Test combining multiple filters."""
    mock_db_session.all.return_value = [sample_memory_observation]
    mock_db_session.count.return_value = 1

    response = await client.get(
        "/api/admin/memories?memory_type=observation&min_importance=0.5&sort_by=importance&sort_order=desc",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["memory_type"] == "observation"
    assert data["items"][0]["importance"] >= 0.5

    # Verify multiple filters were applied
    assert mock_db_session.filter.call_count >= 1


@pytest.mark.asyncio
async def test_list_memories_reflection_type_filter(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_memory_reflection
):
    """Test filtering by reflection memory type."""
    mock_db_session.all.return_value = [sample_memory_reflection]
    mock_db_session.count.return_value = 1

    response = await client.get(
        "/api/admin/memories?memory_type=reflection",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["memory_type"] == "reflection"


@pytest.mark.asyncio
async def test_list_memories_plan_type_filter(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_memory_plan
):
    """Test filtering by plan memory type."""
    mock_db_session.all.return_value = [sample_memory_plan]
    mock_db_session.count.return_value = 1

    response = await client.get(
        "/api/admin/memories?memory_type=plan",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["memory_type"] == "plan"
