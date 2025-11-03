"""Tests for customer profile generator."""

import pytest
from unittest.mock import Mock, patch
from uuid import UUID

from guidance_agent.customer.generator import (
    generate_demographics,
    generate_financial_situation,
    generate_pension_pots,
    generate_goals_and_inquiry,
    generate_customer_profile,
    validate_profile,
)
from guidance_agent.core.types import (
    CustomerProfile,
    CustomerDemographics,
    FinancialSituation,
    PensionPot,
)


class TestGenerateDemographics:
    """Tests for demographic generation."""

    @patch("guidance_agent.customer.generator.completion")
    def test_generate_demographics_returns_valid_structure(self, mock_completion):
        """Test that demographics generation returns valid structure."""
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"age": 45, "gender": "F", "location": "Manchester", "employment_status": "employed", "occupation": "teacher", "financial_literacy": "medium"}'
                    )
                )
            ]
        )

        demographics = generate_demographics()

        assert isinstance(demographics, CustomerDemographics)
        assert demographics.age >= 22 and demographics.age <= 80
        assert demographics.gender in ["M", "F", "Other"]
        assert demographics.employment_status in [
            "employed",
            "self-employed",
            "unemployed",
            "retired",
        ]
        assert demographics.financial_literacy in ["low", "medium", "high"]

    @patch("guidance_agent.customer.generator.completion")
    def test_generate_demographics_with_age_constraint(self, mock_completion):
        """Test generating demographics with age constraint."""
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"age": 30, "gender": "M", "location": "London", "employment_status": "employed", "occupation": "engineer", "financial_literacy": "high"}'
                    )
                )
            ]
        )

        demographics = generate_demographics(age_range=(25, 35))

        assert demographics.age >= 25 and demographics.age <= 35


class TestGenerateFinancialSituation:
    """Tests for financial situation generation."""

    @patch("guidance_agent.customer.generator.completion")
    def test_generate_financial_situation_returns_valid_structure(
        self, mock_completion
    ):
        """Test that financial situation generation returns valid structure."""
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"annual_income": 45000, "total_assets": 150000, "total_debt": 5000, "dependents": 2, "risk_tolerance": "medium"}'
                    )
                )
            ]
        )

        demographics = CustomerDemographics(
            age=40,
            gender="F",
            location="London",
            employment_status="employed",
            financial_literacy="medium",
        )

        financial = generate_financial_situation(demographics)

        assert isinstance(financial, FinancialSituation)
        assert financial.annual_income > 0
        assert financial.total_assets >= 0
        assert financial.total_debt >= 0
        assert financial.dependents >= 0
        assert financial.risk_tolerance in ["low", "medium", "high"]

    @patch("guidance_agent.customer.generator.completion")
    def test_financial_situation_consistent_with_demographics(self, mock_completion):
        """Test that financial situation is consistent with demographics."""
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"annual_income": 25000, "total_assets": 10000, "total_debt": 2000, "dependents": 0, "risk_tolerance": "low"}'
                    )
                )
            ]
        )

        demographics = CustomerDemographics(
            age=25,
            gender="M",
            location="Leeds",
            employment_status="employed",
            financial_literacy="low",
        )

        financial = generate_financial_situation(demographics)

        # Young person should have lower values
        assert financial.annual_income < 60000
        assert financial.total_assets < 200000


class TestGeneratePensionPots:
    """Tests for pension pot generation."""

    @patch("guidance_agent.customer.generator.completion")
    def test_generate_pension_pots_returns_list(self, mock_completion):
        """Test that pension pots generation returns a list."""
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"pot_id": "pot1", "provider": "Aviva", "pot_type": "defined_contribution", "current_value": 25000, "projected_value": 35000, "age_accessible": 55, "is_db_scheme": false, "db_guaranteed_amount": null}'
                    )
                )
            ]
        )

        demographics = CustomerDemographics(
            age=35,
            gender="M",
            location="London",
            employment_status="employed",
            financial_literacy="medium",
        )

        financial = FinancialSituation(
            annual_income=40000,
            total_assets=50000,
            total_debt=5000,
            dependents=1,
            risk_tolerance="medium",
        )

        pots = generate_pension_pots(demographics, financial, num_pots=2)

        assert isinstance(pots, list)
        assert len(pots) == 2
        assert all(isinstance(pot, PensionPot) for pot in pots)

    @patch("guidance_agent.customer.generator.completion")
    def test_pension_pots_have_valid_types(self, mock_completion):
        """Test that pension pots have valid types."""
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"pot_id": "pot1", "provider": "NEST", "pot_type": "defined_contribution", "current_value": 15000, "projected_value": 25000, "age_accessible": 55, "is_db_scheme": false, "db_guaranteed_amount": null}'
                    )
                )
            ]
        )

        demographics = CustomerDemographics(
            age=30,
            gender="F",
            location="Birmingham",
            employment_status="employed",
            financial_literacy="low",
        )

        financial = FinancialSituation(
            annual_income=30000,
            total_assets=20000,
            total_debt=3000,
            dependents=0,
            risk_tolerance="low",
        )

        pots = generate_pension_pots(demographics, financial, num_pots=1)

        assert pots[0].pot_type in ["defined_contribution", "defined_benefit", "private"]

    @patch("guidance_agent.customer.generator.completion")
    def test_older_customers_may_have_db_pensions(self, mock_completion):
        """Test that older customers may have DB pensions."""
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"pot_id": "pot1", "provider": "Local Government", "pot_type": "defined_benefit", "current_value": 0, "projected_value": 0, "age_accessible": 65, "is_db_scheme": true, "db_guaranteed_amount": 15000}'
                    )
                )
            ]
        )

        demographics = CustomerDemographics(
            age=58,
            gender="M",
            location="London",
            employment_status="employed",
            financial_literacy="medium",
        )

        financial = FinancialSituation(
            annual_income=50000,
            total_assets=200000,
            total_debt=10000,
            dependents=0,
            risk_tolerance="medium",
        )

        pots = generate_pension_pots(demographics, financial, num_pots=1)

        # Should be able to generate DB pension for older worker
        assert pots[0].pot_type == "defined_benefit"
        assert pots[0].is_db_scheme is True


class TestGenerateGoalsAndInquiry:
    """Tests for goals and inquiry generation."""

    @patch("guidance_agent.customer.generator.completion")
    def test_generate_goals_and_inquiry_returns_valid_data(self, mock_completion):
        """Test that goals and inquiry generation returns valid data."""
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"goals": "Understand my pensions and plan for retirement", "presenting_question": "I have two pensions and I\'m not sure if I\'m saving enough. Can you help?"}'
                    )
                )
            ]
        )

        demographics = CustomerDemographics(
            age=40,
            gender="F",
            location="Manchester",
            employment_status="employed",
            financial_literacy="low",
        )

        financial = FinancialSituation(
            annual_income=35000,
            total_assets=60000,
            total_debt=5000,
            dependents=1,
            risk_tolerance="low",
        )

        pots = [
            PensionPot(
                pot_id="pot1",
                provider="Aviva",
                pot_type="defined_contribution",
                current_value=20000,
                projected_value=30000,
                age_accessible=55,
            )
        ]

        result = generate_goals_and_inquiry(demographics, financial, pots)

        assert "goals" in result
        assert "presenting_question" in result
        assert len(result["goals"]) > 0
        assert len(result["presenting_question"]) > 0


class TestGenerateCustomerProfile:
    """Tests for complete customer profile generation."""

    @patch("guidance_agent.customer.generator.generate_goals_and_inquiry")
    @patch("guidance_agent.customer.generator.generate_pension_pots")
    @patch("guidance_agent.customer.generator.generate_financial_situation")
    @patch("guidance_agent.customer.generator.generate_demographics")
    def test_generate_complete_customer_profile(
        self,
        mock_demographics,
        mock_financial,
        mock_pots,
        mock_goals,
    ):
        """Test generating a complete customer profile."""
        mock_demographics.return_value = CustomerDemographics(
            age=42,
            gender="M",
            location="London",
            employment_status="employed",
            financial_literacy="medium",
        )

        mock_financial.return_value = FinancialSituation(
            annual_income=45000,
            total_assets=100000,
            total_debt=8000,
            dependents=2,
            risk_tolerance="medium",
        )

        mock_pots.return_value = [
            PensionPot(
                pot_id="pot1",
                provider="NEST",
                pot_type="defined_contribution",
                current_value=30000,
                projected_value=45000,
                age_accessible=55,
            )
        ]

        mock_goals.return_value = {
            "goals": "Consolidate pensions and reduce fees",
            "presenting_question": "Should I combine my pensions?",
        }

        profile = generate_customer_profile()

        assert isinstance(profile, CustomerProfile)
        assert isinstance(profile.customer_id, UUID)
        assert profile.demographics is not None
        assert profile.financial is not None
        assert len(profile.pensions) > 0
        assert profile.goals != ""
        assert profile.presenting_question != ""

    @patch("guidance_agent.customer.generator.generate_goals_and_inquiry")
    @patch("guidance_agent.customer.generator.generate_pension_pots")
    @patch("guidance_agent.customer.generator.generate_financial_situation")
    @patch("guidance_agent.customer.generator.generate_demographics")
    def test_generate_profile_with_diversity_controls(
        self, mock_demographics, mock_financial, mock_pots, mock_goals
    ):
        """Test generating profile with diversity controls."""
        mock_demographics.return_value = CustomerDemographics(
            age=55,
            gender="F",
            location="Edinburgh",
            employment_status="employed",
            financial_literacy="high",
        )

        mock_financial.return_value = FinancialSituation(
            annual_income=60000,
            total_assets=250000,
            total_debt=5000,
            dependents=0,
            risk_tolerance="high",
        )

        mock_pots.return_value = [
            PensionPot(
                pot_id="pot1",
                provider="Aviva",
                pot_type="defined_contribution",
                current_value=80000,
                projected_value=100000,
                age_accessible=55,
            )
        ]

        mock_goals.return_value = {
            "goals": "Maximize retirement income",
            "presenting_question": "What are my options for accessing my pension?",
        }

        profile = generate_customer_profile(
            age_range=(50, 60), complexity="high", literacy="high"
        )

        assert profile.demographics.age >= 50
        assert profile.demographics.age <= 60


class TestValidateProfile:
    """Tests for profile validation."""

    def test_validate_valid_profile(self):
        """Test validating a valid profile."""
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

        result = validate_profile(profile)

        assert result["valid"] is True
        assert len(result["issues"]) == 0

    def test_validate_profile_with_missing_data(self):
        """Test validating profile with missing data."""
        profile = CustomerProfile(
            demographics=None,  # Missing
            financial=FinancialSituation(
                annual_income=45000,
                total_assets=100000,
                total_debt=8000,
                dependents=1,
                risk_tolerance="medium",
            ),
            pensions=[],  # Empty
            goals="",  # Empty
            presenting_question="",  # Empty
        )

        result = validate_profile(profile)

        assert result["valid"] is False
        assert len(result["issues"]) > 0

    def test_validate_profile_with_unrealistic_values(self):
        """Test validating profile with unrealistic values."""
        profile = CustomerProfile(
            demographics=CustomerDemographics(
                age=25,  # Young
                gender="M",
                location="London",
                employment_status="employed",
                financial_literacy="low",
            ),
            financial=FinancialSituation(
                annual_income=20000,
                total_assets=500000,  # Unrealistically high for age/income
                total_debt=0,
                dependents=0,
                risk_tolerance="low",
            ),
            pensions=[
                PensionPot(
                    pot_id="pot1",
                    provider="NEST",
                    pot_type="defined_benefit",  # Unrealistic for young private sector
                    current_value=0,
                    projected_value=0,
                    age_accessible=65,
                    is_db_scheme=True,
                    db_guaranteed_amount=20000,
                )
            ],
            goals="Plan retirement",
            presenting_question="When can I retire?",
        )

        result = validate_profile(profile)

        # Should flag unrealistic aspects
        assert "issues" in result
