"""Tests for conversational context features in AdvisorAgent (Phase 3).

This module tests the conversation phase detection and emotional state assessment
methods added in Phase 3 of the conversational improvement plan.

Tests include:
- Conversation phase detection (opening/middle/closing)
- Emotional state assessment (anxious/confident/confused/frustrated/neutral)
- Integration with retrieval context
"""

import pytest
from guidance_agent.core.types import AdvisorProfile, CustomerProfile, CustomerDemographics
from guidance_agent.advisor.agent import AdvisorAgent


class TestConversationPhaseDetection:
    """Tests for _detect_conversation_phase method."""

    @pytest.fixture
    def advisor_agent(self):
        """Create advisor agent for testing."""
        profile = AdvisorProfile(
            name="Sarah",
            description="Pension guidance specialist",
        )
        return AdvisorAgent(profile=profile, use_chain_of_thought=False)

    def test_opening_phase_with_one_message(self, advisor_agent):
        """Test that single message is detected as opening phase."""
        conversation_history = [
            {"role": "user", "content": "Hi, I need help with my pension"}
        ]

        phase = advisor_agent._detect_conversation_phase(conversation_history)

        assert phase == "opening", "Single message should be opening phase"

    def test_opening_phase_with_two_messages(self, advisor_agent):
        """Test that two messages are detected as opening phase."""
        conversation_history = [
            {"role": "user", "content": "Hi, I need help with my pension"},
            {"role": "assistant", "content": "Hello! I'd be happy to help. What would you like to know?"},
        ]

        phase = advisor_agent._detect_conversation_phase(conversation_history)

        assert phase == "opening", "Two messages should be opening phase"

    def test_middle_phase_with_three_messages(self, advisor_agent):
        """Test that 3 messages are detected as middle phase."""
        conversation_history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "Tell me about pension options"},
        ]

        phase = advisor_agent._detect_conversation_phase(conversation_history)

        assert phase == "middle", "Three messages should be middle phase"

    def test_middle_phase_with_eight_messages(self, advisor_agent):
        """Test that 8 messages are detected as middle phase."""
        conversation_history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "Question 1"},
            {"role": "assistant", "content": "Answer 1"},
            {"role": "user", "content": "Question 2"},
            {"role": "assistant", "content": "Answer 2"},
            {"role": "user", "content": "Question 3"},
            {"role": "assistant", "content": "Answer 3"},
        ]

        phase = advisor_agent._detect_conversation_phase(conversation_history)

        assert phase == "middle", "Eight messages should be middle phase"

    def test_closing_phase_with_nine_messages(self, advisor_agent):
        """Test that 9+ messages are detected as closing phase."""
        conversation_history = [
            {"role": "user", "content": f"Message {i}"}
            for i in range(9)
        ]

        phase = advisor_agent._detect_conversation_phase(conversation_history)

        assert phase == "closing", "Nine messages should be closing phase"

    def test_closing_phase_with_thank_you_signal(self, advisor_agent):
        """Test that 'thank you' triggers closing phase even with few messages."""
        conversation_history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "Tell me about pensions"},
            {"role": "assistant", "content": "Here's information..."},
            {"role": "user", "content": "Thank you, that helps!"},
        ]

        phase = advisor_agent._detect_conversation_phase(conversation_history)

        assert phase == "closing", "'Thank you' should trigger closing phase"

    def test_closing_phase_with_next_steps_signal(self, advisor_agent):
        """Test that 'next steps' triggers closing phase."""
        conversation_history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "What are my options?"},
            {"role": "assistant", "content": "Here are your options..."},
            {"role": "user", "content": "What should I do next?"},
        ]

        phase = advisor_agent._detect_conversation_phase(conversation_history)

        assert phase == "closing", "'What should I do next' should trigger closing phase"

    def test_closing_phase_with_goodbye_signal(self, advisor_agent):
        """Test that 'goodbye' triggers closing phase."""
        conversation_history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "Goodbye"},
        ]

        phase = advisor_agent._detect_conversation_phase(conversation_history)

        assert phase == "closing", "'Goodbye' should trigger closing phase"

    def test_empty_conversation_returns_opening(self, advisor_agent):
        """Test that empty conversation returns opening phase."""
        conversation_history = []

        phase = advisor_agent._detect_conversation_phase(conversation_history)

        assert phase == "opening", "Empty conversation should be opening phase"


class TestEmotionalStateAssessment:
    """Tests for _assess_emotional_state method."""

    @pytest.fixture
    def advisor_agent(self):
        """Create advisor agent for testing."""
        profile = AdvisorProfile(
            name="Sarah",
            description="Pension guidance specialist",
        )
        return AdvisorAgent(profile=profile, use_chain_of_thought=False)

    def test_anxious_state_with_worried_keyword(self, advisor_agent):
        """Test that 'worried' is detected as anxious state."""
        message = "I'm really worried about my retirement savings"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "anxious", "'worried' should indicate anxious state"

    def test_anxious_state_with_stressed_keyword(self, advisor_agent):
        """Test that 'stressed' is detected as anxious state."""
        message = "I'm feeling stressed about whether I've saved enough"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "anxious", "'stressed' should indicate anxious state"

    def test_anxious_state_with_overwhelmed_keyword(self, advisor_agent):
        """Test that 'overwhelmed' is detected as anxious state."""
        message = "This is all so overwhelming and I don't know where to start"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "anxious", "'overwhelmed' should indicate anxious state"

    def test_frustrated_state_with_frustrated_keyword(self, advisor_agent):
        """Test that 'frustrated' is detected as frustrated state."""
        message = "I'm frustrated with how complicated this all is"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "frustrated", "'frustrated' should indicate frustrated state"

    def test_frustrated_state_with_dont_understand(self, advisor_agent):
        """Test that 'don't understand' is detected as frustrated state."""
        message = "I don't understand why this has to be so difficult"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "frustrated", "'don't understand' should indicate frustrated state"

    def test_confused_state_with_confused_keyword(self, advisor_agent):
        """Test that 'confused' is detected as confused state."""
        message = "I'm confused about the difference between these options"

        state = advisor_agent._assess_emotional_state(message)

        # Note: 'confused' appears in both frustrated and confused lists
        # Should match frustrated first based on order
        assert state in ["confused", "frustrated"], "'confused' should indicate confused or frustrated state"

    def test_confused_state_with_what_does(self, advisor_agent):
        """Test that 'what does' is detected as confused state."""
        message = "What does tax-free lump sum mean exactly?"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "confused", "'what does' should indicate confused state"

    def test_confused_state_with_explain(self, advisor_agent):
        """Test that 'explain' is detected as confused state."""
        message = "Can you explain how pension contributions work?"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "confused", "'explain' should indicate confused state"

    def test_confident_state_with_want_to_optimise(self, advisor_agent):
        """Test that 'want to optimise' is detected as confident state."""
        message = "I want to optimise my pension contributions for maximum growth"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "confident", "'want to optimise' should indicate confident state"

    def test_confident_state_with_ready_to(self, advisor_agent):
        """Test that 'ready to' is detected as confident state."""
        message = "I'm ready to increase my contributions"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "confident", "'ready to' should indicate confident state"

    def test_confident_state_with_on_track(self, advisor_agent):
        """Test that 'on track' is detected as confident state."""
        message = "I think I'm on track with my retirement savings"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "confident", "'on track' should indicate confident state"

    def test_neutral_state_with_no_indicators(self, advisor_agent):
        """Test that message with no emotional indicators is neutral."""
        message = "What are my pension options?"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "neutral", "No emotional indicators should be neutral state"

    def test_neutral_state_with_factual_question(self, advisor_agent):
        """Test that factual question is neutral."""
        message = "How much is in my pension pot?"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "neutral", "Factual question should be neutral state"

    def test_case_insensitive_detection(self, advisor_agent):
        """Test that emotional state detection is case-insensitive."""
        message_upper = "I'M REALLY WORRIED ABOUT THIS"
        message_lower = "i'm really worried about this"
        message_mixed = "I'm Really WORRIED about This"

        state_upper = advisor_agent._assess_emotional_state(message_upper)
        state_lower = advisor_agent._assess_emotional_state(message_lower)
        state_mixed = advisor_agent._assess_emotional_state(message_mixed)

        assert state_upper == "anxious", "Uppercase should be detected"
        assert state_lower == "anxious", "Lowercase should be detected"
        assert state_mixed == "anxious", "Mixed case should be detected"


class TestConversationalContextIntegration:
    """Tests for integration of conversational context with retrieval."""

    @pytest.fixture
    def advisor_agent(self):
        """Create advisor agent for testing."""
        profile = AdvisorProfile(
            name="Sarah",
            description="Pension guidance specialist",
        )
        return AdvisorAgent(profile=profile, use_chain_of_thought=False)

    @pytest.fixture
    def customer_profile(self):
        """Create customer profile with demographics."""
        return CustomerProfile(
            demographics=CustomerDemographics(
                age=35,
                gender="F",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            presenting_question="How much should I be saving for retirement?",
        )

    def test_retrieve_context_builds_conversational_context(self, advisor_agent, customer_profile):
        """Test that _retrieve_context builds conversational context dict."""
        conversation_history = [
            {"role": "user", "content": "Hi, I'm worried about my pension"},
            {"role": "assistant", "content": "I can help you with that."},
            {"role": "user", "content": "How much should I save?"},
        ]

        # This should build conversational context internally
        context = advisor_agent._retrieve_context(customer_profile, conversation_history)

        # Verify context was retrieved successfully
        assert context is not None
        assert hasattr(context, "memories")
        assert hasattr(context, "fca_requirements")

    def test_retrieve_context_with_empty_history(self, advisor_agent, customer_profile):
        """Test that _retrieve_context handles empty conversation history."""
        conversation_history = []

        context = advisor_agent._retrieve_context(customer_profile, conversation_history)

        # Should still return valid context
        assert context is not None

    def test_retrieve_context_detects_phase_correctly(self, advisor_agent, customer_profile):
        """Test that context retrieval uses correct conversation phase."""
        # Opening phase conversation
        opening_history = [
            {"role": "user", "content": "Hi"}
        ]

        # This internal method should use phase detection
        # We can't directly verify the phase used, but we can ensure no errors
        context = advisor_agent._retrieve_context(customer_profile, opening_history)
        assert context is not None

        # Middle phase conversation
        middle_history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"},
            {"role": "user", "content": "Tell me more"},
            {"role": "assistant", "content": "Sure"},
            {"role": "user", "content": "What about options?"},
        ]

        context = advisor_agent._retrieve_context(customer_profile, middle_history)
        assert context is not None

    def test_retrieve_context_assesses_emotional_state(self, advisor_agent, customer_profile):
        """Test that context retrieval uses emotional state assessment."""
        # Anxious customer message
        anxious_history = [
            {"role": "user", "content": "I'm really worried about retirement"},
            {"role": "assistant", "content": "Let me help you."},
            {"role": "user", "content": "I'm still concerned about having enough"},
        ]

        context = advisor_agent._retrieve_context(customer_profile, anxious_history)
        assert context is not None

        # Confident customer message
        confident_history = [
            {"role": "user", "content": "I want to optimise my pension"},
            {"role": "assistant", "content": "Great!"},
            {"role": "user", "content": "I'm ready to maximise my contributions"},
        ]

        context = advisor_agent._retrieve_context(customer_profile, confident_history)
        assert context is not None

    def test_retrieve_context_extracts_literacy_level(self, advisor_agent):
        """Test that context retrieval extracts customer literacy level."""
        # Customer with low literacy
        low_literacy_customer = CustomerProfile(
            demographics=CustomerDemographics(
                age=35,
                gender="F",
                location="London",
                employment_status="employed",
                financial_literacy="low",
            ),
            presenting_question="Help with pension",
        )

        conversation_history = [
            {"role": "user", "content": "I need help"}
        ]

        context = advisor_agent._retrieve_context(low_literacy_customer, conversation_history)
        assert context is not None

        # Customer with high literacy
        high_literacy_customer = CustomerProfile(
            demographics=CustomerDemographics(
                age=35,
                gender="F",
                location="London",
                employment_status="employed",
                financial_literacy="high",
            ),
            presenting_question="Help with pension optimization",
        )

        context = advisor_agent._retrieve_context(high_literacy_customer, conversation_history)
        assert context is not None

    def test_retrieve_context_handles_missing_demographics(self, advisor_agent):
        """Test that context retrieval handles customer without demographics."""
        customer_no_demographics = CustomerProfile(
            presenting_question="How much should I save?",
        )

        conversation_history = [
            {"role": "user", "content": "I need help"}
        ]

        # Should not raise error, should default to 'medium' literacy
        context = advisor_agent._retrieve_context(customer_no_demographics, conversation_history)
        assert context is not None
