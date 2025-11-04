"""Pytest fixtures for API tests."""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4


@pytest.fixture
def mock_db_session():
    """Mock database session."""
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
def mock_advisor_agent():
    """Mock AdvisorAgent for testing."""
    from guidance_agent.core.types import AdvisorProfile

    agent = MagicMock()

    # Set profile with real values
    agent.profile = AdvisorProfile(
        name="Sarah",
        description="Test advisor",
        specialization="pension_consolidation",
    )

    # Mock synchronous provide_guidance
    agent.provide_guidance.return_value = "This is test guidance from the advisor."

    # Mock async streaming
    async def mock_stream(*args, **kwargs):
        chunks = [
            "I understand ",
            "your question. ",
            "Here is ",
            "my guidance.",
        ]
        for chunk in chunks:
            yield chunk

    agent.provide_guidance_stream = mock_stream

    # Mock memory_stream with session attribute
    agent.memory_stream = MagicMock()
    agent.memory_stream.session = MagicMock()  # Mock session so checks pass
    agent.memory_stream.retrieve.return_value = []  # Return empty list for retrievals
    agent.memory_stream.add = MagicMock()  # Mock add method

    # Mock _retrieve_context
    from guidance_agent.core.types import RetrievedContext

    agent._retrieve_context.return_value = RetrievedContext(
        memories=[],
        cases=[],
        rules=[],
        fca_requirements="Test FCA requirements",
    )

    # Mock _validate_and_record_async
    async def mock_validate(*args, **kwargs):
        from guidance_agent.compliance.validator import ValidationResult, ValidationIssue, IssueType, IssueSeverity

        # Return a full ValidationResult with reasoning and issues
        return ValidationResult(
            passed=True,
            confidence=0.97,
            issues=[
                ValidationIssue(
                    issue_type=IssueType.CLARITY,
                    severity=IssueSeverity.LOW,
                    description="Consider adding more detail about risk factors",
                )
            ],
            requires_human_review=False,
            reasoning="The guidance provided stays within FCA boundaries for guidance vs advice. "
                      "It provides factual information without making specific recommendations. "
                      "Risk disclosures are adequate. Clarity is generally good with minor room for improvement.",
        )

    agent._validate_and_record_async = mock_validate

    return agent


@pytest.fixture
def mock_compliance_validator():
    """Mock ComplianceValidator."""
    validator = MagicMock()

    # Mock validation result
    mock_result = MagicMock()
    mock_result.passed = True
    mock_result.confidence = 0.97
    mock_result.requires_human_review = False
    mock_result.issues = []

    validator.validate.return_value = mock_result
    validator.validate_async.return_value = mock_result

    return validator


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
def sample_customer_profile_dict():
    """Sample customer profile as dict."""
    return {
        "customer_id": str(uuid4()),
        "demographics": {
            "age": 52,
            "gender": "male",
            "location": "London",
            "employment_status": "employed",
            "financial_literacy": "medium",
        },
        "presenting_question": "Can I combine my pensions?",
        "goals": "Simplify pension management",
    }


@pytest.fixture
def sample_advisor_profile():
    """Sample advisor profile."""
    from guidance_agent.core.types import AdvisorProfile

    return AdvisorProfile(
        name="Sarah",
        description="Pension guidance specialist",
        specialization="pension_consolidation",
    )
