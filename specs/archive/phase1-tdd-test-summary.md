# Phase 1 TDD Test Summary

## Overview

Following Test-Driven Development (TDD) approach, we have written tests FIRST for the Phase 1 conversational improvements described in `/specs/conversational-improvement-plan.md`. All tests currently **FAIL** (as expected), proving they test new functionality that doesn't exist yet.

## Test Results Summary

- **Status**: 4 new tests added, all failing as expected
- **Location**: `/tests/templates/test_template_rendering.py`
- **Existing tests**: 13 tests still passing (no regressions)
- **Date**: 2025-11-05

## New Tests Added

### 1. `test_guidance_main_includes_conversational_guidance()`

**Purpose**: Verify that `advisor/guidance_main.jinja` includes conversational flow instructions.

**Checks for**:
- Conversational flow guidance (opening/middle/closing phases)
- Signposting phrase examples ("let me break this down", "here's what this means", etc.)
- Varied phrasing alternatives (alternatives to repetitive "you could consider")
- Personalization directives (customer's name usage)

**Current Status**: ❌ FAILS - Template does not include signposting phrase examples

**Maps to Spec**: Section 1.1 - Update `templates/advisor/guidance.jinja2`

---

### 2. `test_reasoning_includes_conversational_strategy_analysis()`

**Purpose**: Verify that `advisor/reasoning.jinja` includes conversational strategy section.

**Checks for**:
- "Conversational Strategy" section header
- Conversation phase analysis (opening/middle/closing)
- Customer emotional state assessment (anxious, confident, confused)
- Tone & pacing considerations
- Signposting & transitions planning
- Personalization opportunities

**Current Status**: ❌ FAILS - Template does not include 'Conversational Strategy' section

**Maps to Spec**: Section 1.2 - Update `templates/advisor/guidance_reasoning.jinja2`

---

### 3. `test_guidance_cached_includes_conversational_personality()`

**Purpose**: Verify that `advisor/guidance_cached.jinja` includes conversational style definition.

**Checks for**:
- Conversational style section
- Warmth/rapport keywords (warm, rapport, empathetic, friendly)
- Natural vs robotic guidance/examples
- Key principles: variety, personalization, engagement (at least 2 of 3)

**Current Status**: ❌ FAILS - Template does not define conversational style

**Maps to Spec**: Section 1.3 - Update `templates/advisor/system.jinja2`

**Note**: The spec references `system.jinja2`, but the actual template is `guidance_cached.jinja` (which contains the system message). This test correctly targets the cached template.

---

### 4. `test_guidance_with_reasoning_conversational_integration()`

**Purpose**: Verify that `advisor/guidance_with_reasoning.jinja` integrates conversational elements.

**Checks for**:
- Inclusion of reasoning content
- References to conversational approach (conversational, natural, warm, engage)

**Current Status**: ❌ FAILS - Template does not reference conversational approach when generating guidance

**Maps to Spec**: Section 1.2 (integration with guidance generation)

---

## Test Execution Commands

Run all new Phase 1 tests:
```bash
uv run pytest tests/templates/test_template_rendering.py::TestAdvisorTemplates::test_guidance_main_includes_conversational_guidance \
                tests/templates/test_template_rendering.py::TestAdvisorTemplates::test_reasoning_includes_conversational_strategy_analysis \
                tests/templates/test_template_rendering.py::TestAdvisorTemplates::test_guidance_cached_includes_conversational_personality \
                tests/templates/test_template_rendering.py::TestAdvisorTemplates::test_guidance_with_reasoning_conversational_integration \
                -v
```

Run all advisor template tests (including existing):
```bash
uv run pytest tests/templates/test_template_rendering.py::TestAdvisorTemplates -v
```

## Expected Outcomes After Template Implementation

Once the templates are updated according to Phase 1 spec:

1. ✅ `test_guidance_main_includes_conversational_guidance()` - Should pass when signposting, transitions, and varied phrasing are added
2. ✅ `test_reasoning_includes_conversational_strategy_analysis()` - Should pass when "Conversational Strategy Analysis" section is added
3. ✅ `test_guidance_cached_includes_conversational_personality()` - Should pass when conversational style guidelines are added
4. ✅ `test_guidance_with_reasoning_conversational_integration()` - Should pass when reasoning template references conversational approach

## Templates to Update (Next Steps)

Based on test failures, the following templates need updates:

1. **`src/guidance_agent/templates/advisor/guidance_main.jinja`**
   - Add conversational flow guidance (opening/middle/closing phases)
   - Add signposting phrase examples
   - Add varied phrasing alternatives
   - Add personalization directives

2. **`src/guidance_agent/templates/advisor/reasoning.jinja`**
   - Add "Conversational Strategy Analysis" section
   - Include conversation phase detection
   - Include emotional state assessment
   - Include tone & pacing considerations
   - Include signposting/transition planning
   - Include personalization opportunities

3. **`src/guidance_agent/templates/advisor/guidance_cached.jinja`**
   - Add "Conversational Style" section
   - Define warm, professional personality
   - Provide natural vs robotic examples
   - List key principles (variety, personalization, engagement, warmth)

4. **`src/guidance_agent/templates/advisor/guidance_with_reasoning.jinja`**
   - Add conversational approach references
   - Integrate conversational strategy from reasoning

## Test Keywords Reference

When updating templates, ensure these keywords/phrases appear as indicated in the tests:

**Conversational Flow**:
- "signpost" / "signposting"
- "transition" / "transitions"
- "opening phase" / "middle phase" / "closing phase"
- "personalization" / "customer's name"

**Signposting Examples** (include at least one):
- "let me break this down"
- "here's what this means"
- "first, let's look at"
- "before we dive into"
- "building on"

**Varied Phrasing** (include at least one):
- "one option to explore"
- "you might want to look into"
- "some people in your situation"
- "it's worth thinking about"
- "you have a few paths"

**Conversational Strategy**:
- "conversational strategy"
- "conversation phase"
- "emotional state"
- "tone" and/or "pacing"

**Personality Keywords**:
- "warm" and/or "rapport" and/or "empathetic"
- "natural" vs "robotic"
- "variety", "personalization", "engagement" (at least 2)

## Validation

After implementing template changes, validate with:

1. Run the 4 new tests - all should pass
2. Run all 17 advisor template tests - all should pass
3. Run full template test suite - should maintain 100% pass rate
4. Manual review of rendered templates to ensure natural, conversational tone

---

**Status**: ✅ TDD Tests Complete - Ready for Implementation Phase
**Next Step**: Update templates to make tests pass
