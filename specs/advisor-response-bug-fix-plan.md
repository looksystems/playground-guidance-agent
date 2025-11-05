# Advisor Agent Response Bug - Fix Plan

## Executive Summary

**Date:** November 5, 2025
**Status:** Investigation Complete - Ready for Implementation
**Severity:** HIGH - Critical bug affecting multi-turn conversations
**Consultation ID:** `1f5971c7-d7a9-4219-a595-b98285e87b3a`

---

## Problem Statement

The advisor agent is responding with generic pension information instead of answering the customer's actual question. When a customer asks "what is pension consolidation?", the advisor provides a broad pension overview rather than addressing consolidation specifically.

### Root Cause

The `presenting_question` field in the `CustomerProfile` is **stale** - it uses the initial consultation query instead of the latest customer message. This causes the advisor to respond to old questions rather than current ones in multi-turn conversations.

---

## Investigation Findings

### 1. Actual Conversation Analysis

**Customer Question:**
```
"what is pension consolidation?"
```

**Advisor Response:**
The advisor responded with a generic pension overview instead of answering about pension consolidation. The response begins:

> "Given the customer's question, **'understanding,'** and considering the need for more specific information..."

Then provides general information about State Pension, Personal/Workplace Pensions, Contributions, etc.

**The advisor completely failed to address pension consolidation.**

### 2. Bug Location

**File:** `src/guidance_agent/api/routers/consultations.py` (lines 290-301)

```python
# Build customer profile from consultation
customer = CustomerProfile(
    customer_id=consultation.customer_id,
    demographics=CustomerDemographics(
        age=consultation.meta.get("customer_age", 50),
        gender="unknown",
        location="unknown",
        employment_status="unknown",
        financial_literacy="medium",
    ),
    presenting_question=consultation.meta.get("initial_query", ""),  # ❌ PROBLEM
)
```

**The Issue:**
- `presenting_question` is set to `consultation.meta.get("initial_query", "")`
- This is the **original question from consultation creation**, NOT the current message
- When customer asks follow-up questions, advisor still sees the old `presenting_question`

### 3. Template Usage

Both main prompt templates rely on `customer.presenting_question`:

**File:** `src/guidance_agent/templates/advisor/guidance_cached.jinja` (line 59)
```jinja2
Customer's current question: "{{ customer.presenting_question }}"
```

**File:** `src/guidance_agent/templates/advisor/guidance_main.jinja` (line 52)
```jinja2
CUSTOMER'S CURRENT QUESTION:
"{{ customer.presenting_question }}"
```

The templates emphasize the `presenting_question` field, but this field is stale and contains the initial query, not the latest customer message.

### 4. Secondary Issue: Compliance Validator

The compliance validator **passed** with 0.95 confidence despite the response being irrelevant:

```json
{
  "compliance_score": 0.95,
  "compliance_confidence": 0.95,
  "compliance_passed": true,
  "compliance_reasoning": "PASS - The guidance carefully avoids making specific recommendations..."
}
```

**Problem:** The validator only checks FCA compliance style, not whether the response actually addresses the customer's question.

---

## Implementation Plan

### Phase 1: Fix the Critical Bug ⭐ PRIORITY

**File:** `src/guidance_agent/api/routers/consultations.py`

**Changes to `stream_guidance()` endpoint:**

```python
# Get conversation history (exclude system messages)
conversation_history = [
    {"role": turn["role"], "content": turn["content"]}
    for turn in consultation.conversation
    if turn.get("role") != "system"
]

# Extract the most recent customer message as presenting_question
latest_customer_message = ""
for turn in reversed(consultation.conversation):
    if turn.get("role") == "customer":
        latest_customer_message = turn.get("content", "")
        break

# Build customer profile with CURRENT question
customer = CustomerProfile(
    customer_id=consultation.customer_id,
    demographics=CustomerDemographics(
        age=consultation.meta.get("customer_age", 50),
        gender="unknown",
        location="unknown",
        employment_status="unknown",
        financial_literacy="medium",
    ),
    presenting_question=latest_customer_message,  # ✅ USE CURRENT QUESTION
)
```

**Expected Outcome:**
- First customer message: `presenting_question` = first message
- Follow-up questions: `presenting_question` = latest message
- Advisor responds to the actual current question

### Phase 2: Review Other Endpoints

**Files to Check:**
- `src/guidance_agent/api/routers/consultations.py` - all endpoints that build `CustomerProfile`
- `create_consultation()` endpoint
- Any other API endpoints that might have similar stale data issues

**Action:**
- Search for all instances of `CustomerProfile` construction
- Ensure they use appropriate data sources
- Fix any similar bugs found

### Phase 3: Enhance Compliance Validator with Relevance Checking

**File:** `src/guidance_agent/compliance/validator.py`

**Add relevance assessment:**

```python
class ComplianceValidationResult(BaseModel):
    is_compliant: bool
    score: float
    reasoning: str
    issues_found: list[str]
    timestamp: datetime
    is_relevant: bool  # NEW
    relevance_score: float  # NEW
    relevance_reasoning: str  # NEW
```

**Update validation logic:**
1. Check FCA compliance (existing)
2. Check if response addresses customer's question (new)
3. Return combined result with both compliance and relevance

**File:** `src/guidance_agent/templates/compliance/validation.jinja2`

**Update prompt to include relevance check:**

```jinja2
{# Add after compliance check section #}

RELEVANCE ASSESSMENT:
Does the guidance actually address the customer's question?

Customer asked: "{{ customer_question }}"
Guidance provided: {{ guidance_text }}

Evaluate:
1. Does the response directly answer the customer's question?
2. Is the information provided relevant to what was asked?
3. Are there significant gaps or irrelevant tangents?

Provide:
- relevance_score (0.0-1.0)
- relevance_reasoning (explanation)
- is_relevant (true/false, threshold 0.7)
```

### Phase 4: Add Regression Tests

#### Backend Test 1: Multi-turn Conversation

**File:** `tests/api/test_consultations.py`

**New Test:**
```python
@pytest.mark.asyncio
async def test_multi_turn_conversation_context(client: AsyncClient):
    """Test that advisor responds to current question, not initial query."""

    # Create consultation with initial question
    response = await client.post("/api/consultations", json={
        "customer_id": 1,
        "initial_message": "I want to understand pensions"
    })
    assert response.status_code == 201
    consultation_id = response.json()["id"]

    # Ask follow-up question about specific topic
    response = await client.post(
        f"/api/consultations/{consultation_id}/messages",
        json={"content": "what is pension consolidation?"}
    )
    assert response.status_code == 200

    # Get advisor response
    # Stream guidance and collect response
    guidance_text = ""
    async for chunk in stream_response:
        guidance_text += chunk

    # Verify response addresses consolidation, not general pensions
    assert "consolidation" in guidance_text.lower()
    assert "combining" in guidance_text.lower() or "merge" in guidance_text.lower()

    # Verify it's not just generic pension info
    assert not guidance_text.startswith("Given the customer's question, 'understanding'")
```

#### Backend Test 2: Relevance Checking

**File:** `tests/compliance/test_validator.py` (create if doesn't exist)

**New Test:**
```python
@pytest.mark.asyncio
async def test_compliance_validator_relevance_check():
    """Test that validator detects irrelevant responses."""

    customer_question = "what is pension consolidation?"

    # Test Case 1: Irrelevant response
    irrelevant_guidance = """
    State Pension provides basic income in retirement.
    Personal pensions allow you to save for retirement.
    Workplace pensions are provided by employers.
    """

    result = await validate_compliance(
        guidance=irrelevant_guidance,
        customer_question=customer_question
    )

    assert result.is_relevant is False
    assert result.relevance_score < 0.7
    assert "consolidation" in result.relevance_reasoning.lower()

    # Test Case 2: Relevant response
    relevant_guidance = """
    Pension consolidation involves combining multiple pension pots
    into a single pension plan. This can help you manage your
    retirement savings more easily and potentially reduce fees.
    """

    result = await validate_compliance(
        guidance=relevant_guidance,
        customer_question=customer_question
    )

    assert result.is_relevant is True
    assert result.relevance_score >= 0.7
```

#### Frontend E2E Test

**File:** `frontend/tests/e2e/multi-turn-conversation.spec.ts`

**New Test:**
```typescript
import { test, expect } from '@playwright/test'

test('multi-turn conversation handles follow-up questions correctly', async ({ page }) => {
  await page.goto('/')

  // Start conversation with general question
  await page.fill('textarea', 'I want to understand pensions')
  await page.click('button:has-text("Send")')

  // Wait for advisor response
  await page.waitForSelector('.advisor-message', { timeout: 10000 })

  // Ask specific follow-up question
  await page.fill('textarea', 'what is pension consolidation?')
  await page.click('button:has-text("Send")')

  // Wait for advisor response
  await page.waitForSelector('.advisor-message:nth-of-type(2)', { timeout: 10000 })

  // Verify response addresses consolidation
  const secondResponse = await page.textContent('.advisor-message:nth-of-type(2)')
  expect(secondResponse?.toLowerCase()).toContain('consolidation')
  expect(secondResponse?.toLowerCase()).toMatch(/combin|merg/)

  // Verify it's not the generic pension overview
  expect(secondResponse).not.toContain("Given the customer's question, 'understanding'")
})
```

### Phase 5: Verify Fix with Existing Consultation

**Steps:**
1. Apply the fix to `stream_guidance()` endpoint
2. Restart backend server
3. Navigate to: `http://localhost:3000/consultation/1f5971c7-d7a9-4219-a595-b98285e87b3a`
4. Send a new message: "Can you explain pension consolidation?"
5. Verify advisor responds with consolidation-specific information
6. Check compliance validation includes relevance assessment

---

## Files to Modify

### Backend
1. **src/guidance_agent/api/routers/consultations.py**
   - Fix `stream_guidance()` endpoint (extract latest customer message)
   - Review `create_consultation()` and other endpoints

2. **src/guidance_agent/compliance/validator.py**
   - Add relevance checking logic
   - Update `ComplianceValidationResult` model

3. **src/guidance_agent/templates/compliance/validation.jinja2**
   - Add relevance assessment section to prompt

### Tests
4. **tests/api/test_consultations.py**
   - Add multi-turn conversation test

5. **tests/compliance/test_validator.py** (create if needed)
   - Add relevance checking tests

6. **frontend/tests/e2e/multi-turn-conversation.spec.ts** (create)
   - Add E2E test for follow-up questions

---

## Testing Checklist

- [ ] Backend: Multi-turn conversation test passes
- [ ] Backend: Relevance checking test passes
- [ ] Backend: All existing tests still pass (214 tests)
- [ ] Frontend: E2E multi-turn test passes
- [ ] Frontend: All existing tests still pass (203 tests)
- [ ] Manual: Test with consultation `1f5971c7-d7a9-4219-a595-b98285e87b3a`
- [ ] Manual: Create new conversation with multiple follow-up questions
- [ ] Manual: Verify compliance validation shows relevance scores

---

## Expected Outcomes

### Before Fix
- Customer asks: "what is pension consolidation?"
- Advisor sees: `presenting_question = "understanding"` (stale)
- Advisor responds: Generic pension overview
- Compliance: PASS (but irrelevant)

### After Fix
- Customer asks: "what is pension consolidation?"
- Advisor sees: `presenting_question = "what is pension consolidation?"` (current)
- Advisor responds: Specific information about pension consolidation
- Compliance: PASS with high relevance score

---

## Risk Assessment

**Severity:** HIGH
**Impact:** Makes advisor essentially non-functional for multi-turn conversations
**Probability:** 100% (affects all follow-up questions)
**User Impact:** Critical - customers cannot have meaningful conversations

**Mitigation:**
- Comprehensive test coverage (backend + frontend + E2E)
- Regression tests prevent future recurrence
- Relevance checking ensures quality responses

---

## Success Criteria

1. ✅ Advisor responds to current customer question, not initial query
2. ✅ Multi-turn conversations work correctly
3. ✅ Compliance validator includes relevance assessment
4. ✅ All tests pass (backend: 214+, frontend: 203+)
5. ✅ Existing consultation shows correct behavior after fix
6. ✅ No regressions in other functionality

---

## Related Documentation

- **Architecture:** `specs/architecture.md`
- **Advisor Agent:** `specs/advisor-agent.md`
- **API Integration:** `docs/API_INTEGRATION.md`
- **Testing Guide:** `docs/TESTING.md`
- **CLAUDE.md:** Project instructions for AI assistants

---

## Implementation Notes

### Order of Implementation

1. **Fix the bug first** (Phase 1) - highest priority
2. **Add tests** (Phase 4) - prevent regression
3. **Review other endpoints** (Phase 2) - find similar issues
4. **Add relevance checking** (Phase 3) - enhance quality
5. **Verify with real data** (Phase 5) - confirm fix works

### Development Workflow

```bash
# 1. Apply fix to consultations.py
vim src/guidance_agent/api/routers/consultations.py

# 2. Run existing tests to ensure no regressions
pytest tests/api/test_consultations.py -v

# 3. Add new multi-turn test
vim tests/api/test_consultations.py
pytest tests/api/test_consultations.py::test_multi_turn_conversation_context -v

# 4. Restart backend
docker-compose restart backend

# 5. Manual verification
open http://localhost:3000/consultation/1f5971c7-d7a9-4219-a595-b98285e87b3a

# 6. Run full test suite
pytest  # Backend (214+ tests)
cd frontend && npm test  # Frontend (203+ tests)
```

---

## Appendix: Code Snippets

### Current Buggy Code

```python
# src/guidance_agent/api/routers/consultations.py:300
customer = CustomerProfile(
    customer_id=consultation.customer_id,
    demographics=CustomerDemographics(...),
    presenting_question=consultation.meta.get("initial_query", ""),  # ❌ BUG
)
```

### Fixed Code

```python
# Extract latest customer message
latest_customer_message = ""
for turn in reversed(consultation.conversation):
    if turn.get("role") == "customer":
        latest_customer_message = turn.get("content", "")
        break

customer = CustomerProfile(
    customer_id=consultation.customer_id,
    demographics=CustomerDemographics(...),
    presenting_question=latest_customer_message,  # ✅ FIXED
)
```

---

**End of Plan**
