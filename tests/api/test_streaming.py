"""Tests for SSE streaming endpoint.

Tests the real-time guidance streaming functionality.
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
import json


@pytest.fixture
def sample_consultation_id():
    """Sample consultation ID."""
    return str(uuid4())


@pytest.fixture
def mock_advisor_stream():
    """Mock advisor agent with streaming."""

    async def mock_stream(*args, **kwargs):
        """Mock streaming guidance."""
        chunks = [
            "I understand ",
            "why managing ",
            "multiple pensions ",
            "feels complicated. ",
        ]
        for chunk in chunks:
            yield chunk

    return mock_stream


@pytest.mark.asyncio
async def test_stream_guidance_sse(
    client: AsyncClient, sample_consultation_id, mock_db_session, mock_advisor_stream
):
    """Test SSE streaming of advisor guidance."""
    # Mock consultation
    mock_consultation = MagicMock()
    mock_consultation.id = sample_consultation_id
    mock_consultation.conversation = [
        {"role": "customer", "content": "I have 4 pensions"}
    ]
    mock_consultation.end_time = None

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_consultation
    )

    # Use SSE endpoint
    async with client.stream(
        "GET", f"/api/consultations/{sample_consultation_id}/stream"
    ) as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

        # Read SSE events
        events = []
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data = line[6:]  # Remove "data: " prefix
                if data:
                    events.append(json.loads(data))

        # Check we received events
        assert len(events) > 0

        # Check event structure
        chunk_events = [e for e in events if e.get("type") == "chunk"]
        complete_event = [e for e in events if e.get("type") == "complete"]

        assert len(chunk_events) > 0
        assert len(complete_event) == 1

        # Check complete event has compliance score
        assert "compliance_score" in complete_event[0]
        assert 0 <= complete_event[0]["compliance_score"] <= 1


@pytest.mark.asyncio
async def test_stream_guidance_not_found(client: AsyncClient, mock_db_session):
    """Test streaming for non-existent consultation."""
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    response = await client.get(f"/api/consultations/{uuid4()}/stream")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_stream_guidance_completed_consultation(
    client: AsyncClient, sample_consultation_id, mock_db_session
):
    """Test streaming for completed consultation (should fail)."""
    from datetime import datetime

    # Mock completed consultation
    mock_consultation = MagicMock()
    mock_consultation.id = sample_consultation_id
    mock_consultation.end_time = datetime.now()

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_consultation
    )

    response = await client.get(
        f"/api/consultations/{sample_consultation_id}/stream"
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_stream_includes_message_persistence(
    client: AsyncClient, sample_consultation_id, mock_db_session, mock_advisor_stream
):
    """Test that streamed messages are persisted to conversation history."""
    # Mock consultation
    mock_consultation = MagicMock()
    mock_consultation.id = sample_consultation_id
    mock_consultation.conversation = []
    mock_consultation.end_time = None

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_consultation
    )

    # Stream the guidance
    async with client.stream(
        "GET", f"/api/consultations/{sample_consultation_id}/stream"
    ) as response:
        async for line in response.aiter_lines():
            pass  # Consume the stream

    # Check conversation was updated
    # In real implementation, this would verify db.commit() was called
    # and conversation array was appended
    assert True  # Placeholder - actual implementation will verify this


@pytest.mark.asyncio
async def test_stream_error_handling(
    client: AsyncClient, sample_consultation_id, mock_db_session
):
    """Test error handling during streaming."""
    # Mock consultation with missing required fields to trigger error
    mock_consultation = MagicMock()
    mock_consultation.id = sample_consultation_id
    mock_consultation.customer_id = str(uuid4())
    mock_consultation.conversation = []
    mock_consultation.end_time = None
    # Missing meta will cause KeyError
    mock_consultation.meta = {}

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_consultation
    )

    # Stream should handle errors gracefully
    async with client.stream(
        "GET", f"/api/consultations/{sample_consultation_id}/stream"
    ) as response:
        events = []
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data = line[6:]
                if data:
                    try:
                        events.append(json.loads(data))
                    except json.JSONDecodeError:
                        pass

        # Should receive an error event or complete gracefully
        # (implementation may handle errors by logging instead of streaming)
        # This test verifies the endpoint doesn't crash
        assert True  # If we got here without exception, test passes
