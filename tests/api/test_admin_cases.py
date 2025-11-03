"""Tests for admin cases API endpoints."""

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
def sample_case_consolidation():
    """Sample consolidation case."""
    case = MagicMock()
    case.id = uuid4()
    case.task_type = "pension_consolidation"
    case.customer_situation = "Customer has 3 pensions from previous employers and wants to simplify management"
    case.guidance_provided = "Explained consolidation benefits, fees, and regulatory requirements"
    case.outcome = {
        "customer_satisfaction": 9.0,
        "comprehension": 8.5,
        "decision_made": True,
        "follow_up_required": False
    }
    case.embedding = [0.1] * 1536  # Mock embedding
    case.meta = {"consultation_id": str(uuid4()), "duration_minutes": 45}
    case.created_at = datetime.now(timezone.utc) - timedelta(days=5)
    return case


@pytest.fixture
def sample_case_drawdown():
    """Sample drawdown case."""
    case = MagicMock()
    case.id = uuid4()
    case.task_type = "pension_drawdown"
    case.customer_situation = "Customer aged 58 considering early retirement and pension drawdown options"
    case.guidance_provided = "Discussed drawdown strategies, tax implications, and sustainability of income"
    case.outcome = {
        "customer_satisfaction": 8.5,
        "comprehension": 9.0,
        "decision_made": False,
        "follow_up_required": True
    }
    case.embedding = [0.2] * 1536
    case.meta = {"consultation_id": str(uuid4()), "risk_level": "medium"}
    case.created_at = datetime.now(timezone.utc) - timedelta(days=2)
    return case


@pytest.fixture
def sample_case_transfer():
    """Sample transfer case."""
    case = MagicMock()
    case.id = uuid4()
    case.task_type = "pension_transfer"
    case.customer_situation = "Customer wants to transfer defined benefit pension to defined contribution"
    case.guidance_provided = "Explained risks of DB to DC transfer, regulatory requirements, and alternative options"
    case.outcome = {
        "customer_satisfaction": 7.5,
        "comprehension": 7.0,
        "decision_made": False,
        "follow_up_required": True,
        "high_risk": True
    }
    case.embedding = None  # No embedding
    case.meta = {"consultation_id": str(uuid4()), "requires_specialist": True}
    case.created_at = datetime.now(timezone.utc) - timedelta(hours=6)
    return case


@pytest.mark.asyncio
async def test_list_cases_success(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_case_consolidation,
    sample_case_drawdown,
    sample_case_transfer
):
    """Test listing cases successfully."""
    # Setup mock database response
    mock_db_session.all.return_value = [
        sample_case_consolidation,
        sample_case_drawdown,
        sample_case_transfer
    ]
    mock_db_session.count.return_value = 3

    response = await client.get("/api/admin/cases", headers=admin_headers)

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

    # Check first case structure
    first_case = data["items"][0]
    assert "id" in first_case
    assert "task_type" in first_case
    assert "customer_situation" in first_case
    assert "guidance_provided" in first_case
    assert "outcome" in first_case
    assert "has_embedding" in first_case
    assert "meta" in first_case
    assert "created_at" in first_case

    # Check task types
    task_types = [c["task_type"] for c in data["items"]]
    assert "pension_consolidation" in task_types
    assert "pension_drawdown" in task_types
    assert "pension_transfer" in task_types


@pytest.mark.asyncio
async def test_list_cases_no_auth(client: AsyncClient):
    """Test listing cases without admin auth."""
    response = await client.get("/api/admin/cases")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_cases_with_pagination(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_case_consolidation
):
    """Test listing cases with pagination parameters."""
    # Setup mock for 25 cases
    cases = [sample_case_consolidation] * 25
    mock_db_session.all.return_value = cases[:10]  # Second page
    mock_db_session.count.return_value = 25

    response = await client.get(
        "/api/admin/cases?page=2&page_size=10",
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
async def test_list_cases_filter_by_task_type(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_case_consolidation
):
    """Test filtering cases by task_type."""
    mock_db_session.all.return_value = [sample_case_consolidation]
    mock_db_session.count.return_value = 1

    response = await client.get(
        "/api/admin/cases?task_type=pension_consolidation",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["task_type"] == "pension_consolidation"

    # Verify filter was applied to database query
    mock_db_session.filter.assert_called()


@pytest.mark.asyncio
async def test_list_cases_date_range_filter(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_case_consolidation
):
    """Test filtering cases by date range."""
    mock_db_session.all.return_value = [sample_case_consolidation]
    mock_db_session.count.return_value = 1

    from_date = (datetime.now(timezone.utc) - timedelta(days=7)).date().isoformat()
    to_date = datetime.now(timezone.utc).date().isoformat()

    response = await client.get(
        f"/api/admin/cases?from_date={from_date}&to_date={to_date}",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    mock_db_session.filter.assert_called()


@pytest.mark.asyncio
async def test_list_cases_empty_result(
    client: AsyncClient,
    admin_headers,
    mock_db_session
):
    """Test listing cases with no results."""
    mock_db_session.all.return_value = []
    mock_db_session.count.return_value = 0

    response = await client.get("/api/admin/cases", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 0
    assert len(data["items"]) == 0
    assert data["pages"] == 0


@pytest.mark.asyncio
async def test_list_cases_max_page_size(
    client: AsyncClient,
    admin_headers,
    mock_db_session
):
    """Test that page_size over 100 returns validation error."""
    mock_db_session.all.return_value = []
    mock_db_session.count.return_value = 0

    response = await client.get(
        "/api/admin/cases?page_size=500",  # Over max
        headers=admin_headers
    )

    # Should return validation error for page_size > 100
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_case_by_id_success(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_case_consolidation
):
    """Test getting a specific case by ID."""
    mock_db_session.first.return_value = sample_case_consolidation

    case_id = str(sample_case_consolidation.id)
    response = await client.get(
        f"/api/admin/cases/{case_id}",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Check all fields are present
    assert data["id"] == case_id
    assert data["task_type"] == sample_case_consolidation.task_type
    assert data["customer_situation"] == sample_case_consolidation.customer_situation
    assert data["guidance_provided"] == sample_case_consolidation.guidance_provided
    assert isinstance(data["outcome"], dict)
    assert data["has_embedding"] is True
    assert isinstance(data["meta"], dict)
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_case_by_id_not_found(
    client: AsyncClient,
    admin_headers,
    mock_db_session
):
    """Test getting a non-existent case."""
    mock_db_session.first.return_value = None

    fake_id = str(uuid4())
    response = await client.get(
        f"/api/admin/cases/{fake_id}",
        headers=admin_headers
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_case_by_id_no_auth(client: AsyncClient):
    """Test getting case without admin auth."""
    fake_id = str(uuid4())
    response = await client.get(f"/api/admin/cases/{fake_id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_case_by_id_invalid_uuid(
    client: AsyncClient,
    admin_headers
):
    """Test getting case with invalid UUID."""
    response = await client.get(
        "/api/admin/cases/not-a-uuid",
        headers=admin_headers
    )

    # Should return validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_cases_has_embedding_indicator(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_case_consolidation,
    sample_case_transfer
):
    """Test that has_embedding field correctly indicates embedding presence."""
    mock_db_session.all.return_value = [
        sample_case_consolidation,  # Has embedding
        sample_case_transfer         # No embedding
    ]
    mock_db_session.count.return_value = 2

    response = await client.get("/api/admin/cases", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()

    # First case should have embedding
    assert data["items"][0]["has_embedding"] is True

    # Second case should not have embedding
    assert data["items"][1]["has_embedding"] is False


@pytest.mark.asyncio
async def test_list_cases_outcome_is_dict(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_case_consolidation
):
    """Test that outcome field is returned as dictionary."""
    mock_db_session.all.return_value = [sample_case_consolidation]
    mock_db_session.count.return_value = 1

    response = await client.get("/api/admin/cases", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()

    # Check outcome is dict with expected fields
    outcome = data["items"][0]["outcome"]
    assert isinstance(outcome, dict)
    assert "customer_satisfaction" in outcome
    assert "comprehension" in outcome
    assert "decision_made" in outcome


@pytest.mark.asyncio
async def test_list_cases_multiple_task_types(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_case_consolidation,
    sample_case_drawdown
):
    """Test filtering by different task types."""
    # Test pension_consolidation
    mock_db_session.all.return_value = [sample_case_consolidation]
    mock_db_session.count.return_value = 1

    response = await client.get(
        "/api/admin/cases?task_type=pension_consolidation",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["task_type"] == "pension_consolidation"

    # Test pension_drawdown
    mock_db_session.all.return_value = [sample_case_drawdown]
    mock_db_session.count.return_value = 1

    response = await client.get(
        "/api/admin/cases?task_type=pension_drawdown",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["task_type"] == "pension_drawdown"


@pytest.mark.asyncio
async def test_list_cases_combined_filters(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_case_consolidation
):
    """Test combining task_type and date filters."""
    mock_db_session.all.return_value = [sample_case_consolidation]
    mock_db_session.count.return_value = 1

    from_date = (datetime.now(timezone.utc) - timedelta(days=7)).date().isoformat()
    to_date = datetime.now(timezone.utc).date().isoformat()

    response = await client.get(
        f"/api/admin/cases?task_type=pension_consolidation&from_date={from_date}&to_date={to_date}",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["task_type"] == "pension_consolidation"

    # Verify multiple filters were applied
    assert mock_db_session.filter.call_count >= 1


@pytest.mark.asyncio
async def test_get_case_outcome_structure(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_case_consolidation
):
    """Test that case detail includes full outcome structure."""
    mock_db_session.first.return_value = sample_case_consolidation

    case_id = str(sample_case_consolidation.id)
    response = await client.get(
        f"/api/admin/cases/{case_id}",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Verify outcome structure
    outcome = data["outcome"]
    assert isinstance(outcome, dict)
    assert outcome["customer_satisfaction"] == 9.0
    assert outcome["comprehension"] == 8.5
    assert outcome["decision_made"] is True
    assert outcome["follow_up_required"] is False


@pytest.mark.asyncio
async def test_list_cases_meta_structure(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_case_consolidation
):
    """Test that meta field is returned as dictionary."""
    mock_db_session.all.return_value = [sample_case_consolidation]
    mock_db_session.count.return_value = 1

    response = await client.get("/api/admin/cases", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()

    # Check meta is dict
    meta = data["items"][0]["meta"]
    assert isinstance(meta, dict)
    assert "consultation_id" in meta
