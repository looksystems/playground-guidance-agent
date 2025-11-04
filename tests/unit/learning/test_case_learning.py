"""Unit tests for learning from successful consultations."""

import os
import pytest
from unittest.mock import patch
from uuid import uuid4
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load .env to get correct EMBEDDING_DIMENSION
env_path = Path(__file__).parent.parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from guidance_agent.learning.case_learning import (
    learn_from_successful_consultation,
    extract_case_from_consultation,
    classify_task_type,
    summarize_customer_situation,
)
from guidance_agent.core.types import (
    OutcomeResult,
    OutcomeStatus,
    CustomerProfile,
    CustomerDemographics,
    FinancialSituation,
    PensionPot,
    TaskType,
)
from guidance_agent.retrieval.retriever import CaseBase
from guidance_agent.core.database import Case, get_session

# Get embedding dimension from environment (loaded from .env)
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIMENSION", "1536"))


@pytest.fixture
def db_session():
    """Get a test database session."""
    session = get_session()
    # Cleanup
    session.query(Case).delete()
    session.commit()

    yield session

    # Cleanup
    session.query(Case).delete()
    session.commit()
    session.close()


@pytest.fixture
def case_base(db_session):
    """Create a case base for testing."""
    return CaseBase(session=db_session)


@pytest.fixture
def successful_outcome():
    """Create a successful outcome for testing."""
    return OutcomeResult(
        outcome_id=uuid4(),
        status=OutcomeStatus.SUCCESS,
        successful=True,
        customer_satisfaction=9.0,
        comprehension=8.5,
        goal_alignment=9.0,
        risks_identified=True,
        guidance_appropriate=True,
        fca_compliant=True,
        understanding_checked=True,
        signposted_when_needed=True,
        has_db_pension=False,
        db_warning_given=False,
        reasoning="Customer was satisfied with guidance provided",
        issues=[],
        timestamp=datetime.now(),
    )


@pytest.fixture
def failed_outcome():
    """Create a failed outcome for testing."""
    return OutcomeResult(
        outcome_id=uuid4(),
        status=OutcomeStatus.FAILURE,
        successful=False,
        customer_satisfaction=3.0,
        comprehension=4.0,
        goal_alignment=2.0,
        risks_identified=False,
        guidance_appropriate=False,
        fca_compliant=True,
        understanding_checked=False,
        signposted_when_needed=False,
        reasoning="Customer left confused",
        issues=["Poor explanation of risks", "Did not check understanding"],
        timestamp=datetime.now(),
    )


@pytest.fixture
def sample_customer_profile():
    """Create a sample customer profile."""
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
        customer_id=uuid4(),
        demographics=demographics,
        financial=financial,
        pensions=[pension],
        goals="Planning retirement at age 60",
        presenting_question="What are my options for accessing my pension?",
    )


@pytest.fixture
def sample_guidance():
    """Sample guidance text."""
    return """You have several options for accessing your pension at 55:

1. Take up to 25% as a tax-free lump sum
2. Use pension drawdown for flexible withdrawals
3. Purchase an annuity for guaranteed income
4. Combination of the above

Given your situation, I'd recommend considering drawdown to maintain flexibility
while taking your 25% tax-free lump sum. This would give you control over your
retirement income while preserving capital.

Would you like me to explain any of these options in more detail?"""


@pytest.fixture
def sample_conversation():
    """Sample conversation history."""
    return [
        {"role": "customer", "content": "What are my options for accessing my pension?"},
        {
            "role": "advisor",
            "content": "Let me explain your pension access options...",
        },
        {"role": "customer", "content": "Can I take some money out now?"},
        {
            "role": "advisor",
            "content": "Yes, you can access your pension from age 55...",
        },
    ]


class TestClassifyTaskType:
    """Tests for classify_task_type function."""

    def test_classify_withdrawal_options(self):
        """Test classification of withdrawal options questions."""
        question = "What are my options for accessing my pension?"
        task_type = classify_task_type(question)
        assert task_type == TaskType.WITHDRAWAL_OPTIONS

    def test_classify_pension_transfer(self):
        """Test classification of pension transfer questions."""
        question = "Should I transfer my pension?"
        task_type = classify_task_type(question)
        assert task_type == TaskType.PENSION_TRANSFER

    def test_classify_retirement_planning(self):
        """Test classification of retirement planning questions."""
        question = "How much will I need for retirement?"
        task_type = classify_task_type(question)
        assert task_type == TaskType.RETIREMENT_PLANNING

    def test_classify_tax_implications(self):
        """Test classification of tax questions."""
        question = "How much tax will I pay on pension withdrawals?"
        task_type = classify_task_type(question)
        assert task_type == TaskType.TAX_IMPLICATIONS

    def test_classify_general_inquiry(self):
        """Test classification of general questions."""
        question = "Tell me about pensions"
        task_type = classify_task_type(question)
        assert task_type == TaskType.GENERAL_INQUIRY


class TestSummarizeCustomerSituation:
    """Tests for summarize_customer_situation function."""

    def test_summarize_basic_profile(self, sample_customer_profile):
        """Test summarization of customer profile."""
        summary = summarize_customer_situation(sample_customer_profile)

        assert isinstance(summary, str)
        assert len(summary) > 0
        # Should include key demographic info
        assert "55" in summary or "age 55" in summary.lower()
        # Should include pension value
        assert "150" in summary or "£150" in summary

    def test_summarize_includes_goals(self, sample_customer_profile):
        """Test that summary includes customer goals."""
        summary = summarize_customer_situation(sample_customer_profile)
        assert "retirement" in summary.lower()

    def test_summarize_includes_financial_literacy(self, sample_customer_profile):
        """Test that summary includes financial literacy level."""
        summary = summarize_customer_situation(sample_customer_profile)
        assert "medium" in summary.lower() or "moderate" in summary.lower()


class TestExtractCaseFromConsultation:
    """Tests for extract_case_from_consultation function."""

    @patch("guidance_agent.learning.case_learning.embed")
    def test_extract_case_basic(
        self, mock_embed, sample_customer_profile, sample_guidance, successful_outcome
    ):
        """Test basic case extraction."""
        # Mock embedding
        mock_embed.return_value = [0.1] * EMBEDDING_DIM

        case_data = extract_case_from_consultation(
            customer_profile=sample_customer_profile,
            guidance_provided=sample_guidance,
            outcome=successful_outcome,
        )

        assert "id" in case_data
        assert "task_type" in case_data
        assert "customer_situation" in case_data
        assert "guidance_provided" in case_data
        assert "outcome" in case_data
        assert "embedding" in case_data

    @patch("guidance_agent.learning.case_learning.embed")
    def test_extract_case_has_valid_task_type(
        self, mock_embed, sample_customer_profile, sample_guidance, successful_outcome
    ):
        """Test that extracted case has valid task type."""
        # Mock embedding
        mock_embed.return_value = [0.1] * EMBEDDING_DIM

        case_data = extract_case_from_consultation(
            customer_profile=sample_customer_profile,
            guidance_provided=sample_guidance,
            outcome=successful_outcome,
        )

        task_type = case_data["task_type"]
        assert task_type in [t.value for t in TaskType]

    @patch("guidance_agent.learning.case_learning.embed")
    def test_extract_case_has_embedding(
        self, mock_embed, sample_customer_profile, sample_guidance, successful_outcome
    ):
        """Test that extracted case has embedding."""
        # Mock embedding
        mock_embed.return_value = [0.1] * EMBEDDING_DIM

        case_data = extract_case_from_consultation(
            customer_profile=sample_customer_profile,
            guidance_provided=sample_guidance,
            outcome=successful_outcome,
        )

        embedding = case_data["embedding"]
        assert isinstance(embedding, list)
        assert len(embedding) == EMBEDDING_DIM
        assert all(isinstance(x, float) for x in embedding)

    @patch("guidance_agent.learning.case_learning.embed")
    def test_extract_case_preserves_outcome(
        self, mock_embed, sample_customer_profile, sample_guidance, successful_outcome
    ):
        """Test that extracted case preserves outcome details."""
        # Mock embedding
        mock_embed.return_value = [0.1] * EMBEDDING_DIM

        case_data = extract_case_from_consultation(
            customer_profile=sample_customer_profile,
            guidance_provided=sample_guidance,
            outcome=successful_outcome,
        )

        outcome_dict = case_data["outcome"]
        assert outcome_dict["successful"] is True
        assert outcome_dict["customer_satisfaction"] == 9.0


class TestLearnFromSuccessfulConsultation:
    """Tests for learn_from_successful_consultation function."""

    @patch("guidance_agent.learning.case_learning.embed")
    def test_learn_from_success_adds_case(
        self,
        mock_embed,
        case_base,
        sample_customer_profile,
        sample_guidance,
        successful_outcome,
        db_session,
    ):
        """Test that successful consultation adds case to case base."""
        # Mock embedding
        mock_embed.return_value = [0.1] * EMBEDDING_DIM

        initial_count = db_session.query(Case).count()

        learn_from_successful_consultation(
            case_base=case_base,
            customer_profile=sample_customer_profile,
            guidance_provided=sample_guidance,
            outcome=successful_outcome,
        )

        # Should have added one case
        final_count = db_session.query(Case).count()
        assert final_count == initial_count + 1

    @patch("guidance_agent.learning.case_learning.embed")
    def test_learn_from_success_stores_correct_data(
        self,
        mock_embed,
        case_base,
        sample_customer_profile,
        sample_guidance,
        successful_outcome,
        db_session,
    ):
        """Test that stored case has correct data."""
        # Mock embedding
        mock_embed.return_value = [0.1] * EMBEDDING_DIM

        learn_from_successful_consultation(
            case_base=case_base,
            customer_profile=sample_customer_profile,
            guidance_provided=sample_guidance,
            outcome=successful_outcome,
        )

        # Retrieve the stored case
        case = db_session.query(Case).first()
        assert case is not None
        assert case.task_type in [t.value for t in TaskType]
        assert len(case.customer_situation) > 0
        assert case.guidance_provided == sample_guidance

    def test_learn_from_failure_ignores(
        self, case_base, sample_customer_profile, sample_guidance, failed_outcome, db_session
    ):
        """Test that failed consultations are not added to case base."""
        initial_count = db_session.query(Case).count()

        learn_from_successful_consultation(
            case_base=case_base,
            customer_profile=sample_customer_profile,
            guidance_provided=sample_guidance,
            outcome=failed_outcome,
        )

        # Should not have added any cases
        final_count = db_session.query(Case).count()
        assert final_count == initial_count

    @patch("guidance_agent.learning.case_learning.embed")
    def test_learn_multiple_successful_consultations(
        self, mock_embed, case_base, sample_customer_profile, sample_guidance, successful_outcome, db_session
    ):
        """Test learning from multiple successful consultations."""
        # Mock embedding
        mock_embed.return_value = [0.1] * EMBEDDING_DIM

        # Add three successful consultations
        for i in range(3):
            learn_from_successful_consultation(
                case_base=case_base,
                customer_profile=sample_customer_profile,
                guidance_provided=f"{sample_guidance} (consultation {i})",
                outcome=successful_outcome,
            )

        # Should have added three cases
        case_count = db_session.query(Case).count()
        assert case_count == 3

    @patch("guidance_agent.learning.case_learning.embed")
    def test_learn_from_partial_success(
        self, mock_embed, case_base, sample_customer_profile, sample_guidance, db_session
    ):
        """Test learning from partially successful consultation."""
        # Mock embedding
        mock_embed.return_value = [0.1] * EMBEDDING_DIM

        partial_success = OutcomeResult(
            status=OutcomeStatus.PARTIAL_SUCCESS,
            successful=True,  # Still counts as success
            customer_satisfaction=6.5,
            comprehension=7.0,
            goal_alignment=6.0,
        )

        learn_from_successful_consultation(
            case_base=case_base,
            customer_profile=sample_customer_profile,
            guidance_provided=sample_guidance,
            outcome=partial_success,
        )

        # Should still add case for partial success
        case_count = db_session.query(Case).count()
        assert case_count == 1
