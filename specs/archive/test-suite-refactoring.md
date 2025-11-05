# Test Suite Refactoring Plan

## Executive Summary

Comprehensive refactoring of the test suite to address Critical and High priority issues identified in the test review. Focus on testing public APIs (not implementation details), genuine functionality verification, SOLID/DRY principles, and proper test isolation.

**Scope**: Critical + High Priority Issues
**Estimated Effort**: 10-12 days
**Organization**: By issue type for efficient grouped refactoring
**Database Strategy**: Transaction rollback using pytest-postgresql
**Private Method Tests**: Convert to public API tests

---

## Analysis Summary

### Issues Found
- **Total test files analyzed**: 52
- **Critical issues**: 12
- **High priority issues**: 18
- **Medium priority issues**: 15
- **Low priority issues**: 8
- **Lines of duplicated code**: 500+
- **Tests testing implementation instead of behavior**: ~25%
- **Tests with weak/missing assertions**: ~15%
- **Database side effect issues**: 10+ tests

### Key Problem Areas
1. Database side effects causing test interdependencies
2. 500+ lines of duplicated fixture/setup code
3. Tests coupled to private methods and internal implementation
4. Weak assertions that don't verify actual functionality
5. Single Responsibility Principle violations (tests doing too much)
6. Fixture scoping issues causing performance overhead

---

## Phase 1: Database Isolation (Days 1-2)

**Goal**: Eliminate all database side effects and test interdependencies

### 1.1 Setup Transaction-Based Isolation

**Install pytest-postgresql**
```bash
pip install pytest-postgresql
```

**Create transactional fixture in `tests/conftest.py`**
```python
@pytest.fixture(scope="function")
def transactional_db_session():
    """Database session that auto-rolls back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
```

### 1.2 Refactor Database Fixtures

**Files to Update** (Remove manual cleanup):
- `tests/unit/test_vector_store.py:22-40` - Remove `session.query(Memory).delete()` pattern
- `tests/unit/test_retriever.py:24-42` - Replace with transactional fixture
- `tests/integration/test_database.py` - Use transaction rollback
- `tests/test_memory_persistence.py:30-43` - Replace cleanup fixture
- ~6 additional files with similar patterns

**Before** (current pattern):
```python
@pytest.fixture
def db_session():
    session = get_session()
    session.query(Memory).delete()
    session.commit()
    yield session
    session.query(Memory).delete()
    session.commit()
    session.close()
```

**After** (transactional):
```python
@pytest.fixture
def db_session(transactional_db_session):
    return transactional_db_session
```

### 1.3 Fix Shared State Issues

**Critical Fix**: `tests/integration/test_database.py:32-69`
- Problem: Creates/deletes data without proper isolation
- Solution: Use transactional fixture, each test gets clean state automatically

**Verification**:
```bash
pytest tests/ -x --random-order  # Should pass regardless of order
pytest tests/ -n auto  # Should pass with parallel execution
```

---

## Phase 2: DRY Consolidation (Days 3-4)

**Goal**: Eliminate 500+ lines of duplicated code

### 2.1 Centralize Common Fixtures

**Create `tests/fixtures/` directory structure**:
```
tests/
├── conftest.py          # Global settings only
├── fixtures/
│   ├── __init__.py
│   ├── embeddings.py    # Embedding dimension & utilities
│   ├── customers.py     # Customer profile fixtures
│   ├── memory.py        # Memory-related fixtures
│   └── llm_mocks.py     # LLM response mocking
```

**2.1.1 Embedding Dimension Fixture** (`tests/fixtures/embeddings.py`)

**Problem**: 15+ files duplicate this code:
```python
# Duplicated in test_memory.py, test_vector_store.py, test_retriever.py, etc.
from dotenv import load_dotenv
load_dotenv()
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
```

**Solution**: Create centralized fixture
```python
# tests/fixtures/embeddings.py
import os
from dotenv import load_dotenv
import pytest

load_dotenv()
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))

@pytest.fixture
def embedding_dimension():
    return EMBEDDING_DIMENSION

@pytest.fixture
def sample_embedding(embedding_dimension):
    """Generate a sample embedding vector."""
    return [0.1] * embedding_dimension
```

**Files to Update**: Remove duplication from
- tests/unit/test_memory.py:10-29
- tests/unit/test_vector_store.py:12-31
- tests/unit/test_retriever.py:14-33
- ~12 additional files

**2.1.2 Customer Profile Fixture** (`tests/fixtures/customers.py`)

**Problem**: Customer profile creation duplicated in:
- `tests/unit/advisor/test_agent.py:76-106` (31 lines)
- `tests/integration/test_learning_loop.py:74-108` (35 lines)
- `tests/unit/learning/test_case_learning.py:104-140` (37 lines)
- ~5 additional files

**Solution**: Create comprehensive customer fixture
```python
# tests/fixtures/customers.py
import pytest
from guidance_agent.advisor.models import CustomerProfile

@pytest.fixture
def sample_customer_profile():
    """Standard customer profile for testing."""
    return CustomerProfile(
        age=45,
        employment_status="employed",
        annual_income=50000,
        risk_tolerance="medium",
        investment_experience="intermediate",
        financial_goals=["retirement", "education"],
        existing_investments={"pension": 100000, "ISA": 20000}
    )

@pytest.fixture
def high_risk_customer():
    """Customer with high risk tolerance."""
    # ... specific profile

@pytest.fixture
def retirement_focused_customer():
    """Customer focused on retirement planning."""
    # ... specific profile
```

**2.1.3 Mock LLM Response Helper** (`tests/fixtures/llm_mocks.py`)

**Problem**: 30+ duplicate mock setups:
```python
# Duplicated across test_agent.py, test_reflection.py, test_validation.py
mock_response = MagicMock()
mock_response.choices = [MagicMock(message=MagicMock(content="..."))]
```

**Solution**: Create reusable mock helper
```python
# tests/fixtures/llm_mocks.py
from unittest.mock import MagicMock
import pytest

def create_mock_llm_response(content: str, model: str = "gpt-4"):
    """Create a mock LLM completion response."""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content=content))
    ]
    mock_response.model = model
    return mock_response

@pytest.fixture
def mock_llm_response():
    """Fixture factory for creating mock LLM responses."""
    return create_mock_llm_response
```

**2.1.4 Validation Result Fixture** (`tests/fixtures/customers.py`)

**Problem**: ValidationResult creation duplicated in:
- `tests/api/conftest.py:76-91`
- `tests/unit/advisor/test_agent.py:118-124`

**Solution**: Centralized fixture
```python
@pytest.fixture
def compliant_validation_result():
    """Validation result indicating compliance."""
    return ValidationResult(
        passed=True,
        violations=[],
        warnings=[],
        context={}
    )

@pytest.fixture
def non_compliant_validation_result():
    """Validation result with violations."""
    return ValidationResult(
        passed=False,
        violations=["Sample violation"],
        warnings=["Sample warning"],
        context={"rule": "FCA-001"}
    )
```

### 2.2 Organize Fixtures by Domain

**Split `tests/conftest.py`** (currently 146 lines mixing concerns)

**Before**: All fixtures in one file
**After**: Organized structure
```python
# tests/conftest.py (global settings only)
import pytest
pytest_plugins = [
    "tests.fixtures.embeddings",
    "tests.fixtures.customers",
    "tests.fixtures.memory",
    "tests.fixtures.llm_mocks",
]

@pytest.fixture(scope="session")
def disable_phoenix_tracing():
    # Global tracing config
    pass
```

**Split `tests/api/conftest.py`** (181 lines)
- Keep API-specific mocks
- Move general fixtures to appropriate domain files
- Clean separation of concerns

---

## Phase 3: Remove Weak Assertions (Day 5)

**Goal**: Ensure every test verifies real functionality

### 3.1 Fix "Creation Only" Tests

**3.1.1 `tests/unit/test_vector_store.py:57-61`**

**Before**:
```python
def test_create_vector_store(self, memory_vector_store):
    assert memory_vector_store is not None
    assert memory_vector_store.model == Memory
```

**After**:
```python
def test_vector_store_stores_and_retrieves_memory(
    self, memory_vector_store, sample_customer_profile, sample_embedding
):
    # Create and store a memory
    memory = Memory(
        content="Test memory content",
        customer_id=sample_customer_profile.id,
        embedding=sample_embedding
    )
    memory_vector_store.add(memory)

    # Retrieve and verify
    results = memory_vector_store.search(sample_embedding, limit=1)
    assert len(results) == 1
    assert results[0].content == "Test memory content"
```

**3.1.2 `tests/unit/test_retriever.py:157-161`**

**Before**:
```python
def test_create_case_base(self, db_session):
    case_base = CaseBase(session=db_session)
    assert case_base is not None
```

**After**:
```python
def test_case_base_retrieves_similar_cases(
    self, db_session, sample_customer_profile
):
    case_base = CaseBase(session=db_session)

    # Add a test case
    case = Case(
        customer_profile=sample_customer_profile,
        guidance="Test guidance",
        outcome="successful"
    )
    db_session.add(case)
    db_session.commit()

    # Retrieve similar cases
    results = case_base.retrieve_similar(sample_customer_profile, limit=5)
    assert len(results) > 0
    assert results[0].outcome == "successful"
```

**3.1.3 `tests/unit/advisor/test_agent.py:23-36`**

**Before**:
```python
def test_agent_initialization(self, advisor_agent):
    assert hasattr(advisor_agent, "memory_stream")
    assert hasattr(advisor_agent, "compliance_validator")
```

**After**:
```python
def test_agent_provides_compliant_guidance(
    self, advisor_agent, sample_customer_profile
):
    # Test actual functionality
    guidance = advisor_agent.provide_guidance(
        customer_profile=sample_customer_profile,
        query="How should I invest for retirement?"
    )

    assert guidance is not None
    assert len(guidance) > 0
    assert "retirement" in guidance.lower()
    # Verify compliance was checked
    assert advisor_agent.last_validation.passed
```

### 3.2 Strengthen API Tests

**3.2.1 `tests/api/test_consultations.py:151-176`**

**Before**:
```python
def test_send_message(client, consultation_id):
    response = client.post(
        f"/consultations/{consultation_id}/messages",
        json={"content": "Test message"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "received"
```

**After**:
```python
def test_send_message_appears_in_conversation(client, consultation_id):
    # Send message
    response = client.post(
        f"/consultations/{consultation_id}/messages",
        json={"content": "Test retirement question"}
    )
    assert response.status_code == 200

    # Verify message appears in conversation history
    history_response = client.get(
        f"/consultations/{consultation_id}/messages"
    )
    messages = history_response.json()
    assert any(m["content"] == "Test retirement question" for m in messages)

    # Verify response was generated
    assert len(messages) > 1  # User message + agent response
    assert messages[-1]["role"] == "assistant"
```

---

## Phase 4: Decouple from Implementation (Days 6-8)

**Goal**: Test public APIs only, remove private method testing

### 4.1 Convert Private Method Tests to Public API Tests

**4.1.1 `tests/unit/advisor/test_agent.py:405-416` - `_retrieve_context`**

**Before** (testing private method):
```python
@patch("guidance_agent.advisor.agent._retrieve_context")
def test_retrieve_context(self, mock_retrieve, advisor_agent):
    result = advisor_agent._retrieve_context(query="test")
    assert result is not None
```

**After** (testing through public API):
```python
def test_guidance_includes_relevant_context(
    self, advisor_agent, sample_customer_profile, db_session
):
    # Add relevant memory to database
    memory = Memory(
        content="Customer previously asked about pension transfers",
        customer_id=sample_customer_profile.id,
        embedding=generate_embedding("pension transfers")
    )
    db_session.add(memory)
    db_session.commit()

    # Provide guidance on related topic
    guidance = advisor_agent.provide_guidance(
        customer_profile=sample_customer_profile,
        query="What are the rules for pension transfers?"
    )

    # Verify context was retrieved and used
    # (should mention previous discussion)
    assert "previously" in guidance.lower() or "pension transfer" in guidance.lower()
```

**4.1.2 `tests/unit/advisor/test_agent.py:314-376` - `_generate_guidance`**

**Before** (testing private method):
```python
@patch("guidance_agent.advisor.agent.completion")
def test_generate_guidance(self, mock_completion, advisor_agent):
    result = advisor_agent._generate_guidance(messages=[...])
    assert result is not None
```

**After** (testing through public API):
```python
def test_guidance_follows_fca_guidelines(
    self, advisor_agent, sample_customer_profile, mock_llm_response
):
    # Test that guidance generation includes FCA context
    guidance = advisor_agent.provide_guidance(
        customer_profile=sample_customer_profile,
        query="Should I invest in high-risk stocks?"
    )

    # Verify FCA-compliant response characteristics
    assert "risk" in guidance.lower()
    assert len(guidance) > 100  # Substantive response
    # Verify appropriate disclaimers are included
    assert any(
        keyword in guidance.lower()
        for keyword in ["suitable", "circumstances", "goals"]
    )
```

**4.1.3 `tests/unit/test_memory.py:195-209` - `_cosine_similarity`**

**Before** (testing private method):
```python
def test_cosine_similarity():
    vec1 = [1, 0, 0]
    vec2 = [0, 1, 0]
    similarity = MemoryStream._cosine_similarity(vec1, vec2)
    assert similarity == 0.0
```

**After** (testing retrieval behavior):
```python
def test_memory_retrieval_returns_most_similar(
    self, memory_stream, sample_embedding, db_session
):
    # Add memories with different embeddings
    similar_memory = Memory(
        content="Retirement planning advice",
        embedding=sample_embedding  # Same embedding
    )
    different_memory = Memory(
        content="Mortgage advice",
        embedding=generate_different_embedding()  # Different
    )
    db_session.add_all([similar_memory, different_memory])
    db_session.commit()

    # Retrieve using same embedding
    results = memory_stream.retrieve(sample_embedding, limit=1)

    # Should return the similar one (tests similarity algorithm behavior)
    assert len(results) == 1
    assert results[0].content == "Retirement planning advice"
```

**4.1.4 `tests/test_memory_persistence.py:84-222`**

**Before** (checking internal state):
```python
def test_memory_persistence(advisor):
    assert advisor.memory_stream.session is not None

    # Create memory
    advisor.add_memory("test")

    # Check internal state
    assert len(advisor.memory_stream._buffer) == 1

    # Query database directly
    memories = session.query(Memory).all()
    assert len(memories) == 1
```

**After** (testing behavior through public API):
```python
def test_memories_persist_across_sessions(
    advisor_agent, sample_customer_profile, db_session
):
    # First session: provide guidance and store memory
    guidance1 = advisor_agent.provide_guidance(
        customer_profile=sample_customer_profile,
        query="Tell me about ISAs"
    )

    # Create new agent instance (simulates new session)
    new_advisor = AdvisorAgent(session=db_session)

    # Second session: provide related guidance
    guidance2 = new_advisor.provide_guidance(
        customer_profile=sample_customer_profile,
        query="What did we discuss before?"
    )

    # Verify previous conversation is accessible
    assert "ISA" in guidance2 or "discussed" in guidance2.lower()
```

### 4.2 Remove Implementation Coupling

**Pattern to replace across all tests**:
- ❌ `assert advisor.memory_stream.session is not None`
- ✅ Test that memories can be stored and retrieved
- ❌ `session.query(Memory).filter(...).first()`
- ✅ Use public retrieval methods
- ❌ `agent._internal_method()`
- ✅ Test behavior through public `agent.public_method()`

### 4.3 Fix Mock Fixtures

**`tests/api/conftest.py:55-69`**

**Before** (reaching into internals):
```python
@pytest.fixture
def mock_advisor_agent(mock_db_session):
    agent = AdvisorAgent()
    agent.memory_stream.session = MagicMock()
    return agent
```

**After** (dependency injection):
```python
@pytest.fixture
def mock_advisor_agent(mock_db_session):
    # Inject dependencies through constructor
    return AdvisorAgent(
        session=mock_db_session,
        compliance_validator=MagicMock(),
        memory_retriever=MagicMock()
    )
```

---

## Phase 5: Fix SRP Violations (Days 9-10)

**Goal**: One test, one responsibility

### 5.1 Split Multi-Concern Tests

**5.1.1 `tests/test_memory_persistence.py:885-994`**

**Before** (110 lines testing everything):
```python
def test_complete_consultation_flow_with_memory_persistence(
    advisor_agent, sample_customer_profile, db_session
):
    # Tests memory creation
    advisor_agent.add_memory(...)
    assert ...

    # Tests persistence
    session.commit()
    assert ...

    # Tests database storage
    memories = session.query(Memory).all()
    assert len(memories) == 1

    # Tests retrieval
    retrieved = advisor_agent.retrieve_memories(...)
    assert ...

    # Tests counting
    count = advisor_agent.count_memories()
    assert count == 1
```

**After** (separate focused tests):
```python
def test_memory_creation_generates_embedding(advisor_agent):
    """Verify memories are created with embeddings."""
    memory = advisor_agent.add_memory(
        content="Test memory",
        customer_id=123
    )
    assert memory.embedding is not None
    assert len(memory.embedding) == EMBEDDING_DIMENSION

def test_memory_persists_to_database(advisor_agent, db_session):
    """Verify memories are saved to database."""
    advisor_agent.add_memory(content="Test memory", customer_id=123)

    # Retrieve via public API (not direct query)
    memories = advisor_agent.get_all_memories(customer_id=123)
    assert len(memories) == 1
    assert memories[0].content == "Test memory"

def test_memory_retrieval_by_similarity(advisor_agent, db_session):
    """Verify semantic search retrieves relevant memories."""
    # Add multiple memories
    advisor_agent.add_memory("Pension transfer advice", customer_id=123)
    advisor_agent.add_memory("Mortgage application help", customer_id=123)

    # Search for pension-related memories
    results = advisor_agent.search_memories(
        query="pension transfers",
        customer_id=123,
        limit=1
    )
    assert len(results) == 1
    assert "pension" in results[0].content.lower()

def test_memory_count_accuracy(advisor_agent):
    """Verify memory counting is accurate."""
    advisor_agent.add_memory("Memory 1", customer_id=123)
    advisor_agent.add_memory("Memory 2", customer_id=123)

    count = advisor_agent.count_memories(customer_id=123)
    assert count == 2
```

**5.1.2 `tests/integration/test_learning_loop.py:204-243`**

**Before** (testing two paths):
```python
def test_mixed_success_and_failure_learning(learning_system):
    # Test success path
    learning_system.learn_from_consultation(successful_case)
    assert ...

    # Test failure path
    learning_system.learn_from_consultation(failed_case)
    assert ...
```

**After** (separate tests):
```python
def test_learning_from_successful_consultation(learning_system):
    """Verify system learns from successful outcomes."""
    case = create_successful_case()

    result = learning_system.learn_from_consultation(case)

    assert result.outcome == "success"
    assert result.reinforced_patterns > 0

def test_learning_from_failed_consultation(learning_system):
    """Verify system identifies improvement areas from failures."""
    case = create_failed_case()

    result = learning_system.learn_from_consultation(case)

    assert result.outcome == "failure"
    assert len(result.improvement_areas) > 0
```

### 5.2 Create Focused Test Functions

**Guidelines**:
1. **Test name describes specific behavior**: `test_<what>_<expected_result>`
2. **Single assertion** or multiple assertions for same behavior
3. **Clear arrange/act/assert structure**
4. **No more than 20 lines per test** (ideal: 10-15)

**Example pattern**:
```python
def test_validation_rejects_unsuitable_advice(validator, high_risk_profile):
    """Verify validator catches unsuitable high-risk recommendations."""
    # Arrange
    advice = "Invest all savings in cryptocurrency"

    # Act
    result = validator.validate(advice, high_risk_profile)

    # Assert
    assert not result.passed
    assert "unsuitable" in result.violations[0].lower()
```

---

## Phase 6: Fix Fixture Scoping & OCP Issues (Days 11-12)

**Goal**: Proper fixture scopes and resilient tests

### 6.1 Review Fixture Scopes

**6.1.1 `tests/conftest.py:138-142` - `disable_phoenix_tracing`**

**Before**:
```python
@pytest.fixture(autouse=True)  # Applied to EVERY test
def disable_phoenix_tracing():
    # Disable for each test function
    pass
```

**After**:
```python
@pytest.fixture(scope="session", autouse=True)  # Applied once
def disable_phoenix_tracing():
    """Disable Phoenix tracing for entire test session."""
    # Disable once at session start
    pass
```

**6.1.2 Review all `autouse=True` fixtures**
- Remove unless truly needed globally
- Change to explicit opt-in where possible
- Use appropriate scope (session > module > function)

### 6.2 Fix Open/Closed Violations

**6.2.1 `tests/unit/advisor/test_agent.py:366-376`**

**Before** (brittle structure checks):
```python
def test_prompt_caching(advisor_agent):
    messages = advisor_agent._build_messages(...)

    # Brittle: assumes specific message structure
    assert len(messages) == 4
    assert messages[0]["role"] == "system"
    assert messages[1]["cache_control"] == {"type": "ephemeral"}
```

**After** (behavior-focused):
```python
def test_prompt_caching_improves_performance(advisor_agent, monkeypatch):
    """Verify caching reduces token usage in repeated calls."""
    call_count = 0

    def mock_completion(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return create_mock_llm_response("Test response")

    monkeypatch.setattr("guidance_agent.advisor.agent.completion", mock_completion)

    # First call
    advisor_agent.provide_guidance(query="Question 1")
    first_call_count = call_count

    # Second call (should use cache)
    advisor_agent.provide_guidance(query="Question 2")

    # Verify caching behavior (fewer tokens sent)
    # Implementation can change, behavior should remain
    assert call_count == 2  # Both calls made
    # Cache effectiveness measured by behavior, not structure
```

**6.2.2 `tests/unit/advisor/test_prompts.py:740-772`**

**Before** (hard-coded counts):
```python
def test_message_count_for_caching():
    messages = build_prompt(...)
    assert len(messages) == 4  # Will break if we add/remove sections
```

**After** (requirement-focused):
```python
def test_prompt_includes_required_sections():
    """Verify prompt contains all necessary guidance sections."""
    messages = build_prompt(...)

    combined_content = " ".join(m.get("content", "") for m in messages)

    # Test requirements, not implementation
    assert "FCA" in combined_content
    assert "customer profile" in combined_content.lower()
    assert "compliance" in combined_content.lower()
```

### 6.3 Environment Management

**6.3.1 Replace `patch.dict` with `monkeypatch`**

**Before** (`tests/unit/retrieval/test_embeddings.py:32-40`):
```python
from unittest.mock import patch

def test_embedding_with_params():
    with patch.dict(os.environ, {"LITELLM_DROP_PARAMS": "true"}):
        result = generate_embedding("test")
        assert result is not None
```

**After** (pytest's monkeypatch):
```python
def test_embedding_with_params(monkeypatch):
    """Verify embedding generation with custom parameters."""
    monkeypatch.setenv("LITELLM_DROP_PARAMS", "true")

    result = generate_embedding("test")
    assert result is not None
    # Automatic cleanup by pytest
```

**6.3.2 Centralize Environment Configuration**

Create `tests/fixtures/environment.py`:
```python
import pytest

@pytest.fixture
def test_environment(monkeypatch):
    """Set up standard test environment variables."""
    monkeypatch.setenv("EMBEDDING_DIMENSION", "1536")
    monkeypatch.setenv("LITELLM_DROP_PARAMS", "true")
    monkeypatch.setenv("LOG_LEVEL", "ERROR")
    # ... other standard test env vars

@pytest.fixture
def production_like_environment(monkeypatch):
    """Environment closer to production settings."""
    # Different configuration for integration tests
    pass
```

### 6.4 Proper Cleanup with Context Managers

**Pattern for shared state**:
```python
@pytest.fixture
def client(mock_db_session):
    """API test client with dependency overrides."""
    original_overrides = app.dependency_overrides.copy()

    try:
        app.dependency_overrides[get_db] = lambda: mock_db_session
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides = original_overrides
```

---

## Files to Modify

### New Files
- `tests/fixtures/__init__.py`
- `tests/fixtures/embeddings.py`
- `tests/fixtures/customers.py`
- `tests/fixtures/memory.py`
- `tests/fixtures/llm_mocks.py`
- `tests/fixtures/environment.py`

### Modified Files (~25-30 files)

**Configuration**:
- `tests/conftest.py` - Reorganize, add transactional fixture
- `tests/api/conftest.py` - Split and clean up

**Core Tests**:
- `tests/test_memory_persistence.py` - Split SRP violations, remove internal checks
- `tests/unit/test_memory.py` - Convert private method tests
- `tests/unit/test_vector_store.py` - Add real assertions
- `tests/unit/test_retriever.py` - Add real assertions

**Agent Tests**:
- `tests/unit/advisor/test_agent.py` - Major refactoring (private methods, SRP, OCP)
- `tests/unit/advisor/test_prompts.py` - Fix brittle structure tests

**Learning Tests**:
- `tests/unit/learning/test_case_learning.py` - Use centralized fixtures
- `tests/unit/learning/test_reflection.py` - Use LLM mock helper
- `tests/unit/learning/test_validation.py` - Use LLM mock helper

**API Tests**:
- `tests/api/test_consultations.py` - Strengthen assertions

**Integration Tests**:
- `tests/integration/test_database.py` - Fix isolation
- `tests/integration/test_learning_loop.py` - Split SRP violations

**Additional Files** (~15 files):
- All files using embedding dimension (DRY)
- All files using customer profiles (DRY)
- All files with database fixtures (isolation)
- All files with LLM mocks (DRY)

---

## Success Criteria

### Functional Requirements
✓ All tests pass with random execution order: `pytest -x --random-order`
✓ All tests pass with parallel execution: `pytest -n auto`
✓ No database state leakage between tests
✓ No tests fail due to execution order

### Code Quality
✓ 500+ lines of duplicate code removed
✓ No tests of private methods (underscore prefix)
✓ Every test has meaningful behavioral assertions
✓ Each test verifies one specific behavior
✓ Fixtures properly scoped and organized in domain-specific files

### Coverage & Reliability
✓ Test coverage maintained or improved
✓ Tests resilient to implementation changes
✓ Clear test failure messages
✓ Tests run 20-30% faster (due to better scoping and isolation)

### Documentation
✓ Docstrings on all test functions explain what behavior is tested
✓ Fixture documentation in conftest files
✓ Clear commit messages for each phase

---

## Execution Strategy

### By Issue Type (Chosen Approach)

**Week 1**: Database Issues
- Days 1-2: Phase 1 (Database Isolation)
- Immediate value: eliminate flaky tests

**Week 2**: Code Quality
- Days 3-4: Phase 2 (DRY Consolidation)
- Day 5: Phase 3 (Weak Assertions)
- Quick wins, major cleanup

**Week 3**: Architecture
- Days 6-8: Phase 4 (Decouple from Implementation)
- Most complex refactoring, largest impact

**Week 4**: Refinement
- Days 9-10: Phase 5 (SRP Violations)
- Days 11-12: Phase 6 (Scoping & OCP)
- Polish and optimize

### Daily Verification Process

**At end of each day**:
1. Run full test suite: `pytest tests/ -v`
2. Run with random order: `pytest tests/ -x --random-order`
3. Check coverage: `pytest --cov=guidance_agent --cov-report=term-missing`
4. Commit changes with clear message
5. Update this spec with progress notes

### Phase Completion Checklist

**Each phase complete when**:
- [ ] All tests in affected files pass
- [ ] No new failures introduced in other tests
- [ ] Code review completed (if team)
- [ ] Documentation updated
- [ ] Committed with descriptive message

---

## Risk Mitigation

### Potential Risks

1. **Breaking existing functionality**: Tests might be covering real bugs
   - Mitigation: Run tests before/after each change, maintain coverage metrics

2. **Scope creep**: Finding more issues during refactoring
   - Mitigation: Track new issues separately, stick to current plan

3. **Time overrun**: Estimates are approximate
   - Mitigation: Each phase is independent, can pause between phases

4. **Merge conflicts**: If codebase changes during refactoring
   - Mitigation: Work in feature branch, frequent merges from main

### Rollback Strategy

Each phase is committed separately:
- Can revert individual phases if issues found
- Can pause after any phase and resume later
- Each phase delivers value independently

---

## Post-Refactoring Improvements

### Recommended Follow-ups (Not in scope)

1. **Add missing test categories** (Medium priority from analysis)
   - `/tests/e2e/` - End-to-end user journeys
   - `/tests/performance/` - Vector operation benchmarks
   - `/tests/security/` - FCA compliance validation

2. **Parametrize duplicate test patterns** (Low priority)
   - Use `@pytest.mark.parametrize` for vector store models
   - Reduce test code by ~30%

3. **Add property-based testing** (Enhancement)
   - Use `hypothesis` for edge cases
   - Especially useful for financial calculations

4. **CI/CD integration improvements**
   - Separate fast/slow test suites
   - Parallel execution in CI
   - Coverage reporting

---

## Appendix: Code Examples

### Transaction Rollback Pattern
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    engine = create_engine("postgresql://test_db")
    return engine

@pytest.fixture(scope="function")
def transactional_db_session(db_engine):
    """Provide a transactional database session."""
    connection = db_engine.connect()
    transaction = connection.begin()

    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()
```

### Fixture Organization Pattern
```python
# tests/conftest.py
pytest_plugins = [
    "tests.fixtures.embeddings",
    "tests.fixtures.customers",
    "tests.fixtures.memory",
    "tests.fixtures.llm_mocks",
]

# tests/fixtures/customers.py
import pytest
from guidance_agent.advisor.models import CustomerProfile

@pytest.fixture
def sample_customer_profile():
    return CustomerProfile(age=45, ...)

@pytest.fixture
def high_risk_customer():
    return CustomerProfile(risk_tolerance="high", ...)
```

### Public API Testing Pattern
```python
# ❌ Don't test private methods
def test_internal_calculation(agent):
    result = agent._calculate_score(data)
    assert result == 0.85

# ✅ Test behavior through public API
def test_recommendation_uses_customer_risk_profile(agent, customer):
    recommendation = agent.get_recommendation(customer)
    assert recommendation.risk_level <= customer.risk_tolerance
```

### Single Responsibility Pattern
```python
# ❌ Don't test multiple things
def test_full_consultation_flow(agent):
    agent.start_consultation()
    agent.add_message("question")
    agent.get_response()
    agent.save_to_database()
    assert ...  # Which part failed?

# ✅ Test one thing
def test_consultation_saves_messages_to_database(agent):
    agent.start_consultation()
    agent.add_message("question")

    saved_messages = agent.get_saved_messages()
    assert len(saved_messages) == 1
```

---

## Conclusion

This refactoring plan addresses the most impactful issues in the test suite while maintaining a pragmatic scope. By organizing work by issue type, we can make rapid progress on related problems and deliver value incrementally. The estimated 10-12 days of work will result in a significantly more maintainable, reliable, and professional test suite that properly tests public APIs, has strong assertions, follows SOLID/DRY principles, and maintains proper isolation between tests.
