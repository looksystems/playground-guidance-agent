"""Tests for admin rules API endpoints."""

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
def sample_rule_consolidation():
    """Sample consolidation rule."""
    rule = MagicMock()
    rule.id = uuid4()
    rule.principle = "Always explain consolidation fees before discussing benefits"
    rule.domain = "pension_consolidation"
    rule.confidence = 0.92
    rule.supporting_evidence = [
        {"consultation_id": str(uuid4()), "outcome": "successful"},
        {"consultation_id": str(uuid4()), "outcome": "successful"},
        {"consultation_id": str(uuid4()), "outcome": "successful"}
    ]
    rule.embedding = [0.1] * 1536  # Mock embedding
    rule.meta = {"learned_from": "pattern_analysis", "version": 1}
    rule.created_at = datetime.now(timezone.utc) - timedelta(days=30)
    rule.updated_at = datetime.now(timezone.utc) - timedelta(days=2)
    return rule


@pytest.fixture
def sample_rule_compliance():
    """Sample compliance rule."""
    rule = MagicMock()
    rule.id = uuid4()
    rule.principle = "Risk warnings must be provided before discussing drawdown options"
    rule.domain = "fca_compliance"
    rule.confidence = 0.98
    rule.supporting_evidence = [
        {"regulation": "FCA COBS 19.5", "mandatory": True},
        {"consultation_id": str(uuid4()), "compliant": True}
    ]
    rule.embedding = [0.2] * 1536
    rule.meta = {"regulation": "FCA COBS", "criticality": "high"}
    rule.created_at = datetime.now(timezone.utc) - timedelta(days=60)
    rule.updated_at = datetime.now(timezone.utc) - timedelta(days=5)
    return rule


@pytest.fixture
def sample_rule_communication():
    """Sample communication rule."""
    rule = MagicMock()
    rule.id = uuid4()
    rule.principle = "Use plain language when explaining investment risks"
    rule.domain = "communication"
    rule.confidence = 0.65
    rule.supporting_evidence = [
        {"consultation_id": str(uuid4()), "comprehension_score": 8.5}
    ]
    rule.embedding = None  # No embedding
    rule.meta = {"priority": "medium"}
    rule.created_at = datetime.now(timezone.utc) - timedelta(days=10)
    rule.updated_at = datetime.now(timezone.utc) - timedelta(days=1)
    return rule


@pytest.mark.asyncio
async def test_list_rules_success(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_rule_consolidation,
    sample_rule_compliance,
    sample_rule_communication
):
    """Test listing rules successfully."""
    # Setup mock database response
    mock_db_session.all.return_value = [
        sample_rule_consolidation,
        sample_rule_compliance,
        sample_rule_communication
    ]
    mock_db_session.count.return_value = 3

    response = await client.get("/api/admin/rules", headers=admin_headers)

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

    # Check first rule structure
    first_rule = data["items"][0]
    assert "id" in first_rule
    assert "principle" in first_rule
    assert "domain" in first_rule
    assert "confidence" in first_rule
    assert "supporting_evidence" in first_rule
    assert "evidence_count" in first_rule
    assert "has_embedding" in first_rule
    assert "meta" in first_rule
    assert "created_at" in first_rule
    assert "updated_at" in first_rule

    # Check domains
    domains = [r["domain"] for r in data["items"]]
    assert "pension_consolidation" in domains
    assert "fca_compliance" in domains
    assert "communication" in domains


@pytest.mark.asyncio
async def test_list_rules_no_auth(client: AsyncClient):
    """Test listing rules without admin auth."""
    response = await client.get("/api/admin/rules")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_rules_with_pagination(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_rule_consolidation
):
    """Test listing rules with pagination parameters."""
    # Setup mock for 25 rules
    rules = [sample_rule_consolidation] * 25
    mock_db_session.all.return_value = rules[:10]  # Second page
    mock_db_session.count.return_value = 25

    response = await client.get(
        "/api/admin/rules?page=2&page_size=10",
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
async def test_list_rules_filter_by_domain(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_rule_consolidation
):
    """Test filtering rules by domain."""
    mock_db_session.all.return_value = [sample_rule_consolidation]
    mock_db_session.count.return_value = 1

    response = await client.get(
        "/api/admin/rules?domain=pension_consolidation",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["domain"] == "pension_consolidation"

    # Verify filter was applied to database query
    mock_db_session.filter.assert_called()


@pytest.mark.asyncio
async def test_list_rules_filter_by_confidence_range(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_rule_consolidation,
    sample_rule_compliance
):
    """Test filtering rules by confidence range."""
    mock_db_session.all.return_value = [sample_rule_compliance]
    mock_db_session.count.return_value = 1

    response = await client.get(
        "/api/admin/rules?min_confidence=0.9&max_confidence=1.0",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    first_rule = data["items"][0]
    assert first_rule["confidence"] >= 0.9
    assert first_rule["confidence"] <= 1.0

    # Verify filter was applied
    mock_db_session.filter.assert_called()


@pytest.mark.asyncio
async def test_list_rules_sort_by_confidence(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_rule_consolidation,
    sample_rule_compliance,
    sample_rule_communication
):
    """Test sorting rules by confidence."""
    # Return rules sorted by confidence descending
    mock_db_session.all.return_value = [
        sample_rule_compliance,      # 0.98
        sample_rule_consolidation,   # 0.92
        sample_rule_communication    # 0.65
    ]
    mock_db_session.count.return_value = 3

    response = await client.get(
        "/api/admin/rules?sort_by=confidence&sort_order=desc",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Verify order is descending by confidence
    confidences = [r["confidence"] for r in data["items"]]
    assert confidences == sorted(confidences, reverse=True)

    # Verify order_by was called on database
    mock_db_session.order_by.assert_called()


@pytest.mark.asyncio
async def test_list_rules_sort_by_created_at(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_rule_consolidation
):
    """Test sorting rules by created_at."""
    mock_db_session.all.return_value = [sample_rule_consolidation]
    mock_db_session.count.return_value = 1

    response = await client.get(
        "/api/admin/rules?sort_by=created_at&sort_order=asc",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    mock_db_session.order_by.assert_called()


@pytest.mark.asyncio
async def test_list_rules_sort_by_updated_at(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_rule_consolidation
):
    """Test sorting rules by updated_at (default)."""
    mock_db_session.all.return_value = [sample_rule_consolidation]
    mock_db_session.count.return_value = 1

    response = await client.get(
        "/api/admin/rules?sort_by=updated_at&sort_order=desc",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    mock_db_session.order_by.assert_called()


@pytest.mark.asyncio
async def test_list_rules_date_range_filter(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_rule_consolidation
):
    """Test filtering rules by date range."""
    mock_db_session.all.return_value = [sample_rule_consolidation]
    mock_db_session.count.return_value = 1

    from_date = (datetime.now(timezone.utc) - timedelta(days=60)).date().isoformat()
    to_date = datetime.now(timezone.utc).date().isoformat()

    response = await client.get(
        f"/api/admin/rules?from_date={from_date}&to_date={to_date}",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    mock_db_session.filter.assert_called()


@pytest.mark.asyncio
async def test_list_rules_empty_result(
    client: AsyncClient,
    admin_headers,
    mock_db_session
):
    """Test listing rules with no results."""
    mock_db_session.all.return_value = []
    mock_db_session.count.return_value = 0

    response = await client.get("/api/admin/rules", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 0
    assert len(data["items"]) == 0
    assert data["pages"] == 0


@pytest.mark.asyncio
async def test_list_rules_invalid_confidence_range(
    client: AsyncClient,
    admin_headers
):
    """Test filtering with invalid confidence range."""
    response = await client.get(
        "/api/admin/rules?min_confidence=1.5",  # Max is 1.0
        headers=admin_headers
    )

    # Should return validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_rules_invalid_sort_by(
    client: AsyncClient,
    admin_headers
):
    """Test sorting with invalid sort_by field."""
    response = await client.get(
        "/api/admin/rules?sort_by=invalid_field",
        headers=admin_headers
    )

    # Should return validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_rules_max_page_size(
    client: AsyncClient,
    admin_headers,
    mock_db_session
):
    """Test that page_size over 100 returns validation error."""
    mock_db_session.all.return_value = []
    mock_db_session.count.return_value = 0

    response = await client.get(
        "/api/admin/rules?page_size=500",  # Over max
        headers=admin_headers
    )

    # Should return validation error for page_size > 100
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_rule_by_id_success(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_rule_consolidation
):
    """Test getting a specific rule by ID."""
    mock_db_session.first.return_value = sample_rule_consolidation

    rule_id = str(sample_rule_consolidation.id)
    response = await client.get(
        f"/api/admin/rules/{rule_id}",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Check all fields are present
    assert data["id"] == rule_id
    assert data["principle"] == sample_rule_consolidation.principle
    assert data["domain"] == sample_rule_consolidation.domain
    assert data["confidence"] == sample_rule_consolidation.confidence
    assert isinstance(data["supporting_evidence"], list)
    assert data["evidence_count"] == len(sample_rule_consolidation.supporting_evidence)
    assert data["has_embedding"] is True
    assert isinstance(data["meta"], dict)
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_rule_by_id_not_found(
    client: AsyncClient,
    admin_headers,
    mock_db_session
):
    """Test getting a non-existent rule."""
    mock_db_session.first.return_value = None

    fake_id = str(uuid4())
    response = await client.get(
        f"/api/admin/rules/{fake_id}",
        headers=admin_headers
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_rule_by_id_no_auth(client: AsyncClient):
    """Test getting rule without admin auth."""
    fake_id = str(uuid4())
    response = await client.get(f"/api/admin/rules/{fake_id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_rule_by_id_invalid_uuid(
    client: AsyncClient,
    admin_headers
):
    """Test getting rule with invalid UUID."""
    response = await client.get(
        "/api/admin/rules/not-a-uuid",
        headers=admin_headers
    )

    # Should return validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_rules_has_embedding_indicator(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_rule_consolidation,
    sample_rule_communication
):
    """Test that has_embedding field correctly indicates embedding presence."""
    mock_db_session.all.return_value = [
        sample_rule_consolidation,  # Has embedding
        sample_rule_communication   # No embedding
    ]
    mock_db_session.count.return_value = 2

    response = await client.get("/api/admin/rules", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()

    # First rule should have embedding
    assert data["items"][0]["has_embedding"] is True

    # Second rule should not have embedding
    assert data["items"][1]["has_embedding"] is False


@pytest.mark.asyncio
async def test_list_rules_evidence_count(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_rule_consolidation,
    sample_rule_compliance,
    sample_rule_communication
):
    """Test that evidence_count field is calculated correctly."""
    mock_db_session.all.return_value = [
        sample_rule_consolidation,  # 3 evidence items
        sample_rule_compliance,     # 2 evidence items
        sample_rule_communication   # 1 evidence item
    ]
    mock_db_session.count.return_value = 3

    response = await client.get("/api/admin/rules", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()

    # Check evidence counts
    assert data["items"][0]["evidence_count"] == 3
    assert data["items"][1]["evidence_count"] == 2
    assert data["items"][2]["evidence_count"] == 1


@pytest.mark.asyncio
async def test_list_rules_multiple_filters(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_rule_consolidation
):
    """Test combining multiple filters."""
    mock_db_session.all.return_value = [sample_rule_consolidation]
    mock_db_session.count.return_value = 1

    response = await client.get(
        "/api/admin/rules?domain=pension_consolidation&min_confidence=0.8&sort_by=confidence&sort_order=desc",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["domain"] == "pension_consolidation"
    assert data["items"][0]["confidence"] >= 0.8

    # Verify multiple filters were applied
    assert mock_db_session.filter.call_count >= 1


@pytest.mark.asyncio
async def test_list_rules_fca_compliance_domain(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_rule_compliance
):
    """Test filtering by fca_compliance domain."""
    mock_db_session.all.return_value = [sample_rule_compliance]
    mock_db_session.count.return_value = 1

    response = await client.get(
        "/api/admin/rules?domain=fca_compliance",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["domain"] == "fca_compliance"
    assert data["items"][0]["confidence"] == 0.98


@pytest.mark.asyncio
async def test_list_rules_supporting_evidence_is_list(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_rule_consolidation
):
    """Test that supporting_evidence field is returned as list."""
    mock_db_session.all.return_value = [sample_rule_consolidation]
    mock_db_session.count.return_value = 1

    response = await client.get("/api/admin/rules", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()

    # Check supporting_evidence is list
    evidence = data["items"][0]["supporting_evidence"]
    assert isinstance(evidence, list)
    assert len(evidence) > 0
    assert isinstance(evidence[0], dict)


@pytest.mark.asyncio
async def test_get_rule_full_evidence_structure(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_rule_consolidation
):
    """Test that rule detail includes full supporting evidence structure."""
    mock_db_session.first.return_value = sample_rule_consolidation

    rule_id = str(sample_rule_consolidation.id)
    response = await client.get(
        f"/api/admin/rules/{rule_id}",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Verify evidence structure
    evidence = data["supporting_evidence"]
    assert isinstance(evidence, list)
    assert len(evidence) == 3
    assert data["evidence_count"] == 3

    # Check first evidence item structure
    assert "consultation_id" in evidence[0]
    assert "outcome" in evidence[0]


@pytest.mark.asyncio
async def test_list_rules_default_sort_order(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_rule_consolidation
):
    """Test that default sort is by updated_at desc."""
    mock_db_session.all.return_value = [sample_rule_consolidation]
    mock_db_session.count.return_value = 1

    # Request without explicit sort parameters
    response = await client.get("/api/admin/rules", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    # Verify order_by was called (default should be updated_at desc)
    mock_db_session.order_by.assert_called()


@pytest.mark.asyncio
async def test_list_rules_confidence_sorting_ascending(
    client: AsyncClient,
    admin_headers,
    mock_db_session,
    sample_rule_communication,
    sample_rule_consolidation,
    sample_rule_compliance
):
    """Test sorting rules by confidence ascending."""
    # Return rules sorted by confidence ascending
    mock_db_session.all.return_value = [
        sample_rule_communication,    # 0.65
        sample_rule_consolidation,    # 0.92
        sample_rule_compliance        # 0.98
    ]
    mock_db_session.count.return_value = 3

    response = await client.get(
        "/api/admin/rules?sort_by=confidence&sort_order=asc",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Verify order is ascending by confidence
    confidences = [r["confidence"] for r in data["items"]]
    assert confidences == sorted(confidences)

    # Verify order_by was called
    mock_db_session.order_by.assert_called()
