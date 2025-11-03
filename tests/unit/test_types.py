"""Unit tests for core types."""

import pytest
from uuid import UUID

from guidance_agent.core.types import (
    MemoryType,
    TaskType,
    OutcomeStatus,
    OutcomeResult,
    CustomerProfile,
    CustomerDemographics,
    FinancialSituation,
    PensionPot,
)


class TestEnums:
    """Tests for enum types."""

    def test_memory_type_values(self):
        """Test MemoryType enum values."""
        assert MemoryType.OBSERVATION.value == "observation"
        assert MemoryType.REFLECTION.value == "reflection"
        assert MemoryType.PLAN.value == "plan"

    def test_task_type_values(self):
        """Test TaskType enum has expected values."""
        assert TaskType.GENERAL_INQUIRY.value == "general_inquiry"
        assert TaskType.WITHDRAWAL_OPTIONS.value == "withdrawal_options"
        assert TaskType.DEFINED_BENEFIT_TRANSFER.value == "defined_benefit_transfer"

    def test_outcome_status_values(self):
        """Test OutcomeStatus enum values."""
        assert OutcomeStatus.SUCCESS.value == "success"
        assert OutcomeStatus.FAILURE.value == "failure"


class TestOutcomeResult:
    """Tests for OutcomeResult dataclass."""

    def test_create_default_outcome(self):
        """Test creating an outcome with defaults."""
        outcome = OutcomeResult()

        assert isinstance(outcome.outcome_id, UUID)
        assert outcome.status == OutcomeStatus.SUCCESS
        assert outcome.successful is True
        assert outcome.customer_satisfaction == 0.0
        assert outcome.fca_compliant is True

    def test_create_failed_outcome(self):
        """Test creating a failed outcome."""
        outcome = OutcomeResult(
            status=OutcomeStatus.FAILURE,
            successful=False,
            customer_satisfaction=3.0,
            fca_compliant=False,
            reasoning="Guidance was not appropriate",
            issues=["Risk not disclosed", "No understanding check"],
        )

        assert outcome.successful is False
        assert outcome.status == OutcomeStatus.FAILURE
        assert len(outcome.issues) == 2
        assert "Risk not disclosed" in outcome.issues

    def test_outcome_to_dict(self):
        """Test converting outcome to dictionary."""
        outcome = OutcomeResult(
            customer_satisfaction=8.5,
            comprehension=7.0,
            fca_compliant=True,
        )

        data = outcome.to_dict()

        assert isinstance(data, dict)
        assert data["customer_satisfaction"] == 8.5
        assert data["comprehension"] == 7.0
        assert data["fca_compliant"] is True
        assert isinstance(data["outcome_id"], str)
        assert data["status"] == "success"


class TestCustomerProfile:
    """Tests for CustomerProfile and related types."""

    def test_create_pension_pot(self):
        """Test creating a pension pot."""
        pot = PensionPot(
            pot_id="pot-123",
            provider="Test Provider",
            pot_type="defined_contribution",
            current_value=100000.0,
            projected_value=150000.0,
            age_accessible=55,
        )

        assert pot.pot_id == "pot-123"
        assert pot.current_value == 100000.0
        assert pot.is_db_scheme is False

    def test_create_db_pension_pot(self):
        """Test creating a defined benefit pension pot."""
        pot = PensionPot(
            pot_id="pot-db",
            provider="DB Provider",
            pot_type="defined_benefit",
            current_value=200000.0,
            projected_value=200000.0,
            age_accessible=60,
            is_db_scheme=True,
            db_guaranteed_amount=25000.0,
        )

        assert pot.is_db_scheme is True
        assert pot.db_guaranteed_amount == 25000.0
        assert pot.pot_type == "defined_benefit"

    def test_create_customer_demographics(self):
        """Test creating customer demographics."""
        demographics = CustomerDemographics(
            age=55,
            gender="male",
            location="London",
            employment_status="employed",
            financial_literacy="medium",
        )

        assert demographics.age == 55
        assert demographics.financial_literacy == "medium"

    def test_create_financial_situation(self):
        """Test creating financial situation."""
        financial = FinancialSituation(
            annual_income=50000.0,
            total_assets=200000.0,
            total_debt=50000.0,
            dependents=2,
            risk_tolerance="medium",
        )

        assert financial.annual_income == 50000.0
        assert financial.dependents == 2

    def test_create_full_customer_profile(self, sample_customer_profile):
        """Test creating a complete customer profile."""
        profile = sample_customer_profile

        assert isinstance(profile.customer_id, UUID)
        assert profile.demographics.age == 55
        assert profile.financial.annual_income == 50000.0
        assert len(profile.pensions) == 1
        assert profile.pensions[0].pot_id == "pot-123"
        assert profile.goals == "Planning retirement at age 60"

    def test_customer_profile_defaults(self):
        """Test customer profile with default values."""
        profile = CustomerProfile()

        assert isinstance(profile.customer_id, UUID)
        assert profile.pensions == []
        assert profile.goals == ""
