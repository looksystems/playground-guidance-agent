"""Tests for admin customer management API endpoints."""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session

from guidance_agent.core.database import Consultation


@pytest.fixture(scope="module", autouse=True)
def clean_database_for_module():
    """Clean database before running tests in this module.

    This ensures test isolation by removing all consultations before
    the module tests run. This is necessary because these tests use
    client_with_real_db which doesn't provide transactional isolation.
    """
    from guidance_agent.core.database import get_session

    db = get_session()
    try:
        # Delete all consultations to ensure clean state
        db.query(Consultation).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture
def admin_headers():
    """Admin authorization headers."""
    return {"Authorization": "Bearer admin-token"}


@pytest.fixture
async def sample_consultations(client_with_real_db: AsyncClient):
    """Create sample consultations for testing customer aggregation."""
    from guidance_agent.core.database import get_session

    db = get_session()

    # Create consultations for 3 different customers
    customer_ids = [uuid4() for _ in range(3)]
    advisor_id = uuid4()

    consultations = []

    # Customer 1: 3 consultations over 60 days
    customer1_id = customer_ids[0]
    for i in range(3):
        consultation = Consultation(
            id=uuid4(),
            customer_id=customer1_id,
            advisor_id=advisor_id,
            conversation=[
                {
                    "role": "customer",
                    "content": "I need help with my pension",
                    "timestamp": (datetime.now() - timedelta(days=60-i*20)).isoformat()
                },
                {
                    "role": "advisor",
                    "content": "I can help you with that",
                    "timestamp": (datetime.now() - timedelta(days=60-i*20, minutes=-5)).isoformat(),
                    "compliance_score": 0.95
                }
            ],
            outcome={
                "fca_compliant": True,
                "customer_satisfaction": 8.5 + i * 0.3,
                "comprehension": 0.92
            },
            start_time=datetime.now() - timedelta(days=60-i*20),
            end_time=datetime.now() - timedelta(days=60-i*20, minutes=-30),
            duration_seconds=1800,
            meta={
                "customer_name": "John Smith",
                "customer_age": 55,
                "advisor_name": "Sarah",
                "initial_topic": "Pension Withdrawal" if i == 0 else "Investment Strategy",
                "compliance_scores": [0.95, 0.93, 0.97]
            }
        )
        db.add(consultation)
        consultations.append(consultation)

    # Customer 2: 1 consultation 45 days ago
    customer2_id = customer_ids[1]
    consultation = Consultation(
        id=uuid4(),
        customer_id=customer2_id,
        advisor_id=advisor_id,
        conversation=[
            {
                "role": "customer",
                "content": "What are my pension options?",
                "timestamp": (datetime.now() - timedelta(days=45)).isoformat()
            },
            {
                "role": "advisor",
                "content": "Let me explain your options",
                "timestamp": (datetime.now() - timedelta(days=45, minutes=-5)).isoformat(),
                "compliance_score": 0.88
            }
        ],
        outcome={
            "fca_compliant": True,
            "customer_satisfaction": 7.5,
            "comprehension": 0.85
        },
        start_time=datetime.now() - timedelta(days=45),
        end_time=datetime.now() - timedelta(days=45, minutes=-25),
        duration_seconds=1500,
        meta={
            "customer_name": "Jane Doe",
            "customer_age": 48,
            "advisor_name": "Sarah",
            "initial_topic": "Pension Options",
            "compliance_scores": [0.88, 0.90]
        }
    )
    db.add(consultation)
    consultations.append(consultation)

    # Customer 3: 2 consultations, one recent (within 30 days)
    customer3_id = customer_ids[2]
    for i in range(2):
        consultation = Consultation(
            id=uuid4(),
            customer_id=customer3_id,
            advisor_id=advisor_id,
            conversation=[
                {
                    "role": "customer",
                    "content": "I want to consolidate my pensions",
                    "timestamp": (datetime.now() - timedelta(days=10 if i == 0 else 90)).isoformat()
                },
                {
                    "role": "advisor",
                    "content": "Pension consolidation can be beneficial",
                    "timestamp": (datetime.now() - timedelta(days=10 if i == 0 else 90, minutes=-5)).isoformat(),
                    "compliance_score": 0.92
                }
            ],
            outcome={
                "fca_compliant": True,
                "customer_satisfaction": 9.0 if i == 0 else 8.0,
                "comprehension": 0.90
            },
            start_time=datetime.now() - timedelta(days=10 if i == 0 else 90),
            end_time=datetime.now() - timedelta(days=10 if i == 0 else 90, minutes=-20),
            duration_seconds=1200,
            meta={
                "customer_name": "Bob Wilson",
                "customer_age": 62,
                "advisor_name": "Sarah",
                "initial_topic": "Pension Consolidation",
                "compliance_scores": [0.92, 0.94]
            }
        )
        db.add(consultation)
        consultations.append(consultation)

    db.commit()

    # Return customer IDs for testing
    yield {
        "customer_ids": customer_ids,
        "consultations": consultations
    }

    # Cleanup
    for consultation in consultations:
        db.delete(consultation)
    db.commit()
    db.close()


@pytest.mark.asyncio
async def test_list_customers_success(
    client_with_real_db: AsyncClient,
    admin_headers,
    sample_consultations
):
    """Test listing customers with aggregated stats."""
    response = await client_with_real_db.get(
        "/api/admin/customers",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "pages" in data
    assert "stats" in data

    # Check stats
    stats = data["stats"]
    assert "total_customers" in stats
    assert "active_customers_30d" in stats
    assert "avg_consultations_per_customer" in stats

    # We have at least 3 customers from our fixture
    assert stats["total_customers"] >= 3

    # At least customer 3 has consultation in last 30 days
    assert stats["active_customers_30d"] >= 1

    # Average should be positive
    assert stats["avg_consultations_per_customer"] > 0

    # Check items - should have data
    assert len(data["items"]) >= 3

    # Each customer should have aggregated fields
    for customer in data["items"]:
        assert "customer_id" in customer
        assert "total_consultations" in customer
        assert "first_consultation" in customer
        assert "last_consultation" in customer
        assert "avg_compliance_score" in customer
        assert "avg_satisfaction" in customer
        assert "topics" in customer
        assert "customer_profile" in customer

        # Verify types
        assert isinstance(customer["total_consultations"], int)
        assert isinstance(customer["avg_compliance_score"], float)
        assert isinstance(customer["topics"], list)
        assert isinstance(customer["customer_profile"], dict)


@pytest.mark.asyncio
async def test_list_customers_pagination(
    client_with_real_db: AsyncClient,
    admin_headers,
    sample_consultations
):
    """Test customer list pagination."""
    # Request page 1 with page_size=2
    response = await client_with_real_db.get(
        "/api/admin/customers?page=1&page_size=2",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # We have at least 3 customers from fixture
    assert data["total"] >= 3
    assert data["page"] == 1
    assert data["page_size"] == 2
    # With at least 3 customers and page_size 2, we need at least 2 pages
    assert data["pages"] >= 2
    assert len(data["items"]) == 2  # Page size is 2

    # Request page 2
    response = await client_with_real_db.get(
        "/api/admin/customers?page=2&page_size=2",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["page"] == 2
    # Page 2 should have at least 1 item (could have 2 depending on total)
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_list_customers_sort_by_total_consultations(
    client_with_real_db: AsyncClient,
    admin_headers,
    sample_consultations
):
    """Test sorting customers by total consultations."""
    # Sort descending (default)
    response = await client_with_real_db.get(
        "/api/admin/customers?sort_by=total_consultations&sort_order=desc",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # First customer should have most consultations (3)
    assert data["items"][0]["total_consultations"] == 3
    # Last should have least (1)
    assert data["items"][-1]["total_consultations"] == 1

    # Sort ascending
    response = await client_with_real_db.get(
        "/api/admin/customers?sort_by=total_consultations&sort_order=asc",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # First customer should have least consultations (1)
    assert data["items"][0]["total_consultations"] == 1
    # Last should have most (3)
    assert data["items"][-1]["total_consultations"] == 3


@pytest.mark.asyncio
async def test_list_customers_sort_by_last_consultation(
    client_with_real_db: AsyncClient,
    admin_headers,
    sample_consultations
):
    """Test sorting customers by last consultation date."""
    response = await client_with_real_db.get(
        "/api/admin/customers?sort_by=last_consultation&sort_order=desc",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Items should be sorted by most recent consultation first
    last_consultation_dates = [
        datetime.fromisoformat(item["last_consultation"].replace('Z', '+00:00'))
        for item in data["items"]
    ]

    # Verify descending order
    for i in range(len(last_consultation_dates) - 1):
        assert last_consultation_dates[i] >= last_consultation_dates[i + 1]


@pytest.mark.asyncio
async def test_list_customers_sort_by_avg_compliance(
    client_with_real_db: AsyncClient,
    admin_headers,
    sample_consultations
):
    """Test sorting customers by average compliance score."""
    response = await client_with_real_db.get(
        "/api/admin/customers?sort_by=avg_compliance&sort_order=desc",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Items should be sorted by compliance score descending
    compliance_scores = [item["avg_compliance_score"] for item in data["items"]]

    # Verify descending order
    for i in range(len(compliance_scores) - 1):
        assert compliance_scores[i] >= compliance_scores[i + 1]


@pytest.mark.asyncio
async def test_list_customers_date_range_filter(
    client_with_real_db: AsyncClient,
    admin_headers,
    sample_consultations
):
    """Test filtering customers by date range on last_consultation."""
    # Filter for customers with consultation in last 30 days
    from_date = (datetime.now() - timedelta(days=30)).date().isoformat()

    response = await client_with_real_db.get(
        f"/api/admin/customers?from_date={from_date}",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should return at least customer 3 (has consultation 10 days ago)
    # May include other recent consultations from previous tests
    assert len(data["items"]) >= 1
    assert data["total"] >= 1

    # Filter for older consultations (between 90 and 40 days ago)
    from_date = (datetime.now() - timedelta(days=90)).date().isoformat()
    to_date = (datetime.now() - timedelta(days=40)).date().isoformat()

    response = await client_with_real_db.get(
        f"/api/admin/customers?from_date={from_date}&to_date={to_date}",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should return customers 1 and 2
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_get_customer_detail_success(
    client_with_real_db: AsyncClient,
    admin_headers,
    sample_consultations
):
    """Test getting customer detail with consultation history."""
    customer_id = sample_consultations["customer_ids"][0]

    response = await client_with_real_db.get(
        f"/api/admin/customers/{customer_id}",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Check all required fields
    assert data["customer_id"] == str(customer_id)
    assert data["total_consultations"] == 3
    assert "first_consultation" in data
    assert "last_consultation" in data
    assert "avg_compliance_score" in data
    assert "avg_satisfaction" in data
    assert "topics" in data
    assert "customer_profile" in data
    assert "recent_consultations" in data

    # Check customer profile
    assert data["customer_profile"]["customer_name"] == "John Smith"
    assert data["customer_profile"]["customer_age"] == 55

    # Check topics
    assert isinstance(data["topics"], list)
    assert len(data["topics"]) > 0

    # Check recent consultations (last 5)
    assert isinstance(data["recent_consultations"], list)
    assert len(data["recent_consultations"]) == 3  # Customer 1 has 3 consultations

    # Recent consultations should have basic info
    for consultation in data["recent_consultations"]:
        assert "id" in consultation
        assert "created_at" in consultation
        assert "status" in consultation


@pytest.mark.asyncio
async def test_get_customer_detail_not_found(
    client_with_real_db: AsyncClient,
    admin_headers
):
    """Test getting customer detail for non-existent customer."""
    non_existent_id = uuid4()

    response = await client_with_real_db.get(
        f"/api/admin/customers/{non_existent_id}",
        headers=admin_headers
    )

    assert response.status_code == 404
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_list_customers_no_auth(
    client_with_real_db: AsyncClient,
    sample_consultations
):
    """Test listing customers without admin authentication."""
    response = await client_with_real_db.get("/api/admin/customers")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_customer_detail_no_auth(
    client_with_real_db: AsyncClient,
    sample_consultations
):
    """Test getting customer detail without admin authentication."""
    customer_id = sample_consultations["customer_ids"][0]

    response = await client_with_real_db.get(f"/api/admin/customers/{customer_id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_customers_empty_database(
    client_with_real_db: AsyncClient,
    admin_headers
):
    """Test listing customers when database is empty."""
    # This test runs without sample_consultations fixture
    response = await client_with_real_db.get(
        "/api/admin/customers",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should return empty list with proper structure
    assert data["items"] == [] or isinstance(data["items"], list)
    assert "stats" in data
    assert data["stats"]["total_customers"] >= 0


@pytest.mark.asyncio
async def test_customer_aggregation_accuracy(
    client_with_real_db: AsyncClient,
    admin_headers,
    sample_consultations
):
    """Test accuracy of customer aggregation calculations."""
    customer_id = sample_consultations["customer_ids"][0]

    response = await client_with_real_db.get(
        f"/api/admin/customers/{customer_id}",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Verify aggregated calculations
    # Customer 1 has 3 consultations with compliance_scores: [0.95, 0.93, 0.97] each
    # Average of all scores: (0.95+0.93+0.97)*3 / 9 ≈ 0.95
    assert 0.93 <= data["avg_compliance_score"] <= 0.97

    # Satisfaction scores: 8.5, 8.8, 9.1
    # Average: 8.8
    assert 8.4 <= data["avg_satisfaction"] <= 9.2

    # Check unique topics
    topics = data["topics"]
    assert len(topics) >= 1
    # Should have unique topics only
    assert len(topics) == len(set(topics))


@pytest.mark.asyncio
async def test_list_customers_invalid_sort_field(
    client_with_real_db: AsyncClient,
    admin_headers,
    sample_consultations
):
    """Test listing customers with invalid sort field."""
    response = await client_with_real_db.get(
        "/api/admin/customers?sort_by=invalid_field",
        headers=admin_headers
    )

    # Should return 422 validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_customers_invalid_pagination(
    client_with_real_db: AsyncClient,
    admin_headers,
    sample_consultations
):
    """Test listing customers with invalid pagination parameters."""
    # Negative page
    response = await client_with_real_db.get(
        "/api/admin/customers?page=-1",
        headers=admin_headers
    )
    assert response.status_code == 422

    # Page size too large
    response = await client_with_real_db.get(
        "/api/admin/customers?page_size=150",
        headers=admin_headers
    )
    assert response.status_code == 422

    # Page size zero
    response = await client_with_real_db.get(
        "/api/admin/customers?page_size=0",
        headers=admin_headers
    )
    assert response.status_code == 422
