"""Test data fixtures for template testing.

This module provides pytest fixtures with realistic sample data for testing
Jinja template rendering.
"""

import pytest
from uuid import uuid4
from datetime import datetime

from guidance_agent.core.types import (
    AdvisorProfile,
    CustomerProfile,
    CustomerDemographics,
    FinancialSituation,
    PensionPot,
    Case,
    GuidanceRule,
    RetrievedContext,
    OutcomeResult,
    OutcomeStatus,
)
from guidance_agent.core.memory import MemoryNode, MemoryType
from guidance_agent.compliance.validator import ValidationIssue, IssueType, IssueSeverity


# ============================================================================
# Helper Functions (can be imported and called directly)
# ============================================================================


def get_sample_advisor():
    """Get sample advisor for testing (non-fixture version)."""
    return AdvisorProfile(
        name="Sarah Thompson",
        description="FCA-compliant pension guidance specialist with 10+ years experience",
        specialization="pension_guidance",
        experience_level="senior",
    )


def get_sample_customer():
    """Get sample customer with full profile for testing (non-fixture version)."""
    return CustomerProfile(
        customer_id=uuid4(),
        demographics=CustomerDemographics(
            age=55,
            gender="female",
            location="London",
            employment_status="employed",
            financial_literacy="medium",
        ),
        financial=FinancialSituation(
            annual_income=45000,
            total_assets=250000,
            total_debt=15000,
            dependents=0,
            risk_tolerance="medium",
        ),
        pensions=[
            PensionPot(
                pot_id="pot_001",
                provider="Aviva",
                pot_type="defined_contribution",
                current_value=150000,
                projected_value=180000,
                age_accessible=55,
                is_db_scheme=False,
            ),
            PensionPot(
                pot_id="pot_002",
                provider="Standard Life",
                pot_type="defined_benefit",
                current_value=80000,
                projected_value=100000,
                age_accessible=60,
                is_db_scheme=True,
                db_guaranteed_amount=12000,
            ),
        ],
        goals="Planning early retirement at age 58",
        presenting_question="Should I take my pension at 55 or wait until 60?",
        created_at=datetime.now(),
    )


def get_sample_context():
    """Get sample context with cases, rules, and memories (non-fixture version)."""
    return RetrievedContext(
        cases=[
            Case(
                case_id="case_001",
                task_type="withdrawal_options",
                customer_situation="55-year-old considering early pension access",
                guidance_provided="Explained tax-free lump sum, discussed drawdown vs annuity",
                outcome_summary="Customer decided to wait 2 years for better value",
                similarity_score=0.85,
            ),
            Case(
                case_id="case_002",
                task_type="defined_benefit_transfer",
                customer_situation="DB pension holder considering transfer",
                guidance_provided="Warned about giving up guaranteed income, signposted to FCA advisor",
                outcome_summary="Customer decided not to transfer after understanding risks",
                similarity_score=0.72,
            ),
        ],
        rules=[
            GuidanceRule(
                rule_id="rule_001",
                principle="Always warn about DB transfer risks before age 60",
                domain="defined_benefit",
                confidence=0.95,
                evidence_count=45,
            ),
            GuidanceRule(
                rule_id="rule_002",
                principle="Check understanding of tax implications for early withdrawal",
                domain="tax",
                confidence=0.88,
                evidence_count=32,
            ),
        ],
        memories=[
            MemoryNode(
                memory_id=uuid4(),
                memory_type=MemoryType.OBSERVATION,
                description="Customer expressed concern about market volatility",
                importance=0.8,
                timestamp=datetime.now(),
            ),
            MemoryNode(
                memory_id=uuid4(),
                memory_type=MemoryType.REFLECTION,
                description="Customer may benefit from conservative drawdown strategy",
                importance=0.9,
                timestamp=datetime.now(),
            ),
        ],
        fca_requirements="Provide guidance within FCA boundaries, avoid personal recommendations",
        reasoning="Customer has mixed pension types including DB scheme requiring careful consideration",
    )


def get_sample_conversation_history():
    """Get sample conversation history for testing (non-fixture version)."""
    return [
        {"role": "customer", "content": "Hello, I'm thinking about my pension options."},
        {
            "role": "advisor",
            "content": "Hello! I'd be happy to help guide you through your pension options. Could you tell me a bit more about your situation?",
        },
        {
            "role": "customer",
            "content": "I'm 55 and wondering if I should access my pension now or wait.",
        },
    ]


def get_sample_guidance():
    """Get sample guidance text for validation testing (non-fixture version)."""
    return """Thank you for your question about pension access timing.

Given your age of 55, you do have the option to access your pension now. However, there are several factors to consider:

**Tax-Free Lump Sum:**
You can take up to 25% of your pension pot tax-free. In your case, that would be approximately £37,500 from your Aviva pension.

**Income Options:**
For the remainder, you have several options:
1. Purchase an annuity for guaranteed income
2. Use flexi-access drawdown for flexible withdrawals
3. Take the entire pot as cash (though this has significant tax implications)

**Important Considerations:**
- Your Aviva pension is accessible now, but your Standard Life DB pension isn't accessible until age 60
- The DB pension provides guaranteed income of £12,000/year - this is very valuable
- Early access means your pot has less time to grow
- You need to consider your income needs until State Pension age

I strongly recommend speaking with an FCA-regulated financial advisor before making any decisions about your DB pension, as transfers out of these schemes require specialist advice.

Does this help clarify your options? Would you like me to explain any aspect in more detail?"""


def get_sample_validation_issues():
    """Get sample validation issues for testing (non-fixture version)."""
    return [
        ValidationIssue(
            issue_type=IssueType.ADVICE_BOUNDARY,
            severity=IssueSeverity.HIGH,
            description="Language suggests a personal recommendation ('I would recommend')",
            suggestion="Replace with 'you might consider' or 'some people choose to'"
        ),
        ValidationIssue(
            issue_type=IssueType.CLARITY,
            severity=IssueSeverity.MEDIUM,
            description="Missing explicit statement about guidance vs advice boundary",
            suggestion="Add a clear statement that you're providing guidance, not regulated advice"
        ),
    ]


def get_sample_reasoning():
    """Get sample reasoning output for testing (non-fixture version)."""
    return """Let me think through this step-by-step:

1. **Customer's Real Question:** The customer is asking about timing - should they access at 55 or wait until 60?

2. **Key Considerations:**
   - Two different pension types (DC and DB)
   - DB pension has guaranteed income of £12,000/year
   - DC pension is accessible now, DB isn't until 60
   - Customer wants early retirement at 58

3. **Relevant Context:**
   - Similar case showed customer benefited from waiting
   - Rule about DB transfer risks is highly relevant
   - Customer has expressed market volatility concerns

4. **Risks to Cover:**
   - Giving up DB guaranteed income if transferred
   - Tax implications of early withdrawal
   - Pension pot longevity if accessed too early
   - Need for FCA-regulated advice for DB transfers

5. **Language Adaptation:**
   - Medium literacy level - use clear explanations
   - Avoid jargon, explain terms like "drawdown" and "annuity"
   - Use concrete examples with their actual figures

6. **Understanding Checks:**
   - Ask if explanations are clear
   - Check they understand the DB pension value
   - Confirm they know when specialist advice is needed"""


def get_sample_demographics():
    """Get sample demographics for testing (non-fixture version)."""
    return CustomerDemographics(
        age=55,
        gender="female",
        location="London",
        employment_status="employed",
        financial_literacy="medium",
    )


def get_sample_financial():
    """Get sample financial situation for testing (non-fixture version)."""
    return FinancialSituation(
        annual_income=45000,
        total_assets=250000,
        total_debt=15000,
        dependents=0,
        risk_tolerance="medium",
    )


def get_sample_pension_pots():
    """Get sample pension pots for testing (non-fixture version)."""
    return [
        PensionPot(
            pot_id="pot_001",
            provider="Aviva",
            pot_type="defined_contribution",
            current_value=150000,
            projected_value=180000,
            age_accessible=55,
            is_db_scheme=False,
        ),
        PensionPot(
            pot_id="pot_002",
            provider="Standard Life",
            pot_type="defined_benefit",
            current_value=80000,
            projected_value=100000,
            age_accessible=60,
            is_db_scheme=True,
            db_guaranteed_amount=12000,
        ),
    ]


# ============================================================================
# Pytest Fixtures (wrap helper functions)
# ============================================================================


@pytest.fixture
def sample_advisor():
    """Sample advisor for testing."""
    return get_sample_advisor()


@pytest.fixture
def sample_customer():
    """Sample customer with full profile for testing."""
    return get_sample_customer()


@pytest.fixture
def minimal_customer():
    """Minimal customer profile for testing edge cases."""
    return CustomerProfile(
        customer_id=uuid4(),
        demographics=CustomerDemographics(
            age=45,
            gender="male",
            location="Manchester",
            employment_status="employed",
            financial_literacy="low",
        ),
        presenting_question="What are my pension options?",
    )


@pytest.fixture
def sample_context():
    """Sample context with cases, rules, and memories."""
    return get_sample_context()


@pytest.fixture
def empty_context():
    """Empty context for testing minimal scenarios."""
    return RetrievedContext(
        cases=[],
        rules=[],
        memories=[],
        fca_requirements="Stay within guidance boundary, avoid regulated advice",
    )


@pytest.fixture
def sample_conversation_history():
    """Sample conversation history for testing."""
    return get_sample_conversation_history()


@pytest.fixture
def empty_conversation_history():
    """Empty conversation history for testing initial scenarios."""
    return []


@pytest.fixture
def sample_guidance():
    """Sample guidance text for validation testing."""
    return get_sample_guidance()


@pytest.fixture
def sample_validation_result():
    """Sample validation result for testing."""
    return {
        "is_compliant": True,
        "confidence": 0.9,
        "issues": [],
        "reasoning": "Guidance stays within FCA boundaries, presents options without personal recommendation",
    }


@pytest.fixture
def sample_outcome():
    """Sample outcome result for testing."""
    return OutcomeResult(
        outcome_id=uuid4(),
        status=OutcomeStatus.SUCCESS,
        successful=True,
        customer_satisfaction=8.5,
        comprehension=8.0,
        goal_alignment=9.0,
        risks_identified=True,
        guidance_appropriate=True,
        fca_compliant=True,
        understanding_checked=True,
        signposted_when_needed=True,
        has_db_pension=True,
        db_warning_given=True,
        reasoning="Customer received clear, balanced guidance appropriate to their situation",
        issues=[],
        timestamp=datetime.now(),
    )


@pytest.fixture
def sample_reasoning():
    """Sample reasoning output for testing."""
    return get_sample_reasoning()
