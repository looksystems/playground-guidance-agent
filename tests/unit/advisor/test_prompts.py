"""Tests for advisor prompt templates."""

import pytest
from datetime import datetime

from guidance_agent.core.types import (
    Case,
    CustomerProfile,
    CustomerDemographics,
    FinancialSituation,
    GuidanceRule,
    PensionPot,
    AdvisorProfile,
    RetrievedContext,
    MemoryType,
)
from guidance_agent.core.memory import MemoryNode
from guidance_agent.advisor.prompts import (
    format_customer_profile,
    format_conversation,
    format_cases,
    format_rules,
    format_memories,
    build_guidance_prompt,
    build_reasoning_prompt,
    build_guidance_prompt_with_reasoning,
)


class TestFormatCustomerProfile:
    """Tests for format_customer_profile function."""

    @pytest.fixture
    def customer_profile(self):
        """Create a sample customer profile."""
        return CustomerProfile(
            demographics=CustomerDemographics(
                age=55,
                gender="M",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            financial=FinancialSituation(
                annual_income=50000,
                total_assets=200000,
                total_debt=10000,
                dependents=0,
                risk_tolerance="medium",
            ),
            pensions=[
                PensionPot(
                    pot_id="pot1",
                    provider="Provider A",
                    pot_type="defined_contribution",
                    current_value=100000,
                    projected_value=120000,
                    age_accessible=55,
                )
            ],
            goals="Understanding my pension withdrawal options",
        )

    def test_format_includes_demographics(self, customer_profile):
        """Test that formatting includes demographic information."""
        formatted = format_customer_profile(customer_profile)

        assert "55" in formatted  # age
        assert "London" in formatted  # location
        assert "employed" in formatted  # employment status
        assert "medium" in formatted  # financial literacy

    def test_format_includes_financial_situation(self, customer_profile):
        """Test that formatting includes financial information."""
        formatted = format_customer_profile(customer_profile)

        assert "50000" in formatted or "50,000" in formatted  # income
        assert "medium" in formatted  # risk tolerance

    def test_format_includes_pension_details(self, customer_profile):
        """Test that formatting includes pension pot details."""
        formatted = format_customer_profile(customer_profile)

        assert "Provider A" in formatted
        assert "100000" in formatted or "100,000" in formatted  # current value
        assert "defined_contribution" in formatted or "defined contribution" in formatted

    def test_format_includes_goals(self, customer_profile):
        """Test that formatting includes customer goals."""
        formatted = format_customer_profile(customer_profile)

        assert "Understanding my pension withdrawal options" in formatted

    def test_format_handles_multiple_pensions(self):
        """Test formatting with multiple pension pots."""
        customer = CustomerProfile(
            demographics=CustomerDemographics(
                age=60,
                gender="F",
                location="Manchester",
                employment_status="retired",
                financial_literacy="high",
            ),
            pensions=[
                PensionPot(
                    pot_id="pot1",
                    provider="Provider A",
                    pot_type="defined_contribution",
                    current_value=100000,
                    projected_value=120000,
                    age_accessible=55,
                ),
                PensionPot(
                    pot_id="pot2",
                    provider="Provider B",
                    pot_type="defined_benefit",
                    current_value=200000,
                    projected_value=200000,
                    age_accessible=65,
                    is_db_scheme=True,
                    db_guaranteed_amount=15000,
                ),
            ],
            goals="Maximize retirement income",
        )

        formatted = format_customer_profile(customer)

        assert "Provider A" in formatted
        assert "Provider B" in formatted
        assert "defined_benefit" in formatted or "defined benefit" in formatted

    def test_format_highlights_db_pension(self):
        """Test that DB pensions are highlighted."""
        customer = CustomerProfile(
            demographics=CustomerDemographics(
                age=60,
                gender="F",
                location="Manchester",
                employment_status="retired",
                financial_literacy="medium",
            ),
            pensions=[
                PensionPot(
                    pot_id="pot1",
                    provider="Company Pension",
                    pot_type="defined_benefit",
                    current_value=500000,
                    projected_value=500000,
                    age_accessible=65,
                    is_db_scheme=True,
                    db_guaranteed_amount=20000,
                )
            ],
            goals="Considering transferring pension",
        )

        formatted = format_customer_profile(customer)

        # Should highlight DB scheme
        assert "defined benefit" in formatted.lower() or "db" in formatted.lower()
        assert "20000" in formatted or "20,000" in formatted  # guaranteed amount


class TestFormatConversation:
    """Tests for format_conversation function."""

    def test_format_empty_conversation(self):
        """Test formatting empty conversation history."""
        formatted = format_conversation([])

        assert formatted is not None
        assert len(formatted) > 0  # Should have some placeholder text

    def test_format_single_message(self):
        """Test formatting conversation with single message."""
        conversation = [
            {"role": "customer", "content": "I want to understand my pension options"}
        ]

        formatted = format_conversation(conversation)

        assert "customer" in formatted.lower() or "Customer" in formatted
        assert "pension options" in formatted

    def test_format_multi_turn_conversation(self):
        """Test formatting multi-turn conversation."""
        conversation = [
            {"role": "customer", "content": "I want to understand my pension options"},
            {
                "role": "advisor",
                "content": "I'd be happy to help. What specifically would you like to know?",
            },
            {
                "role": "customer",
                "content": "Can I take some money out before I retire?",
            },
        ]

        formatted = format_conversation(conversation)

        assert "pension options" in formatted
        assert "happy to help" in formatted
        assert "take some money out" in formatted

    def test_format_maintains_conversation_order(self):
        """Test that conversation order is maintained."""
        conversation = [
            {"role": "customer", "content": "First message"},
            {"role": "advisor", "content": "Second message"},
            {"role": "customer", "content": "Third message"},
        ]

        formatted = format_conversation(conversation)

        # First message should appear before second, etc.
        first_pos = formatted.index("First message")
        second_pos = formatted.index("Second message")
        third_pos = formatted.index("Third message")

        assert first_pos < second_pos < third_pos


class TestFormatCases:
    """Tests for format_cases function."""

    def test_format_empty_cases(self):
        """Test formatting with no cases."""
        formatted = format_cases([])

        assert formatted is not None
        # Should indicate no cases available
        assert "no" in formatted.lower() or "none" in formatted.lower()

    def test_format_single_case(self):
        """Test formatting single case."""
        cases = [
            Case(
                case_id="case1",
                task_type="withdrawal_options",
                customer_situation="55-year-old seeking early withdrawal",
                guidance_provided="Explained tax-free lump sum and drawdown options",
                outcome_summary="Customer understood options and satisfied",
                similarity_score=0.95,
            )
        ]

        formatted = format_cases(cases)

        assert "55-year-old" in formatted
        assert "withdrawal" in formatted
        assert "tax-free lump sum" in formatted

    def test_format_multiple_cases(self):
        """Test formatting multiple cases."""
        cases = [
            Case(
                case_id="case1",
                task_type="withdrawal_options",
                customer_situation="55-year-old seeking early withdrawal",
                guidance_provided="Explained options",
                outcome_summary="Successful",
                similarity_score=0.95,
            ),
            Case(
                case_id="case2",
                task_type="retirement_planning",
                customer_situation="60-year-old planning retirement",
                guidance_provided="Discussed income needs",
                outcome_summary="Successful",
                similarity_score=0.87,
            ),
        ]

        formatted = format_cases(cases)

        assert "55-year-old" in formatted
        assert "60-year-old" in formatted
        assert "withdrawal" in formatted
        assert "retirement" in formatted

    def test_format_includes_similarity_scores(self):
        """Test that similarity scores are included."""
        cases = [
            Case(
                case_id="case1",
                task_type="withdrawal_options",
                customer_situation="Test situation",
                guidance_provided="Test guidance",
                outcome_summary="Test outcome",
                similarity_score=0.95,
            )
        ]

        formatted = format_cases(cases)

        # Should include similarity info
        assert "similar" in formatted.lower() or "0.95" in formatted or "95" in formatted


class TestFormatRules:
    """Tests for format_rules function."""

    def test_format_empty_rules(self):
        """Test formatting with no rules."""
        formatted = format_rules([])

        assert formatted is not None
        # Should indicate no rules available
        assert "no" in formatted.lower() or "none" in formatted.lower()

    def test_format_single_rule(self):
        """Test formatting single rule."""
        rules = [
            GuidanceRule(
                rule_id="rule1",
                principle="Always check customer understanding before proceeding",
                domain="communication",
                confidence=0.90,
                evidence_count=10,
            )
        ]

        formatted = format_rules(rules)

        assert "check customer understanding" in formatted
        assert "communication" in formatted

    def test_format_includes_confidence(self):
        """Test that confidence scores are included."""
        rules = [
            GuidanceRule(
                rule_id="rule1",
                principle="Explain risks clearly",
                domain="risk_disclosure",
                confidence=0.85,
                evidence_count=5,
            )
        ]

        formatted = format_rules(rules)

        # Should include confidence info
        assert "0.85" in formatted or "85" in formatted or "confidence" in formatted.lower()

    def test_format_multiple_rules(self):
        """Test formatting multiple rules."""
        rules = [
            GuidanceRule(
                rule_id="rule1",
                principle="Always check understanding",
                domain="communication",
                confidence=0.90,
                evidence_count=10,
            ),
            GuidanceRule(
                rule_id="rule2",
                principle="Explain tax implications",
                domain="tax",
                confidence=0.85,
                evidence_count=8,
            ),
        ]

        formatted = format_rules(rules)

        assert "check understanding" in formatted
        assert "tax implications" in formatted


class TestFormatMemories:
    """Tests for format_memories function."""

    def test_format_empty_memories(self):
        """Test formatting with no memories."""
        formatted = format_memories([])

        assert formatted is not None
        # Should indicate no memories
        assert "no" in formatted.lower() or "none" in formatted.lower()

    def test_format_single_memory(self):
        """Test formatting single memory."""
        memories = [
            MemoryNode(
                description="Customer seemed confused about tax implications",
                timestamp=datetime.now(),
                importance=0.7,
                memory_type=MemoryType.OBSERVATION,
                embedding=[0.1] * 1536,
            )
        ]

        formatted = format_memories(memories)

        assert "confused about tax" in formatted
        assert "observation" in formatted.lower()

    def test_format_includes_memory_types(self):
        """Test that memory types are included."""
        memories = [
            MemoryNode(
                description="Observation test",
                timestamp=datetime.now(),
                importance=0.6,
                memory_type=MemoryType.OBSERVATION,
                embedding=[0.1] * 1536,
            ),
            MemoryNode(
                description="Reflection test",
                timestamp=datetime.now(),
                importance=0.8,
                memory_type=MemoryType.REFLECTION,
                embedding=[0.1] * 1536,
            ),
        ]

        formatted = format_memories(memories)

        assert "observation" in formatted.lower()
        assert "reflection" in formatted.lower()


class TestBuildGuidancePrompt:
    """Tests for build_guidance_prompt function."""

    @pytest.fixture
    def advisor_profile(self):
        """Create an advisor profile."""
        return AdvisorProfile(
            name="Sarah",
            description="Experienced pension guidance specialist",
            specialization="Pension withdrawals",
        )

    @pytest.fixture
    def customer_profile(self):
        """Create a customer profile."""
        return CustomerProfile(
            demographics=CustomerDemographics(
                age=55,
                gender="M",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            financial=FinancialSituation(
                annual_income=50000,
                total_assets=200000,
                total_debt=10000,
                dependents=0,
                risk_tolerance="medium",
            ),
            pensions=[
                PensionPot(
                    pot_id="pot1",
                    provider="Provider A",
                    pot_type="defined_contribution",
                    current_value=100000,
                    projected_value=120000,
                    age_accessible=55,
                )
            ],
            goals="Understanding withdrawal options",
            presenting_question="Can I access my pension now?",
        )

    @pytest.fixture
    def context(self):
        """Create a retrieved context."""
        return RetrievedContext(
            memories=[],
            cases=[
                Case(
                    case_id="case1",
                    task_type="withdrawal_options",
                    customer_situation="Similar customer",
                    guidance_provided="Explained options",
                    outcome_summary="Success",
                    similarity_score=0.9,
                )
            ],
            rules=[
                GuidanceRule(
                    rule_id="rule1",
                    principle="Check understanding",
                    domain="communication",
                    confidence=0.85,
                    evidence_count=5,
                )
            ],
            fca_requirements="Must stay within guidance boundary",
        )

    def test_build_guidance_prompt_includes_advisor(
        self, advisor_profile, customer_profile, context
    ):
        """Test that prompt includes advisor information."""
        conversation = []
        prompt = build_guidance_prompt(
            advisor_profile, customer_profile, context, conversation
        )

        assert "Sarah" in prompt
        assert "pension guidance specialist" in prompt.lower()

    def test_build_guidance_prompt_includes_customer(
        self, advisor_profile, customer_profile, context
    ):
        """Test that prompt includes customer information."""
        conversation = []
        prompt = build_guidance_prompt(
            advisor_profile, customer_profile, context, conversation
        )

        assert "55" in prompt  # age
        assert "withdrawal options" in prompt.lower()
        assert "Can I access my pension now?" in prompt

    def test_build_guidance_prompt_includes_context(
        self, advisor_profile, customer_profile, context
    ):
        """Test that prompt includes retrieved context."""
        conversation = []
        prompt = build_guidance_prompt(
            advisor_profile, customer_profile, context, conversation
        )

        assert "Similar customer" in prompt  # from case
        assert "Check understanding" in prompt  # from rule
        assert "guidance boundary" in prompt  # from FCA requirements

    def test_build_guidance_prompt_includes_fca_requirements(
        self, advisor_profile, customer_profile, context
    ):
        """Test that prompt includes FCA compliance requirements."""
        conversation = []
        prompt = build_guidance_prompt(
            advisor_profile, customer_profile, context, conversation
        )

        assert "FCA" in prompt or "guidance" in prompt.lower()
        assert "boundary" in prompt.lower() or "compliance" in prompt.lower()

    def test_build_guidance_prompt_structure(
        self, advisor_profile, customer_profile, context
    ):
        """Test that prompt has proper structure."""
        conversation = []
        prompt = build_guidance_prompt(
            advisor_profile, customer_profile, context, conversation
        )

        # Should have clear sections
        assert len(prompt) > 100  # Not trivially short
        # Should mention key concepts
        assert any(
            word in prompt.lower()
            for word in ["customer", "guidance", "pension", "question"]
        )


class TestBuildReasoningPrompt:
    """Tests for build_reasoning_prompt function."""

    @pytest.fixture
    def customer_profile(self):
        """Create a customer profile."""
        return CustomerProfile(
            demographics=CustomerDemographics(
                age=55,
                gender="M",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            goals="Understanding withdrawal options",
            presenting_question="Can I access my pension now?",
        )

    @pytest.fixture
    def context(self):
        """Create a retrieved context."""
        return RetrievedContext(
            cases=[],
            rules=[],
            fca_requirements="Stay within guidance boundary",
        )

    def test_build_reasoning_prompt_basic(self, customer_profile, context):
        """Test basic reasoning prompt construction."""
        prompt = build_reasoning_prompt(customer_profile, context)

        assert "reason" in prompt.lower() or "think" in prompt.lower()
        assert "Can I access my pension now?" in prompt

    def test_build_reasoning_prompt_includes_context(self, customer_profile, context):
        """Test that reasoning prompt includes context."""
        prompt = build_reasoning_prompt(customer_profile, context)

        assert "guidance boundary" in prompt.lower()


class TestBuildGuidancePromptWithReasoning:
    """Tests for build_guidance_prompt_with_reasoning function."""

    @pytest.fixture
    def customer_profile(self):
        """Create a customer profile."""
        return CustomerProfile(
            demographics=CustomerDemographics(
                age=55,
                gender="M",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            goals="Understanding withdrawal options",
            presenting_question="Can I access my pension now?",
        )

    @pytest.fixture
    def context(self):
        """Create a retrieved context."""
        return RetrievedContext(
            cases=[],
            rules=[],
            fca_requirements="Stay within guidance boundary",
        )

    def test_build_prompt_with_reasoning(self, customer_profile, context):
        """Test building guidance prompt with reasoning."""
        reasoning = """
        The customer is 55 and asking about pension access.
        At 55, they can access their defined contribution pension.
        Need to explain options without recommending specific choice.
        """

        prompt = build_guidance_prompt_with_reasoning(
            customer_profile, context, reasoning
        )

        assert reasoning in prompt
        assert "Can I access my pension now?" in prompt

    def test_prompt_with_reasoning_instructs_use(self, customer_profile, context):
        """Test that prompt instructs to use the reasoning."""
        reasoning = "Test reasoning"

        prompt = build_guidance_prompt_with_reasoning(
            customer_profile, context, reasoning
        )

        # Should instruct to use the reasoning
        assert "reasoning" in prompt.lower()


class TestBuildGuidancePromptCached:
    """Tests for build_guidance_prompt_cached function (cache-optimized prompts)."""

    @pytest.fixture
    def advisor_profile(self):
        """Create an advisor profile."""
        return AdvisorProfile(
            name="Sarah",
            description="Experienced pension guidance specialist",
            specialization="Pension withdrawals",
        )

    @pytest.fixture
    def customer_profile(self):
        """Create a customer profile."""
        return CustomerProfile(
            demographics=CustomerDemographics(
                age=55,
                gender="M",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            financial=FinancialSituation(
                annual_income=50000,
                total_assets=200000,
                total_debt=10000,
                dependents=0,
                risk_tolerance="medium",
            ),
            pensions=[
                PensionPot(
                    pot_id="pot1",
                    provider="Provider A",
                    pot_type="defined_contribution",
                    current_value=100000,
                    projected_value=120000,
                    age_accessible=55,
                )
            ],
            goals="Understanding withdrawal options",
            presenting_question="Can I access my pension now?",
        )

    @pytest.fixture
    def context(self):
        """Create a retrieved context."""
        return RetrievedContext(
            memories=[],
            cases=[
                Case(
                    case_id="case1",
                    task_type="withdrawal_options",
                    customer_situation="Similar customer",
                    guidance_provided="Explained options",
                    outcome_summary="Success",
                    similarity_score=0.9,
                )
            ],
            rules=[
                GuidanceRule(
                    rule_id="rule1",
                    principle="Check understanding",
                    domain="communication",
                    confidence=0.85,
                    evidence_count=5,
                )
            ],
            fca_requirements="Must stay within guidance boundary",
        )

    def test_cached_prompt_returns_message_array(
        self, advisor_profile, customer_profile, context
    ):
        """Test that cached prompt returns array of messages, not string."""
        from guidance_agent.advisor.prompts import build_guidance_prompt_cached

        messages = build_guidance_prompt_cached(
            advisor_profile, customer_profile, context, []
        )

        # Should return list, not string
        assert isinstance(messages, list)
        assert len(messages) > 0

    def test_cached_prompt_has_correct_structure(
        self, advisor_profile, customer_profile, context
    ):
        """Test that cached prompt has 4-part structure for optimal caching."""
        from guidance_agent.advisor.prompts import build_guidance_prompt_cached

        messages = build_guidance_prompt_cached(
            advisor_profile, customer_profile, context, []
        )

        # Should have 4 messages: system prompt, FCA context, customer context, user message
        assert len(messages) == 4

        # Check roles
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "system"
        assert messages[2]["role"] == "system"
        assert messages[3]["role"] == "user"

    def test_cached_prompt_system_prompt_has_cache_control(
        self, advisor_profile, customer_profile, context
    ):
        """Test that system prompt has cache control marker."""
        from guidance_agent.advisor.prompts import build_guidance_prompt_cached

        messages = build_guidance_prompt_cached(
            advisor_profile, customer_profile, context, []
        )

        # First message (system prompt) should have cache control
        system_message = messages[0]
        assert "content" in system_message
        assert isinstance(system_message["content"], list)
        assert len(system_message["content"]) > 0

        content_block = system_message["content"][0]
        assert "type" in content_block
        assert content_block["type"] == "text"
        assert "cache_control" in content_block
        assert content_block["cache_control"]["type"] == "ephemeral"

    def test_cached_prompt_fca_requirements_has_cache_control(
        self, advisor_profile, customer_profile, context
    ):
        """Test that FCA requirements have cache control marker."""
        from guidance_agent.advisor.prompts import build_guidance_prompt_cached

        messages = build_guidance_prompt_cached(
            advisor_profile, customer_profile, context, []
        )

        # Second message (FCA requirements) should have cache control
        fca_message = messages[1]
        assert "content" in fca_message
        assert isinstance(fca_message["content"], list)

        content_block = fca_message["content"][0]
        assert "cache_control" in content_block
        assert content_block["cache_control"]["type"] == "ephemeral"

    def test_cached_prompt_customer_context_has_cache_control(
        self, advisor_profile, customer_profile, context
    ):
        """Test that customer context has cache control marker."""
        from guidance_agent.advisor.prompts import build_guidance_prompt_cached

        messages = build_guidance_prompt_cached(
            advisor_profile, customer_profile, context, []
        )

        # Third message (customer context) should have cache control
        customer_message = messages[2]
        assert "content" in customer_message
        assert isinstance(customer_message["content"], list)

        content_block = customer_message["content"][0]
        assert "cache_control" in content_block
        assert content_block["cache_control"]["type"] == "ephemeral"

    def test_cached_prompt_user_message_no_cache_control(
        self, advisor_profile, customer_profile, context
    ):
        """Test that user message (variable content) has no cache control."""
        from guidance_agent.advisor.prompts import build_guidance_prompt_cached

        messages = build_guidance_prompt_cached(
            advisor_profile, customer_profile, context, []
        )

        # Fourth message (user question) should NOT have cache control
        user_message = messages[3]
        assert "content" in user_message

        # User message content is plain string (variable, not cached)
        assert isinstance(user_message["content"], str)

    def test_cached_prompt_contains_advisor_info(
        self, advisor_profile, customer_profile, context
    ):
        """Test that system prompt contains advisor information."""
        from guidance_agent.advisor.prompts import build_guidance_prompt_cached

        messages = build_guidance_prompt_cached(
            advisor_profile, customer_profile, context, []
        )

        system_text = messages[0]["content"][0]["text"]
        assert "Sarah" in system_text
        assert "pension guidance specialist" in system_text.lower()

    def test_cached_prompt_contains_fca_requirements(
        self, advisor_profile, customer_profile, context
    ):
        """Test that FCA message contains requirements and rules."""
        from guidance_agent.advisor.prompts import build_guidance_prompt_cached

        messages = build_guidance_prompt_cached(
            advisor_profile, customer_profile, context, []
        )

        fca_text = messages[1]["content"][0]["text"]
        assert "FCA" in fca_text or "guidance boundary" in fca_text.lower()
        assert "Check understanding" in fca_text  # from rule

    def test_cached_prompt_contains_customer_profile(
        self, advisor_profile, customer_profile, context
    ):
        """Test that customer message contains profile and cases."""
        from guidance_agent.advisor.prompts import build_guidance_prompt_cached

        messages = build_guidance_prompt_cached(
            advisor_profile, customer_profile, context, []
        )

        customer_text = messages[2]["content"][0]["text"]
        assert "55" in customer_text  # age
        assert "London" in customer_text  # location
        assert "Similar customer" in customer_text  # from case

    def test_cached_prompt_contains_current_question(
        self, advisor_profile, customer_profile, context
    ):
        """Test that user message contains current question."""
        from guidance_agent.advisor.prompts import build_guidance_prompt_cached

        messages = build_guidance_prompt_cached(
            advisor_profile, customer_profile, context, []
        )

        user_text = messages[3]["content"]
        assert "Can I access my pension now?" in user_text
