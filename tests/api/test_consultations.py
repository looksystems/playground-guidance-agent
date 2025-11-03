"""Tests for consultation API endpoints.

Following TDD approach - these tests define the expected behavior
before implementation.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def sample_customer_profile():
    """Sample customer profile for testing."""
    return {
        "name": "John Smith",
        "age": 52,
        "initial_query": "I have 4 different pensions from old jobs. Can I combine them?",
    }


@pytest.fixture
def sample_consultation_id():
    """Sample consultation ID."""
    return str(uuid4())


@pytest.mark.asyncio
async def test_create_consultation(client: AsyncClient, sample_customer_profile):
    """Test creating a new consultation."""
    response = await client.post(
        "/api/consultations",
        json=sample_customer_profile,
    )

    assert response.status_code == 201
    data = response.json()

    # Check response structure
    assert "id" in data
    assert "customer_id" in data
    assert "status" in data
    assert "created_at" in data
    assert "advisor_name" in data

    # Check values
    assert data["status"] == "active"
    assert data["advisor_name"] == "Sarah"


@pytest.mark.asyncio
async def test_create_consultation_invalid_age(client: AsyncClient):
    """Test creating consultation with invalid age (validation)."""
    response = await client.post(
        "/api/consultations",
        json={
            "name": "John Smith",
            "age": 25,  # Too young for pension guidance
            "initial_query": "Test query",
        },
    )

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_get_consultation(
    client: AsyncClient, sample_consultation_id, mock_db_session
):
    """Test retrieving a consultation by ID."""
    # Mock database response
    mock_consultation = MagicMock()
    mock_consultation.id = sample_consultation_id
    mock_consultation.customer_id = str(uuid4())
    mock_consultation.advisor_id = str(uuid4())
    mock_consultation.conversation = [
        {
            "role": "system",
            "content": "Welcome",
            "timestamp": datetime.now().isoformat(),
        }
    ]
    mock_consultation.start_time = datetime.now()
    mock_consultation.end_time = None
    mock_consultation.outcome = None  # Set to None, not MagicMock
    mock_consultation.meta = {"advisor_name": "Sarah"}

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_consultation
    )

    response = await client.get(f"/api/consultations/{sample_consultation_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == sample_consultation_id
    assert "customer_id" in data
    assert "conversation" in data
    assert "status" in data


@pytest.mark.asyncio
async def test_get_consultation_not_found(client: AsyncClient, mock_db_session):
    """Test retrieving non-existent consultation."""
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    response = await client.get(f"/api/consultations/{uuid4()}")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_list_consultations(client: AsyncClient, mock_db_session):
    """Test listing consultations with pagination."""
    # Mock database response
    mock_consultations = []
    for i in range(3):
        mock_cons = MagicMock()
        mock_cons.id = str(uuid4())
        mock_cons.customer_id = str(uuid4())
        mock_cons.start_time = datetime.now()
        mock_cons.meta = {"advisor_name": "Sarah"}
        mock_consultations.append(mock_cons)

    mock_db_session.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
        mock_consultations
    )
    mock_db_session.query.return_value.count.return_value = 3

    response = await client.get("/api/consultations?skip=0&limit=10")

    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert data["total"] == 3
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_send_message(
    client: AsyncClient, sample_consultation_id, mock_db_session, mock_advisor_agent
):
    """Test sending a customer message (returns immediate acknowledgment)."""
    # Mock consultation
    mock_consultation = MagicMock()
    mock_consultation.id = sample_consultation_id
    mock_consultation.conversation = []
    mock_consultation.end_time = None

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_consultation
    )

    response = await client.post(
        f"/api/consultations/{sample_consultation_id}/messages",
        json={"content": "I'm not sure what type they are"},
    )

    assert response.status_code == 200
    data = response.json()

    assert "message_id" in data
    assert "status" in data
    assert data["status"] == "received"


@pytest.mark.asyncio
async def test_send_message_to_completed_consultation(
    client: AsyncClient, sample_consultation_id, mock_db_session
):
    """Test sending message to completed consultation (should fail)."""
    # Mock completed consultation
    mock_consultation = MagicMock()
    mock_consultation.id = sample_consultation_id
    mock_consultation.end_time = datetime.now()

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_consultation
    )

    response = await client.post(
        f"/api/consultations/{sample_consultation_id}/messages",
        json={"content": "Test message"},
    )

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "completed" in data["detail"].lower()


@pytest.mark.asyncio
async def test_end_consultation(
    client: AsyncClient, sample_consultation_id, mock_db_session
):
    """Test ending an active consultation."""
    # Mock active consultation
    mock_consultation = MagicMock()
    mock_consultation.id = sample_consultation_id
    mock_consultation.customer_id = str(uuid4())
    mock_consultation.end_time = None
    mock_consultation.start_time = datetime.now()
    mock_consultation.conversation = [
        {
            "role": "customer",
            "content": "Test",
            "timestamp": datetime.now().isoformat(),
        },
        {
            "role": "advisor",
            "content": "Response",
            "timestamp": datetime.now().isoformat(),
        },
    ]
    mock_consultation.meta = {
        "advisor_name": "Sarah",
        "compliance_scores": [0.95, 0.97],
    }

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_consultation
    )

    response = await client.post(f"/api/consultations/{sample_consultation_id}/end")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "completed"
    assert "outcome" in data
    # Consultation should be marked as ended
    assert mock_consultation.end_time is not None


@pytest.mark.asyncio
async def test_get_consultation_metrics(
    client: AsyncClient, sample_consultation_id, mock_db_session
):
    """Test getting metrics for a consultation."""
    # Mock consultation with outcome
    mock_consultation = MagicMock()
    mock_consultation.id = sample_consultation_id
    mock_consultation.conversation = [{"role": "customer"}] * 10
    mock_consultation.outcome = {
        "customer_satisfaction": 8.5,
        "comprehension": 9.0,
        "fca_compliant": True,
    }
    mock_consultation.meta = {"compliance_scores": [0.95, 0.97, 0.96]}

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_consultation
    )

    response = await client.get(
        f"/api/consultations/{sample_consultation_id}/metrics"
    )

    assert response.status_code == 200
    data = response.json()

    assert "message_count" in data
    assert "avg_compliance_score" in data
    assert "customer_satisfaction" in data
    assert data["message_count"] == 10
