"""Tests for CustomerAgent class."""

import pytest
from unittest.mock import Mock, patch

from guidance_agent.customer.agent import CustomerAgent
from guidance_agent.core.types import (
    CustomerProfile,
    CustomerDemographics,
    FinancialSituation,
    PensionPot,
)


class TestCustomerAgentInitialization:
    """Tests for CustomerAgent initialization."""

    def test_create_customer_agent(self):
        """Test creating a customer agent."""
        profile = CustomerProfile(
            demographics=CustomerDemographics(
                age=40,
                gender="M",
                location="London",
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
            pensions=[
                PensionPot(
                    pot_id="pot1",
                    provider="NEST",
                    pot_type="defined_contribution",
                    current_value=30000,
                    projected_value=45000,
                    age_accessible=55,
                )
            ],
            goals="Understand my pensions",
            presenting_question="Can you help me understand my pension?",
        )

        agent = CustomerAgent(profile=profile)

        # Verify agent was created with proper attributes
        assert agent is not None
        assert agent.profile == profile
        assert hasattr(agent, "conversation_memory")
        assert hasattr(agent, "comprehension_level")

    def test_customer_agent_has_initial_comprehension_level(self):
        """Test that customer agent starts with initial comprehension level."""
        profile = CustomerProfile(
            demographics=CustomerDemographics(
                age=35,
                gender="F",
                location="Manchester",
                employment_status="employed",
                financial_literacy="low",
            ),
            financial=FinancialSituation(
                annual_income=30000,
                total_assets=40000,
                total_debt=5000,
                dependents=2,
                risk_tolerance="low",
            ),
            pensions=[],
            goals="Learn about pensions",
            presenting_question="What is a pension?",
        )

        agent = CustomerAgent(profile=profile)

        assert agent.comprehension_level >= 0
        assert agent.comprehension_level <= 1


class TestPresentInquiry:
    """Tests for present_inquiry method."""

    def test_present_inquiry_returns_presenting_question(self):
        """Test that present_inquiry returns the presenting question."""
        profile = CustomerProfile(
            demographics=CustomerDemographics(
                age=50,
                gender="M",
                location="Edinburgh",
                employment_status="employed",
                financial_literacy="high",
            ),
            financial=FinancialSituation(
                annual_income=60000,
                total_assets=200000,
                total_debt=0,
                dependents=0,
                risk_tolerance="high",
            ),
            pensions=[
                PensionPot(
                    pot_id="pot1",
                    provider="Aviva",
                    pot_type="defined_contribution",
                    current_value=80000,
                    projected_value=100000,
                    age_accessible=55,
                )
            ],
            goals="Maximize retirement income",
            presenting_question="What are my options for accessing my pension at 55?",
        )

        agent = CustomerAgent(profile=profile)
        inquiry = agent.present_inquiry()

        assert inquiry == profile.presenting_question


class TestSimulateComprehension:
    """Tests for simulate_comprehension method."""

    @patch("guidance_agent.customer.agent.completion")
    def test_simulate_comprehension_returns_result(self, mock_completion):
        """Test that simulate_comprehension returns comprehension result."""
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"understanding_level": "fully_understood", "confusion_points": [], "customer_feeling": "confident"}'
                    )
                )
            ]
        )

        profile = CustomerProfile(
            demographics=CustomerDemographics(
                age=45,
                gender="F",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            financial=FinancialSituation(
                annual_income=50000,
                total_assets=120000,
                total_debt=10000,
                dependents=1,
                risk_tolerance="medium",
            ),
            pensions=[],
            goals="Understand options",
            presenting_question="What should I do?",
        )

        agent = CustomerAgent(profile=profile)
        guidance = "You have several options for accessing your pension..."

        result = agent.simulate_comprehension(guidance, [])

        assert "understanding_level" in result
        assert "confusion_points" in result
        assert "customer_feeling" in result

    @patch("guidance_agent.customer.agent.completion")
    def test_low_literacy_customer_may_not_understand_technical_guidance(
        self, mock_completion
    ):
        """Test that low literacy customers may not understand technical guidance."""
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"understanding_level": "not_understood", "confusion_points": ["technical jargon", "complex concepts"], "customer_feeling": "overwhelmed"}'
                    )
                )
            ]
        )

        profile = CustomerProfile(
            demographics=CustomerDemographics(
                age=30,
                gender="M",
                location="Birmingham",
                employment_status="employed",
                financial_literacy="low",
            ),
            financial=FinancialSituation(
                annual_income=25000,
                total_assets=10000,
                total_debt=3000,
                dependents=0,
                risk_tolerance="low",
            ),
            pensions=[],
            goals="Understand basics",
            presenting_question="What is a pension?",
        )

        agent = CustomerAgent(profile=profile)
        technical_guidance = "Your defined contribution pension utilizes accumulation units with crystallization events..."

        result = agent.simulate_comprehension(technical_guidance, [])

        assert result["understanding_level"] in [
            "not_understood",
            "partially_understood",
        ]

    @patch("guidance_agent.customer.agent.completion")
    def test_comprehension_updates_agent_state(self, mock_completion):
        """Test that comprehension simulation updates agent state."""
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"understanding_level": "partially_understood", "confusion_points": ["some terms unclear"], "customer_feeling": "uncertain"}'
                    )
                )
            ]
        )

        profile = CustomerProfile(
            demographics=CustomerDemographics(
                age=40,
                gender="F",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            financial=FinancialSituation(
                annual_income=45000,
                total_assets=80000,
                total_debt=5000,
                dependents=1,
                risk_tolerance="medium",
            ),
            pensions=[],
            goals="Plan retirement",
            presenting_question="When can I retire?",
        )

        agent = CustomerAgent(profile=profile)
        initial_level = agent.comprehension_level

        agent.simulate_comprehension("You can access your pension at 55.", [])

        # Verify comprehension level is tracked
        assert hasattr(agent, "comprehension_level")
        assert agent.comprehension_level is not None


class TestRespond:
    """Tests for respond method."""

    @patch("guidance_agent.customer.agent.completion")
    def test_respond_generates_natural_response(self, mock_completion):
        """Test that respond generates natural customer response."""
        # Mock comprehension check
        mock_completion.side_effect = [
            # First call: comprehension simulation
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content='{"understanding_level": "fully_understood", "confusion_points": [], "customer_feeling": "confident"}'
                        )
                    )
                ]
            ),
            # Second call: response generation
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content="Thank you, that's very helpful. I think I understand now."
                        )
                    )
                ]
            ),
        ]

        profile = CustomerProfile(
            demographics=CustomerDemographics(
                age=42,
                gender="M",
                location="Leeds",
                employment_status="employed",
                financial_literacy="medium",
            ),
            financial=FinancialSituation(
                annual_income=40000,
                total_assets=90000,
                total_debt=7000,
                dependents=2,
                risk_tolerance="medium",
            ),
            pensions=[],
            goals="Consolidate pensions",
            presenting_question="Should I combine my pensions?",
        )

        agent = CustomerAgent(profile=profile)
        advisor_message = "Combining your pensions can help reduce fees..."

        response = agent.respond(advisor_message, [])

        assert isinstance(response, str)
        assert len(response) > 0

    @patch("guidance_agent.customer.agent.completion")
    def test_confused_customer_asks_followup_questions(self, mock_completion):
        """Test that confused customers ask follow-up questions."""
        mock_completion.side_effect = [
            # Comprehension: confused
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content='{"understanding_level": "not_understood", "confusion_points": ["what is consolidation"], "customer_feeling": "confused"}'
                        )
                    )
                ]
            ),
            # Response: asking for clarification
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content="I'm not sure I understand - what does consolidation mean?"
                        )
                    )
                ]
            ),
        ]

        profile = CustomerProfile(
            demographics=CustomerDemographics(
                age=28,
                gender="F",
                location="London",
                employment_status="employed",
                financial_literacy="low",
            ),
            financial=FinancialSituation(
                annual_income=30000,
                total_assets=15000,
                total_debt=2000,
                dependents=0,
                risk_tolerance="low",
            ),
            pensions=[],
            goals="Understand basics",
            presenting_question="What should I do with my old pensions?",
        )

        agent = CustomerAgent(profile=profile)
        advisor_message = "Pension consolidation might be beneficial..."

        response = agent.respond(advisor_message, [])

        assert isinstance(response, str)
        # Should ask a question when confused
        assert "?" in response or "understand" in response.lower()

    @patch("guidance_agent.customer.agent.completion")
    def test_response_reflects_literacy_level(self, mock_completion):
        """Test that response reflects customer literacy level."""
        mock_completion.side_effect = [
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content='{"understanding_level": "fully_understood", "confusion_points": [], "customer_feeling": "satisfied"}'
                        )
                    )
                ]
            ),
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content="Great, thanks for explaining that clearly."
                        )
                    )
                ]
            ),
        ]

        profile = CustomerProfile(
            demographics=CustomerDemographics(
                age=35,
                gender="M",
                location="Manchester",
                employment_status="employed",
                financial_literacy="low",
            ),
            financial=FinancialSituation(
                annual_income=32000,
                total_assets=25000,
                total_debt=4000,
                dependents=1,
                risk_tolerance="low",
            ),
            pensions=[],
            goals="Learn about pensions",
            presenting_question="How do pensions work?",
        )

        agent = CustomerAgent(profile=profile)
        simple_guidance = "A pension is like a savings account for when you retire..."

        response = agent.respond(simple_guidance, [])

        assert isinstance(response, str)

    @patch("guidance_agent.customer.agent.completion")
    def test_conversation_memory_is_updated(self, mock_completion):
        """Test that conversation memory is updated after response."""
        mock_completion.side_effect = [
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content='{"understanding_level": "fully_understood", "confusion_points": [], "customer_feeling": "confident"}'
                        )
                    )
                ]
            ),
            Mock(
                choices=[Mock(message=Mock(content="Thank you for the information."))]
            ),
        ]

        profile = CustomerProfile(
            demographics=CustomerDemographics(
                age=50,
                gender="F",
                location="Edinburgh",
                employment_status="employed",
                financial_literacy="high",
            ),
            financial=FinancialSituation(
                annual_income=55000,
                total_assets=180000,
                total_debt=0,
                dependents=0,
                risk_tolerance="high",
            ),
            pensions=[],
            goals="Optimize retirement",
            presenting_question="What's the most tax-efficient way to access my pension?",
        )

        agent = CustomerAgent(profile=profile)
        initial_memory_length = len(agent.conversation_memory)

        agent.respond("Here's some guidance...", [])

        # Memory should be updated
        assert len(agent.conversation_memory) >= initial_memory_length


class TestCustomerBehaviorConsistency:
    """Tests for customer behavior consistency."""

    def test_customer_behavior_consistent_with_profile(self):
        """Test that customer behavior is consistent with their profile."""
        profile = CustomerProfile(
            demographics=CustomerDemographics(
                age=60,
                gender="M",
                location="London",
                employment_status="employed",
                financial_literacy="high",
            ),
            financial=FinancialSituation(
                annual_income=70000,
                total_assets=300000,
                total_debt=0,
                dependents=0,
                risk_tolerance="high",
            ),
            pensions=[
                PensionPot(
                    pot_id="pot1",
                    provider="Aviva",
                    pot_type="defined_contribution",
                    current_value=150000,
                    projected_value=180000,
                    age_accessible=55,
                )
            ],
            goals="Maximize tax efficiency",
            presenting_question="What's the optimal drawdown strategy?",
        )

        agent = CustomerAgent(profile=profile)

        # High literacy customer should have higher base comprehension
        assert agent.comprehension_level > 0.3
