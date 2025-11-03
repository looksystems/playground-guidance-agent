"""Unit tests for EventOrchestrator."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from guidance_agent.environment.orchestrator import EventOrchestrator, ConsultationResult
from guidance_agent.advisor.agent import AdvisorAgent
from guidance_agent.customer.agent import CustomerAgent
from guidance_agent.compliance.validator import ValidationResult
from guidance_agent.core.types import (
    AdvisorProfile,
    CustomerProfile,
    CustomerDemographics,
    FinancialSituation,
    PensionPot,
    OutcomeStatus,
    OutcomeResult,
)


class TestEventOrchestrator:
    """Test consultation orchestration."""

    @pytest.fixture
    def advisor_profile(self):
        """Create an advisor profile."""
        return AdvisorProfile(
            name="Sarah",
            description="Experienced pension guidance specialist",
        )

    @pytest.fixture
    def simple_customer_profile(self):
        """Create a simple customer profile."""
        return CustomerProfile(
            demographics=CustomerDemographics(
                age=30,
                gender="F",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            financial=FinancialSituation(
                annual_income=35000,
                total_assets=45000,
                total_debt=5000,
                dependents=0,
                risk_tolerance="medium",
            ),
            pensions=[
                PensionPot(
                    pot_id="pot1",
                    provider="NEST",
                    pot_type="defined_contribution",
                    current_value=15000,
                    projected_value=25000,
                    age_accessible=55,
                )
            ],
            goals="Understand my pension",
            presenting_question="How much should I be saving for retirement?",
        )

    @pytest.fixture
    def mock_llm_calls(self):
        """Create a context manager for mocking all LLM calls."""
        def _create_mocks():
            with patch("guidance_agent.advisor.agent.completion") as mock_advisor, \
                 patch("guidance_agent.customer.agent.completion") as mock_customer, \
                 patch("guidance_agent.customer.simulator.completion") as mock_outcome:
                return mock_advisor, mock_customer, mock_outcome
        return _create_mocks

    def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly."""
        orchestrator = EventOrchestrator()

        assert orchestrator is not None
        assert orchestrator.max_turns == 20  # Default max turns

    def test_orchestrator_custom_max_turns(self):
        """Test orchestrator with custom max turns."""
        orchestrator = EventOrchestrator(max_turns=10)

        assert orchestrator.max_turns == 10

    def test_run_consultation_basic(self, advisor_profile, simple_customer_profile):
        """Test running a basic consultation."""
        with patch("guidance_agent.advisor.agent.completion") as mock_advisor, \
             patch("guidance_agent.customer.agent.completion") as mock_customer, \
             patch("guidance_agent.customer.simulator.completion") as mock_outcome:

            orchestrator = EventOrchestrator()
            advisor = AdvisorAgent(profile=advisor_profile)
            customer = CustomerAgent(profile=simple_customer_profile)

            # Mock advisor response
            mock_advisor.return_value = Mock(
                choices=[Mock(message=Mock(content="Good question. Let me help."))]
            )

            # Mock customer responses
            mock_customer.side_effect = [
                Mock(choices=[Mock(message=Mock(content='{"understanding_level": "fully_understood", "confusion_points": [], "customer_feeling": "confident"}'))]),
                Mock(choices=[Mock(message=Mock(content="Thank you!"))]),
            ]

            # Mock outcome
            mock_outcome.return_value = Mock(
                choices=[Mock(message=Mock(content='{"customer_satisfaction": 8.5, "comprehension": 9.0, "goal_alignment": 8.0, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": true, "signposted_when_needed": false, "has_db_pension": false, "db_warning_given": false, "reasoning": "Good guidance"}'))]
            )

            # Mock validator
            with patch.object(advisor.compliance_validator, "validate") as mock_validate:
                mock_validate.return_value = ValidationResult(
                    passed=True, confidence=0.95, requires_human_review=False, issues=[], reasoning="OK"
                )

                result = orchestrator.run_consultation(advisor, customer)

                assert isinstance(result, ConsultationResult)
                assert result.conversation_history is not None
                assert len(result.conversation_history) > 0
                assert result.turn_count > 0

    def test_consultation_turn_count(self, advisor_profile, simple_customer_profile):
        """Test that consultation counts turns correctly."""
        with patch("guidance_agent.advisor.agent.completion") as mock_advisor, \
             patch("guidance_agent.customer.agent.completion") as mock_customer, \
             patch("guidance_agent.customer.simulator.completion") as mock_outcome:

            orchestrator = EventOrchestrator(max_turns=5)
            # Disable chain-of-thought to simplify mocking
            advisor = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)
            customer = CustomerAgent(profile=simple_customer_profile)

            # Mock 3 advisor turns
            mock_advisor.side_effect = [
                Mock(choices=[Mock(message=Mock(content="Response 1"))]),
                Mock(choices=[Mock(message=Mock(content="Response 2"))]),
                Mock(choices=[Mock(message=Mock(content="Response 3"))]),
            ]

            # Mock customer responses for 3 turns
            mock_customer.side_effect = [
                Mock(choices=[Mock(message=Mock(content='{"understanding_level": "partially_understood", "confusion_points": ["targets"], "customer_feeling": "uncertain"}'))]),
                Mock(choices=[Mock(message=Mock(content="Could you explain more?"))]),
                Mock(choices=[Mock(message=Mock(content='{"understanding_level": "partially_understood", "confusion_points": [], "customer_feeling": "uncertain"}'))]),
                Mock(choices=[Mock(message=Mock(content="I see"))]),
                Mock(choices=[Mock(message=Mock(content='{"understanding_level": "fully_understood", "confusion_points": [], "customer_feeling": "confident"}'))]),
                Mock(choices=[Mock(message=Mock(content="Thank you!"))]),
            ]

            mock_outcome.return_value = Mock(
                choices=[Mock(message=Mock(content='{"customer_satisfaction": 8.0, "comprehension": 8.0, "goal_alignment": 8.0, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": true, "signposted_when_needed": false, "has_db_pension": false, "db_warning_given": false, "reasoning": "OK"}'))]
            )

            with patch.object(advisor.compliance_validator, "validate") as mock_validate:
                mock_validate.return_value = ValidationResult(passed=True, confidence=0.95, requires_human_review=False, issues=[], reasoning="OK")

                result = orchestrator.run_consultation(advisor, customer)
                assert result.turn_count == 3

    def test_consultation_respects_max_turns(self, advisor_profile, simple_customer_profile):
        """Test that consultation stops at max turns."""
        with patch("guidance_agent.advisor.agent.completion") as mock_advisor, \
             patch("guidance_agent.customer.agent.completion") as mock_customer, \
             patch("guidance_agent.customer.simulator.completion") as mock_outcome:

            orchestrator = EventOrchestrator(max_turns=3)
            advisor = AdvisorAgent(profile=advisor_profile)
            customer = CustomerAgent(profile=simple_customer_profile)

            # Mock responses that keep going
            mock_advisor.return_value = Mock(choices=[Mock(message=Mock(content="Continuing..."))])
            mock_customer.side_effect = [
                Mock(choices=[Mock(message=Mock(content='{"understanding_level": "partially_understood", "confusion_points": [], "customer_feeling": "uncertain"}'))]),
                Mock(choices=[Mock(message=Mock(content="Tell me more"))]),
            ] * 20

            mock_outcome.return_value = Mock(
                choices=[Mock(message=Mock(content='{"customer_satisfaction": 7.0, "comprehension": 7.0, "goal_alignment": 7.0, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": false, "signposted_when_needed": false, "has_db_pension": false, "db_warning_given": false, "reasoning": "Hit max turns"}'))]
            )

            with patch.object(advisor.compliance_validator, "validate") as mock_validate:
                mock_validate.return_value = ValidationResult(passed=True, confidence=0.95, requires_human_review=False, issues=[], reasoning="OK")

                result = orchestrator.run_consultation(advisor, customer)
                assert result.turn_count <= 3

    def test_detect_completion_thank_you(self, advisor_profile, simple_customer_profile):
        """Test detection of consultation completion via thank you."""
        with patch("guidance_agent.advisor.agent.completion") as mock_advisor, \
             patch("guidance_agent.customer.agent.completion") as mock_customer, \
             patch("guidance_agent.customer.simulator.completion") as mock_outcome:

            orchestrator = EventOrchestrator()
            advisor = AdvisorAgent(profile=advisor_profile)
            customer = CustomerAgent(profile=simple_customer_profile)

            mock_advisor.return_value = Mock(choices=[Mock(message=Mock(content="Glad to help!"))])
            mock_customer.side_effect = [
                Mock(choices=[Mock(message=Mock(content='{"understanding_level": "fully_understood", "confusion_points": [], "customer_feeling": "satisfied"}'))]),
                Mock(choices=[Mock(message=Mock(content="Thank you so much!"))]),
            ]
            mock_outcome.return_value = Mock(
                choices=[Mock(message=Mock(content='{"customer_satisfaction": 9.0, "comprehension": 9.0, "goal_alignment": 9.0, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": true, "signposted_when_needed": false, "has_db_pension": false, "db_warning_given": false, "reasoning": "Natural completion"}'))]
            )

            with patch.object(advisor.compliance_validator, "validate") as mock_validate:
                mock_validate.return_value = ValidationResult(passed=True, confidence=0.95, requires_human_review=False, issues=[], reasoning="OK")

                result = orchestrator.run_consultation(advisor, customer)
                assert result.turn_count < 20
                assert result.completed_naturally is True

    def test_detect_completion_satisfied(self, advisor_profile, simple_customer_profile):
        """Test detection of consultation completion via satisfaction."""
        with patch("guidance_agent.advisor.agent.completion") as mock_advisor, \
             patch("guidance_agent.customer.agent.completion") as mock_customer, \
             patch("guidance_agent.customer.simulator.completion") as mock_outcome:

            orchestrator = EventOrchestrator()
            advisor = AdvisorAgent(profile=advisor_profile)
            customer = CustomerAgent(profile=simple_customer_profile)

            mock_advisor.return_value = Mock(choices=[Mock(message=Mock(content="Anything else?"))])
            mock_customer.side_effect = [
                Mock(choices=[Mock(message=Mock(content='{"understanding_level": "fully_understood", "confusion_points": [], "customer_feeling": "satisfied"}'))]),
                Mock(choices=[Mock(message=Mock(content="No, I understand now."))]),
            ]
            mock_outcome.return_value = Mock(
                choices=[Mock(message=Mock(content='{"customer_satisfaction": 9.0, "comprehension": 9.0, "goal_alignment": 9.0, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": true, "signposted_when_needed": false, "has_db_pension": false, "db_warning_given": false, "reasoning": "Satisfied"}'))]
            )

            with patch.object(advisor.compliance_validator, "validate") as mock_validate:
                mock_validate.return_value = ValidationResult(passed=True, confidence=0.95, requires_human_review=False, issues=[], reasoning="OK")

                result = orchestrator.run_consultation(advisor, customer)
                assert result.completed_naturally is True

    def test_conversation_history_structure(self, advisor_profile, simple_customer_profile):
        """Test conversation history has correct structure."""
        with patch("guidance_agent.advisor.agent.completion") as mock_advisor, \
             patch("guidance_agent.customer.agent.completion") as mock_customer, \
             patch("guidance_agent.customer.simulator.completion") as mock_outcome:

            orchestrator = EventOrchestrator()
            advisor = AdvisorAgent(profile=advisor_profile)
            customer = CustomerAgent(profile=simple_customer_profile)

            mock_advisor.return_value = Mock(choices=[Mock(message=Mock(content="Response"))])
            mock_customer.side_effect = [
                Mock(choices=[Mock(message=Mock(content='{"understanding_level": "fully_understood", "confusion_points": [], "customer_feeling": "satisfied"}'))]),
                Mock(choices=[Mock(message=Mock(content="Thanks!"))]),
            ]
            mock_outcome.return_value = Mock(
                choices=[Mock(message=Mock(content='{"customer_satisfaction": 8.0, "comprehension": 8.0, "goal_alignment": 8.0, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": true, "signposted_when_needed": false, "has_db_pension": false, "db_warning_given": false, "reasoning": "OK"}'))]
            )

            with patch.object(advisor.compliance_validator, "validate") as mock_validate:
                mock_validate.return_value = ValidationResult(passed=True, confidence=0.95, requires_human_review=False, issues=[], reasoning="OK")

                result = orchestrator.run_consultation(advisor, customer)

                assert len(result.conversation_history) > 0
                for message in result.conversation_history:
                    assert "role" in message
                    assert "content" in message
                    assert message["role"] in ["customer", "advisor"]

    def test_consultation_with_outcome(self, advisor_profile, simple_customer_profile):
        """Test consultation includes outcome simulation."""
        with patch("guidance_agent.advisor.agent.completion") as mock_advisor, \
             patch("guidance_agent.customer.agent.completion") as mock_customer, \
             patch("guidance_agent.customer.simulator.completion") as mock_outcome:

            orchestrator = EventOrchestrator()
            advisor = AdvisorAgent(profile=advisor_profile)
            customer = CustomerAgent(profile=simple_customer_profile)

            mock_advisor.return_value = Mock(choices=[Mock(message=Mock(content="Response"))])
            mock_customer.side_effect = [
                Mock(choices=[Mock(message=Mock(content='{"understanding_level": "fully_understood", "confusion_points": [], "customer_feeling": "satisfied"}'))]),
                Mock(choices=[Mock(message=Mock(content="Thank you!"))]),
            ]
            mock_outcome.return_value = Mock(
                choices=[Mock(message=Mock(content='{"customer_satisfaction": 9.0, "comprehension": 9.0, "goal_alignment": 9.0, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": true, "signposted_when_needed": false, "has_db_pension": false, "db_warning_given": false, "reasoning": "Excellent"}'))]
            )

            with patch.object(advisor.compliance_validator, "validate") as mock_validate:
                mock_validate.return_value = ValidationResult(passed=True, confidence=0.95, requires_human_review=False, issues=[], reasoning="OK")

                result = orchestrator.run_consultation(advisor, customer)
                assert result.outcome is not None
                assert result.outcome.successful is True

    def test_detect_completion_signals(self):
        """Test completion signal detection."""
        orchestrator = EventOrchestrator()

        # Thank you signals
        assert orchestrator._is_completion_signal("Thank you so much!") is True
        assert orchestrator._is_completion_signal("Thanks, that's all I needed") is True
        assert orchestrator._is_completion_signal("I appreciate your help") is True

        # Negative/closure signals
        assert orchestrator._is_completion_signal("No, that's all") is True
        assert orchestrator._is_completion_signal("Nothing else, thanks") is True

        # Satisfaction signals
        assert orchestrator._is_completion_signal("I understand now") is True
        assert orchestrator._is_completion_signal("That makes sense") is True

        # Non-completion signals
        assert orchestrator._is_completion_signal("Could you explain more?") is False
        assert orchestrator._is_completion_signal("What about DB pensions?") is False
