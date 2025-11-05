"""Tests for conversational quality calculation in AdvisorAgent.

This module tests the _calculate_conversational_quality() method that evaluates
the naturalness and engagement of advisor responses based on:
- Language variety (30% weight) - avoids repetitive phrases
- Signposting/transitions (30% weight) - uses guiding language
- Personalization (20% weight) - uses customer name
- Engagement questions (20% weight) - asks questions

All tests follow TDD approach: written BEFORE implementation.
"""

import pytest
from unittest.mock import Mock, patch
from guidance_agent.core.types import AdvisorProfile
from guidance_agent.advisor.agent import AdvisorAgent


class TestConversationalQualityCalculation:
    """Tests for _calculate_conversational_quality method."""

    @pytest.fixture
    def advisor_agent(self):
        """Create advisor agent for testing."""
        profile = AdvisorProfile(
            name="Sarah",
            description="Pension guidance specialist",
        )
        return AdvisorAgent(profile=profile, use_chain_of_thought=False)

    @pytest.mark.asyncio
    async def test_high_quality_conversation_scores_above_0_7(self, advisor_agent):
        """Test that high-quality conversation (varied, personalized, engaging) scores > 0.7."""
        # High quality: varied language, signposting, personalization, questions
        conversation_history = [
            {
                "role": "user",
                "content": "My name is John, I need help with my pension",
                "customer_name": "John",
            },
            {
                "role": "assistant",
                "content": "Great to meet you, John! Let me break this down for you. "
                "First, let's explore your current situation. What would be most helpful to discuss?",
            },
            {"role": "user", "content": "My pension amount"},
            {
                "role": "assistant",
                "content": "Perfect, John. You have £20,000 at age 30. "
                "Here's a helpful way to think about retirement planning. "
                "Would you like me to walk you through the details?",
            },
            {"role": "user", "content": "Yes please"},
            {
                "role": "assistant",
                "content": "Excellent, John! Building on that, let's look at where you could be "
                "by retirement age. One option to explore is increasing your contributions. "
                "Does that make sense so far?",
            },
        ]

        quality_score = await advisor_agent._calculate_conversational_quality(
            conversation_history, db=None
        )

        # High quality should score above 0.7
        assert quality_score > 0.7, f"High-quality conversation should score >0.7, got {quality_score}"
        assert 0.0 <= quality_score <= 1.0, "Score must be between 0 and 1"

    @pytest.mark.asyncio
    async def test_low_quality_conversation_scores_below_0_5(self, advisor_agent):
        """Test that low-quality conversation (repetitive, impersonal, robotic) scores < 0.5."""
        # Low quality: repetitive phrases, no personalization, no questions, no signposting
        conversation_history = [
            {"role": "user", "content": "Help me with pensions", "customer_name": "Sarah"},
            {
                "role": "assistant",
                "content": "Based on the information provided, you could consider increasing contributions. "
                "You could also consider consolidating pensions. The pros and cons are that "
                "you could consider reviewing annually.",
            },
            {"role": "user", "content": "What else"},
            {
                "role": "assistant",
                "content": "Based on your situation, you could consider seeking professional advice. "
                "The pros and cons are clear. You could consider the tax implications. "
                "Based on regulations, you could consider next steps.",
            },
            {"role": "user", "content": "Ok"},
            {
                "role": "assistant",
                "content": "You could consider reviewing your pension pot value. The pros and cons "
                "are important. Based on your age, you could consider contribution levels.",
            },
        ]

        quality_score = await advisor_agent._calculate_conversational_quality(
            conversation_history, db=None
        )

        # Low quality should score below 0.5
        assert quality_score < 0.5, f"Low-quality conversation should score <0.5, got {quality_score}"
        assert 0.0 <= quality_score <= 1.0, "Score must be between 0 and 1"

    @pytest.mark.asyncio
    async def test_medium_quality_conversation_scores_between_0_4_and_0_7(
        self, advisor_agent
    ):
        """Test that medium-quality conversation scores between 0.4 and 0.7."""
        # Medium quality: some variety, minimal personalization, few questions
        conversation_history = [
            {"role": "user", "content": "Tell me about pensions", "customer_name": "Mike"},
            {
                "role": "assistant",
                "content": "Pensions are retirement savings that build up over your working life. "
                "There are different types available.",
            },
            {"role": "user", "content": "What types"},
            {
                "role": "assistant",
                "content": "The main types are defined contribution and defined benefit pensions. "
                "Each has different features. Let me explain the key differences.",
            },
            {"role": "user", "content": "Which is better"},
            {
                "role": "assistant",
                "content": "It depends on your circumstances. Defined benefit provides guaranteed income. "
                "Defined contribution gives you more flexibility.",
            },
        ]

        quality_score = await advisor_agent._calculate_conversational_quality(
            conversation_history, db=None
        )

        # Medium quality should score between 0.4 and 0.7
        assert (
            0.4 <= quality_score <= 0.7
        ), f"Medium-quality conversation should score 0.4-0.7, got {quality_score}"

    @pytest.mark.asyncio
    async def test_empty_conversation_returns_zero_score(self, advisor_agent):
        """Test that empty conversation history returns 0.0 score."""
        conversation_history = []

        quality_score = await advisor_agent._calculate_conversational_quality(
            conversation_history, db=None
        )

        assert quality_score == 0.0, "Empty conversation should return 0.0 score"

    @pytest.mark.asyncio
    async def test_single_message_conversation(self, advisor_agent):
        """Test conversational quality with only one advisor message."""
        conversation_history = [
            {"role": "user", "content": "Hello", "customer_name": "Emma"},
            {
                "role": "assistant",
                "content": "Hello Emma! How can I help you with your pension today?",
            },
        ]

        quality_score = await advisor_agent._calculate_conversational_quality(
            conversation_history, db=None
        )

        # Should calculate a valid score even with one message
        assert 0.0 <= quality_score <= 1.0, "Single message should return valid score"

    @pytest.mark.asyncio
    async def test_conversation_without_customer_name(self, advisor_agent):
        """Test that conversation without customer name still calculates quality."""
        conversation_history = [
            {"role": "user", "content": "Help me"},
            {
                "role": "assistant",
                "content": "Let me break this down for you. First, let's explore your options. "
                "Some people find it helpful to consider different approaches. What matters most to you?",
            },
            {"role": "user", "content": "Saving more"},
            {
                "role": "assistant",
                "content": "Building on that, here's what you could do. One path is increasing your "
                "monthly contributions. Does that make sense?",
            },
        ]

        quality_score = await advisor_agent._calculate_conversational_quality(
            conversation_history, db=None
        )

        # Should score well on variety, signposting, engagement but miss personalization
        # (30% variety + 30% signposting + 20% engagement = 80% max without personalization)
        assert 0.0 <= quality_score <= 1.0, "Should calculate valid score without name"
        # Likely in medium-high range due to good signposting and engagement
        assert quality_score > 0.4, "Should still score reasonably without personalization"

    @pytest.mark.asyncio
    async def test_language_variety_component(self, advisor_agent):
        """Test that language variety (avoiding repetition) is scored correctly."""
        # Very repetitive language - should score low on variety
        repetitive_history = [
            {"role": "user", "content": "Help"},
            {
                "role": "assistant",
                "content": "You could consider option A. Based on this, you could consider option B. "
                "The pros and cons are that you could consider option C.",
            },
            {"role": "user", "content": "More"},
            {
                "role": "assistant",
                "content": "Based on your situation, you could consider reviewing annually. "
                "The pros and cons show you could consider alternatives.",
            },
        ]

        # Varied language - should score high on variety
        varied_history = [
            {"role": "user", "content": "Help"},
            {
                "role": "assistant",
                "content": "Let me explore some options with you. One path to take is reviewing "
                "your contributions. Another approach is consolidation.",
            },
            {"role": "user", "content": "More"},
            {
                "role": "assistant",
                "content": "Here's how to think about it. Some people find it helpful to start with "
                "their current situation. It's worth looking into your pension providers.",
            },
        ]

        repetitive_score = await advisor_agent._calculate_conversational_quality(
            repetitive_history, db=None
        )
        varied_score = await advisor_agent._calculate_conversational_quality(
            varied_history, db=None
        )

        # Varied language should score higher than repetitive
        assert varied_score > repetitive_score, (
            f"Varied language ({varied_score}) should score higher than "
            f"repetitive ({repetitive_score})"
        )

    @pytest.mark.asyncio
    async def test_signposting_usage_component(self, advisor_agent):
        """Test that signposting and transition phrases are scored correctly."""
        # With signposting phrases
        signposted_history = [
            {"role": "user", "content": "Explain pensions"},
            {
                "role": "assistant",
                "content": "Let me break this down for you. First, let's look at the basics. "
                "Before we dive into details, here's the overview.",
            },
            {"role": "user", "content": "Continue"},
            {
                "role": "assistant",
                "content": "Building on that, here's what this means for you. Let's explore the options together.",
            },
        ]

        # Without signposting phrases
        unsignposted_history = [
            {"role": "user", "content": "Explain pensions"},
            {
                "role": "assistant",
                "content": "Pensions are retirement savings. They accumulate over time. "
                "There are different types.",
            },
            {"role": "user", "content": "Continue"},
            {
                "role": "assistant",
                "content": "You need to contribute regularly. The money grows with investment returns. "
                "You can access it at retirement age.",
            },
        ]

        signposted_score = await advisor_agent._calculate_conversational_quality(
            signposted_history, db=None
        )
        unsignposted_score = await advisor_agent._calculate_conversational_quality(
            unsignposted_history, db=None
        )

        # Signposted conversation should score higher
        assert signposted_score > unsignposted_score, (
            f"Signposted conversation ({signposted_score}) should score higher than "
            f"unsignposted ({unsignposted_score})"
        )

    @pytest.mark.asyncio
    async def test_personalization_component(self, advisor_agent):
        """Test that customer name usage (personalization) is scored correctly."""
        # With personalization (name usage)
        personalized_history = [
            {"role": "user", "content": "I need help", "customer_name": "Alice"},
            {
                "role": "assistant",
                "content": "Of course, Alice! Let me help you with that. Alice, here's what I suggest.",
            },
            {"role": "user", "content": "Tell me more"},
            {
                "role": "assistant",
                "content": "Certainly, Alice. Based on what you've told me, Alice, I can guide you through this.",
            },
        ]

        # Without personalization (no name usage)
        impersonal_history = [
            {"role": "user", "content": "I need help", "customer_name": "Alice"},
            {
                "role": "assistant",
                "content": "Of course! Let me help you with that. Here's what I suggest.",
            },
            {"role": "user", "content": "Tell me more"},
            {
                "role": "assistant",
                "content": "Certainly. Based on what you've told me, I can guide you through this.",
            },
        ]

        personalized_score = await advisor_agent._calculate_conversational_quality(
            personalized_history, db=None
        )
        impersonal_score = await advisor_agent._calculate_conversational_quality(
            impersonal_history, db=None
        )

        # Personalized conversation should score higher
        assert personalized_score > impersonal_score, (
            f"Personalized conversation ({personalized_score}) should score higher than "
            f"impersonal ({impersonal_score})"
        )

    @pytest.mark.asyncio
    async def test_engagement_questions_component(self, advisor_agent):
        """Test that engagement through questions is scored correctly."""
        # High engagement (many questions)
        engaging_history = [
            {"role": "user", "content": "Help me"},
            {
                "role": "assistant",
                "content": "I'd be happy to help! What specific aspect concerns you? "
                "Have you thought about your retirement timeline? Would you like to explore options together?",
            },
            {"role": "user", "content": "Yes"},
            {
                "role": "assistant",
                "content": "Great! What's your current pension value? When do you plan to retire? "
                "Does that make sense so far?",
            },
        ]

        # Low engagement (no questions)
        unengaging_history = [
            {"role": "user", "content": "Help me"},
            {
                "role": "assistant",
                "content": "I can help you with pensions. Pensions provide retirement income. "
                "You should review your pension regularly.",
            },
            {"role": "user", "content": "Tell me more"},
            {
                "role": "assistant",
                "content": "Pensions accumulate over time. Contributions are invested. "
                "You can access funds at retirement age.",
            },
        ]

        engaging_score = await advisor_agent._calculate_conversational_quality(
            engaging_history, db=None
        )
        unengaging_score = await advisor_agent._calculate_conversational_quality(
            unengaging_history, db=None
        )

        # Engaging conversation should score higher
        assert engaging_score > unengaging_score, (
            f"Engaging conversation ({engaging_score}) should score higher than "
            f"unengaging ({unengaging_score})"
        )

    @pytest.mark.asyncio
    async def test_conversation_with_only_user_messages(self, advisor_agent):
        """Test that conversation with only user messages returns 0.0."""
        conversation_history = [
            {"role": "user", "content": "Hello"},
            {"role": "user", "content": "Help me"},
            {"role": "user", "content": "Are you there?"},
        ]

        quality_score = await advisor_agent._calculate_conversational_quality(
            conversation_history, db=None
        )

        # No advisor messages means no conversational quality to measure
        assert quality_score == 0.0, "Conversation with only user messages should return 0.0"

    @pytest.mark.asyncio
    async def test_score_is_always_between_0_and_1(self, advisor_agent):
        """Test that score is always normalized between 0.0 and 1.0."""
        # Test various conversation types
        test_conversations = [
            # Minimal conversation
            [
                {"role": "user", "content": "Hi"},
                {"role": "assistant", "content": "Hello"},
            ],
            # Very high quality
            [
                {"role": "user", "content": "Help", "customer_name": "Bob"},
                {
                    "role": "assistant",
                    "content": "Hi Bob! Let me break this down. First, let's explore options. "
                    "What would help most? Building on your question, Bob, here's what matters. "
                    "Does that make sense?",
                },
            ],
            # Very low quality
            [
                {"role": "user", "content": "Help"},
                {
                    "role": "assistant",
                    "content": "Based on information, you could consider options. "
                    "You could consider alternatives. The pros and cons are you could consider reviewing.",
                },
            ],
        ]

        for conversation in test_conversations:
            quality_score = await advisor_agent._calculate_conversational_quality(
                conversation, db=None
            )
            assert 0.0 <= quality_score <= 1.0, (
                f"Score must be between 0.0 and 1.0, got {quality_score}"
            )

    @pytest.mark.asyncio
    async def test_mixed_quality_indicators(self, advisor_agent):
        """Test conversation with mixed quality indicators (some good, some bad)."""
        # Good: signposting, engagement questions
        # Bad: repetitive language, no personalization
        mixed_history = [
            {"role": "user", "content": "Pension help", "customer_name": "David"},
            {
                "role": "assistant",
                "content": "Let me break this down for you. Based on information provided, "
                "you could consider your options. You could also consider alternatives. "
                "Does that help?",
            },
            {"role": "user", "content": "Yes"},
            {
                "role": "assistant",
                "content": "Here's what this means. Based on your situation, you could consider "
                "reviewing annually. The pros and cons are clear. What do you think?",
            },
        ]

        quality_score = await advisor_agent._calculate_conversational_quality(
            mixed_history, db=None
        )

        # Should be in medium range (some positives, some negatives)
        assert 0.3 <= quality_score <= 0.7, (
            f"Mixed quality should score in medium range, got {quality_score}"
        )

    @pytest.mark.asyncio
    async def test_realistic_example_from_spec(self, advisor_agent):
        """Test realistic example from the conversational improvement plan spec."""
        # Based on the "Desired Style Example" from the spec (updated for FCA neutrality)
        realistic_high_quality = [
            {
                "role": "user",
                "content": "Am I saving enough for retirement? I'm 30 and have £15,000 in NEST",
                "customer_name": "Sarah",
            },
            {
                "role": "assistant",
                "content": "Great question, and I'm glad you're thinking about this now! "
                "You have £15,000 in your NEST pension at 30, Sarah. "
                "Here's a helpful way to think about it: many people aim to save roughly half "
                "their age as a percentage of their salary (including what your employer puts in). "
                "For you at 30, that would be around 15%.\n\n"
                "Would you like to explore what this means for your retirement planning? "
                "We could work through the numbers together.",
            },
        ]

        # Based on the "Current Style Example" (more robotic)
        realistic_low_quality = [
            {
                "role": "user",
                "content": "Am I saving enough for retirement? I'm 30 and have £15,000 in NEST",
                "customer_name": "Sarah",
            },
            {
                "role": "assistant",
                "content": "You have £15,000 in your pension at age 30. "
                "The general rule of thumb is to save about half your age as a percentage of "
                "your salary. At 30, that would be 15% including employer contributions. "
                "Would you like to explore what this means for your situation?",
            },
        ]

        high_score = await advisor_agent._calculate_conversational_quality(
            realistic_high_quality, db=None
        )
        low_score = await advisor_agent._calculate_conversational_quality(
            realistic_low_quality, db=None
        )

        # High quality example should score significantly better
        assert high_score > low_score, (
            f"Spec's desired style ({high_score}) should score higher than "
            f"current robotic style ({low_score})"
        )
        assert high_score > 0.6, "Desired conversational style should score >0.6"

    @pytest.mark.asyncio
    async def test_weights_are_correctly_applied(self, advisor_agent):
        """Test that component weights (variety 30%, signposting 30%, personalization 20%, engagement 20%) work."""
        # Perfect on all components except personalization (no name)
        no_personalization = [
            {"role": "user", "content": "Help"},
            {
                "role": "assistant",
                "content": "Let me break this down. First, let's explore your options. "
                "Some people find it helpful to think differently. One approach is planning ahead. "
                "What would be most useful? Does that make sense? Would you like me to continue?",
            },
        ]

        # Perfect on all components except variety (very repetitive)
        no_variety = [
            {"role": "user", "content": "Help", "customer_name": "Tom"},
            {
                "role": "assistant",
                "content": "Let me help you, Tom. Based on information, you could consider options. "
                "Based on your situation, you could consider alternatives, Tom. The pros and cons "
                "are that you could consider reviewing, Tom. Does that help? What do you think?",
            },
        ]

        no_personalization_score = await advisor_agent._calculate_conversational_quality(
            no_personalization, db=None
        )
        no_variety_score = await advisor_agent._calculate_conversational_quality(
            no_variety, db=None
        )

        # Both should score in similar range (missing 20-30% of total)
        # But no_personalization should be slightly higher (only missing 20% vs 30%)
        assert 0.6 <= no_personalization_score <= 1.0, (
            "Missing only personalization (20%) should score 0.6-1.0"
        )
        assert 0.5 <= no_variety_score <= 0.9, (
            "Missing variety (30%) should score 0.5-0.9"
        )
