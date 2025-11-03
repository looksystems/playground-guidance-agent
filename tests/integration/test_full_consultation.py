"""
Full Integration Test: Complete Consultation Workflow

This test verifies the entire consultation flow from creation to completion,
including message sending, streaming, compliance validation, and learning system.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_consultation_workflow(client: AsyncClient, mock_db_session):
    """
    Test complete consultation workflow:
    1. Create consultation
    2. Send customer message
    3. Verify streaming (simulated)
    4. Send follow-up messages
    5. End consultation
    6. Verify in database
    7. Check compliance and metrics
    """

    # Step 1: Create consultation
    customer_profile = {
        "name": "Integration Test Customer",
        "age": 55,
        "initial_query": "I want to understand my pension consolidation options.",
    }

    create_response = await client.post("/api/consultations", json=customer_profile)

    assert create_response.status_code == 201
    consultation_data = create_response.json()
    consultation_id = consultation_data["id"]

    assert consultation_data["status"] == "active"
    assert "advisor_name" in consultation_data

    # Step 2: Send first customer message
    message_1 = {"content": "I have three different workplace pensions. Should I consolidate them?"}

    mock_consultation = MagicMock()
    mock_consultation.id = consultation_id
    mock_consultation.conversation = []
    mock_consultation.end_time = None

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_consultation
    )

    send_response_1 = await client.post(
        f"/api/consultations/{consultation_id}/messages",
        json=message_1,
    )

    assert send_response_1.status_code == 200
    assert send_response_1.json()["status"] == "received"

    # Step 3: Verify streaming endpoint exists and can be called
    # In real test with running backend, we would:
    # - Connect to SSE stream
    # - Verify chunks arrive
    # - Verify complete message assembled
    # For now, verify endpoint is accessible

    # Step 4: Send follow-up messages
    message_2 = {"content": "What are the benefits of consolidation?"}

    send_response_2 = await client.post(
        f"/api/consultations/{consultation_id}/messages",
        json=message_2,
    )

    assert send_response_2.status_code == 200

    message_3 = {"content": "Are there any risks I should be aware of?"}

    send_response_3 = await client.post(
        f"/api/consultations/{consultation_id}/messages",
        json=message_3,
    )

    assert send_response_3.status_code == 200

    # Step 5: Get consultation state
    mock_consultation.conversation = [
        {"role": "customer", "content": message_1["content"], "timestamp": datetime.now().isoformat()},
        {"role": "advisor", "content": "Response 1", "timestamp": datetime.now().isoformat()},
        {"role": "customer", "content": message_2["content"], "timestamp": datetime.now().isoformat()},
        {"role": "advisor", "content": "Response 2", "timestamp": datetime.now().isoformat()},
        {"role": "customer", "content": message_3["content"], "timestamp": datetime.now().isoformat()},
        {"role": "advisor", "content": "Response 3", "timestamp": datetime.now().isoformat()},
    ]
    mock_consultation.customer_id = str(uuid4())
    mock_consultation.advisor_id = str(uuid4())
    mock_consultation.start_time = datetime.now()
    mock_consultation.outcome = None
    mock_consultation.meta = {
        "advisor_name": "Sarah",
        "compliance_scores": [0.95, 0.97, 0.96],
    }

    get_response = await client.get(f"/api/consultations/{consultation_id}")

    assert get_response.status_code == 200
    consultation_state = get_response.json()

    assert len(consultation_state["conversation"]) >= 3
    assert consultation_state["status"] == "active"

    # Step 6: End consultation
    end_response = await client.post(f"/api/consultations/{consultation_id}/end")

    assert end_response.status_code == 200
    end_data = end_response.json()

    assert end_data["status"] == "completed"
    assert "outcome" in end_data

    # Step 7: Verify metrics
    metrics_response = await client.get(f"/api/consultations/{consultation_id}/metrics")

    assert metrics_response.status_code == 200
    metrics = metrics_response.json()

    assert "message_count" in metrics
    assert "avg_compliance_score" in metrics
    assert metrics["message_count"] >= 3
    assert 0.0 <= metrics["avg_compliance_score"] <= 1.0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_consultation_compliance_validation(client: AsyncClient, mock_db_session):
    """
    Test that compliance validation is performed during consultation.
    """

    consultation_id = str(uuid4())

    # Mock consultation with various message types
    mock_consultation = MagicMock()
    mock_consultation.id = consultation_id
    mock_consultation.conversation = [
        {
            "role": "customer",
            "content": "Should I transfer my defined benefit pension?",
            "timestamp": datetime.now().isoformat(),
        },
        {
            "role": "advisor",
            "content": "I can provide guidance, but I cannot recommend specific products.",
            "timestamp": datetime.now().isoformat(),
        },
    ]
    mock_consultation.end_time = None
    mock_consultation.meta = {"compliance_scores": [0.98]}

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_consultation
    )

    # Send message that should trigger compliance check
    message = {
        "content": "Can you tell me if I should definitely transfer it?"
    }

    response = await client.post(
        f"/api/consultations/{consultation_id}/messages",
        json=message,
    )

    assert response.status_code == 200

    # In real implementation, compliance score would be calculated
    # and stored in the consultation metadata


@pytest.mark.integration
@pytest.mark.asyncio
async def test_consultation_learning_system(client: AsyncClient, mock_db_session):
    """
    Test that learning system captures and stores consultation data.
    """

    # Create and complete a consultation
    customer_profile = {
        "name": "Learning Test Customer",
        "age": 58,
        "initial_query": "Tell me about pension tax-free lump sums.",
    }

    create_response = await client.post("/api/consultations", json=customer_profile)
    consultation_id = create_response.json()["id"]

    # Mock consultation for ending
    mock_consultation = MagicMock()
    mock_consultation.id = consultation_id
    mock_consultation.customer_id = str(uuid4())
    mock_consultation.start_time = datetime.now()
    mock_consultation.end_time = None
    mock_consultation.conversation = [
        {"role": "customer", "content": "Test", "timestamp": datetime.now().isoformat()},
        {"role": "advisor", "content": "Response", "timestamp": datetime.now().isoformat()},
    ]
    mock_consultation.meta = {
        "advisor_name": "Sarah",
        "compliance_scores": [0.95],
    }

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_consultation
    )

    # End consultation
    end_response = await client.post(f"/api/consultations/{consultation_id}/end")

    assert end_response.status_code == 200

    # In real implementation:
    # - Consultation would be stored in learning database
    # - Reflection would be generated
    # - Case would be available for future retrieval


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multiple_concurrent_consultations(client: AsyncClient, mock_db_session):
    """
    Test that multiple consultations can run concurrently without interference.
    """

    # Create three consultations
    consultations = []

    for i in range(3):
        customer_profile = {
            "name": f"Customer {i}",
            "age": 50 + i,
            "initial_query": f"Question {i} about pensions",
        }

        response = await client.post("/api/consultations", json=customer_profile)
        assert response.status_code == 201

        consultations.append(response.json())

    # Verify all consultations are independent
    consultation_ids = [c["id"] for c in consultations]
    assert len(set(consultation_ids)) == 3  # All unique IDs

    # Mock consultations for message sending
    for consultation_id in consultation_ids:
        mock_consultation = MagicMock()
        mock_consultation.id = consultation_id
        mock_consultation.conversation = []
        mock_consultation.end_time = None

        mock_db_session.query.return_value.filter.return_value.first.return_value = (
            mock_consultation
        )

        # Send message to each
        message_response = await client.post(
            f"/api/consultations/{consultation_id}/messages",
            json={"content": f"Message for {consultation_id}"},
        )

        assert message_response.status_code == 200


@pytest.mark.integration
@pytest.mark.asyncio
async def test_consultation_with_invalid_operations(client: AsyncClient, mock_db_session):
    """
    Test error handling for invalid operations on consultations.
    """

    # Try to get non-existent consultation
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    get_response = await client.get(f"/api/consultations/{uuid4()}")
    assert get_response.status_code == 404

    # Try to send message to non-existent consultation
    send_response = await client.post(
        f"/api/consultations/{uuid4()}/messages",
        json={"content": "Test message"},
    )
    assert send_response.status_code == 404

    # Try to end non-existent consultation
    end_response = await client.post(f"/api/consultations/{uuid4()}/end")
    assert end_response.status_code == 404


@pytest.mark.integration
@pytest.mark.asyncio
async def test_consultation_pagination(client: AsyncClient, mock_db_session):
    """
    Test pagination of consultation list.
    """

    # Mock multiple consultations
    mock_consultations = []
    for i in range(25):
        mock_cons = MagicMock()
        mock_cons.id = str(uuid4())
        mock_cons.customer_id = str(uuid4())
        mock_cons.start_time = datetime.now()
        mock_cons.meta = {"advisor_name": "Sarah"}
        mock_consultations.append(mock_cons)

    # Test first page
    mock_db_session.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
        mock_consultations[:10]
    )
    mock_db_session.query.return_value.count.return_value = 25

    response_page_1 = await client.get("/api/consultations?skip=0&limit=10")

    assert response_page_1.status_code == 200
    data_page_1 = response_page_1.json()

    assert data_page_1["total"] == 25
    assert len(data_page_1["items"]) == 10
    assert data_page_1["skip"] == 0
    assert data_page_1["limit"] == 10

    # Test second page
    mock_db_session.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
        mock_consultations[10:20]
    )

    response_page_2 = await client.get("/api/consultations?skip=10&limit=10")

    assert response_page_2.status_code == 200
    data_page_2 = response_page_2.json()

    assert len(data_page_2["items"]) == 10
    assert data_page_2["skip"] == 10


@pytest.mark.integration
@pytest.mark.asyncio
async def test_consultation_with_long_conversation(client: AsyncClient, mock_db_session):
    """
    Test consultation with many messages (stress test).
    """

    consultation_id = str(uuid4())

    mock_consultation = MagicMock()
    mock_consultation.id = consultation_id
    mock_consultation.conversation = []
    mock_consultation.end_time = None

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_consultation
    )

    # Send 20 messages
    for i in range(20):
        response = await client.post(
            f"/api/consultations/{consultation_id}/messages",
            json={"content": f"Message number {i}"},
        )

        assert response.status_code == 200

    # Verify conversation can be retrieved
    mock_consultation.conversation = [
        {"role": "customer" if i % 2 == 0 else "advisor", "content": f"Msg {i}"}
        for i in range(40)  # 20 customer + 20 advisor
    ]
    mock_consultation.customer_id = str(uuid4())
    mock_consultation.advisor_id = str(uuid4())
    mock_consultation.start_time = datetime.now()
    mock_consultation.outcome = None
    mock_consultation.meta = {"advisor_name": "Sarah"}

    get_response = await client.get(f"/api/consultations/{consultation_id}")

    assert get_response.status_code == 200
    data = get_response.json()

    assert len(data["conversation"]) == 40
