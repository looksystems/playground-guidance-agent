"""Tests for outcome simulation."""

import pytest
from unittest.mock import Mock, patch

from guidance_agent.customer.simulator import simulate_outcome
from guidance_agent.customer.agent import CustomerAgent
from guidance_agent.core.types import (
    CustomerProfile,
    CustomerDemographics,
    FinancialSituation,
    PensionPot,
    OutcomeResult,
    OutcomeStatus,
)


class TestSimulateOutcome:
    """Tests for simulate_outcome function."""

    @pytest.fixture
    def customer_profile(self):
        """Create a customer profile for testing."""
        return CustomerProfile(
            demographics=CustomerDemographics(
                age=45,
                gender="M",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            financial=FinancialSituation(
                annual_income=50000,
                total_assets=150000,
                total_debt=10000,
                dependents=1,
                risk_tolerance="medium",
            ),
            pensions=[
                PensionPot(
                    pot_id="pot1",
                    provider="NEST",
                    pot_type="defined_contribution",
                    current_value=50000,
                    projected_value=70000,
                    age_accessible=55,
                )
            ],
            goals="Understand my pension options and plan for retirement",
            presenting_question="I have a pension with NEST. What are my options?",
        )

    @pytest.fixture
    def customer_agent(self, customer_profile):
        """Create a customer agent for testing."""
        return CustomerAgent(profile=customer_profile)

    @patch("guidance_agent.customer.simulator.completion")
    def test_simulate_outcome_returns_outcome_result(
        self, mock_completion, customer_agent
    ):
        """Test that simulate_outcome returns an OutcomeResult."""
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"customer_satisfaction": 8.5, "comprehension": 9.0, "goal_alignment": 8.0, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": true, "signposted_when_needed": true, "has_db_pension": false, "db_warning_given": false, "reasoning": "Good guidance provided"}'
                    )
                )
            ]
        )

        conversation_history = [
            {"role": "customer", "content": "What are my pension options?"},
            {
                "role": "advisor",
                "content": "You have several options including leaving it invested, taking lump sums, or regular income.",
            },
            {"role": "customer", "content": "That makes sense, thank you."},
        ]

        result = simulate_outcome(customer_agent, conversation_history)

        assert isinstance(result, OutcomeResult)
        assert result.customer_satisfaction >= 0
        assert result.customer_satisfaction <= 10
        assert result.comprehension >= 0
        assert result.comprehension <= 10
        assert result.goal_alignment >= 0
        assert result.goal_alignment <= 10

    @patch("guidance_agent.customer.simulator.completion")
    def test_successful_outcome_when_satisfaction_high(
        self, mock_completion, customer_agent
    ):
        """Test that outcome is successful when metrics are high."""
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"customer_satisfaction": 9.0, "comprehension": 8.5, "goal_alignment": 9.0, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": true, "signposted_when_needed": true, "has_db_pension": false, "db_warning_given": false, "reasoning": "Excellent guidance"}'
                    )
                )
            ]
        )

        conversation_history = [
            {"role": "customer", "content": "I need help with my pension."},
            {
                "role": "advisor",
                "content": "I can help you understand your options...",
            },
        ]

        result = simulate_outcome(customer_agent, conversation_history)

        assert result.successful is True
        assert result.status == OutcomeStatus.SUCCESS

    @patch("guidance_agent.customer.simulator.completion")
    def test_unsuccessful_outcome_when_satisfaction_low(
        self, mock_completion, customer_agent
    ):
        """Test that outcome is unsuccessful when metrics are low."""
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"customer_satisfaction": 4.0, "comprehension": 3.5, "goal_alignment": 4.5, "risks_identified": false, "guidance_appropriate": false, "fca_compliant": true, "understanding_checked": false, "signposted_when_needed": false, "has_db_pension": false, "db_warning_given": false, "reasoning": "Customer left confused"}'
                    )
                )
            ]
        )

        conversation_history = [
            {"role": "customer", "content": "I'm confused about my pension."},
            {
                "role": "advisor",
                "content": "Your pension has accumulation units...",
            },
            {"role": "customer", "content": "I don't understand."},
        ]

        result = simulate_outcome(customer_agent, conversation_history)

        assert result.successful is False
        assert result.status in [OutcomeStatus.FAILURE, OutcomeStatus.PARTIAL_SUCCESS]

    @patch("guidance_agent.customer.simulator.completion")
    def test_outcome_fails_on_compliance_violation(
        self, mock_completion, customer_agent
    ):
        """Test that outcome fails if FCA compliance is violated."""
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"customer_satisfaction": 8.0, "comprehension": 8.0, "goal_alignment": 8.0, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": false, "understanding_checked": true, "signposted_when_needed": true, "has_db_pension": false, "db_warning_given": false, "reasoning": "Crossed guidance boundary"}'
                    )
                )
            ]
        )

        conversation_history = [
            {"role": "customer", "content": "What should I invest in?"},
            {
                "role": "advisor",
                "content": "You should invest in stocks.",
            },  # Advice, not guidance
        ]

        result = simulate_outcome(customer_agent, conversation_history)

        # Compliance must be perfect
        assert result.successful is False
        assert result.fca_compliant is False

    @patch("guidance_agent.customer.simulator.completion")
    def test_outcome_includes_db_pension_check(self, mock_completion):
        """Test that outcome checks for DB pension warnings."""
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"customer_satisfaction": 8.0, "comprehension": 8.0, "goal_alignment": 8.0, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": true, "signposted_when_needed": true, "has_db_pension": true, "db_warning_given": true, "reasoning": "Proper DB warning given"}'
                    )
                )
            ]
        )

        profile = CustomerProfile(
            demographics=CustomerDemographics(
                age=58,
                gender="M",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            financial=FinancialSituation(
                annual_income=60000,
                total_assets=250000,
                total_debt=0,
                dependents=0,
                risk_tolerance="medium",
            ),
            pensions=[
                PensionPot(
                    pot_id="pot1",
                    provider="Local Government",
                    pot_type="defined_benefit",
                    current_value=0,
                    projected_value=0,
                    age_accessible=65,
                    is_db_scheme=True,
                    db_guaranteed_amount=18000,
                )
            ],
            goals="Understand DB pension options",
            presenting_question="Should I transfer my DB pension?",
        )

        agent = CustomerAgent(profile=profile)

        conversation_history = [
            {"role": "customer", "content": "Should I transfer my DB pension?"},
            {
                "role": "advisor",
                "content": "Transferring DB pensions requires regulated advice and most people are worse off...",
            },
        ]

        result = simulate_outcome(agent, conversation_history)

        assert result.has_db_pension is True
        # Should track whether DB warning was given
        assert isinstance(result.db_warning_given, bool)

    @patch("guidance_agent.customer.simulator.completion")
    def test_outcome_reasoning_is_recorded(self, mock_completion, customer_agent):
        """Test that outcome includes reasoning."""
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"customer_satisfaction": 8.0, "comprehension": 8.5, "goal_alignment": 8.0, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": true, "signposted_when_needed": true, "has_db_pension": false, "db_warning_given": false, "reasoning": "Advisor provided clear, compliant guidance that addressed customer goals"}'
                    )
                )
            ]
        )

        conversation_history = [
            {"role": "customer", "content": "I need guidance."},
            {"role": "advisor", "content": "Here's what you need to know..."},
        ]

        result = simulate_outcome(customer_agent, conversation_history)

        assert result.reasoning is not None
        assert len(result.reasoning) > 0

    @patch("guidance_agent.customer.simulator.completion")
    def test_outcome_with_comprehension_tracking(self, mock_completion, customer_agent):
        """Test that outcome considers comprehension throughout conversation."""
        # Simulate customer with tracked comprehension
        customer_agent.comprehension_level = 0.8  # High comprehension achieved

        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"customer_satisfaction": 9.0, "comprehension": 8.5, "goal_alignment": 8.5, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": true, "signposted_when_needed": true, "has_db_pension": false, "db_warning_given": false, "reasoning": "Customer demonstrated good understanding throughout"}'
                    )
                )
            ]
        )

        conversation_history = [
            {"role": "customer", "content": "Tell me about my pension."},
            {
                "role": "advisor",
                "content": "Let me explain your options clearly...",
            },
            {"role": "customer", "content": "I understand, thank you."},
        ]

        result = simulate_outcome(customer_agent, conversation_history)

        # High comprehension should correlate with success
        assert result.comprehension >= 7.0
        assert result.successful is True

    @patch("guidance_agent.customer.simulator.completion")
    def test_partial_success_outcome(self, mock_completion, customer_agent):
        """Test partial success when some goals met but not all."""
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"customer_satisfaction": 6.5, "comprehension": 7.0, "goal_alignment": 6.0, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": true, "signposted_when_needed": false, "has_db_pension": false, "db_warning_given": false, "reasoning": "Some goals addressed but customer wanted more depth"}'
                    )
                )
            ]
        )

        conversation_history = [
            {"role": "customer", "content": "I have many questions."},
            {"role": "advisor", "content": "Let me address your main concern..."},
            {"role": "customer", "content": "That helps but I still have questions."},
        ]

        result = simulate_outcome(customer_agent, conversation_history)

        assert result.status == OutcomeStatus.PARTIAL_SUCCESS

    @patch("guidance_agent.customer.simulator.completion")
    def test_outcome_simulation_error_handling(self, mock_completion, customer_agent):
        """Test that outcome simulation handles errors gracefully."""
        # Simulate LLM error
        mock_completion.side_effect = Exception("LLM error")

        conversation_history = [
            {"role": "customer", "content": "Help me."},
            {"role": "advisor", "content": "Here's some guidance."},
        ]

        result = simulate_outcome(customer_agent, conversation_history)

        # Should return a default outcome, not crash
        assert isinstance(result, OutcomeResult)
        assert result.status in [
            OutcomeStatus.SUCCESS,
            OutcomeStatus.PARTIAL_SUCCESS,
            OutcomeStatus.FAILURE,
        ]


class TestOutcomeMetrics:
    """Tests for outcome metric calculation."""

    @patch("guidance_agent.customer.simulator.completion")
    def test_outcome_metrics_are_in_valid_range(self, mock_completion):
        """Test that all outcome metrics are in valid ranges."""
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"customer_satisfaction": 8.0, "comprehension": 7.5, "goal_alignment": 8.5, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": true, "signposted_when_needed": true, "has_db_pension": false, "db_warning_given": false, "reasoning": "Good outcome"}'
                    )
                )
            ]
        )

        profile = CustomerProfile(
            demographics=CustomerDemographics(
                age=40,
                gender="F",
                location="Manchester",
                employment_status="employed",
                financial_literacy="medium",
            ),
            financial=FinancialSituation(
                annual_income=45000,
                total_assets=100000,
                total_debt=8000,
                dependents=1,
                risk_tolerance="medium",
            ),
            pensions=[],
            goals="Understand options",
            presenting_question="What should I do?",
        )

        agent = CustomerAgent(profile=profile)
        conversation_history = [
            {"role": "customer", "content": "What should I do?"},
            {"role": "advisor", "content": "Here are your options..."},
        ]

        result = simulate_outcome(agent, conversation_history)

        # All scores should be 0-10
        assert 0 <= result.customer_satisfaction <= 10
        assert 0 <= result.comprehension <= 10
        assert 0 <= result.goal_alignment <= 10

        # Booleans should be bool type
        assert isinstance(result.risks_identified, bool)
        assert isinstance(result.guidance_appropriate, bool)
        assert isinstance(result.fca_compliant, bool)
        assert isinstance(result.understanding_checked, bool)
        assert isinstance(result.signposted_when_needed, bool)
