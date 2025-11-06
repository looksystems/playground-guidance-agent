# Conversational Flow Implementation Guide

Quick reference for implementing the changes tested in `test_conversational_flow.py`.

## Files to Modify

1. `src/guidance_agent/templates/advisor/guidance_main.jinja`
2. `src/guidance_agent/templates/advisor/guidance_with_reasoning.jinja`
3. `src/guidance_agent/templates/advisor/guidance_cached.jinja`

## Change 1: Remove Contradictory Phrase

### File: `guidance_main.jinja`

**Location**: Line ~55 in "Varied Phrasing Alternatives" section

**REMOVE this line**:
```jinja
- "Some people in your situation find it helpful to..."
```

**Rationale**: This phrase also appears in the FCA Social Proof Prohibition section (line ~97) as an example of what NOT to say. It's contradictory to show it as both recommended AND prohibited.

**Keep**: The phrase should remain in the prohibition section as a negative example.

---

## Change 2: Replace Numbered Task List - guidance_main.jinja

### File: `guidance_main.jinja`

**Location**: Lines ~136-144

**REPLACE**:
```jinja
TASK:
Provide appropriate pension guidance that:
1. Addresses the customer's specific question
2. Uses language appropriate for their literacy level ({{ customer.demographics.financial_literacy if customer.demographics else 'medium' }})
3. Presents balanced information (pros and cons)
4. Stays clearly within the FCA guidance boundary
5. Checks customer understanding

Your guidance:
```

**WITH**:
```jinja
Respond to the customer's message in a natural, conversational way that addresses their question whilst:
- Using language appropriate for their context
- Presenting balanced information where relevant
- Staying within FCA guidance boundaries
- Naturally checking understanding when exploring complex topics

Treat this as a flowing dialogue between two people, not a structured information delivery. Let the conversation develop naturally whilst satisfying these requirements throughout the exchange.

Your guidance:
```

**Key Changes**:
- Replace "TASK:" with "Respond to the customer's message"
- Replace numbered list (1. 2. 3.) with bullet points (-)
- Add "natural, conversational way" language
- Add instruction to treat as "flowing dialogue"
- Remove explicit mention of literacy level (still adapted internally)
- Use "whilst" (British English) instead of "while"

---

## Change 3: Replace Numbered Task List - guidance_with_reasoning.jinja

### File: `guidance_with_reasoning.jinja`

**Location**: Lines ~71-78

**REPLACE**:
```jinja
TASK:
Based on your reasoning above, provide pension guidance that:
1. Addresses the customer's question
2. Uses appropriate language for their literacy level
3. Presents balanced information
4. Stays within FCA guidance boundary
5. Checks customer understanding
6. Applies the conversational strategy from your reasoning (warm, natural, engaging tone with appropriate signposting and personalization)

Your guidance:
```

**WITH**:
```jinja
Based on your reasoning above, respond to the customer in a natural, conversational way that:
- Addresses their question directly
- Uses appropriate language for their context
- Presents balanced information where relevant
- Stays within FCA guidance boundaries
- Naturally checks understanding when exploring complex topics
- Applies your planned conversational strategy (warm, natural, engaging tone with signposting and personalization)

Treat this as a flowing dialogue, not a structured information delivery. Let the conversation develop naturally whilst satisfying these requirements throughout the exchange.

Your guidance:
```

**Key Changes**:
- Replace "TASK:" with "respond to the customer"
- Replace numbered list with bullet points
- Add "natural, conversational way" language
- Add "flowing dialogue" instruction
- Keep reference to reasoning strategy (point 6 becomes last bullet)

---

## Change 4: Replace Numbered List - guidance_cached.jinja

### File: `guidance_cached.jinja`

**Location**: Line ~59 (in the user message content)

**REPLACE** (within the Jinja concatenation):
```jinja
Please provide appropriate pension guidance that:
1. Addresses the customer's specific question
2. Uses language appropriate for their literacy level (" ~ (customer.demographics.financial_literacy if customer.demographics else 'medium') ~ ")
3. Presents balanced information (pros and cons)
4. Stays clearly within the FCA guidance boundary
5. Checks customer understanding
```

**WITH**:
```jinja
Please respond to the customer's message in a natural, conversational way that addresses their question whilst:
- Using language appropriate for their context
- Presenting balanced information where relevant
- Staying within FCA guidance boundaries
- Naturally checking understanding when exploring complex topics

Treat this as a flowing dialogue between two people, not a structured information delivery. Let the conversation develop naturally whilst satisfying these requirements throughout the exchange.
```

**Note**: This is inside a Jinja template concatenation string, so ensure proper escaping:
- Use `\n` for newlines within the concatenated string
- Use `\"` for quotes within the concatenated string
- The full line will look like:

```jinja
"content": {{ ("Previous conversation:\n" ~ (conversation_history | conversation) ~ "\n\nCustomer's current question: \"" ~ customer.presenting_question ~ "\"\n\nPlease respond to the customer's message in a natural, conversational way that addresses their question whilst:\n- Using language appropriate for their context\n- Presenting balanced information where relevant\n- Staying within FCA guidance boundaries\n- Naturally checking understanding when exploring complex topics\n\nTreat this as a flowing dialogue between two people, not a structured information delivery. Let the conversation develop naturally whilst satisfying these requirements throughout the exchange.\n\nYour guidance:") | tojson }}
```

---

## Verification After Changes

### Run the TDD tests:

```bash
# 1. Comment out the pytestmark skip line in test_conversational_flow.py
#    (line ~785: pytestmark = pytest.mark.skip(...))

# 2. Run the tests
pytest tests/test_conversational_flow.py -v

# Expected: 26 PASSED, 0 FAILED
```

### Run existing template tests:

```bash
# Ensure no regressions
pytest tests/templates/ -v
```

### Manual verification:

1. Start the backend: `uv run uvicorn guidance_agent.api.main:app --reload`
2. Start the frontend: `cd frontend && npm run dev`
3. Test a conversation - responses should:
   - Flow naturally without feeling like a checklist
   - Not explicitly mention task completion
   - Feel like dialogue between two people
   - Still maintain all FCA compliance requirements

---

## What NOT to Change

These should remain UNCHANGED:

1. **FCA Neutrality Requirements section** - Keep all prohibition examples
2. **Social Proof Prohibition section** - Keep "Some people in your situation" as prohibited example
3. **Conversational Approach section** - Already correct with signposting, transitions, etc.
4. **Customer Profile / Context sections** - No changes needed
5. **Filter definitions** - No changes to Jinja filters
6. **Variable names** - No changes to template variables

---

## British English Note

The changes use British English conventions:
- "whilst" instead of "while" in formal requirement contexts
- This maintains consistency with the rest of the British English improvements

---

## Testing Checklist

After implementation:

- [ ] All 26 tests in `test_conversational_flow.py` pass
- [ ] All existing template tests still pass
- [ ] No numbered lists (1. 2. 3.) in any of the 3 guidance templates
- [ ] "Some people in your situation" removed from Varied Phrasing section
- [ ] "Some people in your situation" still present in FCA Prohibition section
- [ ] Templates contain "natural, conversational way" language
- [ ] Templates contain "flowing dialogue" instruction
- [ ] Templates use bullet points (-) for requirements
- [ ] Templates use "whilst" in formal contexts
- [ ] FCA Neutrality sections remain intact
- [ ] Manual testing shows natural conversational flow

---

## Estimated Time

- Template modifications: 15-20 minutes
- Test verification: 5 minutes
- Manual testing: 10 minutes
- **Total: ~30-35 minutes**

---

## Questions?

Refer to:
- Specs document: `specs/british-english-conversational-improvements.md` Section 2
- Test file: `tests/test_conversational_flow.py`
- Test summary: `tests/TEST_CONVERSATIONAL_FLOW_SUMMARY.md`
