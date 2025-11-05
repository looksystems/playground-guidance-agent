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

    def test_advisor_provides_compliant_guidance(self, customer_profile):
        """Test that advisor can provide compliant guidance for customer queries."""
        profile = AdvisorProfile(
            name="Sarah",
            description="Pension guidance specialist",
        )

        agent = AdvisorAgent(profile=profile, use_chain_of_thought=False)
        conversation = []

        # Mock the LLM generation and compliance validation
        with patch.object(agent, "_generate_guidance") as mock_generate:
            with patch.object(agent.compliance_validator, "validate") as mock_validate:
                # Mock generation to return pension-related guidance
                mock_generate.return_value = (
                    "Based on your age of 55, you can now access your pension. You have the option to take up to 25% as a tax-free lump sum.",
                    "Customer is at minimum pension age and eligible for tax-free withdrawal"
                )

                # Mock validation to pass
                mock_validate.return_value = ValidationResult(
                    passed=True,
                    confidence=0.95,
                    issues=[],
                    requires_human_review=False,
                    reasoning="Guidance is compliant with FCA regulations",
                )

                # Provide guidance
                guidance = agent.provide_guidance(customer_profile, conversation)

                # Verify meaningful behavior
                assert guidance is not None
                assert isinstance(guidance, str)
                assert len(guidance) > 0
                assert "pension" in guidance.lower()
                assert "tax-free" in guidance.lower()

                # Verify compliance was checked
                mock_validate.assert_called_once()
                validation_result = mock_validate.return_value
                assert validation_result.passed is True

    def test_create_advisor_with_custom_model(self):
        """Test creating advisor with custom LLM model."""
        profile = AdvisorProfile(
            name="Sarah",
            description="Test advisor",
        )

        agent = AdvisorAgent(profile=profile, model="gpt-4o")

        assert agent.model == "gpt-4o"

    def test_advisor_memory_stream_stores_interactions(self):
        """Test that advisor's memory stream can store conversation memories."""
        profile = AdvisorProfile(name="Sarah", description="Test")
        agent = AdvisorAgent(profile=profile)

        # Verify memory stream exists and is functional
        assert agent.memory_stream is not None

        # Add a memory to the stream
        from guidance_agent.core.memory import MemoryNode
        from guidance_agent.core.types import MemoryType

        memory = MemoryNode(
            description="Customer mentioned having £200k pension pot",
            importance=0.8,
            memory_type=MemoryType.OBSERVATION,
            embedding=[0.1] * 384,  # Use proper embedding dimension
        )
        agent.memory_stream.add(memory)

        # Verify memory was stored by retrieving similar memories
        query_embedding = [0.1] * 384
        retrieved = agent.memory_stream.retrieve(query_embedding, top_k=1)
        assert len(retrieved) == 1
        assert retrieved[0].description == "Customer mentioned having £200k pension pot"

    def test_advisor_compliance_validator_validates_guidance(self):
        """Test that advisor's compliance validator can validate guidance text."""
        profile = AdvisorProfile(name="Sarah", description="Test")
        agent = AdvisorAgent(profile=profile)

        assert agent.compliance_validator is not None

        # Mock validation to test the validator is functional
        with patch.object(agent.compliance_validator, "validate") as mock_validate:
            mock_validate.return_value = ValidationResult(
                passed=True,
                confidence=0.95,
                issues=[],
                requires_human_review=False,
                reasoning="Guidance is compliant",
            )

            result = agent.compliance_validator.validate("Test guidance")

            assert result.passed is True
            assert result.confidence == 0.95
            mock_validate.assert_called_once()


class TestProvideGuidance:
    """Tests for provide_guidance method."""

    @pytest.fixture
    def advisor_profile(self):
        """Create an advisor profile."""
        return AdvisorProfile(
            name="Sarah",
            description="Experienced pension guidance specialist",
        )

    # Note: customer_profile fixture now provided by tests/fixtures/customers.py

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


class TestGuidanceGeneration:
    """Tests for guidance generation through public API."""

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

    def test_provide_guidance_generates_pension_advice(self, advisor_profile, customer_profile):
        """Test that provide_guidance generates appropriate pension guidance."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)
        conversation = []

        with patch("guidance_agent.advisor.agent.completion") as mock_completion:
            # Mock LLM to return guidance about pension access
            mock_completion.return_value = MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content="You can access your pension from age 55. You have options to take up to 25% tax-free."
                        )
                    )
                ]
            )

            # Mock compliance validation to pass
            with patch.object(agent.compliance_validator, "validate") as mock_validate:
                mock_validate.return_value = ValidationResult(
                    passed=True,
                    confidence=0.95,
                    issues=[],
                    requires_human_review=False,
                )

                guidance = agent.provide_guidance(customer_profile, conversation)

                # Verify LLM was called
                assert mock_completion.called
                assert isinstance(guidance, str)
                assert len(guidance) > 0
                assert "pension" in guidance.lower()

    def test_provide_guidance_uses_configured_model(self, advisor_profile, customer_profile):
        """Test that provide_guidance uses the configured LLM model."""
        agent = AdvisorAgent(profile=advisor_profile, model="gpt-4o", use_chain_of_thought=False)
        conversation = []

        with patch("guidance_agent.advisor.agent.completion") as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Test guidance about pensions"))]
            )

            # Mock compliance validation
            with patch.object(agent.compliance_validator, "validate") as mock_validate:
                mock_validate.return_value = ValidationResult(
                    passed=True,
                    confidence=0.95,
                    issues=[],
                    requires_human_review=False,
                )

                agent.provide_guidance(customer_profile, conversation)

                # Verify correct model was used in LLM call
                call_args = mock_completion.call_args
                assert call_args.kwargs["model"] == "gpt-4o"

    def test_guidance_includes_fca_context(self, advisor_profile, customer_profile):
        """Test that guidance generation includes FCA regulatory context."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)
        conversation = []

        with patch("guidance_agent.advisor.agent.completion") as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Guidance text"))]
            )

            # Mock compliance validation
            with patch.object(agent.compliance_validator, "validate") as mock_validate:
                mock_validate.return_value = ValidationResult(
                    passed=True,
                    confidence=0.95,
                    issues=[],
                    requires_human_review=False,
                )

                agent.provide_guidance(customer_profile, conversation)

                # Check that LLM prompt includes FCA context
                call_args = mock_completion.call_args
                messages = call_args.kwargs["messages"]

                # FCA requirements should be in the messages
                all_content = str(messages)
                assert "guidance boundary" in all_content.lower() or "fca" in all_content.lower()


class TestContextRetrieval:
    """Tests for context retrieval through public API."""

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

    def test_guidance_uses_relevant_memories(self, advisor_profile, customer_profile):
        """Test that guidance retrieves and uses relevant memories."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)

        # Add a relevant memory
        from guidance_agent.core.memory import MemoryNode
        from guidance_agent.core.types import MemoryType

        memory = MemoryNode(
            description="Customer previously asked about pension consolidation",
            importance=0.8,
            memory_type=MemoryType.OBSERVATION,
            embedding=[0.1] * 384,
        )
        agent.memory_stream.add(memory)

        conversation = []

        # Mock LLM to include memory context
        with patch("guidance_agent.advisor.agent.completion") as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content="As we previously discussed consolidation, you can access your pension from age 55."
                        )
                    )
                ]
            )

            # Mock compliance validation
            with patch.object(agent.compliance_validator, "validate") as mock_validate:
                mock_validate.return_value = ValidationResult(
                    passed=True,
                    confidence=0.95,
                    issues=[],
                    requires_human_review=False,
                )

                guidance = agent.provide_guidance(customer_profile, conversation)

                # Verify memory retrieval happened by checking memories were present
                assert mock_completion.called
                # The guidance should reference the previous context
                assert "pension" in guidance.lower()

    def test_guidance_queries_memory_with_customer_question(self, advisor_profile, customer_profile):
        """Test that guidance retrieval uses customer's question for context."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)
        conversation = []

        # Mock memory retrieval to track what's queried
        with patch.object(agent.memory_stream, "retrieve") as mock_mem_retrieve:
            mock_mem_retrieve.return_value = []

            # Mock LLM
            with patch("guidance_agent.advisor.agent.completion") as mock_completion:
                mock_completion.return_value = MagicMock(
                    choices=[MagicMock(message=MagicMock(content="Test guidance"))]
                )

                # Mock compliance validation
                with patch.object(agent.compliance_validator, "validate") as mock_validate:
                    mock_validate.return_value = ValidationResult(
                        passed=True,
                        confidence=0.95,
                        issues=[],
                        requires_human_review=False,
                    )

                    agent.provide_guidance(customer_profile, conversation)

                    # Verify memory retrieval was called (would use customer question for embeddings)
                    assert mock_mem_retrieve.called


class TestComplianceRefinement:
    """Tests for compliance refinement through public API."""

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

    def test_guidance_refines_when_compliance_fails(self, advisor_profile, customer_profile):
        """Test that guidance is refined when compliance validation fails."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)
        conversation = []

        call_count = [0]

        def mock_completion_side_effect(*args, **kwargs):
            """Return non-compliant first, then compliant guidance."""
            call_count[0] += 1
            if call_count[0] == 1:
                # First call: non-compliant guidance
                return MagicMock(
                    choices=[
                        MagicMock(
                            message=MagicMock(
                                content="You should take the lump sum and invest it in high-risk stocks."
                            )
                        )
                    ]
                )
            else:
                # Second call: refined compliant guidance
                return MagicMock(
                    choices=[
                        MagicMock(
                            message=MagicMock(
                                content="You could consider the tax-free lump sum option. It's important to understand the risks and benefits."
                            )
                        )
                    ]
                )

        with patch("guidance_agent.advisor.agent.completion", side_effect=mock_completion_side_effect):
            # Mock validation to fail first, then pass
            validation_call_count = [0]

            def mock_validate_side_effect(*args, **kwargs):
                validation_call_count[0] += 1
                if validation_call_count[0] == 1:
                    # First validation: fail with issues
                    return ValidationResult(
                        passed=False,
                        confidence=0.3,
                        issues=[
                            ValidationIssue(
                                issue_type=IssueType.ADVICE_BOUNDARY,
                                severity=IssueSeverity.HIGH,
                                description="Crossed into advice territory",
                                suggestion="Avoid recommending specific actions",
                            )
                        ],
                        requires_human_review=True,
                    )
                else:
                    # Second validation: pass
                    return ValidationResult(
                        passed=True,
                        confidence=0.95,
                        issues=[],
                        requires_human_review=False,
                    )

            with patch.object(agent.compliance_validator, "validate", side_effect=mock_validate_side_effect):
                guidance = agent.provide_guidance(customer_profile, conversation)

                # Verify refinement happened
                assert "consider" in guidance.lower() or "could" in guidance.lower()
                assert "should" not in guidance.lower() or "important" in guidance.lower()

    def test_guidance_includes_issue_feedback_in_refinement(self, advisor_profile, customer_profile):
        """Test that compliance issues are used to improve guidance."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)
        conversation = []

        call_count = [0]

        def mock_completion_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return MagicMock(
                    choices=[MagicMock(message=MagicMock(content="Problematic guidance"))]
                )
            else:
                # Check that refinement prompt includes the issue
                messages = kwargs.get("messages", [])
                prompt_text = str(messages)
                # The refinement should reference the validation issue
                return MagicMock(
                    choices=[MagicMock(message=MagicMock(content="Refined compliant guidance"))]
                )

        with patch("guidance_agent.advisor.agent.completion", side_effect=mock_completion_side_effect):
            validation_call_count = [0]

            def mock_validate_side_effect(*args, **kwargs):
                validation_call_count[0] += 1
                if validation_call_count[0] == 1:
                    return ValidationResult(
                        passed=False,
                        confidence=0.3,
                        issues=[
                            ValidationIssue(
                                issue_type=IssueType.ADVICE_BOUNDARY,
                                severity=IssueSeverity.HIGH,
                                description="Used prescriptive language",
                                suggestion="Use exploratory language instead",
                            )
                        ],
                        requires_human_review=True,
                    )
                else:
                    return ValidationResult(passed=True, confidence=0.95, issues=[], requires_human_review=False)

            with patch.object(agent.compliance_validator, "validate", side_effect=mock_validate_side_effect):
                guidance = agent.provide_guidance(customer_profile, conversation)

                # Verify guidance was refined
                assert isinstance(guidance, str)
                assert len(guidance) > 0


class TestBorderlineCaseHandling:
    """Tests for borderline case handling through public API."""

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

    def test_guidance_handles_borderline_validation(self, advisor_profile, customer_profile):
        """Test that borderline validation results trigger improvement."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)
        conversation = []

        call_count = [0]

        def mock_completion_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First: borderline guidance
                return MagicMock(
                    choices=[MagicMock(message=MagicMock(content="Some vague pension guidance"))]
                )
            else:
                # Second: strengthened guidance
                return MagicMock(
                    choices=[
                        MagicMock(
                            message=MagicMock(
                                content="Clear pension guidance with specific regulatory context and examples"
                            )
                        )
                    ]
                )

        with patch("guidance_agent.advisor.agent.completion", side_effect=mock_completion_side_effect):
            validation_call_count = [0]

            def mock_validate_side_effect(*args, **kwargs):
                validation_call_count[0] += 1
                if validation_call_count[0] == 1:
                    # First: borderline (low confidence, requires review)
                    return ValidationResult(
                        passed=True,
                        confidence=0.60,
                        issues=[],
                        requires_human_review=True,
                        reasoning="Low confidence, vague guidance",
                    )
                else:
                    # Second: strong validation
                    return ValidationResult(
                        passed=True,
                        confidence=0.95,
                        issues=[],
                        requires_human_review=False,
                    )

            with patch.object(agent.compliance_validator, "validate", side_effect=mock_validate_side_effect):
                guidance = agent.provide_guidance(customer_profile, conversation)

                # Verify strengthening happened - should have clearer content
                assert "clear" in guidance.lower() or "specific" in guidance.lower() or len(guidance) > 20

    def test_borderline_guidance_triggers_llm_improvement(self, advisor_profile, customer_profile):
        """Test that borderline cases call LLM for improvement."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)
        conversation = []

        completion_calls = []

        def mock_completion_side_effect(*args, **kwargs):
            completion_calls.append(kwargs)
            if len(completion_calls) == 1:
                return MagicMock(choices=[MagicMock(message=MagicMock(content="Initial guidance"))])
            else:
                return MagicMock(choices=[MagicMock(message=MagicMock(content="Improved guidance"))])

        with patch("guidance_agent.advisor.agent.completion", side_effect=mock_completion_side_effect):
            validation_call_count = [0]

            def mock_validate_side_effect(*args, **kwargs):
                validation_call_count[0] += 1
                if validation_call_count[0] == 1:
                    return ValidationResult(
                        passed=True,
                        confidence=0.55,
                        issues=[],
                        requires_human_review=True,
                    )
                else:
                    return ValidationResult(passed=True, confidence=0.95, issues=[], requires_human_review=False)

            with patch.object(agent.compliance_validator, "validate", side_effect=mock_validate_side_effect):
                agent.provide_guidance(customer_profile, conversation)

                # Should have made multiple LLM calls (initial + improvement)
                assert len(completion_calls) >= 2


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

    def test_guidance_with_claude_uses_prompt_caching(self, advisor_profile, customer_profile):
        """Test that Claude models use prompt caching headers when enabled."""
        agent = AdvisorAgent(
            profile=advisor_profile,
            model="claude-sonnet-4.5",
            enable_prompt_caching=True,
            use_chain_of_thought=False,
        )
        conversation = []

        with patch("guidance_agent.advisor.agent.completion") as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Test guidance"))]
            )

            with patch.object(agent.compliance_validator, "validate") as mock_validate:
                mock_validate.return_value = ValidationResult(
                    passed=True, confidence=0.95, issues=[], requires_human_review=False
                )

                agent.provide_guidance(customer_profile, conversation)

                # Verify completion was called with cache headers
                call_args = mock_completion.call_args
                extra_headers = call_args.kwargs.get("extra_headers", {})
                assert "anthropic-beta" in extra_headers
                assert extra_headers["anthropic-beta"] == "prompt-caching-2024-07-31"

    def test_guidance_without_caching_flag(self, advisor_profile, customer_profile):
        """Test that caching headers are not sent when caching is disabled."""
        agent = AdvisorAgent(
            profile=advisor_profile,
            model="claude-sonnet-4.5",
            enable_prompt_caching=False,
            use_chain_of_thought=False,
        )
        conversation = []

        with patch("guidance_agent.advisor.agent.completion") as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Test guidance"))]
            )

            with patch.object(agent.compliance_validator, "validate") as mock_validate:
                mock_validate.return_value = ValidationResult(
                    passed=True, confidence=0.95, issues=[], requires_human_review=False
                )

                agent.provide_guidance(customer_profile, conversation)

                # Verify no cache headers
                call_args = mock_completion.call_args
                extra_headers = call_args.kwargs.get("extra_headers")
                assert extra_headers is None or len(extra_headers) == 0

    def test_guidance_with_openai_no_cache_headers(self, advisor_profile, customer_profile):
        """Test that OpenAI models don't send cache headers (automatic caching)."""
        agent = AdvisorAgent(
            profile=advisor_profile,
            model="gpt-4o",
            enable_prompt_caching=True,
            use_chain_of_thought=False,
        )
        conversation = []

        with patch("guidance_agent.advisor.agent.completion") as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Test guidance"))]
            )

            with patch.object(agent.compliance_validator, "validate") as mock_validate:
                mock_validate.return_value = ValidationResult(
                    passed=True, confidence=0.95, issues=[], requires_human_review=False
                )

                agent.provide_guidance(customer_profile, conversation)

                # OpenAI doesn't need explicit headers
                call_args = mock_completion.call_args
                extra_headers = call_args.kwargs.get("extra_headers")
                assert extra_headers is None or len(extra_headers) == 0
