"""Integration tests for customer-advisor consultation loop."""

import pytest
from unittest.mock import Mock, patch

from guidance_agent.customer.generator import generate_customer_profile
from guidance_agent.customer.agent import CustomerAgent
from guidance_agent.customer.simulator import simulate_outcome
from guidance_agent.advisor.agent import AdvisorAgent
from guidance_agent.core.types import (
    AdvisorProfile,
    CustomerProfile,
    CustomerDemographics,
    FinancialSituation,
    PensionPot,
    OutcomeStatus,
)


class TestCustomerAdvisorLoop:
    """Integration tests for full customer-advisor consultation loop."""

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
            goals="Understand my pension and check if I'm saving enough",
            presenting_question="I have a pension with NEST. Am I saving enough for retirement?",
        )

    @patch("guidance_agent.customer.simulator.completion")
    @patch("guidance_agent.customer.agent.completion")
    @patch("guidance_agent.advisor.agent.completion")
    def test_simple_consultation_completes(
        self,
        mock_advisor_completion,
        mock_customer_completion,
        mock_outcome_completion,
        advisor_profile,
        simple_customer_profile,
    ):
        """Test that a simple consultation completes successfully."""
        # Mock advisor response
        mock_advisor_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content="Based on your age and income, having £15,000 in your pension is a good start. The general rule of thumb is to save about half your age as a percentage of your salary. At 30, that would be 15% including employer contributions. Let me help you understand if you're on track."
                    )
                )
            ]
        )

        # Mock customer comprehension and response
        mock_customer_completion.side_effect = [
            # Comprehension check
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content='{"understanding_level": "fully_understood", "confusion_points": [], "customer_feeling": "confident"}'
                        )
                    )
                ]
            ),
            # Customer response
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content="Thank you, that's helpful. So I'm on the right track?"
                        )
                    )
                ]
            ),
        ]

        # Mock outcome simulation
        mock_outcome_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"customer_satisfaction": 8.5, "comprehension": 9.0, "goal_alignment": 8.0, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": true, "signposted_when_needed": false, "has_db_pension": false, "db_warning_given": false, "reasoning": "Good guidance provided"}'
                    )
                )
            ]
        )

        # Run consultation
        advisor = AdvisorAgent(profile=advisor_profile)
        customer = CustomerAgent(profile=simple_customer_profile)

        # Customer presents inquiry
        inquiry = customer.present_inquiry()
        assert inquiry == simple_customer_profile.presenting_question

        # Advisor provides guidance
        conversation_history = [{"role": "customer", "content": inquiry}]
        guidance = advisor.provide_guidance(customer.profile, conversation_history)
        assert guidance is not None
        assert len(guidance) > 0

        # Customer responds
        conversation_history.append({"role": "advisor", "content": guidance})
        customer_response = customer.respond(guidance, conversation_history)
        assert customer_response is not None

        # Simulate outcome
        conversation_history.append({"role": "customer", "content": customer_response})
        outcome = simulate_outcome(customer, conversation_history)

        assert outcome is not None
        assert outcome.status in [OutcomeStatus.SUCCESS, OutcomeStatus.PARTIAL_SUCCESS]

    @patch("guidance_agent.customer.simulator.completion")
    @patch("guidance_agent.customer.agent.completion")
    @patch("guidance_agent.advisor.agent.completion")
    def test_multi_turn_consultation(
        self,
        mock_advisor_completion,
        mock_customer_completion,
        mock_outcome_completion,
        advisor_profile,
        simple_customer_profile,
    ):
        """Test a multi-turn consultation."""
        # Mock multiple turns - each provide_guidance call makes multiple completion calls:
        # 1. Initial guidance generation
        # 2. Compliance validation
        # 3. Refinement (if needed)
        mock_advisor_completion.side_effect = [
            # Turn 1 - Initial guidance
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content="Let me help you understand your pension options."
                        )
                    )
                ]
            ),
            # Turn 1 - Validation result
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content='{"passed": true, "score": 0.95, "issues": [], "reasoning": "Clear guidance"}'
                        )
                    )
                ]
            ),
            # Turn 1 - Refinement (if borderline)
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content="Let me help you understand your pension options."
                        )
                    )
                ]
            ),
            # Turn 2 - Initial guidance
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content="Yes, you're making good progress. Keep it up!"
                        )
                    )
                ]
            ),
            # Turn 2 - Validation result
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content='{"passed": true, "score": 0.95, "issues": [], "reasoning": "Supportive response"}'
                        )
                    )
                ]
            ),
            # Turn 2 - Refinement (if borderline)
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content="Yes, you're making good progress. Keep it up!"
                        )
                    )
                ]
            ),
        ]

        mock_customer_completion.side_effect = [
            # First comprehension
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content='{"understanding_level": "partially_understood", "confusion_points": ["contribution rates"], "customer_feeling": "uncertain"}'
                        )
                    )
                ]
            ),
            # First response
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content="Could you explain more about contribution rates?"
                        )
                    )
                ]
            ),
            # Second comprehension
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content='{"understanding_level": "fully_understood", "confusion_points": [], "customer_feeling": "confident"}'
                        )
                    )
                ]
            ),
            # Second response
            Mock(
                choices=[Mock(message=Mock(content="Thank you, I understand now."))]
            ),
        ]

        mock_outcome_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"customer_satisfaction": 9.0, "comprehension": 8.5, "goal_alignment": 8.5, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": true, "signposted_when_needed": false, "has_db_pension": false, "db_warning_given": false, "reasoning": "Patient explanation led to understanding"}'
                    )
                )
            ]
        )

        advisor = AdvisorAgent(profile=advisor_profile)
        customer = CustomerAgent(profile=simple_customer_profile)

        conversation_history = []

        # Turn 1
        inquiry = customer.present_inquiry()
        conversation_history.append({"role": "customer", "content": inquiry})

        guidance1 = advisor.provide_guidance(customer.profile, conversation_history)
        conversation_history.append({"role": "advisor", "content": guidance1})

        response1 = customer.respond(guidance1, conversation_history)
        conversation_history.append({"role": "customer", "content": response1})

        # Turn 2
        guidance2 = advisor.provide_guidance(customer.profile, conversation_history)
        conversation_history.append({"role": "advisor", "content": guidance2})

        response2 = customer.respond(guidance2, conversation_history)
        conversation_history.append({"role": "customer", "content": response2})

        # Outcome
        outcome = simulate_outcome(customer, conversation_history)

        assert len(conversation_history) >= 4  # Multiple turns
        assert outcome.successful is True

    @patch("guidance_agent.customer.generator.completion")
    def test_generated_customer_profile_works_in_consultation(
        self, mock_generator_completion
    ):
        """Test that generated customer profiles work in consultation."""
        # Mock customer generation
        mock_generator_completion.side_effect = [
            # Demographics
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content='{"gender": "M", "location": "Manchester", "employment_status": "employed", "occupation": "teacher", "financial_literacy": "medium"}'
                        )
                    )
                ]
            ),
            # Financial situation
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content='{"annual_income": 40000, "total_assets": 60000, "total_debt": 8000, "dependents": 1, "risk_tolerance": "medium"}'
                        )
                    )
                ]
            ),
            # Pension pot
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content='{"pot_id": "pot1", "provider": "Aviva", "pot_type": "defined_contribution", "current_value": 25000, "projected_value": 35000, "age_accessible": 55, "is_db_scheme": false, "db_guaranteed_amount": null}'
                        )
                    )
                ]
            ),
            # Goals and inquiry
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content='{"goals": "Consolidate pensions", "presenting_question": "Should I combine my pensions?"}'
                        )
                    )
                ]
            ),
        ]

        # Generate customer profile
        profile = generate_customer_profile()

        # Should be able to create customer agent
        customer = CustomerAgent(profile=profile)

        # Should be able to present inquiry
        inquiry = customer.present_inquiry()
        assert inquiry is not None
        assert len(inquiry) > 0

    @pytest.fixture
    def complex_customer_profile(self):
        """Create a complex customer profile with DB pension."""
        return CustomerProfile(
            demographics=CustomerDemographics(
                age=58,
                gender="M",
                location="Edinburgh",
                employment_status="employed",
                financial_literacy="high",
            ),
            financial=FinancialSituation(
                annual_income=65000,
                total_assets=280000,
                total_debt=0,
                dependents=0,
                risk_tolerance="high",
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
                ),
                PensionPot(
                    pot_id="pot2",
                    provider="Aviva",
                    pot_type="defined_contribution",
                    current_value=120000,
                    projected_value=150000,
                    age_accessible=55,
                ),
            ],
            goals="Understand options for DB pension and plan retirement",
            presenting_question="I have a DB pension from my old job and a DC pension. What are my options?",
        )

    @patch("guidance_agent.customer.simulator.completion")
    @patch("guidance_agent.customer.agent.completion")
    @patch("guidance_agent.advisor.agent.completion")
    def test_db_pension_warning_tracked(
        self,
        mock_advisor_completion,
        mock_customer_completion,
        mock_outcome_completion,
        advisor_profile,
        complex_customer_profile,
    ):
        """Test that DB pension warnings are tracked in outcome."""
        # Mock advisor giving DB warning
        mock_advisor_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content="Your DB pension is very valuable. Transferring out of a DB scheme requires regulated financial advice and most people are worse off. I can provide guidance on understanding your options, but not advice on whether to transfer."
                    )
                )
            ]
        )

        # Mock customer response
        mock_customer_completion.side_effect = [
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content='{"understanding_level": "fully_understood", "confusion_points": [], "customer_feeling": "informed"}'
                        )
                    )
                ]
            ),
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content="I understand. I should seek regulated advice if I'm considering transferring."
                        )
                    )
                ]
            ),
        ]

        # Mock outcome with DB warning given
        mock_outcome_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"customer_satisfaction": 9.0, "comprehension": 9.0, "goal_alignment": 8.5, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": true, "signposted_when_needed": true, "has_db_pension": true, "db_warning_given": true, "reasoning": "Proper DB warning and signposting provided"}'
                    )
                )
            ]
        )

        advisor = AdvisorAgent(profile=advisor_profile)
        customer = CustomerAgent(profile=complex_customer_profile)

        conversation_history = [
            {"role": "customer", "content": customer.present_inquiry()}
        ]

        guidance = advisor.provide_guidance(
            complex_customer_profile, conversation_history
        )
        conversation_history.append({"role": "advisor", "content": guidance})

        response = customer.respond(guidance, conversation_history)
        conversation_history.append({"role": "customer", "content": response})

        outcome = simulate_outcome(customer, conversation_history)

        # Should track DB pension
        assert outcome.has_db_pension is True
        assert outcome.db_warning_given is True
        assert outcome.successful is True


class TestOutcomeQualityMetrics:
    """Integration tests for outcome quality metrics."""

    @patch("guidance_agent.customer.simulator.completion")
    @patch("guidance_agent.customer.agent.completion")
    @patch("guidance_agent.advisor.agent.completion")
    def test_low_literacy_customer_poor_outcome_with_technical_guidance(
        self, mock_advisor_completion, mock_customer_completion, mock_outcome_completion
    ):
        """Test that technical guidance to low literacy customer results in poor outcome."""
        # Mock overly technical advisor response
        mock_advisor_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content="Your defined contribution pension utilizes accumulation units with crystallization events at your selected retirement age, subject to HMRC lifetime allowance considerations."
                    )
                )
            ]
        )

        # Mock customer confusion
        mock_customer_completion.side_effect = [
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content='{"understanding_level": "not_understood", "confusion_points": ["all technical terms"], "customer_feeling": "overwhelmed"}'
                        )
                    )
                ]
            ),
            Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content="I don't understand any of that. Can you explain in simpler terms?"
                        )
                    )
                ]
            ),
        ]

        # Mock poor outcome
        mock_outcome_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"customer_satisfaction": 3.0, "comprehension": 2.0, "goal_alignment": 3.0, "risks_identified": false, "guidance_appropriate": false, "fca_compliant": true, "understanding_checked": false, "signposted_when_needed": false, "has_db_pension": false, "db_warning_given": false, "reasoning": "Customer left confused due to overly technical language"}'
                    )
                )
            ]
        )

        profile = CustomerProfile(
            demographics=CustomerDemographics(
                age=28,
                gender="F",
                location="London",
                employment_status="employed",
                financial_literacy="low",
            ),
            financial=FinancialSituation(
                annual_income=28000,
                total_assets=12000,
                total_debt=3000,
                dependents=0,
                risk_tolerance="low",
            ),
            pensions=[],
            goals="Understand basics",
            presenting_question="What is a pension?",
        )

        advisor = AdvisorAgent(profile=AdvisorProfile(name="Test", description="Test"))
        customer = CustomerAgent(profile=profile)

        conversation_history = [{"role": "customer", "content": "What is a pension?"}]
        guidance = advisor.provide_guidance(profile, conversation_history)
        conversation_history.append({"role": "advisor", "content": guidance})

        response = customer.respond(guidance, conversation_history)
        conversation_history.append({"role": "customer", "content": response})

        outcome = simulate_outcome(customer, conversation_history)

        # Poor outcome expected
        assert outcome.successful is False
        assert outcome.comprehension < 5.0
        assert outcome.customer_satisfaction < 5.0
