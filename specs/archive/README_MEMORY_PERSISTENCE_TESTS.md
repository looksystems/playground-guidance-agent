# Memory Persistence Tests

## Overview

Comprehensive test suite for the memory persistence system in `guidance-agent`, created following Test-Driven Development (TDD) principles. These tests validate all scenarios outlined in the `specs/memory-system-fix.md` specification.

## Test File Location

```
tests/test_memory_persistence.py
```

## Test Coverage

The test suite contains **28 comprehensive tests** organized into 8 test classes:

### 1. TestAdvisorAgentMemoryPersistence (5 tests)
Tests for AdvisorAgent memory persistence integration:
- ✅ `test_advisor_agent_initialized_with_database_session` - Verifies MemoryStream has DB session when AdvisorAgent is created with one
- ✅ `test_advisor_agent_initialized_without_database_session` - Verifies in-memory-only mode when no session provided
- ✅ `test_advisor_agent_memory_persists_to_database` - Validates memories are saved to database
- ✅ `test_advisor_agent_memory_not_persisted_without_session` - Ensures memories stay in-memory only without session
- ✅ `test_advisor_agent_loads_existing_memories_from_database` - Tests memory loading across agent restarts

### 2. TestConsultationMemoryCreation (3 tests)
Tests for memory creation during consultations:
- ✅ `test_customer_message_creates_memory_node` - Customer messages create observation memories
- ✅ `test_advisor_response_creates_memory_node` - Advisor responses create reflection memories
- ✅ `test_multiple_conversation_turns_create_multiple_memories` - Full conversation creates multiple memories

### 3. TestMemoryImportanceThresholds (4 tests)
Tests for importance-based memory filtering:
- ✅ `test_high_importance_memory_is_stored` - High-importance memories are persisted
- ✅ `test_low_importance_memory_can_be_filtered` - Application logic can filter low-importance items
- ✅ `test_importance_threshold_for_customer_observations` - Customer messages use 0.3 threshold
- ✅ `test_importance_threshold_for_advisor_insights` - Advisor responses use 0.5 threshold

### 4. TestMemoryEmbeddings (3 tests)
Tests for embedding generation and storage:
- ✅ `test_memory_has_embedding` - Embeddings are stored with correct dimensions (768)
- ✅ `test_embedding_enables_similarity_search` - Semantic search works with embeddings
- ✅ `test_embedding_generation_integration` - Integration with `embed()` function

### 5. TestMemoryPersistenceErrorHandling (5 tests)
Tests for error handling scenarios:
- ✅ `test_persistence_failure_raises_exception` - DB failures raise exceptions
- ✅ `test_persistence_failure_rolls_back_transaction` - Failed commits trigger rollback
- ✅ `test_in_memory_operation_continues_on_persistence_failure` - In-memory operations work despite DB failures
- ✅ `test_invalid_embedding_dimension_handling` - Handles wrong embedding dimensions
- ✅ `test_null_embedding_handling` - Supports null embeddings

### 6. TestMemoryRetrievalFromDatabase (3 tests)
Tests for retrieving persisted memories:
- ✅ `test_retrieve_memories_after_agent_restart` - Memories survive agent destruction/recreation
- ✅ `test_retrieve_memories_with_filters` - Filter by memory type (observation, reflection)
- ✅ `test_retrieve_recent_memories_from_database` - Time-based filtering works

### 7. TestImportanceRating (3 tests)
Tests for the `rate_importance()` function:
- ✅ `test_rate_importance_returns_normalized_score` - Scores normalized to 0-1 range
- ✅ `test_rate_importance_high_value_content` - Important content gets high scores (>0.7)
- ✅ `test_rate_importance_low_value_content` - Casual content gets low scores (<0.3)

### 8. TestCompleteIntegrationScenarios (2 tests)
End-to-end integration tests:
- ✅ `test_complete_consultation_flow_with_memory_persistence` - Full consultation with memory creation
- ✅ `test_memory_continuity_across_multiple_consultations` - Memories accumulate across consultations

## Fixtures

### Database Fixtures
- **`db_session`** - Test database session with automatic cleanup before/after each test
- **`mock_db_session`** - Mocked session for testing error handling

### Profile Fixtures
- **`advisor_profile`** - Sample `AdvisorProfile` for creating test agents

### Embedding Fixtures
- **`mock_embedding`** - Mock 768-dimension embedding vector (matches `.env` config)

## Running the Tests

### Run all memory persistence tests:
```bash
source .venv/bin/activate
pytest tests/test_memory_persistence.py -v
```

### Run specific test class:
```bash
pytest tests/test_memory_persistence.py::TestAdvisorAgentMemoryPersistence -v
```

### Run specific test:
```bash
pytest tests/test_memory_persistence.py::TestAdvisorAgentMemoryPersistence::test_advisor_agent_memory_persists_to_database -v
```

### Run with detailed output:
```bash
pytest tests/test_memory_persistence.py -v --tb=short
```

## Test Results

All 28 tests passing:
```
======================== 28 passed, 1 warning in 0.23s =========================
```

## Key Implementation Details

### Embedding Dimensions
- Tests use **768 dimensions** (configured via `EMBEDDING_DIMENSION` env var)
- Automatically adapts to environment configuration
- Database schema supports pgvector with configurable dimensions

### Timezone Handling
- Tests use timezone-aware datetimes where required
- Some tests use timezone-naive datetimes to match implementation
- Properly handles both scenarios

### Mock Objects
- Uses `unittest.mock` for mocking LLM responses
- Properly structured mock responses matching LiteLLM format
- Mocks database sessions for error testing

### Error Handling
- Tests verify exception raising and rollback behavior
- Tests validate graceful degradation scenarios
- Covers database failures, invalid data, and edge cases

## Spec Compliance

This test suite covers all scenarios from `specs/memory-system-fix.md`:

1. ✅ Memories persisted when AdvisorAgent initialized with database session
2. ✅ Memories NOT persisted when AdvisorAgent has no session (in-memory only)
3. ✅ Customer messages create MemoryNode objects during consultations
4. ✅ Advisor responses create MemoryNode objects during consultations
5. ✅ Memories retrieved from database in subsequent consultations
6. ✅ Memory importance thresholds (filtering low-importance items)
7. ✅ Embeddings generated for memories
8. ✅ Error handling when memory persistence fails

## Dependencies

Tests require:
- `pytest` - Test framework
- `sqlalchemy` - Database ORM
- `unittest.mock` - Mocking framework
- `numpy` - For embedding comparison
- Database with pgvector extension

## Notes

- Tests use actual database connections (not fully mocked)
- Each test includes cleanup to prevent test pollution
- Tests are idempotent and can run in any order
- Comprehensive docstrings explain each test scenario
- Follows pytest best practices and naming conventions

## Future Enhancements

Potential additions to the test suite:
- Performance tests for large memory datasets
- Concurrency tests for parallel memory operations
- Integration tests with actual LLM API calls
- Benchmark tests for memory retrieval speed
- Tests for memory consolidation and pruning
