"""Shared pytest fixtures for tests."""

import pytest
from guidance_agent.core import AgentConfig
from guidance_agent.core.database import engine, SessionLocal

# Import all domain-specific fixtures
pytest_plugins = [
    "tests.fixtures.embeddings",
    "tests.fixtures.customers",
    "tests.fixtures.memory",
    "tests.fixtures.llm_mocks",
    "tests.fixtures.template_data",
]


@pytest.fixture(scope="function")
def transactional_db_session():
    """Database session that auto-rolls back after each test.

    This fixture provides complete test isolation by:
    1. Creating a new connection and transaction
    2. Binding a session to that transaction
    3. Rolling back the transaction after the test completes

    This means all database changes are automatically discarded,
    ensuring tests don't affect each other.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def agent_config():
    """Create a sample agent configuration."""
    return AgentConfig(
        name="Test Agent",
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=1000,
    )


@pytest.fixture(scope="session", autouse=True)
def disable_phoenix_tracing():
    """Disable Phoenix tracing for entire test session.

    Session-scoped to avoid redundant setup for every test function.
    This is a one-time configuration that applies to the entire test run.

    Note: We use os.environ directly instead of monkeypatch because
    monkeypatch is function-scoped and can't be used with session scope.
    """
    import os
    original_value = os.environ.get("PHOENIX_AUTO_SETUP")
    os.environ["PHOENIX_AUTO_SETUP"] = "false"

    yield

    # Restore original value after session
    if original_value is None:
        os.environ.pop("PHOENIX_AUTO_SETUP", None)
    else:
        os.environ["PHOENIX_AUTO_SETUP"] = original_value
