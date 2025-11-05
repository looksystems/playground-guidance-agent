"""Integration tests for conversational quality tracking (Phase 2).

These tests verify:
- Conversational quality calculation in consultation flow
- Dialogue patterns storage
- Case extraction with dialogue techniques for high-quality consultations
- Reflection template with conversational effectiveness analysis
"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import patch, AsyncMock

from guidance_agent.core.database import Consultation, Case
from guidance_agent.learning.case_learning import (
    extract_case_from_consultation,
    _extract_dialogue_techniques,
)
from guidance_agent.core.types import (
    OutcomeResult,
    OutcomeStatus,
    CustomerProfile,
    CustomerDemographics,
)
from guidance_agent.advisor.agent import AdvisorAgent
from tests.fixtures.embeddings import EMBEDDING_DIMENSION as EMBEDDING_DIM


@pytest.fixture
def db_session(transactional_db_session):
    """Get a test database session with automatic rollback."""
    return transactional_db_session


@pytest.fixture
def sample_conversation_history():
    """Sample conversation with good conversational techniques."""
    return [
        {"role": "customer", "content": "I need help with my pension", "customer_name": "John"},
        {
            "role": "advisor",
            "content": "Hi John! Let me help you understand your pension options. First, can you tell me more about your current situation?",
        },
        {"role": "customer", "content": "I'm 55 and want to retire soon", "customer_name": "John"},
        {
            "role": "advisor",
            "content": "Thanks for sharing that, John. Let me break this down for you. At 55, you have several options. Here's what this means for your situation - would you like to explore each option?",
        },
        {"role": "customer", "content": "Yes please", "customer_name": "John"},
        {
            "role": "advisor",
            "content": "Let's look at the three main routes. One option is taking a 25% tax-free lump sum. Before we dive deeper, do you have any specific goals in mind?",
        },
    ]


@pytest.fixture
def high_quality_conversation():
    """Conversation with high quality score (>0.7)."""
    return [
        {"role": "customer", "content": "What are my pension options?", "customer_name": "Sarah"},
        {
            "role": "advisor",
            "content": "Hi Sarah! Let me help you understand your options. First, could you tell me about your current pension situation?",
        },
        {"role": "customer", "content": "I have £100k in my pension", "customer_name": "Sarah"},
        {
            "role": "advisor",
            "content": "Thanks Sarah. Here's what this means for you. Let me break this down into three main options. One approach is to take your 25% tax-free lump sum. Does this make sense so far?",
        },
        {"role": "customer", "content": "Yes, continue", "customer_name": "Sarah"},
        {
            "role": "advisor",
            "content": "Excellent, Sarah! Building on that, let's explore drawdown as another option. Some people find this gives them flexibility. What are your thoughts?",
        },
    ]


class TestConversationalQualityCalculation:
    """Test conversational quality calculation."""

    @pytest.mark.asyncio
    async def test_calculate_quality_with_good_conversation(self, sample_conversation_history):
        """Test quality calculation with a well-structured conversation."""
        # Create advisor agent
        from guidance_agent.core.types import AdvisorProfile

        advisor = AdvisorAgent(
            profile=AdvisorProfile(
                name="Sarah",
                description="FCA-compliant pension guidance specialist",
                specialization="Pension Guidance",
                experience_level="senior",
            )
        )

        # Calculate quality
        quality = await advisor._calculate_conversational_quality(
            conversation_history=sample_conversation_history,
            db=None,
        )

        # Should have reasonable quality score
        assert 0.0 <= quality <= 1.0
        assert quality > 0.5  # Good conversation should score above 0.5

    @pytest.mark.asyncio
    async def test_calculate_quality_with_high_quality_conversation(self, high_quality_conversation):
        """Test quality calculation with high-quality techniques."""
        from guidance_agent.core.types import AdvisorProfile

        advisor = AdvisorAgent(
            profile=AdvisorProfile(
                name="Sarah",
                description="FCA-compliant pension guidance specialist",
                specialization="Pension Guidance",
                experience_level="senior",
            )
        )

        quality = await advisor._calculate_conversational_quality(
            conversation_history=high_quality_conversation,
            db=None,
        )

        # High-quality conversation should score well
        assert quality > 0.6

    @pytest.mark.asyncio
    async def test_calculate_quality_empty_conversation(self):
        """Test quality calculation with empty conversation."""
        from guidance_agent.core.types import AdvisorProfile

        advisor = AdvisorAgent(
            profile=AdvisorProfile(
                name="Sarah",
                description="FCA-compliant pension guidance specialist",
                specialization="Pension Guidance",
                experience_level="senior",
            )
        )

        quality = await advisor._calculate_conversational_quality(
            conversation_history=[],
            db=None,
        )

        assert quality == 0.0


class TestDialoguePatternsStorage:
    """Test dialogue patterns are stored correctly."""

    def test_extract_dialogue_patterns_from_conversation(self, sample_conversation_history):
        """Test extraction of dialogue patterns."""
        # Extract advisor messages
        advisor_messages = [
            msg["content"]
            for msg in sample_conversation_history
            if msg.get("role") == "advisor"
        ]

        # Count signposting
        signpost_phrases = [
            "let me break this down",
            "let me help",
            "here's what",
            "let's look",
            "before we",
            "one option",
        ]
        signpost_count = sum(
            1
            for msg in advisor_messages
            if any(phrase in msg.lower() for phrase in signpost_phrases)
        )

        assert signpost_count > 0  # Should have signposting

        # Check personalization (name usage)
        customer_name = "John"
        name_usage = sum(1 for msg in advisor_messages if customer_name.lower() in msg.lower())
        assert name_usage > 0  # Should use customer's name

        # Check engagement (questions)
        question_count = sum(msg.count("?") for msg in advisor_messages)
        assert question_count > 0  # Should ask questions


class TestCaseExtractionWithDialogueTechniques:
    """Test case extraction captures dialogue techniques for high-quality consultations."""

    @patch("guidance_agent.learning.case_learning.embed")
    def test_extract_case_with_high_quality_includes_techniques(
        self, mock_embed, high_quality_conversation
    ):
        """Test case extraction includes dialogue techniques for quality > 0.7."""
        mock_embed.return_value = [0.1] * EMBEDDING_DIM

        customer = CustomerProfile(
            customer_id=uuid4(),
            demographics=CustomerDemographics(
                age=55,
                gender="female",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            presenting_question="What are my pension options?",
        )

        outcome = OutcomeResult(
            status=OutcomeStatus.SUCCESS,
            successful=True,
            customer_satisfaction=9.0,
            comprehension=9.0,
            goal_alignment=9.0,
        )

        # Extract case with high quality
        case_data = extract_case_from_consultation(
            customer_profile=customer,
            guidance_provided="Comprehensive pension guidance provided",
            outcome=outcome,
            conversational_quality=0.85,  # High quality
            conversation_history=high_quality_conversation,
        )

        # Should include dialogue techniques
        assert "dialogue_techniques" in case_data
        techniques = case_data["dialogue_techniques"]
        assert techniques["quality_score"] == 0.85
        assert "signposting_examples" in techniques
        assert "engagement_questions" in techniques
        assert "personalization_examples" in techniques

    @patch("guidance_agent.learning.case_learning.embed")
    def test_extract_case_with_low_quality_no_techniques(self, mock_embed):
        """Test case extraction doesn't include techniques for quality < 0.7."""
        mock_embed.return_value = [0.1] * EMBEDDING_DIM

        customer = CustomerProfile(
            customer_id=uuid4(),
            demographics=CustomerDemographics(
                age=55,
                gender="male",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            presenting_question="What are my pension options?",
        )

        outcome = OutcomeResult(
            status=OutcomeStatus.SUCCESS,
            successful=True,
            customer_satisfaction=7.0,
            comprehension=7.0,
            goal_alignment=7.0,
        )

        # Extract case with low quality
        case_data = extract_case_from_consultation(
            customer_profile=customer,
            guidance_provided="Basic pension guidance",
            outcome=outcome,
            conversational_quality=0.5,  # Low quality
            conversation_history=[
                {"role": "customer", "content": "Help me"},
                {"role": "advisor", "content": "Here's some info"},
            ],
        )

        # Should not include dialogue techniques
        assert "dialogue_techniques" not in case_data


class TestDialogueTechniqueExtraction:
    """Test dialogue technique extraction logic."""

    def test_extract_dialogue_techniques(self, high_quality_conversation):
        """Test extraction of specific dialogue techniques."""
        techniques = _extract_dialogue_techniques(high_quality_conversation, 0.85)

        assert techniques["quality_score"] == 0.85
        assert len(techniques["signposting_examples"]) > 0
        assert len(techniques["engagement_questions"]) > 0
        assert len(techniques["personalization_examples"]) > 0
        assert techniques["total_advisor_messages"] == 3
        assert techniques["avg_message_length"] > 0

    def test_extract_techniques_limits_examples(self):
        """Test that technique extraction limits examples to top 3/2."""
        long_conversation = [
            {"role": "advisor", "content": f"Let me explain point {i}. Does this make sense?"}
            for i in range(10)
        ]

        techniques = _extract_dialogue_techniques(long_conversation, 0.9)

        # Should limit to top 3 signposting examples
        assert len(techniques["signposting_examples"]) <= 3
        # Should limit to top 3 engagement questions
        assert len(techniques["engagement_questions"]) <= 3


class TestReflectionTemplateWithQuality:
    """Test reflection template includes conversational quality analysis."""

    def test_reflection_template_renders_with_quality(self):
        """Test that reflection template includes conversational analysis."""
        from guidance_agent.core.template_engine import render_template

        customer = CustomerProfile(
            customer_id=uuid4(),
            demographics=CustomerDemographics(
                age=55,
                gender="male",
                location="London",
                employment_status="employed",
                financial_literacy="low",
            ),
            presenting_question="What should I do with my pension?",
        )

        outcome = OutcomeResult(
            status=OutcomeStatus.FAILURE,
            successful=False,
            customer_satisfaction=3.0,
            comprehension=2.0,
            goal_alignment=3.0,
            issues=["Poor communication", "Too technical"],
            reasoning="Customer did not understand the guidance provided",
        )

        # Render with conversational quality
        prompt = render_template(
            "learning/reflection.jinja",
            customer=customer,
            guidance="Technical explanation of pension options with complex terminology",
            outcome=outcome,
            conversational_quality=0.3,  # Low quality
        )

        # Should include conversational analysis section
        assert "Conversational Effectiveness Analysis" in prompt
        assert "Language Naturalness" in prompt
        assert "Dialogue Flow" in prompt
        assert "Engagement" in prompt
        assert "Successful Techniques" in prompt
        assert "Areas for Improvement" in prompt
        assert "0.30 / 1.0" in prompt

    def test_reflection_template_without_quality(self):
        """Test that reflection template works without conversational quality."""
        from guidance_agent.core.template_engine import render_template

        customer = CustomerProfile(
            customer_id=uuid4(),
            demographics=CustomerDemographics(
                age=55,
                gender="male",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            presenting_question="What are my options?",
        )

        outcome = OutcomeResult(
            status=OutcomeStatus.FAILURE,
            successful=False,
            customer_satisfaction=4.0,
            comprehension=3.0,
            goal_alignment=4.0,
            issues=["Incomplete information"],
            reasoning="Guidance was incomplete",
        )

        # Render without conversational quality
        prompt = render_template(
            "learning/reflection.jinja",
            customer=customer,
            guidance="Incomplete pension guidance",
            outcome=outcome,
        )

        # Should not include conversational analysis section
        assert "Conversational Effectiveness Analysis" not in prompt
        assert "Language Naturalness" not in prompt
