"""Tests for admin API endpoints."""

import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime, timedelta
from unittest.mock import MagicMock


@pytest.fixture
def admin_headers():
    """Admin authorization headers."""
    return {"Authorization": "Bearer admin-token"}


@pytest.mark.asyncio
async def test_list_consultations_with_filters(
    client: AsyncClient, admin_headers, mock_db_session
):
    """Test listing consultations with admin filters."""
    # Mock consultations
    mock_consultations = []
    for i in range(5):
        mock_cons = MagicMock()
        mock_cons.id = str(uuid4())
        mock_cons.customer_id = str(uuid4())
        mock_cons.start_time = datetime.now() - timedelta(days=i)
        mock_cons.end_time = datetime.now() - timedelta(days=i, hours=1) if i > 2 else None
        mock_cons.meta = {
            "advisor_name": "Sarah",
            "compliance_scores": [0.95, 0.97],
        }
        mock_cons.outcome = {"fca_compliant": True} if i > 2 else None
        mock_consultations.append(mock_cons)

    mock_db_session.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
        mock_consultations
    )
    mock_db_session.query.return_value.filter.return_value.count.return_value = 5

    # Test with status filter
    response = await client.get(
        "/api/admin/consultations?status=active", headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_list_consultations_no_auth(client: AsyncClient, mock_db_session):
    """Test listing consultations without admin auth."""
    response = await client.get("/api/admin/consultations")

    # Should require authentication
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_consultation_review(
    client: AsyncClient, admin_headers, mock_db_session
):
    """Test getting detailed consultation for review."""
    consultation_id = str(uuid4())

    # Mock consultation with full details
    mock_consultation = MagicMock()
    mock_consultation.id = consultation_id
    mock_consultation.customer_id = str(uuid4())
    mock_consultation.conversation = [
        {
            "role": "customer",
            "content": "I have 4 pensions",
            "timestamp": datetime.now().isoformat(),
        },
        {
            "role": "advisor",
            "content": "Let me help you understand...",
            "timestamp": datetime.now().isoformat(),
            "compliance_score": 0.97,
            "compliance_confidence": 0.98,
        },
    ]
    mock_consultation.outcome = {
        "customer_satisfaction": 8.5,
        "comprehension": 9.0,
        "fca_compliant": True,
    }
    mock_consultation.start_time = datetime.now()
    mock_consultation.end_time = datetime.now() + timedelta(minutes=15)
    mock_consultation.meta = {
        "advisor_name": "Sarah",
        "customer_name": "John",
        "customer_age": 52,
    }

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_consultation
    )

    response = await client.get(
        f"/api/admin/consultations/{consultation_id}", headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Check detailed structure
    assert data["id"] == consultation_id
    assert "conversation" in data
    assert "outcome" in data
    assert "metrics" in data

    # Check metrics calculation
    metrics = data["metrics"]
    assert "message_count" in metrics
    assert "avg_compliance_score" in metrics
    assert "duration_minutes" in metrics


@pytest.mark.asyncio
async def test_get_compliance_metrics(
    client: AsyncClient, admin_headers, mock_db_session
):
    """Test getting overall compliance metrics."""
    # Mock consultations with various compliance scores
    mock_consultations = []
    for i in range(10):
        mock_cons = MagicMock()
        mock_cons.id = str(uuid4())
        mock_cons.meta = {
            "compliance_scores": [0.95, 0.97, 0.96],
        }
        mock_cons.outcome = {
            "fca_compliant": True if i < 9 else False,
            "customer_satisfaction": 8.0 + (i * 0.1),
        }
        mock_consultations.append(mock_cons)

    mock_db_session.query.return_value.filter.return_value.all.return_value = (
        mock_consultations
    )

    response = await client.get("/api/admin/metrics/compliance", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()

    assert "total_consultations" in data
    assert "avg_compliance_score" in data
    assert "compliant_percentage" in data
    assert "avg_satisfaction" in data

    assert data["total_consultations"] == 10
    assert data["compliant_percentage"] == 90.0  # 9 out of 10


@pytest.mark.asyncio
async def test_get_time_series_metrics(
    client: AsyncClient, admin_headers, mock_db_session
):
    """Test getting compliance metrics over time."""
    # Mock consultations over time
    mock_consultations = []
    for i in range(30):
        mock_cons = MagicMock()
        mock_cons.start_time = datetime.now() - timedelta(days=i)
        mock_cons.meta = {"compliance_scores": [0.95, 0.96]}
        mock_consultations.append(mock_cons)

    mock_db_session.query.return_value.filter.return_value.all.return_value = (
        mock_consultations
    )

    response = await client.get(
        "/api/admin/metrics/time-series?days=30", headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert "data_points" in data
    assert len(data["data_points"]) > 0

    # Check data point structure
    point = data["data_points"][0]
    assert "date" in point
    assert "avg_compliance" in point
    assert "consultation_count" in point


@pytest.mark.asyncio
async def test_export_consultation(
    client: AsyncClient, admin_headers, mock_db_session
):
    """Test exporting consultation as JSON."""
    consultation_id = str(uuid4())

    mock_consultation = MagicMock()
    mock_consultation.id = consultation_id
    mock_consultation.customer_id = str(uuid4())
    mock_consultation.conversation = []
    mock_consultation.outcome = {}
    mock_consultation.start_time = datetime.now()

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_consultation
    )

    response = await client.get(
        f"/api/admin/consultations/{consultation_id}/export", headers=admin_headers
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    data = response.json()
    assert "id" in data
    assert "conversation" in data
    assert "outcome" in data
