# TDD Test Suite for Conversational Flow Improvements - Summary

## Overview

Created comprehensive Test Driven Development (TDD) test suite for implementing the conversational flow improvements documented in:
**`specs/british-english-conversational-improvements.md` Section 2**

## Test File Created

**`tests/test_conversational_flow.py`**
- 26 tests across 8 test classes
- Tests verify natural conversational prompts instead of numbered task lists
- Tests check for removal of contradictory phrases
- Tests ensure British English conventions

## Current Test Results (Expected Failures)

**Result**: 12 FAILED, 14 PASSED

This is **exactly as expected** - tests fail because templates still have the old task-based structure.

### Failed Tests (12) - Need Implementation

These failures indicate what needs to be fixed in the templates:

#### 1. Numbered Task Lists (6 failures)
```
FAILED test_guidance_main_no_numbered_task_list
FAILED test_guidance_reasoning_no_numbered_task_list
FAILED test_guidance_cached_no_numbered_task_list
FAILED test_guidance_main_task_heading_not_followed_by_numbered_list
FAILED test_guidance_reasoning_task_heading_not_followed_by_numbered_list
FAILED test_guidance_cached_no_numbered_list_in_final_instruction
```

**Issue**: All 3 templates contain numbered lists (1. 2. 3. etc.)
- `guidance_main.jinja`: 9 numbered items found
- `guidance_with_reasoning.jinja`: 10 numbered items found
- `guidance_cached.jinja`: 5 numbered items in user message

**Example from guidance_main.jinja (lines 136-144)**:
```jinja
TASK:
Provide appropriate pension guidance that:
1. Addresses the customer's specific question
2. Uses language appropriate for their literacy level
3. Presents balanced information (pros and cons)
4. Stays clearly within the FCA guidance boundary
5. Checks customer understanding
```

**Required Change**: Replace with conversational instruction using bullet points:
```jinja
Respond to the customer's message in a natural, conversational way that addresses their question whilst:
- Using language appropriate for their context
- Presenting balanced information where relevant
- Staying within FCA guidance boundaries
- Naturally checking understanding when exploring complex topics

Treat this as a flowing dialogue between two people, not a structured information delivery.
```

#### 2. Missing Conversational Language (3 failures)
```
FAILED test_guidance_main_has_natural_conversational_language
FAILED test_guidance_main_instructs_flowing_dialogue_not_checklist
FAILED test_guidance_main_replaces_task_heading_with_conversational_instruction
```

**Issue**: Templates don't contain key phrases:
- "natural, conversational way"
- "flowing dialogue"
- "Let the conversation develop naturally"

#### 3. Contradictory Phrase (1 failure)
```
FAILED test_guidance_main_no_contradictory_phrase_in_varied_phrasing
```

**Issue**: `guidance_main.jinja` line ~55 has contradictory phrase:

**Varied Phrasing section** (SHOULD BE REMOVED):
```
- "Some people in your situation find it helpful to..."
```

**FCA Prohibition section** (SHOULD REMAIN):
```
❌ PROHIBITED:
- "Some people in your situation find it helpful to..."
```

This phrase appears in BOTH recommended phrasing AND prohibited phrasing sections - contradictory!

**Fix**: Remove from "Varied Phrasing Alternatives" section (keep only in prohibition section).

#### 4. Requirements Structure (2 failures)
```
FAILED test_guidance_main_has_balanced_information_without_list
FAILED test_guidance_main_has_fca_boundary_without_list
```

**Issue**: Requirements like "balanced information" and "FCA boundaries" appear in numbered lists.

**Fix**: Convert to bullet points or natural prose, not numbered items.

### Passed Tests (14) - Already Compliant

These tests pass, indicating templates already have some correct elements:

1. ✅ FCA Neutrality sections maintained in all templates
2. ✅ Customer profile and context sections maintained
3. ✅ Contradictory phrase correctly appears in prohibition section
4. ✅ Templates reference "conversation" and "dialogue"
5. ✅ Task section positioned near end of templates
6. ✅ Templates contain "naturally" in some contexts
7. ✅ Templates mention ongoing requirements

## Test Classes

### 1. TestConversationalFlowStructure (3 tests)
Verifies no numbered task lists (1. 2. 3.) in templates.

### 2. TestConversationalLanguagePresence (5 tests)
Checks for new conversational language like "natural, conversational way" and "flowing dialogue".

### 3. TestContradictoryPhraseRemoval (3 tests)
Ensures "Some people in your situation" is removed from varied phrasing but remains in prohibition section.

### 4. TestConversationalFlowInstructions (5 tests)
Verifies templates instruct to treat as flowing dialogue, not structured checklist.

### 5. TestBulletPointsInsteadOfNumberedList (2 tests)
Checks that templates use bullet points (-) instead of numbered lists, and use British English "whilst".

### 6. TestKeyPhrasesPresence (3 tests)
Ensures specific key phrases from specs are present.

### 7. TestTemplateStructuralChanges (3 tests)
Verifies structural integrity - FCA sections maintained, context sections intact.

### 8. TestNoTaskHeadingWithNumberedList (3 tests)
Ensures TASK: heading is not followed by numbered list.

## What Needs to Be Done

### Templates to Update

1. **`src/guidance_agent/templates/advisor/guidance_main.jinja`**
   - Lines ~55: Remove "Some people in your situation" from Varied Phrasing section
   - Lines ~136-144: Replace numbered task list with conversational instruction

2. **`src/guidance_agent/templates/advisor/guidance_with_reasoning.jinja`**
   - Lines ~71-78: Replace numbered task list with conversational instruction

3. **`src/guidance_agent/templates/advisor/guidance_cached.jinja`**
   - Line ~59 (user message): Replace numbered task list with conversational instruction

### Replacement Text (from specs)

Replace numbered lists with:
```jinja
Respond to the customer's message in a natural, conversational way that addresses their question whilst:
- Using language appropriate for their context
- Presenting balanced information where relevant
- Staying within FCA guidance boundaries
- Naturally checking understanding when exploring complex topics

Treat this as a flowing dialogue between two people, not a structured information delivery. Let the conversation develop naturally whilst satisfying these requirements throughout the exchange.
```

## Running the Tests

```bash
# Run full test suite
uv run pytest tests/test_conversational_flow.py -v

# Run specific test class
uv run pytest tests/test_conversational_flow.py::TestConversationalFlowStructure -v

# Run with detailed output
uv run pytest tests/test_conversational_flow.py -v --tb=short
```

## Expected Outcome After Implementation

Once the templates are updated with conversational flow improvements:
- **All 26 tests should PASS**
- **0 failures**

The TDD approach ensures:
1. Clear specification of requirements
2. Automated verification of changes
3. Regression protection for future modifications
4. Documentation of expected behavior

## Additional Notes

### British English Conventions
Tests also check for British English usage:
- "whilst" instead of "while" in formal contexts
- Other British spellings (covered in separate tests)

### FCA Compliance Maintained
Tests verify that conversational improvements DON'T compromise FCA compliance:
- FCA Neutrality sections remain intact
- Prohibition examples preserved
- Compliance requirements still present (just not in numbered list format)

### Template Rendering
All templates will still render correctly - only the instruction wording changes, not the template structure or Jinja2 syntax.

## Test Development Approach

These tests follow TDD best practices:
1. **Red**: Tests fail initially (current state)
2. **Green**: Tests pass after implementation (target state)
3. **Refactor**: Templates improved while maintaining compliance

The comprehensive test coverage ensures nothing is broken during the refactoring process.
