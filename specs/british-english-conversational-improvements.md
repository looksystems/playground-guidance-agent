# British English & Conversational Improvements

**Status**: Planned
**Date**: 2025-11-06

## Overview

This document outlines planned improvements to ensure:
1. British English spelling and phrases throughout the system
2. Natural conversational flow without task-based structure
3. Emotional arc tracking across full conversations

## 1. British English Spelling Changes (29 instances)

### Templates (5 files)

**`src/guidance_agent/templates/advisor/guidance_with_reasoning.jinja`**
- Line 15: "analyzed" → "analysed"

**`src/guidance_agent/templates/advisor/guidance_cached.jinja`**
- Line 2: "optimized" → "optimised"
- Line 8: "optimizes" → "optimises"

**`src/guidance_agent/templates/compliance/validation.jinja`**
- Line 69: "behavior" → "behaviour"

**`src/guidance_agent/templates/customer/response.jinja`**
- Line 48: "behavior" → "behaviour"

**`src/guidance_agent/templates/learning/reflection.jinja`**
- Line 4: "analyzes" → "analyses"

### Python Files (9 files)

**`src/guidance_agent/customer/agent.py`**
- Line 1: "behavior" → "behaviour" (docstring)
- Line 17: "behavior" → "behaviour" (docstring)

**`src/guidance_agent/advisor/prompts.py`**
- Line 188: "optimized" → "optimised"
- Line 190: "maximize" → "maximise"

**`src/guidance_agent/learning/case_learning.py`**
- Line 76: Function name `summarize_customer_situation` → `summarise_customer_situation`
- Line 83: Parameter docstring "summarize" → "summarise"
- Line 89: Example docstring "summarize" → "summarise"
- Line 167: Function call `summarize_customer_situation` → `summarise_customer_situation`

**`src/guidance_agent/learning/__init__.py`**
- Line 14: Import `summarize_customer_situation` → `summarise_customer_situation`
- Line 36: `__all__` entry "summarize_customer_situation" → "summarise_customer_situation"

**`src/guidance_agent/learning/reflection.py`**
- Line 28: "analyze" → "analyse"

**`src/guidance_agent/evaluation/__init__.py`**
- Line 26: Import `analyze_confidence_calibration` → `analyse_confidence_calibration`
- Line 46: `__all__` entry "analyze_confidence_calibration" → "analyse_confidence_calibration"

**`src/guidance_agent/evaluation/judge_validation.py`**
- Line 265: Function name `analyze_confidence_calibration` → `analyse_confidence_calibration`
- Line 286: Example docstring "analyze" → "analyse"
- Line 393: Function call `analyze_confidence_calibration` → `analyse_confidence_calibration`

**`src/guidance_agent/api/routers/admin.py`**
- Line 258: Description "analyze" → "analyse"
- Line 409: Description "analyze" → "analyse"
- Line 486: Description "analyze" → "analyse"

**`src/guidance_agent/knowledge/pension_knowledge.py`**
- Line 198: "maximize_income" → "maximise_income"
- Line 212: "favored" → "favoured"

**`src/guidance_agent/advisor/agent.py`**
- Line 796: "optimize" → "optimise"
- Line 797: "maximize" → "maximise"

## 2. Remove Task-Based Structure

### Problem

Current templates structure responses as numbered tasks:
```
TASK:
Provide appropriate pension guidance that:
1. Addresses the customer's specific question
2. Uses language appropriate for their literacy level
3. Presents balanced information (pros and cons)
4. Stays clearly within the FCA guidance boundary
5. Checks customer understanding
```

This encourages the advisor to treat each point as a separate heading/section rather than a flowing dialogue.

### Solution

**Files to update:**
- `src/guidance_agent/templates/advisor/guidance_main.jinja` (lines ~136-144)
- `src/guidance_agent/templates/advisor/guidance_with_reasoning.jinja` (lines ~136-144)
- `src/guidance_agent/templates/advisor/guidance_cached.jinja` (system prompt section)

**Replace numbered task list with:**
```jinja
Respond to the customer's message in a natural, conversational way that addresses their question whilst:
- Using language appropriate for their context
- Presenting balanced information where relevant
- Staying within FCA guidance boundaries
- Naturally checking understanding when exploring complex topics

Treat this as a flowing dialogue between two people, not a structured information delivery. Let the conversation develop naturally whilst satisfying these requirements throughout the exchange.
```

### Additional Fix: Remove Contradictory Phrase

**Also remove from "Varied Phrasing Alternatives" section** (line ~55 in each template):
- "Some people in your situation find it helpful to..."

This phrase appears in both the "varied phrasing" section AND the FCA prohibition section, which is contradictory. It should only appear in the prohibition section since it evaluates customer circumstances.

## 3. Emotional Arc Tracking

### Problem

Current implementation only assesses emotional state from the last customer message:

**File:** `src/guidance_agent/advisor/agent.py` (lines ~334-340)
```python
customer_messages = [
    msg["content"]
    for msg in conversation_history
    if msg.get("role") == "user"
]
last_customer_message = customer_messages[-1] if customer_messages else ""
emotional_state = assess_emotional_state(last_customer_message)
```

This misses emotional evolution across the conversation (e.g., customer starting anxious but becoming more confident).

### Solution

**Change to pass full conversation context:**
```python
# Use full conversation for emotional arc
customer_messages = [
    msg["content"]
    for msg in conversation_history
    if msg.get("role") == "user"
]
full_customer_context = "\n".join(customer_messages) if customer_messages else ""
emotional_state = assess_emotional_state(full_customer_context)
```

**Also update:** `src/guidance_agent/advisor/prompts.py` - Update `assess_emotional_state` function docstring to reflect it now receives full conversation context instead of a single message.

## 4. Verification Notes

### Current State (Confirmed Working)

✅ **Conversation History**: Already passing full conversation history to the LLM
- `consultations.py:310-315` extracts full history from consultation
- `agent.py:193-215` passes it to prompt builder
- `guidance_main.jinja:115-117` includes it in the prompt

✅ **Financial Literacy**: Advisor does NOT explicitly mention literacy levels to customers
- Literacy is used internally to adapt language complexity
- No instances of "Given your medium financial literacy..." in templates

✅ **Session Memory**: Working memory system with vector retrieval
- Stores observations and reflections with importance scoring
- Retrieved based on semantic similarity to current question

### Testing After Changes

```bash
# Template regression tests
pytest tests/templates/

# Integration tests
pytest tests/integration/

# Advisor-specific tests
pytest tests/advisor/

# Full test suite
pytest

# Frontend tests
cd frontend && npm test
```

**Manual verification:**
- Check generated responses use British English
- Confirm conversational flow without task headings
- Test emotional state assessment across multi-turn conversations
- Verify function renames work correctly (`summarise_*`, `analyse_*`)

## Impact Assessment

### Low Risk Changes
- Spelling corrections (no logic changes)
- Template instruction rewording (same intent, clearer guidance)

### Medium Risk Changes
- Function renames (`summarize` → `summarise`, `analyze` → `analyse`)
  - Need to update all imports and call sites
  - Comprehensive test coverage should catch issues

### Testing Priority
1. Template rendering tests (most likely to catch issues)
2. Integration tests (end-to-end advisor flow)
3. Function call sites (renamed functions)

## Implementation Notes

### British English Conventions
- -ise endings: optimise, maximise, analyse, summarise
- -our endings: behaviour, favour
- -ed participles: analysed (not analyzed)

### Conversational Flow Principles
- Natural dialogue between two people
- Requirements satisfied throughout exchange, not as checklist
- Signposting and transitions for clarity
- Avoid repetitive phrasing patterns
- Phase-appropriate tone (opening/middle/closing)

### Emotional Intelligence
- Track emotional evolution across conversation
- Detect patterns: anxious → confident, confused → understanding
- Adapt responses to current emotional state
- Use full conversation context for assessment
