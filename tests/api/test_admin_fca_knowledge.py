"""Tests for admin FCA Knowledge API endpoints."""

import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock
from uuid import uuid4
from datetime import datetime, timedelta


@pytest.fixture
def admin_headers():
    """Admin authorization headers."""
    return {"Authorization": "Bearer admin-token"}


@pytest.fixture
def mock_fca_knowledge():
    """Mock FCA Knowledge records."""
    from guidance_agent.core.database import FCAKnowledge

    base_date = datetime.now()

    records = []
    for i in range(25):
        record = FCAKnowledge()
        record.id = uuid4()
        record.content = f"FCA Knowledge content {i+1}"
        record.source = f"FCA Handbook Section {i+1}" if i % 2 == 0 else None
        record.category = "Risk Assessment" if i % 3 == 0 else "Documentation" if i % 3 == 1 else "Client Suitability"
        record.embedding = [0.1] * 1536 if i % 2 == 0 else None  # Some have embeddings
        record.meta = {"tag": f"tag{i}"}
        record.created_at = base_date - timedelta(days=i)
        records.append(record)

    return records


@pytest.mark.asyncio
async def test_list_fca_knowledge_default_params(
    client_with_real_db: AsyncClient, admin_headers
):
    """Test listing FCA knowledge with default parameters."""
    response = await client_with_real_db.get(
        "/api/admin/fca-knowledge",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Check pagination structure
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "pages" in data

    # Check defaults
    assert data["page"] == 1
    assert data["page_size"] == 20

    # Check data types
    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)
    assert isinstance(data["pages"], int)


@pytest.mark.asyncio
async def test_list_fca_knowledge_with_category_filter(
    client_with_real_db: AsyncClient, admin_headers
):
    """Test listing FCA knowledge with category filter."""
    response = await client_with_real_db.get(
        "/api/admin/fca-knowledge",
        headers=admin_headers,
        params={"category": "Risk Assessment"}
    )

    assert response.status_code == 200
    data = response.json()

    # If there are results, check they match the filter
    if data["items"]:
        for item in data["items"]:
            assert item["category"] == "Risk Assessment"


@pytest.mark.asyncio
async def test_list_fca_knowledge_with_search(
    client_with_real_db: AsyncClient, admin_headers
):
    """Test listing FCA knowledge with text search."""
    response = await client_with_real_db.get(
        "/api/admin/fca-knowledge",
        headers=admin_headers,
        params={"search": "compliance"}
    )

    assert response.status_code == 200
    data = response.json()

    # Should return valid pagination structure
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_list_fca_knowledge_with_date_range(
    client_with_real_db: AsyncClient, admin_headers
):
    """Test listing FCA knowledge with date range filter."""
    from_date = (datetime.now() - timedelta(days=30)).date().isoformat()
    to_date = datetime.now().date().isoformat()

    response = await client_with_real_db.get(
        "/api/admin/fca-knowledge",
        headers=admin_headers,
        params={"from_date": from_date, "to_date": to_date}
    )

    assert response.status_code == 200
    data = response.json()

    # Should return valid pagination structure
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_list_fca_knowledge_pagination(
    client_with_real_db: AsyncClient, admin_headers
):
    """Test FCA knowledge pagination."""
    # Test page 1 with page_size 5
    response1 = await client_with_real_db.get(
        "/api/admin/fca-knowledge",
        headers=admin_headers,
        params={"page": 1, "page_size": 5}
    )

    assert response1.status_code == 200
    data1 = response1.json()

    assert data1["page"] == 1
    assert data1["page_size"] == 5

    # Test page 2
    response2 = await client_with_real_db.get(
        "/api/admin/fca-knowledge",
        headers=admin_headers,
        params={"page": 2, "page_size": 5}
    )

    assert response2.status_code == 200
    data2 = response2.json()

    assert data2["page"] == 2
    assert data2["page_size"] == 5


@pytest.mark.asyncio
async def test_list_fca_knowledge_max_page_size(
    client_with_real_db: AsyncClient, admin_headers
):
    """Test FCA knowledge max page size limit."""
    # Try to request more than max (100) - should return validation error
    response = await client_with_real_db.get(
        "/api/admin/fca-knowledge",
        headers=admin_headers,
        params={"page_size": 150}
    )

    # Should return 422 validation error for exceeding max
    assert response.status_code == 422

    # Test with max allowed value (100)
    response_max = await client_with_real_db.get(
        "/api/admin/fca-knowledge",
        headers=admin_headers,
        params={"page_size": 100}
    )

    assert response_max.status_code == 200
    data = response_max.json()
    assert data["page_size"] == 100


@pytest.mark.asyncio
async def test_list_fca_knowledge_empty_results(
    client_with_real_db: AsyncClient, admin_headers
):
    """Test FCA knowledge with filter that returns no results."""
    response = await client_with_real_db.get(
        "/api/admin/fca-knowledge",
        headers=admin_headers,
        params={"category": "NonexistentCategory12345"}
    )

    assert response.status_code == 200
    data = response.json()

    # Should return empty list but valid structure
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_fca_knowledge_combined_filters(
    client_with_real_db: AsyncClient, admin_headers
):
    """Test FCA knowledge with multiple filters combined."""
    from_date = (datetime.now() - timedelta(days=30)).date().isoformat()

    response = await client_with_real_db.get(
        "/api/admin/fca-knowledge",
        headers=admin_headers,
        params={
            "category": "Risk Assessment",
            "search": "assessment",
            "from_date": from_date,
            "page_size": 10
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert data["page_size"] == 10


@pytest.mark.asyncio
async def test_list_fca_knowledge_no_auth(client: AsyncClient):
    """Test listing FCA knowledge without admin auth."""
    response = await client.get("/api/admin/fca-knowledge")

    # Should require authentication
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_fca_knowledge_by_id_success(
    client_with_real_db: AsyncClient, admin_headers
):
    """Test getting a single FCA knowledge record by ID."""
    # First, get a list to find a valid ID
    list_response = await client_with_real_db.get(
        "/api/admin/fca-knowledge",
        headers=admin_headers,
        params={"page_size": 1}
    )

    assert list_response.status_code == 200
    list_data = list_response.json()

    # If we have at least one item, test detail endpoint
    if list_data["items"]:
        item_id = list_data["items"][0]["id"]

        response = await client_with_real_db.get(
            f"/api/admin/fca-knowledge/{item_id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check required fields
        assert "id" in data
        assert "content" in data
        assert "category" in data
        assert "has_embedding" in data
        assert "meta" in data
        assert "created_at" in data

        # Check data types
        assert isinstance(data["id"], str)
        assert isinstance(data["content"], str)
        assert isinstance(data["category"], str)
        assert isinstance(data["has_embedding"], bool)
        assert isinstance(data["meta"], dict)
        assert isinstance(data["created_at"], str)

        # Optional fields
        if data.get("source"):
            assert isinstance(data["source"], str)


@pytest.mark.asyncio
async def test_get_fca_knowledge_by_id_not_found(
    client_with_real_db: AsyncClient, admin_headers
):
    """Test getting FCA knowledge with invalid ID returns 404."""
    invalid_id = str(uuid4())

    response = await client_with_real_db.get(
        f"/api/admin/fca-knowledge/{invalid_id}",
        headers=admin_headers
    )

    # Should return 404
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_fca_knowledge_by_id_invalid_uuid(
    client_with_real_db: AsyncClient, admin_headers
):
    """Test getting FCA knowledge with malformed UUID."""
    response = await client_with_real_db.get(
        "/api/admin/fca-knowledge/not-a-uuid",
        headers=admin_headers
    )

    # Should return 422 (validation error)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_fca_knowledge_by_id_no_auth(client: AsyncClient):
    """Test getting FCA knowledge by ID without admin auth."""
    response = await client.get(f"/api/admin/fca-knowledge/{uuid4()}")

    # Should require authentication
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_fca_knowledge_has_embedding_field(
    client_with_real_db: AsyncClient, admin_headers
):
    """Test that has_embedding field is correctly set."""
    response = await client_with_real_db.get(
        "/api/admin/fca-knowledge",
        headers=admin_headers,
        params={"page_size": 20}
    )

    assert response.status_code == 200
    data = response.json()

    # Check that all items have the has_embedding field
    for item in data["items"]:
        assert "has_embedding" in item
        assert isinstance(item["has_embedding"], bool)


@pytest.mark.asyncio
async def test_list_fca_knowledge_response_structure(
    client_with_real_db: AsyncClient, admin_headers
):
    """Test that list response has correct structure."""
    response = await client_with_real_db.get(
        "/api/admin/fca-knowledge",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Check required fields in response
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "pages" in data

    # Check that each item has required fields
    for item in data["items"]:
        assert "id" in item
        assert "content" in item
        assert "category" in item
        assert "has_embedding" in item
        assert "meta" in item
        assert "created_at" in item
        # source is optional
