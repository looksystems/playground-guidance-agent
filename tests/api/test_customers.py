"""Tests for customer profile API endpoints."""

import pytest
from httpx import AsyncClient
from uuid import uuid4
from unittest.mock import MagicMock


@pytest.fixture
def sample_customer_id():
    """Sample customer ID."""
    return str(uuid4())


@pytest.mark.asyncio
async def test_get_customer_profile(
    client: AsyncClient, sample_customer_id, mock_db_session
):
    """Test retrieving customer profile."""
    # Mock consultations for this customer
    mock_consultations = []
    for i in range(2):
        mock_cons = MagicMock()
        mock_cons.id = str(uuid4())
        mock_cons.customer_id = sample_customer_id
        mock_cons.meta = {
            "customer_name": "John Smith",
            "customer_age": 52,
            "initial_query": "Test query",
        }
        mock_consultations.append(mock_cons)

    mock_db_session.query.return_value.filter.return_value.all.return_value = (
        mock_consultations
    )

    response = await client.get(f"/api/customers/{sample_customer_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["customer_id"] == sample_customer_id
    assert "name" in data
    assert "consultation_count" in data
    assert data["consultation_count"] == 2


@pytest.mark.asyncio
async def test_get_customer_not_found(client: AsyncClient, mock_db_session):
    """Test retrieving non-existent customer."""
    mock_db_session.query.return_value.filter.return_value.all.return_value = []

    response = await client.get(f"/api/customers/{uuid4()}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_customer_consultations(
    client: AsyncClient, sample_customer_id, mock_db_session
):
    """Test listing consultations for a customer."""
    from datetime import datetime

    # Mock consultations
    mock_consultations = []
    for i in range(3):
        mock_cons = MagicMock()
        mock_cons.id = str(uuid4())
        mock_cons.customer_id = sample_customer_id
        mock_cons.start_time = datetime.now()
        mock_cons.end_time = datetime.now() if i > 0 else None
        mock_cons.meta = {"advisor_name": "Sarah"}
        mock_consultations.append(mock_cons)

    mock_db_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = (
        mock_consultations
    )

    response = await client.get(
        f"/api/customers/{sample_customer_id}/consultations"
    )

    assert response.status_code == 200
    data = response.json()

    assert "consultations" in data
    assert len(data["consultations"]) == 3

    # Check active vs completed
    active = [c for c in data["consultations"] if c["status"] == "active"]
    completed = [c for c in data["consultations"] if c["status"] == "completed"]

    assert len(active) == 1
    assert len(completed) == 2
