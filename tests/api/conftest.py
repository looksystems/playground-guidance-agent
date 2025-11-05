"""Pytest fixtures for API tests."""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock

# Note: mock_advisor_agent and mock_compliance_validator are now in tests/fixtures/llm_mocks.py
# and imported automatically via pytest_plugins in tests/conftest.py


@pytest.fixture
def mock_db_session():
    """Mock database session for API tests."""
    session = MagicMock()
    # Setup common query chain methods
    session.query.return_value = session
    session.filter.return_value = session
    session.order_by.return_value = session
    session.offset.return_value = session
    session.limit.return_value = session
    session.first.return_value = None
    session.all.return_value = []
    session.count.return_value = 0
    return session


@pytest.fixture
async def client(mock_db_session, mock_advisor_agent):
    """Create test client with mocked dependencies."""
    # Import here to avoid circular dependencies
    from guidance_agent.api.main import app
    from guidance_agent.api.dependencies import get_db, get_advisor_agent

    # Override dependencies
    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_advisor_agent] = lambda: mock_advisor_agent

    # Create async client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
async def client_with_real_db(mock_advisor_agent):
    """Create test client with real database for integration tests."""
    # Import here to avoid circular dependencies
    from guidance_agent.api.main import app
    from guidance_agent.api.dependencies import get_advisor_agent

    # Only override advisor agent, use real database
    app.dependency_overrides[get_advisor_agent] = lambda: mock_advisor_agent

    # Create async client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def sample_advisor_profile():
    """Sample advisor profile."""
    from guidance_agent.core.types import AdvisorProfile

    return AdvisorProfile(
        name="Sarah",
        description="Pension guidance specialist",
        specialization="pension_consolidation",
    )
