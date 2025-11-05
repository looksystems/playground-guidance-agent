# Phase 2 TDD Tests - Database Schema Changes

## Overview

This document summarizes the TDD tests created for Phase 2 of the conversational improvement plan.

## Test Files Created

### 1. `test_consultation_conversational_fields.py`

Tests for two new fields in the `Consultation` model:

#### `conversational_quality` field
- **Type**: Float
- **Nullable**: True
- **Range**: 0.0 to 1.0
- **Purpose**: Store quality score for conversational naturalness

**Tests (13 total):**
- `test_consultation_has_conversational_quality_field` - Field exists and accepts values
- `test_consultation_conversational_quality_accepts_float_range` - Accepts 0.0-1.0 range
- `test_consultation_conversational_quality_is_nullable` - Can be None by default
- `test_consultation_conversational_quality_can_be_set_to_none` - Can explicitly set to None
- `test_consultation_conversational_quality_can_be_updated` - Can be updated after creation
- `test_consultation_query_by_conversational_quality` - Can query by quality score
- `test_consultation_conversational_quality_type_validation` - Type validation works

#### `dialogue_patterns` field
- **Type**: JSONB
- **Nullable**: True
- **Purpose**: Store captured dialogue techniques and patterns used

**Tests:**
- `test_consultation_has_dialogue_patterns_field` - Field exists and stores JSON
- `test_consultation_dialogue_patterns_is_nullable` - Can be None by default
- `test_consultation_dialogue_patterns_stores_complex_json` - Stores complex nested structures
- `test_consultation_dialogue_patterns_can_be_updated` - Can be updated after creation
- `test_consultation_dialogue_patterns_empty_dict` - Can be empty dict
- `test_consultation_both_new_fields_together` - Both fields work together

### 2. `test_case_conversational_fields.py`

Tests for one new field in the `Case` model:

#### `dialogue_techniques` field
- **Type**: JSONB
- **Nullable**: True
- **Purpose**: Store successful conversational techniques used in the case

**Tests (11 total):**
- `test_case_has_dialogue_techniques_field` - Field exists and stores JSON
- `test_case_dialogue_techniques_is_nullable` - Can be None by default
- `test_case_dialogue_techniques_stores_complex_json` - Stores complex nested structures
- `test_case_dialogue_techniques_can_be_updated` - Can be updated after creation
- `test_case_dialogue_techniques_empty_dict` - Can be empty dict
- `test_case_dialogue_techniques_with_existing_fields` - Works with existing Case fields
- `test_case_query_by_dialogue_techniques_presence` - Can query by presence/absence
- `test_case_dialogue_techniques_json_querying` - Can query nested JSON values
- `test_case_dialogue_techniques_with_array_fields` - Stores and retrieves arrays
- `test_case_dialogue_techniques_supports_nested_dicts` - Supports nested dicts
- `test_case_retrieve_multiple_cases_with_dialogue_techniques` - Multiple cases work correctly

## Test Results

### Expected Results (TDD - Tests Should FAIL)

Both test suites are currently **FAILING** as expected:

#### Consultation Tests: 13/13 FAILED ✓
```
TypeError: 'conversational_quality' is an invalid keyword argument for Consultation
TypeError: 'dialogue_patterns' is an invalid keyword argument for Consultation
AttributeError: 'Consultation' object has no attribute 'conversational_quality'
AttributeError: 'Consultation' object has no attribute 'dialogue_patterns'
```

#### Case Tests: 11/11 FAILED ✓
```
TypeError: 'dialogue_techniques' is an invalid keyword argument for Case
AttributeError: 'Case' object has no attribute 'dialogue_techniques'
```

**This is the correct TDD behavior** - tests are written first and fail because the implementation doesn't exist yet.

## What These Tests Validate

### Consultation Model Tests
1. ✅ Field existence and basic functionality
2. ✅ Nullable behavior (can be None)
3. ✅ Data type validation (Float for quality, JSONB for patterns)
4. ✅ Value range validation (0.0-1.0 for quality)
5. ✅ Complex JSON structure storage
6. ✅ Update operations
7. ✅ Query operations (filtering by quality score)
8. ✅ Both fields working together

### Case Model Tests
1. ✅ Field existence and basic functionality
2. ✅ Nullable behavior (can be None)
3. ✅ Data type validation (JSONB)
4. ✅ Complex JSON structure storage (nested dicts, arrays)
5. ✅ Update operations
6. ✅ Query operations (presence, nested values)
7. ✅ Integration with existing Case fields
8. ✅ Multiple cases with different techniques

## Example JSON Structures

### Consultation.dialogue_patterns
```json
{
  "signposting_used": true,
  "personalization_level": "high",
  "engagement_level": "high",
  "effective_phrases": [
    "Let me break this down for you",
    "Here's what this means"
  ],
  "conversation_phase": "middle",
  "tone_adjustments": {
    "empathy_level": "high",
    "formality": "professional"
  },
  "question_types": ["open-ended", "confirmatory"],
  "transition_count": 5,
  "name_usage_count": 3
}
```

### Case.dialogue_techniques
```json
{
  "successful_patterns": [
    "Used signposting effectively",
    "Natural transitions between topics"
  ],
  "effective_phrases": [
    "Let me break this down for you, John",
    "Building on what you mentioned"
  ],
  "engagement_approach": "high",
  "personalization_style": "high",
  "conversation_phases": ["opening", "middle", "closing"],
  "tone_adjustments": {
    "empathy_level": "high",
    "formality": "professional-friendly",
    "pacing": "moderate"
  },
  "metrics": {
    "signpost_count": 5,
    "name_usage_count": 3,
    "question_count": 7,
    "transition_phrases": 4
  }
}
```

## Next Steps

1. **Update Models** (`src/guidance_agent/core/database.py`)
   - Add `conversational_quality` field to Consultation model
   - Add `dialogue_patterns` field to Consultation model
   - Add `dialogue_techniques` field to Case model

2. **Create Migration**
   ```bash
   alembic revision --autogenerate -m "add_conversational_quality_fields"
   alembic upgrade head
   ```

3. **Run Tests Again**
   ```bash
   uv run pytest tests/unit/models/test_consultation_conversational_fields.py -v
   uv run pytest tests/unit/models/test_case_conversational_fields.py -v
   ```

   After implementation, all 24 tests should **PASS**.

## Test Patterns Used

These tests follow existing codebase patterns:

1. **Fixtures**: Use `transactional_db_session` for database isolation
2. **Async tests**: All tests are async with `@pytest.mark.asyncio`
3. **UUID generation**: Use `uuid4()` for IDs
4. **Timezone-aware datetimes**: Use `datetime.now(timezone.utc)`
5. **Comprehensive assertions**: Test both positive and edge cases
6. **Query testing**: Test SQLAlchemy query operations

## Coverage

The tests cover:
- ✅ Basic CRUD operations
- ✅ Nullable behavior
- ✅ Type validation
- ✅ Range validation (for quality score)
- ✅ Complex JSON structures
- ✅ Nested objects and arrays
- ✅ Query operations (filtering, presence checks)
- ✅ Integration with existing fields
- ✅ Update operations
- ✅ Edge cases (empty dicts, None values)

---

**Status**: Tests written and failing (TDD Phase 1 complete)
**Next**: Implement model changes and migration (TDD Phase 2)
