"""Regression tests to ensure Jinja templates produce identical output to f-strings.

This test suite compares the output of new Jinja2 templates against the original
f-string implementations to ensure the migration maintains behavioral compatibility.

Strategy:
1. Use identical input data for both implementations
2. Normalize whitespace before comparison (strip lines, remove empty lines)
3. Test all 20 original prompt functions against their template equivalents
4. Fail if outputs differ after normalization

Note: These tests will initially fail until templates are created. They serve as
a specification for the migration and will pass once templates match originals.
"""

import pytest
from guidance_agent.core.template_engine import render_template, get_template_engine

# Import original f-string implementations
from tests.regression.original_prompts import (
    original_build_guidance_prompt,
    original_build_guidance_prompt_cached,
    original_build_reasoning_prompt,
    original_build_guidance_prompt_with_reasoning,
    original_refine_for_compliance_prompt,
    original_handle_borderline_case_prompt,
    original_build_validation_prompt,
    original_simulate_comprehension_prompt,
    original_customer_respond_prompt,
    original_simulate_outcome_prompt,
    original_generate_demographics_prompt,
    original_generate_financial_situation_prompt,
    original_generate_pension_pot_prompt,
    original_generate_goals_and_inquiry_prompt,
    original_reflect_on_failure_prompt,
    original_validate_principle_prompt,
    original_refine_principle_prompt,
    original_judge_rule_value_prompt,
    original_rate_importance_prompt,
    original_llm_judge_evaluate_prompt,
)

# Import sample data fixtures
from tests.fixtures.template_data import (
    get_sample_advisor,
    get_sample_customer,
    get_sample_context,
    get_sample_conversation_history,
    get_sample_guidance,
    get_sample_validation_issues,
    get_sample_reasoning,
    get_sample_demographics,
    get_sample_financial,
    get_sample_pension_pots,
)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace for comparison.

    This function:
    1. Strips leading/trailing whitespace from each line
    2. Removes empty lines
    3. Joins with single newline

    This allows templates to use different spacing/indentation while
    maintaining semantic equivalence to the original f-strings.

    Args:
        text: Text to normalize

    Returns:
        Normalized text with consistent whitespace
    """
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line]
    return '\n'.join(lines)


class TestGuidancePromptRegression:
    """Ensure guidance templates match original f-strings."""

    def test_guidance_main_matches_original(self):
        """Test advisor/guidance_main.jinja matches original f-string.

        Source: src/guidance_agent/advisor/prompts.py:155-216
        Original: original_build_guidance_prompt()
        Template: advisor/guidance_main.jinja
        """
        advisor = get_sample_advisor()
        customer = get_sample_customer()
        context = get_sample_context()
        conversation_history = get_sample_conversation_history()

        # Original f-string output
        original = original_build_guidance_prompt(
            advisor=advisor,
            customer=customer,
            context=context,
            conversation_history=conversation_history,
        )

        # New template output
        new = render_template(
            "advisor/guidance_main.jinja",
            advisor=advisor,
            customer=customer,
            context=context,
            conversation_history=conversation_history,
        )

        # Compare with normalized whitespace
        assert normalize_whitespace(original) == normalize_whitespace(new), \
            "guidance_main.jinja output differs from original f-string"

    def test_guidance_cached_matches_original(self):
        """Test advisor/guidance_cached.jinja matches original f-string.

        Source: src/guidance_agent/advisor/prompts.py:219-316
        Original: original_build_guidance_prompt_cached()
        Template: advisor/guidance_cached.jinja

        Note: This template returns a list of message dicts, not a string.
        """
        advisor = get_sample_advisor()
        customer = get_sample_customer()
        context = get_sample_context()
        conversation_history = get_sample_conversation_history()

        # Original f-string output
        original = original_build_guidance_prompt_cached(
            advisor=advisor,
            customer=customer,
            context=context,
            conversation_history=conversation_history,
        )

        # New template output (uses render_messages for JSON)
        new = get_template_engine().render_messages(
            "advisor/guidance_cached.jinja",
            advisor=advisor,
            customer=customer,
            context=context,
            conversation_history=conversation_history,
        )

        # Compare message structures
        assert len(original) == len(new), "Message count differs"

        for i, (orig_msg, new_msg) in enumerate(zip(original, new)):
            assert orig_msg["role"] == new_msg["role"], \
                f"Message {i} role differs"

            # For system messages with content arrays, compare text content
            if isinstance(orig_msg["content"], list):
                orig_text = orig_msg["content"][0]["text"]
                new_text = new_msg["content"][0]["text"]
                assert normalize_whitespace(orig_text) == normalize_whitespace(new_text), \
                    f"Message {i} content differs"
            else:
                # For user messages with string content
                assert normalize_whitespace(orig_msg["content"]) == normalize_whitespace(new_msg["content"]), \
                    f"Message {i} content differs"

    def test_reasoning_matches_original(self):
        """Test advisor/reasoning.jinja matches original f-string.

        Source: src/guidance_agent/advisor/prompts.py:319-361
        Original: original_build_reasoning_prompt()
        Template: advisor/reasoning.jinja
        """
        customer = get_sample_customer()
        context = get_sample_context()

        # Original f-string output
        original = original_build_reasoning_prompt(
            customer=customer,
            context=context,
        )

        # New template output
        new = render_template(
            "advisor/reasoning.jinja",
            customer=customer,
            context=context,
        )

        # Compare with normalized whitespace
        assert normalize_whitespace(original) == normalize_whitespace(new), \
            "reasoning.jinja output differs from original f-string"

    def test_guidance_with_reasoning_matches_original(self):
        """Test advisor/guidance_with_reasoning.jinja matches original f-string.

        Source: src/guidance_agent/advisor/prompts.py:364-403
        Original: original_build_guidance_prompt_with_reasoning()
        Template: advisor/guidance_with_reasoning.jinja
        """
        customer = get_sample_customer()
        context = get_sample_context()
        reasoning = get_sample_reasoning()

        # Original f-string output
        original = original_build_guidance_prompt_with_reasoning(
            customer=customer,
            context=context,
            reasoning=reasoning,
        )

        # New template output
        new = render_template(
            "advisor/guidance_with_reasoning.jinja",
            customer=customer,
            context=context,
            reasoning=reasoning,
        )

        # Compare with normalized whitespace
        assert normalize_whitespace(original) == normalize_whitespace(new), \
            "guidance_with_reasoning.jinja output differs from original f-string"

    def test_refine_for_compliance_matches_original(self):
        """Test advisor/compliance_refinement.jinja matches original f-string.

        Source: src/guidance_agent/advisor/agent.py:461-490
        Original: original_refine_for_compliance_prompt()
        Template: advisor/compliance_refinement.jinja
        """
        guidance = get_sample_guidance()
        issues = get_sample_validation_issues()
        customer = get_sample_customer()

        # Original f-string output
        original = original_refine_for_compliance_prompt(
            guidance=guidance,
            issues=issues,
            customer=customer,
        )

        # New template output
        new = render_template(
            "advisor/compliance_refinement.jinja",
            guidance=guidance,
            issues=issues,
            customer=customer,
        )

        # Compare with normalized whitespace
        assert normalize_whitespace(original) == normalize_whitespace(new), \
            "compliance_refinement.jinja output differs from original f-string"

    def test_handle_borderline_case_matches_original(self):
        """Test advisor/borderline_strengthening.jinja matches original f-string.

        Source: src/guidance_agent/advisor/agent.py:504-540
        Original: original_handle_borderline_case_prompt()
        Template: advisor/borderline_strengthening.jinja
        """
        from dataclasses import dataclass

        @dataclass
        class MockValidation:
            confidence: float
            reasoning: str

        guidance = get_sample_guidance()
        validation = MockValidation(
            confidence=0.72,
            reasoning="Language is mostly appropriate but could be more explicit about guidance boundary",
        )
        context = get_sample_context()

        # Original f-string output
        original = original_handle_borderline_case_prompt(
            guidance=guidance,
            validation=validation,
            context=context,
        )

        # New template output
        new = render_template(
            "advisor/borderline_strengthening.jinja",
            guidance=guidance,
            validation=validation,
            context=context,
        )

        # Compare with normalized whitespace
        assert normalize_whitespace(original) == normalize_whitespace(new), \
            "borderline_strengthening.jinja output differs from original f-string"


class TestCompliancePromptRegression:
    """Ensure compliance templates match originals."""

    def test_validation_matches_original(self):
        """Test compliance/validation.jinja matches original f-string.

        Source: src/guidance_agent/compliance/validator.py:182-274
        Original: original_build_validation_prompt()
        Template: compliance/validation.jinja
        """
        guidance = get_sample_guidance()
        customer = get_sample_customer()
        reasoning = get_sample_reasoning()

        # Original f-string output
        original = original_build_validation_prompt(
            guidance=guidance,
            customer=customer,
            reasoning=reasoning,
        )

        # New template output
        new = render_template(
            "compliance/validation.jinja",
            guidance=guidance,
            customer=customer,
            reasoning=reasoning,
        )

        # Compare with normalized whitespace
        assert normalize_whitespace(original) == normalize_whitespace(new), \
            "validation.jinja output differs from original f-string"


class TestCustomerPromptRegression:
    """Ensure customer templates match originals."""

    def test_simulate_comprehension_matches_original(self):
        """Test customer/comprehension.jinja matches original f-string.

        Source: src/guidance_agent/customer/agent.py:78-101
        Original: original_simulate_comprehension_prompt()
        Template: customer/comprehension.jinja
        """
        profile = get_sample_customer()
        guidance = get_sample_guidance()

        # Original f-string output
        original = original_simulate_comprehension_prompt(
            profile=profile,
            guidance=guidance,
        )

        # New template output
        new = render_template(
            "customer/comprehension.jinja",
            profile=profile,
            guidance=guidance,
        )

        # Compare with normalized whitespace
        assert normalize_whitespace(original) == normalize_whitespace(new), \
            "comprehension.jinja output differs from original f-string"

    def test_customer_respond_matches_original(self):
        """Test customer/response.jinja matches original f-string.

        Source: src/guidance_agent/customer/agent.py:146-179
        Original: original_customer_respond_prompt()
        Template: customer/response.jinja
        """
        profile = get_sample_customer()
        advisor_message = "Have you thought about when you might want to access your pension?"
        comprehension = {
            "understanding_level": "partially_understood",
            "confusion_points": ["tax implications"],
            "customer_feeling": "uncertain",
        }

        # Original f-string output
        original = original_customer_respond_prompt(
            profile=profile,
            advisor_message=advisor_message,
            comprehension=comprehension,
        )

        # New template output
        new = render_template(
            "customer/response.jinja",
            profile=profile,
            advisor_message=advisor_message,
            comprehension=comprehension,
        )

        # Compare with normalized whitespace
        assert normalize_whitespace(original) == normalize_whitespace(new), \
            "response.jinja output differs from original f-string"

    def test_simulate_outcome_matches_original(self):
        """Test customer/outcome.jinja matches original f-string.

        Source: src/guidance_agent/customer/simulator.py:43-86
        Original: original_simulate_outcome_prompt()
        Template: customer/outcome.jinja
        """
        from dataclasses import dataclass

        @dataclass
        class MockCustomerAgent:
            profile: object
            comprehension_level: float

        customer = MockCustomerAgent(
            profile=get_sample_customer(),
            comprehension_level=0.75,
        )
        conversation_history = get_sample_conversation_history()
        has_db_pension = False

        # Original f-string output
        original = original_simulate_outcome_prompt(
            customer=customer,
            conversation_history=conversation_history,
            has_db_pension=has_db_pension,
        )

        # New template output
        new = render_template(
            "customer/outcome.jinja",
            customer=customer,
            conversation_history=conversation_history,
            has_db_pension=has_db_pension,
        )

        # Compare with normalized whitespace
        assert normalize_whitespace(original) == normalize_whitespace(new), \
            "outcome.jinja output differs from original f-string"

    def test_generate_demographics_matches_original(self):
        """Test customer/generation/demographics.jinja matches original f-string.

        Source: src/guidance_agent/customer/generator.py:49-70
        Original: original_generate_demographics_prompt()
        Template: customer/generation/demographics.jinja
        """
        age = 55
        literacy = "medium"

        # Original f-string output
        original = original_generate_demographics_prompt(
            age=age,
            literacy=literacy,
        )

        # New template output
        new = render_template(
            "customer/generation/demographics.jinja",
            age=age,
            literacy=literacy,
        )

        # Compare with normalized whitespace
        assert normalize_whitespace(original) == normalize_whitespace(new), \
            "generation/demographics.jinja output differs from original f-string"

    def test_generate_financial_situation_matches_original(self):
        """Test customer/generation/financial.jinja matches original f-string.

        Source: src/guidance_agent/customer/generator.py:113-138
        Original: original_generate_financial_situation_prompt()
        Template: customer/generation/financial.jinja
        """
        demographics = get_sample_demographics()

        # Original f-string output
        original = original_generate_financial_situation_prompt(
            demographics=demographics,
        )

        # New template output
        new = render_template(
            "customer/generation/financial.jinja",
            demographics=demographics,
        )

        # Compare with normalized whitespace
        assert normalize_whitespace(original) == normalize_whitespace(new), \
            "generation/financial.jinja output differs from original f-string"

    def test_generate_pension_pot_matches_original(self):
        """Test customer/generation/pension_pots.jinja matches original f-string.

        Source: src/guidance_agent/customer/generator.py:203-231
        Original: original_generate_pension_pot_prompt()
        Template: customer/generation/pension_pots.jinja
        """
        demographics = get_sample_demographics()
        pot_number = 1
        total_pots = 2
        pot_type = "defined_contribution"

        # Original f-string output
        original = original_generate_pension_pot_prompt(
            demographics=demographics,
            pot_number=pot_number,
            total_pots=total_pots,
            pot_type=pot_type,
        )

        # New template output
        new = render_template(
            "customer/generation/pension_pots.jinja",
            demographics=demographics,
            pot_number=pot_number,
            total_pots=total_pots,
            pot_type=pot_type,
        )

        # Compare with normalized whitespace
        assert normalize_whitespace(original) == normalize_whitespace(new), \
            "generation/pension_pots.jinja output differs from original f-string"

    def test_generate_goals_and_inquiry_matches_original(self):
        """Test customer/generation/goals.jinja matches original f-string.

        Source: src/guidance_agent/customer/generator.py:287-314
        Original: original_generate_goals_and_inquiry_prompt()
        Template: customer/generation/goals.jinja
        """
        demographics = get_sample_demographics()
        financial = get_sample_financial()
        pots = get_sample_pension_pots()

        # Original f-string output
        original = original_generate_goals_and_inquiry_prompt(
            demographics=demographics,
            financial=financial,
            pots=pots,
        )

        # New template output
        new = render_template(
            "customer/generation/goals.jinja",
            demographics=demographics,
            financial=financial,
            pots=pots,
        )

        # Compare with normalized whitespace
        assert normalize_whitespace(original) == normalize_whitespace(new), \
            "generation/goals.jinja output differs from original f-string"


class TestLearningPromptRegression:
    """Ensure learning templates match originals."""

    def test_reflect_on_failure_matches_original(self):
        """Test learning/reflection.jinja matches original f-string.

        Source: src/guidance_agent/learning/reflection.py:45-67
        Original: original_reflect_on_failure_prompt()
        Template: learning/reflection.jinja
        """
        from dataclasses import dataclass

        @dataclass
        class MockOutcome:
            customer_satisfaction: int
            comprehension: int
            issues: list
            reasoning: str

        customer_profile = get_sample_customer()
        guidance_provided = get_sample_guidance()
        outcome = MockOutcome(
            customer_satisfaction=4,
            comprehension=5,
            issues=["unclear language", "missing risk disclosure"],
            reasoning="Customer was confused by technical terms and didn't understand risks",
        )

        # Original f-string output
        original = original_reflect_on_failure_prompt(
            customer_profile=customer_profile,
            guidance_provided=guidance_provided,
            outcome=outcome,
        )

        # New template output
        new = render_template(
            "learning/reflection.jinja",
            customer_profile=customer_profile,
            guidance_provided=guidance_provided,
            outcome=outcome,
        )

        # Compare with normalized whitespace
        assert normalize_whitespace(original) == normalize_whitespace(new), \
            "reflection.jinja output differs from original f-string"

    def test_validate_principle_matches_original(self):
        """Test learning/principle_validation.jinja matches original f-string.

        Source: src/guidance_agent/learning/reflection.py:108-126
        Original: original_validate_principle_prompt()
        Template: learning/principle_validation.jinja
        """
        principle = "Always explain tax implications before discussing withdrawal options"

        # Original f-string output
        original = original_validate_principle_prompt(
            principle=principle,
        )

        # New template output
        new = render_template(
            "learning/principle_validation.jinja",
            principle=principle,
        )

        # Compare with normalized whitespace
        assert normalize_whitespace(original) == normalize_whitespace(new), \
            "principle_validation.jinja output differs from original f-string"

    def test_refine_principle_matches_original(self):
        """Test learning/principle_refinement.jinja matches original f-string.

        Source: src/guidance_agent/learning/reflection.py:166-176
        Original: original_refine_principle_prompt()
        Template: learning/principle_refinement.jinja
        """
        principle = "Be clear about risks"
        domain = "risk_disclosure"

        # Original f-string output
        original = original_refine_principle_prompt(
            principle=principle,
            domain=domain,
        )

        # New template output
        new = render_template(
            "learning/principle_refinement.jinja",
            principle=principle,
            domain=domain,
        )

        # Compare with normalized whitespace
        assert normalize_whitespace(original) == normalize_whitespace(new), \
            "principle_refinement.jinja output differs from original f-string"

    def test_judge_rule_value_matches_original(self):
        """Test learning/rule_judgment.jinja matches original f-string.

        Source: src/guidance_agent/learning/reflection.py:210-228
        Original: original_judge_rule_value_prompt()
        Template: learning/rule_judgment.jinja
        """
        rule_principle = "Always explain tax implications before discussing withdrawal options"
        domain = "risk_disclosure"

        # Original f-string output
        original = original_judge_rule_value_prompt(
            rule_principle=rule_principle,
            domain=domain,
        )

        # New template output
        new = render_template(
            "learning/rule_judgment.jinja",
            rule_principle=rule_principle,
            domain=domain,
        )

        # Compare with normalized whitespace
        assert normalize_whitespace(original) == normalize_whitespace(new), \
            "rule_judgment.jinja output differs from original f-string"


class TestMemoryPromptRegression:
    """Ensure memory templates match originals."""

    def test_rate_importance_matches_original(self):
        """Test memory/importance_rating.jinja matches original f-string.

        Source: src/guidance_agent/core/memory.py:389-397
        Original: original_rate_importance_prompt()
        Template: memory/importance_rating.jinja
        """
        observation = "Customer expressed strong anxiety about running out of money and mentioned their mother's financial struggles in retirement"

        # Original f-string output
        original = original_rate_importance_prompt(
            observation=observation,
        )

        # New template output
        new = render_template(
            "memory/importance_rating.jinja",
            observation=observation,
        )

        # Compare with normalized whitespace
        assert normalize_whitespace(original) == normalize_whitespace(new), \
            "importance_rating.jinja output differs from original f-string"


class TestEvaluationPromptRegression:
    """Ensure evaluation templates match originals."""

    def test_llm_judge_evaluate_matches_original(self):
        """Test evaluation/llm_judge_evaluate.jinja matches original f-string.

        Source: src/guidance_agent/evaluation/judge_validation.py:75-86
        Original: original_llm_judge_evaluate_prompt()
        Template: evaluation/llm_judge_evaluate.jinja
        """
        transcript = """Advisor: Hello, I understand you have questions about pension access.
Customer: Yes, I'm 55 and wondering if I should take my pension now.
Advisor: There are several options you could consider. At 55, you can access your pension, including taking a 25% tax-free lump sum. However, taking it early means your pot has less time to grow.
Customer: What would you recommend?
Advisor: I can't make recommendations, but I can help you understand the pros and cons of different options so you can make an informed decision."""

        # Original f-string output
        original = original_llm_judge_evaluate_prompt(
            transcript=transcript,
        )

        # New template output
        new = render_template(
            "evaluation/llm_judge_evaluate.jinja",
            transcript=transcript,
        )

        # Compare with normalized whitespace
        assert normalize_whitespace(original) == normalize_whitespace(new), \
            "llm_judge_evaluate.jinja output differs from original f-string"


# ============================================================================
# Test Summary
# ============================================================================

"""
Regression Test Coverage Summary:

Class TestGuidancePromptRegression:
    1. test_guidance_main_matches_original - advisor/guidance_main.jinja
    2. test_guidance_cached_matches_original - advisor/guidance_cached.jinja
    3. test_reasoning_matches_original - advisor/reasoning.jinja
    4. test_guidance_with_reasoning_matches_original - advisor/guidance_with_reasoning.jinja
    5. test_refine_for_compliance_matches_original - advisor/refine_for_compliance.jinja
    6. test_handle_borderline_case_matches_original - advisor/handle_borderline_case.jinja

Class TestCompliancePromptRegression:
    7. test_validation_matches_original - compliance/validation.jinja

Class TestCustomerPromptRegression:
    8. test_simulate_comprehension_matches_original - customer/simulate_comprehension.jinja
    9. test_customer_respond_matches_original - customer/customer_respond.jinja
    10. test_simulate_outcome_matches_original - customer/simulate_outcome.jinja
    11. test_generate_demographics_matches_original - customer/generate_demographics.jinja
    12. test_generate_financial_situation_matches_original - customer/generate_financial_situation.jinja
    13. test_generate_pension_pot_matches_original - customer/generate_pension_pot.jinja
    14. test_generate_goals_and_inquiry_matches_original - customer/generate_goals_and_inquiry.jinja

Class TestLearningPromptRegression:
    15. test_reflect_on_failure_matches_original - learning/reflect_on_failure.jinja
    16. test_validate_principle_matches_original - learning/validate_principle.jinja
    17. test_refine_principle_matches_original - learning/refine_principle.jinja
    18. test_judge_rule_value_matches_original - learning/judge_rule_value.jinja

Class TestMemoryPromptRegression:
    19. test_rate_importance_matches_original - memory/rate_importance.jinja

Class TestEvaluationPromptRegression:
    20. test_llm_judge_evaluate_matches_original - evaluation/llm_judge_evaluate.jinja

Total: 20 regression test methods covering all original prompt functions.

Each test:
- Uses identical sample data from tests/fixtures/template_data.py
- Calls both the original f-string function and the new template
- Normalizes whitespace before comparison
- Provides clear error messages if outputs differ
- Documents the source file, original function, and template path

These tests will guide the migration by failing until each template is
created and produces output identical to its original f-string equivalent.
"""
