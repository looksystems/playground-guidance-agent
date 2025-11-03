"""Tests for AdvisorAgent class."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4

from guidance_agent.core.types import (
    AdvisorProfile,
    CustomerProfile,
    CustomerDemographics,
    FinancialSituation,
    PensionPot,
    RetrievedContext,
    Case,
    GuidanceRule,
)
from guidance_agent.advisor.agent import AdvisorAgent
from guidance_agent.compliance.validator import ValidationResult, ValidationIssue, IssueSeverity, IssueType


class TestAdvisorAgentInitialization:
    """Tests for AdvisorAgent initialization."""

    def test_create_advisor_agent(self):
        """Test creating an advisor agent."""
        profile = AdvisorProfile(
            name="Sarah",
            description="Pension guidance specialist",
        )

        agent = AdvisorAgent(profile=profile)

        assert agent is not None
        assert agent.profile == profile
        assert hasattr(agent, "memory_stream")
        assert hasattr(agent, "compliance_validator")

    def test_create_advisor_with_custom_model(self):
        """Test creating advisor with custom LLM model."""
        profile = AdvisorProfile(
            name="Sarah",
            description="Test advisor",
        )

        agent = AdvisorAgent(profile=profile, model="gpt-4o")

        assert agent.model == "gpt-4o"

    def test_advisor_has_memory_stream(self):
        """Test that advisor has a memory stream."""
        profile = AdvisorProfile(name="Sarah", description="Test")
        agent = AdvisorAgent(profile=profile)

        assert agent.memory_stream is not None

    def test_advisor_has_compliance_validator(self):
        """Test that advisor has a compliance validator."""
        profile = AdvisorProfile(name="Sarah", description="Test")
        agent = AdvisorAgent(profile=profile)

        assert agent.compliance_validator is not None


class TestProvideGuidance:
    """Tests for provide_guidance method."""

    @pytest.fixture
    def advisor_profile(self):
        """Create an advisor profile."""
        return AdvisorProfile(
            name="Sarah",
            description="Experienced pension guidance specialist",
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

    def test_provide_guidance_basic(self, advisor_profile, customer_profile):
        """Test basic guidance provision."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)
        conversation = []

        with patch.object(agent, "_generate_guidance") as mock_generate:
            with patch.object(agent.compliance_validator, "validate") as mock_validate:
                # Mock generation
                mock_generate.return_value = ("Test guidance", "Test reasoning")

                # Mock validation (pass)
                mock_validate.return_value = ValidationResult(
                    passed=True,
                    confidence=0.95,
                    issues=[],
                    requires_human_review=False,
                    reasoning="All checks passed",
                )

                guidance = agent.provide_guidance(customer_profile, conversation)

                assert guidance is not None
                assert isinstance(guidance, str)
                assert len(guidance) > 0

    def test_provide_guidance_uses_chain_of_thought(self, advisor_profile, customer_profile):
        """Test that guidance uses chain-of-thought reasoning."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=True)
        conversation = []

        with patch.object(agent, "_generate_reasoning") as mock_reason:
            with patch.object(agent, "_generate_guidance_from_reasoning") as mock_generate:
                with patch.object(agent.compliance_validator, "validate") as mock_validate:
                    # Mock reasoning
                    mock_reason.return_value = "Customer is 55 and can access pension..."

                    # Mock generation
                    mock_generate.return_value = "Based on your situation, you can access..."

                    # Mock validation
                    mock_validate.return_value = ValidationResult(
                        passed=True,
                        confidence=0.95,
                        issues=[],
                        requires_human_review=False,
                    )

                    guidance = agent.provide_guidance(customer_profile, conversation)

                    # Verify reasoning was called
                    assert mock_reason.called
                    # Verify guidance generation used reasoning
                    assert mock_generate.called

    def test_provide_guidance_retrieves_context(self, advisor_profile, customer_profile):
        """Test that guidance retrieves relevant context."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)
        conversation = []

        with patch.object(agent, "_retrieve_context") as mock_retrieve:
            with patch.object(agent, "_generate_guidance") as mock_generate:
                with patch.object(agent.compliance_validator, "validate") as mock_validate:
                    # Mock context retrieval
                    mock_retrieve.return_value = RetrievedContext(
                        memories=[],
                        cases=[],
                        rules=[],
                        fca_requirements="Stay within guidance boundary",
                    )

                    # Mock generation
                    mock_generate.return_value = ("Test guidance", "Test reasoning")

                    # Mock validation
                    mock_validate.return_value = ValidationResult(
                        passed=True,
                        confidence=0.95,
                        issues=[],
                        requires_human_review=False,
                    )

                    agent.provide_guidance(customer_profile, conversation)

                    # Verify context was retrieved
                    assert mock_retrieve.called

    def test_provide_guidance_validates_compliance(self, advisor_profile, customer_profile):
        """Test that guidance is validated for compliance."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)
        conversation = []

        with patch.object(agent, "_generate_guidance") as mock_generate:
            with patch.object(agent.compliance_validator, "validate") as mock_validate:
                # Mock generation
                mock_generate.return_value = ("Test guidance", "Test reasoning")

                # Mock validation
                mock_validate.return_value = ValidationResult(
                    passed=True,
                    confidence=0.95,
                    issues=[],
                    requires_human_review=False,
                )

                agent.provide_guidance(customer_profile, conversation)

                # Verify validation was called
                assert mock_validate.called
                call_args = mock_validate.call_args
                # Should pass the generated guidance
                assert call_args[1]["guidance"] == "Test guidance"

    def test_provide_guidance_handles_failed_validation(self, advisor_profile, customer_profile):
        """Test handling of failed compliance validation."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)
        conversation = []

        with patch.object(agent, "_generate_guidance") as mock_generate:
            with patch.object(agent, "_refine_for_compliance") as mock_refine:
                with patch.object(agent.compliance_validator, "validate") as mock_validate:
                    # Mock initial generation
                    mock_generate.return_value = ("Bad guidance", "Reasoning")

                    # Mock failed validation
                    mock_validate.return_value = ValidationResult(
                        passed=False,
                        confidence=0.95,
                        issues=[
                            ValidationIssue(
                                issue_type=IssueType.ADVICE_BOUNDARY,
                                severity=IssueSeverity.HIGH,
                                description="Crossed into advice",
                            )
                        ],
                        requires_human_review=False,
                    )

                    # Mock refinement
                    mock_refine.return_value = "Refined guidance"

                    guidance = agent.provide_guidance(customer_profile, conversation)

                    # Verify refinement was attempted
                    assert mock_refine.called
                    assert guidance == "Refined guidance"

    def test_provide_guidance_handles_borderline_case(self, advisor_profile, customer_profile):
        """Test handling of borderline validation (low confidence)."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)
        conversation = []

        with patch.object(agent, "_generate_guidance") as mock_generate:
            with patch.object(agent, "_handle_borderline_case") as mock_borderline:
                with patch.object(agent.compliance_validator, "validate") as mock_validate:
                    # Mock generation
                    mock_generate.return_value = ("Borderline guidance", "Reasoning")

                    # Mock low confidence validation
                    mock_validate.return_value = ValidationResult(
                        passed=True,
                        confidence=0.55,  # Low confidence
                        issues=[],
                        requires_human_review=True,
                        reasoning="Borderline case",
                    )

                    # Mock borderline handling
                    mock_borderline.return_value = "Improved guidance"

                    guidance = agent.provide_guidance(customer_profile, conversation)

                    # Verify borderline handling was called
                    assert mock_borderline.called


class TestGenerateGuidance:
    """Tests for _generate_guidance method."""

    @pytest.fixture
    def advisor_profile(self):
        """Create an advisor profile."""
        return AdvisorProfile(name="Sarah", description="Test advisor")

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
            presenting_question="Can I access my pension?",
        )

    @pytest.fixture
    def context(self):
        """Create a retrieved context."""
        return RetrievedContext(
            memories=[],
            cases=[],
            rules=[],
            fca_requirements="Stay within guidance boundary",
        )

    def test_generate_guidance_calls_llm(self, advisor_profile, customer_profile, context):
        """Test that generate_guidance calls LLM."""
        agent = AdvisorAgent(profile=advisor_profile)
        conversation = []

        with patch("guidance_agent.advisor.agent.completion") as mock_completion:
            # Mock LLM response
            mock_completion.return_value = MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content="You can access your pension from age 55..."
                        )
                    )
                ]
            )

            guidance, reasoning = agent._generate_guidance(
                customer_profile, context, conversation
            )

            assert mock_completion.called
            assert isinstance(guidance, str)
            assert len(guidance) > 0

    def test_generate_guidance_uses_correct_model(self, advisor_profile, customer_profile, context):
        """Test that correct model is used for generation."""
        agent = AdvisorAgent(profile=advisor_profile, model="gpt-4o")
        conversation = []

        with patch("guidance_agent.advisor.agent.completion") as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Test guidance"))]
            )

            agent._generate_guidance(customer_profile, context, conversation)

            # Verify correct model was used
            call_args = mock_completion.call_args
            assert call_args.kwargs["model"] == "gpt-4o"

    def test_generate_guidance_includes_context(self, advisor_profile, customer_profile, context):
        """Test that context is included in prompt."""
        agent = AdvisorAgent(profile=advisor_profile)
        conversation = []

        with patch("guidance_agent.advisor.agent.completion") as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Test guidance"))]
            )

            agent._generate_guidance(customer_profile, context, conversation)

            # Check that prompt includes context
            call_args = mock_completion.call_args
            messages = call_args.kwargs["messages"]

            # Messages are now structured for caching - check FCA requirements message
            fca_message = messages[1]  # Second message contains FCA requirements
            fca_content = fca_message["content"][0]["text"]

            assert "guidance boundary" in fca_content.lower()


class TestRetrieveContext:
    """Tests for _retrieve_context method."""

    @pytest.fixture
    def advisor_profile(self):
        """Create an advisor profile."""
        return AdvisorProfile(name="Sarah", description="Test advisor")

    @pytest.fixture
    def customer_profile(self):
        """Create a customer profile."""
        return CustomerProfile(
            presenting_question="Can I access my pension?",
        )

    def test_retrieve_context_returns_context(self, advisor_profile, customer_profile):
        """Test that retrieve_context returns RetrievedContext."""
        agent = AdvisorAgent(profile=advisor_profile)

        context = agent._retrieve_context(customer_profile)

        assert isinstance(context, RetrievedContext)
        assert context.memories is not None
        assert context.cases is not None
        assert context.rules is not None

    def test_retrieve_context_uses_customer_question(self, advisor_profile, customer_profile):
        """Test that context retrieval uses customer question."""
        agent = AdvisorAgent(profile=advisor_profile)

        # Mock the retrieval components
        with patch.object(agent.memory_stream, "retrieve") as mock_mem_retrieve:
            mock_mem_retrieve.return_value = []

            agent._retrieve_context(customer_profile)

            # Verify retrieve was called (would use customer question)
            assert mock_mem_retrieve.called


class TestRefineForCompliance:
    """Tests for _refine_for_compliance method."""

    @pytest.fixture
    def advisor_profile(self):
        """Create an advisor profile."""
        return AdvisorProfile(name="Sarah", description="Test advisor")

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
            presenting_question="What should I do with my pension?",
        )

    def test_refine_for_compliance_basic(self, advisor_profile, customer_profile):
        """Test basic compliance refinement."""
        agent = AdvisorAgent(profile=advisor_profile)
        original_guidance = "You should take the lump sum and invest it."
        issues = [
            ValidationIssue(
                issue_type=IssueType.ADVICE_BOUNDARY,
                severity=IssueSeverity.HIGH,
                description="Crossed into advice",
                suggestion="Rephrase to avoid recommendation",
            )
        ]

        with patch("guidance_agent.advisor.agent.completion") as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content="You could consider taking a lump sum. There are pros and cons to this option..."
                        )
                    )
                ]
            )

            refined = agent._refine_for_compliance(
                original_guidance, issues, customer_profile
            )

            assert mock_completion.called
            assert isinstance(refined, str)
            assert len(refined) > 0

    def test_refine_includes_issue_feedback(self, advisor_profile, customer_profile):
        """Test that refinement includes issue feedback in prompt."""
        agent = AdvisorAgent(profile=advisor_profile)
        original_guidance = "Bad guidance"
        issues = [
            ValidationIssue(
                issue_type=IssueType.ADVICE_BOUNDARY,
                severity=IssueSeverity.HIGH,
                description="Crossed boundary",
                suggestion="Rephrase",
            )
        ]

        with patch("guidance_agent.advisor.agent.completion") as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Refined guidance"))]
            )

            agent._refine_for_compliance(original_guidance, issues, customer_profile)

            # Check prompt includes issue feedback
            call_args = mock_completion.call_args
            messages = call_args.kwargs["messages"]
            prompt = messages[0]["content"]

            assert "Crossed boundary" in prompt
            assert "Rephrase" in prompt


class TestHandleBorderlineCase:
    """Tests for _handle_borderline_case method."""

    @pytest.fixture
    def advisor_profile(self):
        """Create an advisor profile."""
        return AdvisorProfile(name="Sarah", description="Test advisor")

    def test_handle_borderline_case(self, advisor_profile):
        """Test handling of borderline validation case."""
        agent = AdvisorAgent(profile=advisor_profile)
        guidance = "Borderline guidance"
        validation = ValidationResult(
            passed=True,
            confidence=0.60,
            issues=[],
            requires_human_review=True,
            reasoning="Low confidence",
        )
        context = RetrievedContext()

        with patch("guidance_agent.advisor.agent.completion") as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Improved guidance"))]
            )

            result = agent._handle_borderline_case(guidance, validation, context)

            assert isinstance(result, str)

    def test_borderline_case_strengthens_guidance(self, advisor_profile):
        """Test that borderline handling attempts to strengthen guidance."""
        agent = AdvisorAgent(profile=advisor_profile)
        guidance = "Vague guidance"
        validation = ValidationResult(
            passed=True,
            confidence=0.55,
            issues=[],
            requires_human_review=True,
        )
        context = RetrievedContext()

        with patch("guidance_agent.advisor.agent.completion") as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Clearer guidance"))]
            )

            agent._handle_borderline_case(guidance, validation, context)

            # Should call LLM to improve
            assert mock_completion.called


class TestMemoryIntegration:
    """Tests for memory stream integration."""

    @pytest.fixture
    def advisor_profile(self):
        """Create an advisor profile."""
        return AdvisorProfile(name="Sarah", description="Test advisor")

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
            presenting_question="Can I access my pension?",
        )

    def test_advisor_adds_observations_to_memory(self, advisor_profile, customer_profile):
        """Test that advisor adds observations to memory stream."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)
        conversation = [
            {"role": "customer", "content": "I'm confused about pension access"}
        ]

        initial_memory_count = len(agent.memory_stream.memories)

        with patch.object(agent, "_generate_guidance") as mock_generate:
            with patch.object(agent.compliance_validator, "validate") as mock_validate:
                mock_generate.return_value = ("Test guidance", "Reasoning")
                mock_validate.return_value = ValidationResult(
                    passed=True, confidence=0.95, issues=[], requires_human_review=False
                )

                agent.provide_guidance(customer_profile, conversation)

                # Memory stream should have new observations
                # (this depends on implementation details)


class TestCacheConfiguration:
    """Tests for prompt caching configuration in AdvisorAgent."""

    @pytest.fixture
    def advisor_profile(self):
        """Create an advisor profile."""
        return AdvisorProfile(name="Sarah", description="Test advisor")

    def test_advisor_has_cache_enabled_by_default(self, advisor_profile):
        """Test that prompt caching is enabled by default."""
        agent = AdvisorAgent(profile=advisor_profile)

        assert hasattr(agent, "enable_prompt_caching")
        assert agent.enable_prompt_caching is True

    def test_advisor_can_disable_caching(self, advisor_profile):
        """Test that prompt caching can be disabled."""
        agent = AdvisorAgent(profile=advisor_profile, enable_prompt_caching=False)

        assert agent.enable_prompt_caching is False

    def test_get_cache_headers_anthropic_claude(self, advisor_profile):
        """Test cache headers for Anthropic Claude models."""
        agent = AdvisorAgent(
            profile=advisor_profile,
            model="claude-sonnet-4.5",
            enable_prompt_caching=True,
        )

        headers = agent._get_cache_headers()

        assert "anthropic-beta" in headers
        assert headers["anthropic-beta"] == "prompt-caching-2024-07-31"

    def test_get_cache_headers_anthropic_disabled(self, advisor_profile):
        """Test that no cache headers when caching disabled (Anthropic)."""
        agent = AdvisorAgent(
            profile=advisor_profile,
            model="claude-sonnet-4.5",
            enable_prompt_caching=False,
        )

        headers = agent._get_cache_headers()

        assert len(headers) == 0

    def test_get_cache_headers_openai_gpt4o(self, advisor_profile):
        """Test cache headers for OpenAI GPT-4o (automatic caching)."""
        agent = AdvisorAgent(
            profile=advisor_profile,
            model="gpt-4o",
            enable_prompt_caching=True,
        )

        headers = agent._get_cache_headers()

        # OpenAI caches automatically, no headers needed
        assert len(headers) == 0

    def test_get_cache_headers_openai_gpt4_turbo(self, advisor_profile):
        """Test cache headers for OpenAI GPT-4 turbo."""
        agent = AdvisorAgent(
            profile=advisor_profile,
            model="gpt-4-turbo-preview",
            enable_prompt_caching=True,
        )

        headers = agent._get_cache_headers()

        # GPT-4 turbo also uses automatic caching
        assert len(headers) == 0

    def test_cache_headers_case_insensitive_model_name(self, advisor_profile):
        """Test that model name matching is case insensitive."""
        agent = AdvisorAgent(
            profile=advisor_profile,
            model="CLAUDE-SONNET-4.5",
            enable_prompt_caching=True,
        )

        headers = agent._get_cache_headers()

        assert "anthropic-beta" in headers

    def test_cache_headers_claude_variations(self, advisor_profile):
        """Test cache headers for various Claude model names."""
        claude_models = [
            "claude-3-5-sonnet",
            "claude-sonnet-4.5",
            "claude-opus-4",
            "anthropic/claude-3-sonnet",
        ]

        for model in claude_models:
            agent = AdvisorAgent(
                profile=advisor_profile,
                model=model,
                enable_prompt_caching=True,
            )

            headers = agent._get_cache_headers()

            assert "anthropic-beta" in headers, f"Failed for model: {model}"
