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
            "age": 17,  # Too young - must be 18+
            "initial_query": "Test query that is long enough to pass validation",
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
    from datetime import timezone

    # Mock active consultation
    mock_consultation = MagicMock()
    mock_consultation.id = sample_consultation_id
    mock_consultation.customer_id = str(uuid4())
    mock_consultation.end_time = None
    mock_consultation.start_time = datetime.now(timezone.utc)
    mock_consultation.conversation = [
        {
            "role": "customer",
            "content": "Test",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        {
            "role": "advisor",
            "content": "Response",
            "timestamp": datetime.now(timezone.utc).isoformat(),
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


# ========================================
# NEW TESTS: Validation Reasoning Display
# ========================================


@pytest.mark.asyncio
async def test_validation_reasoning_stored_in_conversation(
    client: AsyncClient, sample_consultation_id, mock_db_session
):
    """Test that validation reasoning is stored in conversation JSONB.

    This test verifies that when an advisor provides guidance, the full
    validation details (reasoning, issues, passed flag, review flag) are
    stored in the conversation JSONB field for later retrieval.
    """
    # Mock active consultation
    mock_consultation = MagicMock()
    mock_consultation.id = sample_consultation_id
    mock_consultation.customer_id = str(uuid4())
    mock_consultation.end_time = None
    mock_consultation.conversation = []
    mock_consultation.meta = {
        "advisor_name": "Sarah",
        "customer_age": 52,
        "initial_query": "Test query",
    }

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_consultation
    )

    # Stream guidance to trigger advisor response
    response = await client.get(f"/api/consultations/{sample_consultation_id}/stream")

    # Read all SSE events
    content = b""
    async for chunk in response.aiter_bytes():
        content += chunk

    # Verify advisor message was added to conversation
    assert len(mock_consultation.conversation) == 1
    advisor_message = mock_consultation.conversation[0]

    # Verify all validation fields are present
    assert advisor_message["role"] == "advisor"
    assert "content" in advisor_message
    assert "compliance_score" in advisor_message
    assert "compliance_confidence" in advisor_message

    # NEW: Verify validation reasoning fields
    assert "compliance_reasoning" in advisor_message
    assert "compliance_issues" in advisor_message
    assert "compliance_passed" in advisor_message
    assert "requires_human_review" in advisor_message

    # Verify reasoning is a non-empty string
    assert isinstance(advisor_message["compliance_reasoning"], str)
    assert len(advisor_message["compliance_reasoning"]) > 0

    # Verify issues is a list
    assert isinstance(advisor_message["compliance_issues"], list)

    # Verify flags are booleans
    assert isinstance(advisor_message["compliance_passed"], bool)
    assert isinstance(advisor_message["requires_human_review"], bool)


@pytest.mark.asyncio
async def test_validation_issues_serialization(
    client: AsyncClient, sample_consultation_id, mock_db_session
):
    """Test that ValidationIssue objects are properly converted to dicts.

    ValidationIssue dataclass objects must be serialized to JSON-compatible
    dicts with category, severity, and description fields.
    """
    # Mock active consultation
    mock_consultation = MagicMock()
    mock_consultation.id = sample_consultation_id
    mock_consultation.customer_id = str(uuid4())
    mock_consultation.end_time = None
    mock_consultation.conversation = []
    mock_consultation.meta = {
        "advisor_name": "Sarah",
        "customer_age": 52,
        "initial_query": "Test query",
    }

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_consultation
    )

    # Stream guidance
    response = await client.get(f"/api/consultations/{sample_consultation_id}/stream")

    async for chunk in response.aiter_bytes():
        pass  # Consume stream

    # Get advisor message
    advisor_message = mock_consultation.conversation[0]
    issues = advisor_message["compliance_issues"]

    # Verify issues structure
    assert isinstance(issues, list)

    # If there are issues, verify their structure
    if len(issues) > 0:
        issue = issues[0]
        assert isinstance(issue, dict)
        assert "category" in issue
        assert "severity" in issue
        assert "description" in issue

        # Verify field types
        assert isinstance(issue["category"], str)
        assert isinstance(issue["severity"], str)
        assert isinstance(issue["description"], str)


@pytest.mark.asyncio
async def test_validation_passed_flag_stored(
    client: AsyncClient, sample_consultation_id, mock_db_session
):
    """Test that validation passed/failed flag is stored correctly."""
    # Mock active consultation
    mock_consultation = MagicMock()
    mock_consultation.id = sample_consultation_id
    mock_consultation.customer_id = str(uuid4())
    mock_consultation.end_time = None
    mock_consultation.conversation = []
    mock_consultation.meta = {
        "advisor_name": "Sarah",
        "customer_age": 52,
        "initial_query": "Test query",
    }

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_consultation
    )

    # Stream guidance
    response = await client.get(f"/api/consultations/{sample_consultation_id}/stream")

    async for chunk in response.aiter_bytes():
        pass

    advisor_message = mock_consultation.conversation[0]

    # Verify passed flag is boolean
    assert "compliance_passed" in advisor_message
    assert isinstance(advisor_message["compliance_passed"], bool)


@pytest.mark.asyncio
async def test_validation_review_flag_stored(
    client: AsyncClient, sample_consultation_id, mock_db_session
):
    """Test that requires_human_review flag is stored correctly."""
    # Mock active consultation
    mock_consultation = MagicMock()
    mock_consultation.id = sample_consultation_id
    mock_consultation.customer_id = str(uuid4())
    mock_consultation.end_time = None
    mock_consultation.conversation = []
    mock_consultation.meta = {
        "advisor_name": "Sarah",
        "customer_age": 52,
        "initial_query": "Test query",
    }

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_consultation
    )

    # Stream guidance
    response = await client.get(f"/api/consultations/{sample_consultation_id}/stream")

    async for chunk in response.aiter_bytes():
        pass

    advisor_message = mock_consultation.conversation[0]

    # Verify review flag is boolean
    assert "requires_human_review" in advisor_message
    assert isinstance(advisor_message["requires_human_review"], bool)


@pytest.mark.asyncio
async def test_consultation_detail_returns_validation_fields(
    client: AsyncClient, sample_consultation_id, mock_db_session
):
    """Test that consultation detail API returns new validation fields.

    The GET /consultations/{id} endpoint should return the new validation
    fields in the conversation turns.
    """
    # Mock consultation with validation data
    mock_consultation = MagicMock()
    mock_consultation.id = sample_consultation_id
    mock_consultation.customer_id = str(uuid4())
    mock_consultation.start_time = datetime.now()
    mock_consultation.end_time = None
    mock_consultation.outcome = None
    mock_consultation.meta = {"advisor_name": "Sarah"}
    mock_consultation.conversation = [
        {
            "role": "customer",
            "content": "Test question",
            "timestamp": datetime.now().isoformat(),
        },
        {
            "role": "advisor",
            "content": "Test guidance",
            "timestamp": datetime.now().isoformat(),
            "compliance_score": 0.95,
            "compliance_confidence": 0.95,
            "compliance_reasoning": "The guidance stays within FCA boundaries...",
            "compliance_issues": [
                {
                    "category": "clarity",
                    "severity": "low",
                    "description": "Could be clearer about risks",
                }
            ],
            "compliance_passed": True,
            "requires_human_review": False,
        },
    ]

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_consultation
    )

    # Get consultation detail
    response = await client.get(f"/api/consultations/{sample_consultation_id}")

    assert response.status_code == 200
    data = response.json()

    # Verify conversation is returned
    assert "conversation" in data
    assert len(data["conversation"]) == 2

    # Find advisor turn
    advisor_turn = next(t for t in data["conversation"] if t["role"] == "advisor")

    # Verify all validation fields are present in response
    assert "compliance_score" in advisor_turn
    assert "compliance_confidence" in advisor_turn
    assert "compliance_reasoning" in advisor_turn
    assert "compliance_issues" in advisor_turn
    assert "compliance_passed" in advisor_turn
    assert "requires_human_review" in advisor_turn

    # Verify values
    assert advisor_turn["compliance_reasoning"] == "The guidance stays within FCA boundaries..."
    assert len(advisor_turn["compliance_issues"]) == 1
    assert advisor_turn["compliance_issues"][0]["category"] == "clarity"
    assert advisor_turn["compliance_passed"] is True
    assert advisor_turn["requires_human_review"] is False
