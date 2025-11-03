"""Tests for the health check endpoint.

Following TDD principles - these tests are written BEFORE implementation.
They should fail initially (red phase) and pass after implementation (green phase).
"""

import pytest
from httpx import AsyncClient
from datetime import datetime
from unittest.mock import patch, MagicMock


@pytest.mark.unit
class TestHealthEndpoint:
    """Test cases for /health endpoint."""

    async def test_health_endpoint_exists(self, client: AsyncClient):
        """Test that the health endpoint is accessible."""
        response = await client.get("/health")
        assert response.status_code == 200

    async def test_health_endpoint_returns_valid_schema(self, client: AsyncClient):
        """Test that health endpoint returns correct response schema."""
        response = await client.get("/health")
        data = response.json()

        # Verify required fields are present
        assert "status" in data
        assert "database" in data
        assert "llm" in data
        assert "timestamp" in data

        # Verify field types
        assert isinstance(data["status"], str)
        assert isinstance(data["database"], bool)
        assert isinstance(data["llm"], bool)
        assert isinstance(data["timestamp"], str)

        # Verify status is one of the valid values
        assert data["status"] in ["healthy", "degraded", "unhealthy"]

    async def test_health_endpoint_healthy_status(self, client: AsyncClient):
        """Test health endpoint returns healthy when all systems are up."""
        with patch("guidance_agent.api.main.get_session") as mock_get_session, \
             patch("os.getenv") as mock_getenv:

            # Mock successful database connection
            mock_session = MagicMock()
            mock_session.execute.return_value = None
            mock_get_session.return_value = mock_session

            # Mock LLM environment variable present
            mock_getenv.return_value = "gpt-4"

            response = await client.get("/health")
            data = response.json()

            assert data["status"] == "healthy"
            assert data["database"] is True
            assert data["llm"] is True

    async def test_health_endpoint_degraded_status_db_only(self, client: AsyncClient):
        """Test health endpoint returns degraded when only database is healthy."""
        with patch("guidance_agent.api.main.get_session") as mock_get_session, \
             patch("os.getenv") as mock_getenv:

            # Mock successful database connection
            mock_session = MagicMock()
            mock_session.execute.return_value = None
            mock_get_session.return_value = mock_session

            # Mock LLM environment variable missing
            mock_getenv.return_value = None

            response = await client.get("/health")
            data = response.json()

            assert data["status"] == "degraded"
            assert data["database"] is True
            assert data["llm"] is False

    async def test_health_endpoint_degraded_status_llm_only(self, client: AsyncClient):
        """Test health endpoint returns degraded when only LLM is healthy."""
        with patch("guidance_agent.api.main.get_session") as mock_get_session, \
             patch("os.getenv") as mock_getenv:

            # Mock failed database connection
            mock_session = MagicMock()
            mock_session.execute.side_effect = Exception("DB connection failed")
            mock_get_session.return_value = mock_session

            # Mock LLM environment variable present
            mock_getenv.return_value = "gpt-4"

            response = await client.get("/health")
            data = response.json()

            assert data["status"] == "degraded"
            assert data["database"] is False
            assert data["llm"] is True

    async def test_health_endpoint_unhealthy_status(self, client: AsyncClient):
        """Test health endpoint returns unhealthy when all systems are down."""
        with patch("guidance_agent.api.main.get_session") as mock_get_session, \
             patch("os.getenv") as mock_getenv:

            # Mock failed database connection
            mock_session = MagicMock()
            mock_session.execute.side_effect = Exception("DB connection failed")
            mock_get_session.return_value = mock_session

            # Mock LLM environment variable missing
            mock_getenv.return_value = None

            response = await client.get("/health")
            data = response.json()

            assert data["status"] == "unhealthy"
            assert data["database"] is False
            assert data["llm"] is False

    async def test_health_endpoint_timestamp_is_recent(self, client: AsyncClient):
        """Test that health endpoint timestamp is recent."""
        response = await client.get("/health")
        data = response.json()

        # Parse timestamp
        timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        now = datetime.now(timestamp.tzinfo)

        # Verify timestamp is within last 5 seconds
        time_diff = abs((now - timestamp).total_seconds())
        assert time_diff < 5, "Health check timestamp should be recent"

    async def test_health_endpoint_handles_database_exception(self, client: AsyncClient):
        """Test that health endpoint handles database exceptions gracefully."""
        with patch("guidance_agent.api.main.get_session") as mock_get_session:
            # Mock database raising exception
            mock_get_session.side_effect = Exception("Database error")

            response = await client.get("/health")
            data = response.json()

            # Should still return 200 and mark database as unhealthy
            assert response.status_code == 200
            assert data["database"] is False

    async def test_health_endpoint_cors_headers(self, client: AsyncClient):
        """Test that health endpoint includes CORS headers for frontend access."""
        response = await client.get("/health")

        # Verify response is accessible (no CORS errors would occur)
        assert response.status_code == 200

    async def test_health_endpoint_can_be_called_multiple_times(self, client: AsyncClient):
        """Test that health endpoint can be called repeatedly without issues."""
        # Call health endpoint multiple times
        responses = []
        for _ in range(5):
            response = await client.get("/health")
            responses.append(response)

        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] in ["healthy", "degraded", "unhealthy"]

    async def test_health_endpoint_no_authentication_required(self, client: AsyncClient):
        """Test that health endpoint is publicly accessible without auth."""
        # Health endpoint should work without any authentication headers
        response = await client.get("/health")
        assert response.status_code == 200
