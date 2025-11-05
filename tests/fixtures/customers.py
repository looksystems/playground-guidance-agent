"""Customer profile and validation result fixtures."""

import pytest
from uuid import uuid4

from guidance_agent.core.types import (
    CustomerProfile,
    CustomerDemographics,
    FinancialSituation,
    PensionPot,
)


@pytest.fixture
def sample_customer_profile():
    """Standard customer profile for testing.

    A 55-year-old employed male with medium risk tolerance,
    medium financial literacy, and a defined contribution pension.
    """
    demographics = CustomerDemographics(
        age=55,
        gender="male",
        location="London",
        employment_status="employed",
        financial_literacy="medium",
    )

    financial = FinancialSituation(
        annual_income=50000.0,
        total_assets=200000.0,
        total_debt=50000.0,
        dependents=2,
        risk_tolerance="medium",
    )

    pension = PensionPot(
        pot_id="pot-123",
        provider="ABC Pension Co",
        pot_type="defined_contribution",
        current_value=150000.0,
        projected_value=200000.0,
        age_accessible=55,
    )

    return CustomerProfile(
        demographics=demographics,
        financial=financial,
        pensions=[pension],
        goals="Planning retirement at age 60",
        presenting_question="What are my options for accessing my pension?",
    )


@pytest.fixture
def customer_profile(sample_customer_profile):
    """Alias for sample_customer_profile for backward compatibility."""
    return sample_customer_profile


@pytest.fixture
def high_risk_customer():
    """Customer with high risk tolerance and investment experience."""
    demographics = CustomerDemographics(
        age=42,
        gender="female",
        location="Manchester",
        employment_status="employed",
        financial_literacy="high",
    )

    financial = FinancialSituation(
        annual_income=85000.0,
        total_assets=400000.0,
        total_debt=20000.0,
        dependents=1,
        risk_tolerance="high",
    )

    pension = PensionPot(
        pot_id="pot-456",
        provider="XYZ Pensions",
        pot_type="defined_contribution",
        current_value=250000.0,
        projected_value=400000.0,
        age_accessible=55,
    )

    return CustomerProfile(
        demographics=demographics,
        financial=financial,
        pensions=[pension],
        goals="Maximize growth before retirement",
        presenting_question="Should I consolidate my pension pots for better growth?",
    )


@pytest.fixture
def retirement_focused_customer():
    """Customer approaching retirement with conservative goals."""
    demographics = CustomerDemographics(
        age=63,
        gender="male",
        location="Edinburgh",
        employment_status="employed",
        financial_literacy="medium",
    )

    financial = FinancialSituation(
        annual_income=45000.0,
        total_assets=300000.0,
        total_debt=0.0,
        dependents=0,
        risk_tolerance="low",
    )

    pension1 = PensionPot(
        pot_id="pot-789",
        provider="Old Pension Provider",
        pot_type="defined_contribution",
        current_value=100000.0,
        projected_value=105000.0,
        age_accessible=55,
    )

    pension2 = PensionPot(
        pot_id="pot-790",
        provider="New Pension Provider",
        pot_type="defined_contribution",
        current_value=120000.0,
        projected_value=125000.0,
        age_accessible=55,
    )

    return CustomerProfile(
        demographics=demographics,
        financial=financial,
        pensions=[pension1, pension2],
        goals="Generate stable retirement income",
        presenting_question="How should I draw down my pensions in retirement?",
    )


@pytest.fixture
def sample_customer_profile_dict():
    """Sample customer profile as dict for API testing."""
    return {
        "customer_id": str(uuid4()),
        "demographics": {
            "age": 52,
            "gender": "male",
            "location": "London",
            "employment_status": "employed",
            "financial_literacy": "medium",
        },
        "presenting_question": "Can I combine my pensions?",
        "goals": "Simplify pension management",
    }


@pytest.fixture
def compliant_validation_result():
    """Validation result indicating compliance with no issues."""
    from guidance_agent.compliance.validator import (
        ValidationResult,
        ValidationIssue,
        IssueType,
        IssueSeverity,
    )

    return ValidationResult(
        passed=True,
        confidence=0.97,
        issues=[],
        requires_human_review=False,
        reasoning="The guidance provided stays within FCA boundaries.",
    )


@pytest.fixture
def non_compliant_validation_result():
    """Validation result with violations requiring human review."""
    from guidance_agent.compliance.validator import (
        ValidationResult,
        ValidationIssue,
        IssueType,
        IssueSeverity,
    )

    return ValidationResult(
        passed=False,
        confidence=0.65,
        issues=[
            ValidationIssue(
                issue_type=IssueType.ADVICE_BOUNDARY,
                severity=IssueSeverity.HIGH,
                description="Guidance crosses into specific recommendation territory",
            ),
            ValidationIssue(
                issue_type=IssueType.RISK_DISCLOSURE,
                severity=IssueSeverity.MEDIUM,
                description="Insufficient risk disclosure for the proposed action",
            ),
        ],
        requires_human_review=True,
        reasoning="The response appears to provide specific advice rather than guidance.",
    )


@pytest.fixture
def validation_result_with_warnings():
    """Validation result that passes but has minor warnings."""
    from guidance_agent.compliance.validator import (
        ValidationResult,
        ValidationIssue,
        IssueType,
        IssueSeverity,
    )

    return ValidationResult(
        passed=True,
        confidence=0.85,
        issues=[
            ValidationIssue(
                issue_type=IssueType.CLARITY,
                severity=IssueSeverity.LOW,
                description="Consider adding more detail about risk factors",
            ),
        ],
        requires_human_review=False,
        reasoning="Guidance is compliant but could be clearer in some areas.",
    )
