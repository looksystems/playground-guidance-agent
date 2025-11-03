# Original Prompt Functions Backup Summary

**Date:** 2025-11-03
**Purpose:** Preserve original f-string prompt implementations for regression testing during Jinja template migration

## Backup Location

- **File:** `/Users/adrian/Work/guidance-agent/tests/regression/original_prompts.py`
- **Total Functions Backed Up:** 20 prompt-building functions

## Detailed Inventory

### 1. src/guidance_agent/advisor/prompts.py (4 functions)

#### Function: `original_build_guidance_prompt`
- **Lines:** 155-216
- **Purpose:** Build complete prompt for guidance generation
- **Key Features:**
  - Multi-section prompt with advisor role, customer profile, context, and task
  - Uses formatted helpers for customer profile, conversation, cases, rules, memories

#### Function: `original_build_guidance_prompt_cached`
- **Lines:** 219-316
- **Purpose:** Build cache-optimized prompt with structured messages
- **Key Features:**
  - 4-part message structure for cache optimization
  - System prompts with cache control markers
  - Separates static, semi-static, and variable content

#### Function: `original_build_reasoning_prompt`
- **Lines:** 319-361
- **Purpose:** Build prompt for chain-of-thought reasoning
- **Key Features:**
  - 6-step reasoning framework
  - Includes customer profile, question, context
  - Step-by-step thinking guide

#### Function: `original_build_guidance_prompt_with_reasoning`
- **Lines:** 364-403
- **Purpose:** Build guidance prompt given pre-generated reasoning
- **Key Features:**
  - Incorporates reasoning output
  - Focused task instructions
  - Customer context integration

---

### 2. src/guidance_agent/advisor/agent.py (2 inline prompts)

#### Function: `original_refine_for_compliance_prompt`
- **Lines:** 461-490
- **Purpose:** Refine guidance to address compliance issues
- **Key Features:**
  - Original guidance + issues list
  - Customer context for personalization
  - Clear revision instructions

#### Function: `original_handle_borderline_case_prompt`
- **Lines:** 504-540
- **Purpose:** Strengthen borderline guidance (low confidence)
- **Key Features:**
  - Includes validation concerns
  - 5-point strengthening checklist
  - Maintains compliance while improving clarity

---

### 3. src/guidance_agent/compliance/validator.py (1 function)

#### Function: `original_build_validation_prompt`
- **Lines:** 182-274
- **Purpose:** Validate guidance for FCA compliance
- **Key Features:**
  - 5-point compliance checklist
  - DB pension special handling
  - Structured response format (ANALYSIS/OVERALL/CONFIDENCE/ISSUES)
  - Detailed criteria for each compliance area

---

### 4. src/guidance_agent/customer/agent.py (2 functions)

#### Function: `original_simulate_comprehension_prompt`
- **Lines:** 78-101
- **Purpose:** Simulate customer comprehension of guidance
- **Key Features:**
  - 5 comprehension assessment criteria
  - JSON output format
  - Three-level understanding scale
  - Confusion point identification

#### Function: `original_customer_respond_prompt`
- **Lines:** 146-179
- **Purpose:** Generate realistic customer response
- **Key Features:**
  - Reflects comprehension level
  - Matches literacy level
  - Natural conversational tone (1-3 sentences)
  - Realistic customer behavior

---

### 5. src/guidance_agent/customer/simulator.py (1 function)

#### Function: `original_simulate_outcome_prompt`
- **Lines:** 43-86
- **Purpose:** Simulate consultation outcome evaluation
- **Key Features:**
  - 11 evaluation metrics
  - Comprehensive scoring (satisfaction, comprehension, goal alignment)
  - Boolean checks (risks, compliance, signposting)
  - JSON output format

---

### 6. src/guidance_agent/customer/generator.py (4 functions)

#### Function: `original_generate_demographics_prompt`
- **Lines:** 49-70
- **Purpose:** Generate realistic UK customer demographics
- **Key Features:**
  - Age-appropriate employment status
  - Diverse occupations and backgrounds
  - JSON output format

#### Function: `original_generate_financial_situation_prompt`
- **Lines:** 113-138
- **Purpose:** Generate realistic financial situation
- **Key Features:**
  - Age and employment-based guidelines
  - Realistic UK income/asset ranges
  - Lifecycle-appropriate values

#### Function: `original_generate_pension_pot_prompt`
- **Lines:** 203-231
- **Purpose:** Generate pension pot details
- **Key Features:**
  - DC vs DB handling
  - Age-appropriate values
  - Realistic UK providers
  - Legacy provider considerations

#### Function: `original_generate_goals_and_inquiry_prompt`
- **Lines:** 287-314
- **Purpose:** Generate customer goals and presenting question
- **Key Features:**
  - Age-specific goal suggestions
  - Literacy-appropriate language
  - Natural conversational tone
  - Genuine confusion/guidance needs

---

### 7. src/guidance_agent/learning/reflection.py (4 functions)

#### Function: `original_reflect_on_failure_prompt`
- **Lines:** 45-67
- **Purpose:** Extract learning principle from failed consultation
- **Key Features:**
  - Customer profile + guidance + outcome
  - Specific, actionable principle extraction
  - Domain identification

#### Function: `original_validate_principle_prompt`
- **Lines:** 108-126
- **Purpose:** Validate principle against FCA guidelines
- **Key Features:**
  - 4-point validation checklist
  - Invalid pattern detection
  - Confidence scoring
  - Structured output (Valid/Confidence/Reason)

#### Function: `original_refine_principle_prompt`
- **Lines:** 166-176
- **Purpose:** Refine principle to be more specific and actionable
- **Key Features:**
  - 3-point refinement criteria (specific, actionable, measurable)
  - Domain context
  - Length constraint (2-3 sentences)

#### Function: `original_judge_rule_value_prompt`
- **Lines:** 210-228
- **Purpose:** Judge if rule is valuable enough to store
- **Key Features:**
  - Valuable vs not valuable criteria
  - Value scoring (0-1)
  - Common sense filter

---

### 8. src/guidance_agent/core/memory.py (1 function)

#### Function: `original_rate_importance_prompt`
- **Lines:** 389-397
- **Purpose:** Rate observation importance using LLM
- **Key Features:**
  - 1-10 scale with examples
  - Mundane (1) to extremely important (10)
  - Normalized to 0-1 range in code

---

### 9. src/guidance_agent/evaluation/judge_validation.py (1 inline prompt)

#### Function: `original_llm_judge_evaluate_prompt`
- **Lines:** 75-86
- **Purpose:** Evaluate consultation for FCA compliance
- **Key Features:**
  - PASS/FAIL decision
  - Confidence score (0-1)
  - Brief reasoning
  - Structured format (PASS|0.9|Reasoning)

---

## Verification Checklist

- [x] All 20 prompt functions identified and backed up
- [x] Line numbers documented for each function
- [x] Source file paths recorded
- [x] Functions preserved with exact f-string formatting
- [x] Helper function imports maintained
- [x] Comments added indicating original location
- [x] "DO NOT MODIFY" warnings included
- [x] File saved to `/Users/adrian/Work/guidance-agent/tests/regression/original_prompts.py`

## Missing or Ambiguous Prompts

**None found.** All expected prompt functions were located and backed up successfully.

## Usage for Regression Testing

These original functions should be used to:

1. **Generate baseline outputs** - Run original prompts with test inputs to capture expected outputs
2. **Compare with Jinja templates** - After migration, run Jinja templates with same inputs
3. **Validate equivalence** - Ensure Jinja templates produce equivalent or better output
4. **Regression test suite** - Include in automated test suite to prevent regressions

## Next Steps

1. Create test fixtures with representative inputs for each prompt type
2. Generate baseline outputs using these original functions
3. Migrate prompts to Jinja templates
4. Run regression tests comparing original vs Jinja output
5. Document any intentional differences or improvements

## Notes

- All functions use f-string formatting with embedded variables
- Some functions use helper formatters from `guidance_agent.advisor.prompts` (format_customer_profile, format_conversation, format_cases, format_rules, format_memories)
- Inline prompts from `agent.py` and `judge_validation.py` have been extracted into standalone functions
- Cache control structures in `build_guidance_prompt_cached` are preserved for reference
