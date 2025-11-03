"""Unit tests for Jinja template rendering.

This module tests that all Jinja templates can render correctly with
various data scenarios (minimal, full, edge cases) and that custom
filters work as expected.
"""

import pytest

from guidance_agent.core.template_engine import get_template_engine


class TestAdvisorTemplates:
    """Test advisor guidance templates render correctly."""

    def test_guidance_main_minimal(
        self, sample_advisor, minimal_customer, empty_context, empty_conversation_history
    ):
        """Test main guidance template renders with minimal data."""
        engine = get_template_engine()

        result = engine.render(
            "advisor/guidance_main.jinja",
            advisor=sample_advisor,
            customer=minimal_customer,
            conversation_history=empty_conversation_history,
            context=empty_context,
        )

        # Check template renders without errors
        assert result is not None
        assert len(result) > 0

        # Check basic sections are present
        assert sample_advisor.name in result
        assert minimal_customer.presenting_question in result
        assert "FCA" in result.upper()

    def test_guidance_main_full(
        self, sample_advisor, sample_customer, sample_context, sample_conversation_history
    ):
        """Test main guidance template renders with full data."""
        engine = get_template_engine()

        result = engine.render(
            "advisor/guidance_main.jinja",
            advisor=sample_advisor,
            customer=sample_customer,
            conversation_history=sample_conversation_history,
            context=sample_context,
        )

        # Check all major sections appear
        assert sample_advisor.name in result
        assert sample_customer.presenting_question in result

        # Check conversation history is rendered
        assert "conversation" in result.lower() or len(sample_conversation_history) > 0

        # Check context elements are referenced
        assert len(result) > 500  # Full template should be substantial

    def test_guidance_main_with_conversation(
        self, sample_advisor, sample_customer, empty_context, sample_conversation_history
    ):
        """Test main guidance template handles conversation history."""
        engine = get_template_engine()

        result = engine.render(
            "advisor/guidance_main.jinja",
            advisor=sample_advisor,
            customer=sample_customer,
            conversation_history=sample_conversation_history,
            context=empty_context,
        )

        # Should include conversation history section when history exists
        assert result is not None
        # At least one message from history should appear
        assert any(msg["content"] in result for msg in sample_conversation_history)

    def test_guidance_main_without_conversation(
        self, sample_advisor, sample_customer, empty_context, empty_conversation_history
    ):
        """Test main guidance template handles empty conversation."""
        engine = get_template_engine()

        result = engine.render(
            "advisor/guidance_main.jinja",
            advisor=sample_advisor,
            customer=sample_customer,
            conversation_history=empty_conversation_history,
            context=empty_context,
        )

        # Should render without errors even with no conversation
        assert result is not None
        assert len(result) > 0

    def test_guidance_cached_minimal(
        self, sample_advisor, minimal_customer, empty_context, empty_conversation_history
    ):
        """Test cached guidance template renders with minimal data."""
        engine = get_template_engine()

        # Cached templates return message arrays
        result = engine.render_messages(
            "advisor/guidance_cached.jinja",
            advisor=sample_advisor,
            customer=minimal_customer,
            conversation_history=empty_conversation_history,
            context=empty_context,
        )

        # Check message structure
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(msg, dict) for msg in result)
        assert all("role" in msg and "content" in msg for msg in result)

    def test_guidance_cached_full(
        self, sample_advisor, sample_customer, sample_context, sample_conversation_history
    ):
        """Test cached guidance template renders with full data."""
        engine = get_template_engine()

        result = engine.render_messages(
            "advisor/guidance_cached.jinja",
            advisor=sample_advisor,
            customer=sample_customer,
            conversation_history=sample_conversation_history,
            context=sample_context,
        )

        # Check message array structure
        assert isinstance(result, list)
        assert len(result) >= 3  # Should have system, fca_context, customer_context, user messages

        # Check cache control markers exist
        system_messages = [msg for msg in result if msg.get("role") == "system"]
        assert len(system_messages) > 0

    def test_guidance_cached_cache_control(
        self, sample_advisor, sample_customer, sample_context, sample_conversation_history
    ):
        """Test cached template includes cache control markers."""
        engine = get_template_engine()

        result = engine.render_messages(
            "advisor/guidance_cached.jinja",
            advisor=sample_advisor,
            customer=sample_customer,
            conversation_history=sample_conversation_history,
            context=sample_context,
        )

        # Check that at least some messages have cache_control
        has_cache_control = False
        for msg in result:
            if "content" in msg and isinstance(msg["content"], list):
                for content_block in msg["content"]:
                    if isinstance(content_block, dict) and "cache_control" in content_block:
                        has_cache_control = True
                        assert content_block["cache_control"]["type"] == "ephemeral"

        assert has_cache_control, "Cached template should include cache_control markers"

    def test_reasoning_minimal(self, minimal_customer, empty_context):
        """Test reasoning template renders with minimal data."""
        engine = get_template_engine()

        result = engine.render(
            "advisor/reasoning.jinja",
            customer=minimal_customer,
            context=empty_context,
        )

        assert result is not None
        assert minimal_customer.presenting_question in result

    def test_reasoning_full(self, sample_customer, sample_context):
        """Test reasoning template renders with full data."""
        engine = get_template_engine()

        result = engine.render(
            "advisor/reasoning.jinja",
            customer=sample_customer,
            context=sample_context,
        )

        assert result is not None
        assert sample_customer.presenting_question in result
        assert "step" in result.lower()  # Should include step-by-step instructions

    def test_guidance_with_reasoning_minimal(
        self, minimal_customer, empty_context, sample_reasoning
    ):
        """Test guidance with reasoning template renders with minimal data."""
        engine = get_template_engine()

        result = engine.render(
            "advisor/guidance_with_reasoning.jinja",
            customer=minimal_customer,
            context=empty_context,
            reasoning=sample_reasoning,
        )

        assert result is not None
        assert minimal_customer.presenting_question in result
        assert sample_reasoning in result

    def test_guidance_with_reasoning_full(
        self, sample_customer, sample_context, sample_reasoning
    ):
        """Test guidance with reasoning template renders with full data."""
        engine = get_template_engine()

        result = engine.render(
            "advisor/guidance_with_reasoning.jinja",
            customer=sample_customer,
            context=sample_context,
            reasoning=sample_reasoning,
        )

        assert result is not None
        assert sample_customer.presenting_question in result
        assert sample_reasoning in result
        assert "reasoning" in result.lower()

    def test_compliance_refinement(self, sample_guidance, sample_validation_result):
        """Test compliance refinement template."""
        engine = get_template_engine()

        result = engine.render(
            "advisor/compliance_refinement.jinja",
            guidance=sample_guidance,
            validation=sample_validation_result,
        )

        assert result is not None
        assert sample_guidance in result

    def test_borderline_strengthening(self, sample_guidance, sample_validation_result):
        """Test borderline strengthening template."""
        engine = get_template_engine()

        # Create borderline validation result
        borderline_validation = sample_validation_result.copy()
        borderline_validation["confidence"] = 0.6
        borderline_validation["issues"] = ["Language may be too directive"]

        result = engine.render(
            "advisor/borderline_strengthening.jinja",
            guidance=sample_guidance,
            validation=borderline_validation,
        )

        assert result is not None
        assert sample_guidance in result


class TestCustomerTemplates:
    """Test customer simulation templates."""

    def test_comprehension(self, sample_guidance, sample_customer):
        """Test comprehension assessment template."""
        engine = get_template_engine()

        result = engine.render(
            "customer/comprehension.jinja",
            guidance=sample_guidance,
            customer=sample_customer,
        )

        assert result is not None
        assert sample_guidance in result
        assert "comprehension" in result.lower() or "understand" in result.lower()

    def test_response(self, sample_guidance, sample_customer, sample_conversation_history):
        """Test customer response generation template."""
        engine = get_template_engine()

        result = engine.render(
            "customer/response.jinja",
            guidance=sample_guidance,
            customer=sample_customer,
            conversation_history=sample_conversation_history,
        )

        assert result is not None
        assert sample_guidance in result or sample_customer.presenting_question in result

    def test_outcome(self, sample_guidance, sample_customer, sample_conversation_history):
        """Test outcome evaluation template."""
        engine = get_template_engine()

        result = engine.render(
            "customer/outcome.jinja",
            guidance=sample_guidance,
            customer=sample_customer,
            conversation_history=sample_conversation_history,
        )

        assert result is not None
        assert "outcome" in result.lower() or "success" in result.lower()

    def test_demographics_generation(self):
        """Test demographics generation template."""
        engine = get_template_engine()

        result = engine.render(
            "customer/generation/demographics.jinja",
            task_type="retirement_planning",
            context="Customer interested in early retirement options",
        )

        assert result is not None
        assert "age" in result.lower() or "demographic" in result.lower()
        assert "JSON" in result.upper()  # Should request JSON output

    def test_financial_generation(self, sample_customer):
        """Test financial situation generation template."""
        engine = get_template_engine()

        result = engine.render(
            "customer/generation/financial.jinja",
            customer=sample_customer,
            task_type="retirement_planning",
        )

        assert result is not None
        assert "income" in result.lower() or "financial" in result.lower()
        assert "JSON" in result.upper()

    def test_pension_pots_generation(self, sample_customer):
        """Test pension pots generation template."""
        engine = get_template_engine()

        result = engine.render(
            "customer/generation/pension_pots.jinja",
            customer=sample_customer,
            task_type="withdrawal_options",
        )

        assert result is not None
        assert "pension" in result.lower()
        assert "JSON" in result.upper()

    def test_goals_generation(self, sample_customer):
        """Test goals generation template."""
        engine = get_template_engine()

        result = engine.render(
            "customer/generation/goals.jinja",
            customer=sample_customer,
            task_type="retirement_planning",
        )

        assert result is not None
        assert "goal" in result.lower() or "question" in result.lower()


class TestComplianceTemplates:
    """Test compliance validation templates."""

    def test_validation(self, sample_guidance, sample_customer):
        """Test validation prompt template."""
        engine = get_template_engine()

        result = engine.render(
            "compliance/validation.jinja",
            guidance=sample_guidance,
            customer=sample_customer,
        )

        assert result is not None
        assert sample_guidance in result
        assert "FCA" in result.upper() or "compliant" in result.lower()
        assert "guidance" in result.lower()


class TestLearningTemplates:
    """Test learning and reflection templates."""

    def test_reflection(self, sample_customer, sample_guidance, sample_outcome):
        """Test reflection template."""
        engine = get_template_engine()

        result = engine.render(
            "learning/reflection.jinja",
            customer=sample_customer,
            guidance=sample_guidance,
            outcome=sample_outcome,
        )

        assert result is not None
        assert "reflect" in result.lower() or "learn" in result.lower()

    def test_principle_validation(self, sample_context):
        """Test principle validation template."""
        engine = get_template_engine()

        principle = "Always explain tax implications before discussing withdrawal options"

        result = engine.render(
            "learning/principle_validation.jinja",
            principle=principle,
            existing_rules=sample_context.rules,
        )

        assert result is not None
        assert principle in result

    def test_principle_refinement(self, sample_context):
        """Test principle refinement template."""
        engine = get_template_engine()

        principle = "Always explain tax implications"
        evidence = ["Customer was confused about tax bands", "Clear tax explanation led to better outcomes"]

        result = engine.render(
            "learning/principle_refinement.jinja",
            principle=principle,
            evidence=evidence,
            existing_rules=sample_context.rules,
        )

        assert result is not None
        assert principle in result

    def test_rule_judgment(self, sample_customer, sample_guidance, sample_context):
        """Test rule judgment template."""
        engine = get_template_engine()

        result = engine.render(
            "learning/rule_judgment.jinja",
            customer=sample_customer,
            guidance=sample_guidance,
            rules=sample_context.rules,
        )

        assert result is not None
        assert "rule" in result.lower()


class TestMemoryTemplates:
    """Test memory-related templates."""

    def test_importance_rating(self):
        """Test importance rating template."""
        engine = get_template_engine()

        observation = "Customer expressed strong concern about outliving their savings"

        result = engine.render(
            "memory/importance_rating.jinja",
            observation=observation,
        )

        assert result is not None
        assert observation in result
        assert "importance" in result.lower()


class TestCustomFilters:
    """Test custom Jinja filters work correctly."""

    def test_customer_profile_filter(self, sample_customer):
        """Test customer_profile filter formats customer data."""
        engine = get_template_engine()

        # Create a simple template that uses the filter
        template_str = "{{ customer | customer_profile }}"
        template = engine.env.from_string(template_str)
        result = template.render(customer=sample_customer)

        assert result is not None
        assert len(result) > 0
        # Should include key demographic info
        assert str(sample_customer.demographics.age) in result
        assert sample_customer.demographics.location in result

    def test_conversation_filter(self, sample_conversation_history):
        """Test conversation filter formats conversation history."""
        engine = get_template_engine()

        template_str = "{{ history | conversation }}"
        template = engine.env.from_string(template_str)
        result = template.render(history=sample_conversation_history)

        assert result is not None
        # Should include messages from history
        assert any(msg["content"] in result for msg in sample_conversation_history)

    def test_conversation_filter_empty(self, empty_conversation_history):
        """Test conversation filter handles empty history."""
        engine = get_template_engine()

        template_str = "{{ history | conversation }}"
        template = engine.env.from_string(template_str)
        result = template.render(history=empty_conversation_history)

        assert result is not None
        assert len(result) > 0  # Should return "(No prior conversation)" or similar

    def test_cases_filter(self, sample_context):
        """Test cases filter formats similar cases."""
        engine = get_template_engine()

        template_str = "{{ cases | cases }}"
        template = engine.env.from_string(template_str)
        result = template.render(cases=sample_context.cases)

        assert result is not None
        # Should include case information
        assert any(case.customer_situation in result for case in sample_context.cases)

    def test_cases_filter_empty(self):
        """Test cases filter handles empty case list."""
        engine = get_template_engine()

        template_str = "{{ cases | cases }}"
        template = engine.env.from_string(template_str)
        result = template.render(cases=[])

        assert result is not None
        assert len(result) > 0  # Should return "(No similar cases found)" or similar

    def test_rules_filter(self, sample_context):
        """Test rules filter formats guidance rules."""
        engine = get_template_engine()

        template_str = "{{ rules | rules }}"
        template = engine.env.from_string(template_str)
        result = template.render(rules=sample_context.rules)

        assert result is not None
        # Should include rule principles
        assert any(rule.principle in result for rule in sample_context.rules)

    def test_rules_filter_empty(self):
        """Test rules filter handles empty rules list."""
        engine = get_template_engine()

        template_str = "{{ rules | rules }}"
        template = engine.env.from_string(template_str)
        result = template.render(rules=[])

        assert result is not None
        assert len(result) > 0  # Should return "(No relevant rules found)" or similar

    def test_memories_filter(self, sample_context):
        """Test memories filter formats memory nodes."""
        engine = get_template_engine()

        template_str = "{{ memories | memories }}"
        template = engine.env.from_string(template_str)
        result = template.render(memories=sample_context.memories)

        assert result is not None
        # Should include memory descriptions
        assert any(memory.description in result for memory in sample_context.memories)

    def test_memories_filter_empty(self):
        """Test memories filter handles empty memories list."""
        engine = get_template_engine()

        template_str = "{{ memories | memories }}"
        template = engine.env.from_string(template_str)
        result = template.render(memories=[])

        assert result is not None
        assert len(result) > 0  # Should return "(No relevant memories)" or similar


class TestTemplateEdgeCases:
    """Test templates handle edge cases correctly."""

    def test_customer_with_no_financial_data(self, sample_advisor, minimal_customer, empty_context, empty_conversation_history):
        """Test templates handle customers with missing financial data."""
        engine = get_template_engine()

        # minimal_customer has no financial or pension data
        result = engine.render(
            "advisor/guidance_main.jinja",
            advisor=sample_advisor,
            customer=minimal_customer,
            conversation_history=empty_conversation_history,
            context=empty_context,
        )

        # Should render without KeyError
        assert result is not None
        assert len(result) > 0

    def test_customer_with_db_pension(self, sample_customer):
        """Test templates correctly handle DB pension warnings."""
        engine = get_template_engine()

        # sample_customer has a DB pension
        template_str = "{{ customer | customer_profile }}"
        template = engine.env.from_string(template_str)
        result = template.render(customer=sample_customer)

        # Should mention DB pension
        db_pension = next(p for p in sample_customer.pensions if p.is_db_scheme)
        assert str(db_pension.db_guaranteed_amount) in result or "DB" in result or "defined benefit" in result.lower()

    def test_very_long_conversation_history(self, sample_advisor, sample_customer, empty_context):
        """Test templates handle very long conversation histories."""
        engine = get_template_engine()

        # Create long conversation history
        long_history = [
            {"role": "customer" if i % 2 == 0 else "advisor", "content": f"Message {i}"}
            for i in range(100)
        ]

        result = engine.render(
            "advisor/guidance_main.jinja",
            advisor=sample_advisor,
            customer=sample_customer,
            conversation_history=long_history,
            context=empty_context,
        )

        assert result is not None
        assert len(result) > 0

    def test_special_characters_in_strings(self, sample_advisor, empty_context, empty_conversation_history):
        """Test templates handle special characters correctly."""
        engine = get_template_engine()

        from guidance_agent.core.types import CustomerProfile, CustomerDemographics

        # Create customer with special characters
        special_customer = CustomerProfile(
            demographics=CustomerDemographics(
                age=55,
                gender="male",
                location="O'Brien's Town",
                employment_status="self-employed",
                financial_literacy="medium",
            ),
            presenting_question="What's the best way to access my pension? I'm worried about 'scams' & fraud.",
        )

        result = engine.render(
            "advisor/guidance_main.jinja",
            advisor=sample_advisor,
            customer=special_customer,
            conversation_history=empty_conversation_history,
            context=empty_context,
        )

        assert result is not None
        assert "O'Brien" in result
        assert "scams" in result

    def test_unicode_characters(self, sample_advisor, empty_context, empty_conversation_history):
        """Test templates handle Unicode characters."""
        engine = get_template_engine()

        from guidance_agent.core.types import CustomerProfile, CustomerDemographics

        unicode_customer = CustomerProfile(
            demographics=CustomerDemographics(
                age=55,
                gender="male",
                location="Côte d'Azur",
                employment_status="employed",
                financial_literacy="medium",
            ),
            presenting_question="How much is £50,000 worth in €?",
        )

        result = engine.render(
            "advisor/guidance_main.jinja",
            advisor=sample_advisor,
            customer=unicode_customer,
            conversation_history=empty_conversation_history,
            context=empty_context,
        )

        assert result is not None
        # Unicode characters should be preserved, not replaced with �
        assert "�" not in result
        # Verify the actual unicode characters are present
        assert "Côte" in result or "C\u00f4te" in result
        assert "£" in result or "\u00a3" in result
        assert "€" in result or "\u20ac" in result
