"""Mock LLM response fixtures and helpers."""

import pytest
from unittest.mock import MagicMock, AsyncMock


def create_mock_llm_response(content: str, model: str = "gpt-4") -> MagicMock:
    """Create a mock LLM completion response.

    Args:
        content: The text content of the response
        model: The model name to include in the response

    Returns:
        A MagicMock object with the structure of an OpenAI chat completion response
    """
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content=content))
    ]
    mock_response.model = model
    mock_response.usage = MagicMock(
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
    )
    return mock_response


def create_mock_streaming_response(chunks: list[str], model: str = "gpt-4"):
    """Create a mock streaming LLM response.

    Args:
        chunks: List of text chunks to stream
        model: The model name to include in the response

    Returns:
        An async generator that yields mock streaming chunks
    """
    async def stream_generator():
        for chunk_text in chunks:
            chunk = MagicMock()
            chunk.choices = [
                MagicMock(delta=MagicMock(content=chunk_text))
            ]
            chunk.model = model
            yield chunk

    return stream_generator()


@pytest.fixture
def mock_llm_response():
    """Fixture factory for creating mock LLM responses.

    Usage in tests:
        def test_something(mock_llm_response):
            response = mock_llm_response("Hello, world!")
            assert response.choices[0].message.content == "Hello, world!"
    """
    return create_mock_llm_response


@pytest.fixture
def mock_streaming_response():
    """Fixture factory for creating mock streaming LLM responses.

    Usage in tests:
        def test_streaming(mock_streaming_response):
            stream = mock_streaming_response(["Hello", " ", "world"])
            chunks = [chunk async for chunk in stream]
    """
    return create_mock_streaming_response


@pytest.fixture
def mock_advisor_agent():
    """Mock AdvisorAgent for testing."""
    from guidance_agent.core.types import AdvisorProfile, RetrievedContext

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

    # Mock memory_stream (public interface only)
    agent.memory_stream = MagicMock()
    agent.memory_stream.retrieve.return_value = []
    agent.memory_stream.add = MagicMock()
    agent.memory_stream.get_memory_count = MagicMock(return_value=0)
    agent.memory_stream.session = None  # No DB session by default

    # Mock compliance_validator (public interface)
    agent.compliance_validator = MagicMock()

    from guidance_agent.compliance.validator import (
        ValidationResult,
        ValidationIssue,
        IssueType,
        IssueSeverity,
    )

    agent.compliance_validator.validate.return_value = ValidationResult(
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
        reasoning="The guidance provided stays within FCA boundaries for guidance vs advice.",
    )

    async def mock_validate_async(*args, **kwargs):
        return ValidationResult(
            passed=True,
            confidence=0.97,
            issues=[],
            requires_human_review=False,
            reasoning="The guidance provided stays within FCA boundaries for guidance vs advice.",
        )

    agent.compliance_validator.validate_async = mock_validate_async

    # Mock private methods that API endpoints use
    # These are internal implementation details but necessary for testing

    def mock_retrieve_context(customer):
        """Mock context retrieval."""
        return RetrievedContext(
            cases=[],
            rules=[],
            memories=[],
        )

    agent._retrieve_context = mock_retrieve_context

    async def mock_validate_and_record_async(guidance, customer, context):
        """Mock async validation with recording."""
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
            reasoning="The guidance provided stays within FCA boundaries for guidance vs advice.",
        )

    agent._validate_and_record_async = mock_validate_and_record_async

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
