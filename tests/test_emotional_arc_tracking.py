"""
TDD tests for emotional arc tracking improvements - Section 3 of british-english-conversational-improvements.md

Tests verify that:
1. advisor agent passes FULL conversation context (not just last message) to emotional state assessment
2. _assess_emotional_state() receives all customer messages joined with "\n"
3. Emotional arc is tracked across multi-turn conversations
4. Emotional evolution is detected (e.g., anxious → confident)

STATUS: These tests are written BEFORE implementation (TDD approach).
EXPECTED: Many tests will FAIL initially since the code still uses `last_customer_message`.
"""

import pytest
from unittest.mock import patch, MagicMock
from guidance_agent.advisor.agent import AdvisorAgent
from guidance_agent.core.types import (
    AdvisorProfile,
    CustomerProfile,
    CustomerDemographics,
    FinancialSituation,
    PensionPot,
    RetrievedContext,
)


@pytest.fixture
def advisor_agent():
    """Create an advisor agent instance for testing."""
    profile = AdvisorProfile(
        name="Sarah",
        description="FCA-compliant pension guidance specialist",
        specialization="Pension Guidance",
        experience_level="senior",
    )
    return AdvisorAgent(profile=profile, session=None)


@pytest.fixture
def sample_customer():
    """Create a sample customer profile."""
    return CustomerProfile(
        demographics=CustomerDemographics(
            age=45,
            gender="M",
            location="Manchester",
            employment_status="employed",
            financial_literacy="medium",
        ),
        financial=FinancialSituation(
            annual_income=55000,
            total_assets=150000,
            total_debt=10000,
            dependents=2,
            risk_tolerance="medium",
        ),
        pensions=[
            PensionPot(
                pot_id="aviva-001",
                provider="Aviva",
                pot_type="defined_contribution",
                current_value=150000,
                projected_value=320000,
                age_accessible=55,
                is_db_scheme=False,
            )
        ],
        goals="Understand retirement options",
        presenting_question="What should I do with my pension?",
    )


class TestFullConversationContextPassed:
    """Test that _retrieve_context passes full conversation to emotional assessment."""

    def test_assess_emotional_state_receives_all_customer_messages(
        self, advisor_agent, sample_customer
    ):
        """Test that _assess_emotional_state receives ALL customer messages joined with newlines.

        EXPECTED TO FAIL: Current implementation only passes last_customer_message.
        After fix: Should pass full_customer_context with all messages.
        """
        # Multi-turn conversation
        conversation_history = [
            {"role": "user", "content": "I'm really worried about my pension savings"},
            {"role": "assistant", "content": "I understand. Let me help you."},
            {"role": "user", "content": "I don't know if I've saved enough"},
            {"role": "assistant", "content": "Let's look at your situation."},
            {"role": "user", "content": "Actually, now that I think about it, maybe I'm doing okay"},
        ]

        # Patch _assess_emotional_state to capture what it receives
        with patch.object(
            advisor_agent, "_assess_emotional_state", return_value="neutral"
        ) as mock_assess:
            # Call _retrieve_context
            advisor_agent._retrieve_context(sample_customer, conversation_history)

            # Verify _assess_emotional_state was called
            assert mock_assess.called, "_assess_emotional_state should be called"

            # CRITICAL: Should receive ALL customer messages joined with "\n"
            expected_full_context = "\n".join([
                "I'm really worried about my pension savings",
                "I don't know if I've saved enough",
                "Actually, now that I think about it, maybe I'm doing okay",
            ])

            actual_call_arg = mock_assess.call_args[0][0]

            # THIS TEST WILL FAIL until implementation is fixed
            assert actual_call_arg == expected_full_context, (
                f"Expected full conversation context, but got: {actual_call_arg}"
            )

    def test_empty_conversation_history(self, advisor_agent, sample_customer):
        """Test that empty conversation history is handled gracefully."""
        conversation_history = []

        with patch.object(
            advisor_agent, "_assess_emotional_state", return_value="neutral"
        ) as mock_assess:
            advisor_agent._retrieve_context(sample_customer, conversation_history)

            # Should call with empty string
            mock_assess.assert_called_once_with("")

    def test_single_message_conversation(self, advisor_agent, sample_customer):
        """Test that single message is passed correctly (no join needed)."""
        conversation_history = [
            {"role": "user", "content": "I need help with my pension"},
        ]

        with patch.object(
            advisor_agent, "_assess_emotional_state", return_value="neutral"
        ) as mock_assess:
            advisor_agent._retrieve_context(sample_customer, conversation_history)

            # Should call with the single message
            mock_assess.assert_called_once_with("I need help with my pension")

    def test_filters_only_user_messages(self, advisor_agent, sample_customer):
        """Test that only user/customer messages are included, not assistant messages."""
        conversation_history = [
            {"role": "user", "content": "First customer message"},
            {"role": "assistant", "content": "First advisor response"},
            {"role": "user", "content": "Second customer message"},
            {"role": "advisor", "content": "Second advisor response"},  # Different role name
            {"role": "user", "content": "Third customer message"},
        ]

        with patch.object(
            advisor_agent, "_assess_emotional_state", return_value="neutral"
        ) as mock_assess:
            advisor_agent._retrieve_context(sample_customer, conversation_history)

            expected_context = "\n".join([
                "First customer message",
                "Second customer message",
                "Third customer message",
            ])

            actual_call_arg = mock_assess.call_args[0][0]

            # THIS TEST WILL FAIL until implementation is fixed
            assert actual_call_arg == expected_context


class TestEmotionalArcTracking:
    """Test that emotional arc is tracked across multi-turn conversations."""

    def test_emotional_evolution_anxious_to_confident(self, advisor_agent):
        """Test detecting emotional evolution from anxious to confident.

        EXPECTED TO FAIL: Current implementation only looks at last message,
        so it would miss the anxious → confident arc.
        """
        # Conversation showing emotional evolution
        conversation_showing_arc = [
            {"role": "user", "content": "I'm really worried and stressed about retirement"},
            {"role": "assistant", "content": "Let me help you understand your options."},
            {"role": "user", "content": "I'm still a bit nervous but that helps"},
            {"role": "assistant", "content": "Let's break this down step by step."},
            {"role": "user", "content": "I'm feeling more confident now, ready to proceed"},
        ]

        # Build full context as implementation should
        customer_messages = [
            "I'm really worried and stressed about retirement",
            "I'm still a bit nervous but that helps",
            "I'm feeling more confident now, ready to proceed",
        ]
        full_context = "\n".join(customer_messages)

        # The full context should reveal the emotional arc
        emotional_state = advisor_agent._assess_emotional_state(full_context)

        # Current implementation only looks at last message, so it would return "confident"
        # But with full context, the assessment could detect the arc and adapt accordingly
        # This test documents the expected behavior after fix
        assert emotional_state in ["confident", "neutral"], (
            "With full context, should detect confidence or balanced state"
        )

    def test_emotional_evolution_confused_to_understanding(self, advisor_agent):
        """Test detecting evolution from confused to understanding."""
        customer_messages = [
            "I don't understand what drawdown means",
            "What's the difference between annuity and drawdown?",
            "Okay, I think I'm starting to get it",
        ]
        full_context = "\n".join(customer_messages)

        emotional_state = advisor_agent._assess_emotional_state(full_context)

        # Full context shows progression from confused to understanding
        # Current implementation would only see "starting to get it" (last message)
        assert emotional_state in ["neutral", "confused"], (
            "Should reflect the learning journey"
        )

    def test_persistent_anxiety_throughout_conversation(self, advisor_agent):
        """Test detecting persistent anxiety across multiple messages."""
        customer_messages = [
            "I'm worried I haven't saved enough",
            "I'm concerned about running out of money in retirement",
            "I'm anxious about making the wrong decision",
        ]
        full_context = "\n".join(customer_messages)

        emotional_state = advisor_agent._assess_emotional_state(full_context)

        # Full context shows consistent anxiety
        assert emotional_state == "anxious", (
            "Should detect persistent anxiety across conversation"
        )


class TestContextRetrievalIntegration:
    """Test that _retrieve_context correctly integrates emotional assessment."""

    def test_conversational_context_dict_contains_emotional_state(
        self, advisor_agent, sample_customer
    ):
        """Test that conversational_context dict includes emotional_state from full conversation."""
        conversation_history = [
            {"role": "user", "content": "I'm worried about my savings"},
            {"role": "assistant", "content": "Let me help."},
            {"role": "user", "content": "I'm stressed about retirement"},
        ]

        # Mock _assess_emotional_state to verify it's called with full context
        with patch.object(
            advisor_agent, "_assess_emotional_state", return_value="anxious"
        ) as mock_assess:
            context = advisor_agent._retrieve_context(sample_customer, conversation_history)

            # Verify emotional state was assessed
            assert mock_assess.called

            # EXPECTED TO FAIL: Verify it was called with full context
            expected_full_context = "I'm worried about my savings\nI'm stressed about retirement"
            actual_call_arg = mock_assess.call_args[0][0]

            assert actual_call_arg == expected_full_context

    def test_no_conversation_history_sets_neutral_emotional_context(
        self, advisor_agent, sample_customer
    ):
        """Test that empty conversation history results in appropriate emotional assessment."""
        # Mock to track if assessment happens with empty string
        with patch.object(
            advisor_agent, "_assess_emotional_state", return_value="neutral"
        ) as mock_assess:
            context = advisor_agent._retrieve_context(sample_customer, [])

            # Should call with empty string
            mock_assess.assert_called_once_with("")


class TestAssessEmotionalStateDocstring:
    """Test that _assess_emotional_state docstring reflects full context usage."""

    def test_docstring_mentions_full_conversation_context(self, advisor_agent):
        """Test that docstring indicates function receives full conversation context.

        EXPECTED TO FAIL: Current docstring says 'customer message' (singular).
        After fix: Should say 'full conversation context' or 'all customer messages'.
        """
        docstring = advisor_agent._assess_emotional_state.__doc__

        # Check for indicators of full context
        assert docstring is not None, "_assess_emotional_state should have a docstring"

        # EXPECTED TO FAIL: Current docstring says "customer's message text"
        # After fix, should mention "full conversation" or "all messages"
        full_context_indicators = [
            "full conversation",
            "all customer messages",
            "conversation context",
            "conversation history",
            "all messages",
        ]

        has_full_context_indicator = any(
            indicator in docstring.lower() for indicator in full_context_indicators
        )

        assert has_full_context_indicator, (
            f"Docstring should indicate full conversation context is passed, "
            f"but got: {docstring}"
        )

    def test_parameter_name_reflects_full_context(self, advisor_agent):
        """Test that parameter name suggests full context, not single message.

        EXPECTED TO FAIL: Current parameter is 'customer_message' (singular).
        After fix: Should be 'customer_context' or 'full_customer_context'.
        """
        import inspect

        signature = inspect.signature(advisor_agent._assess_emotional_state)
        param_names = list(signature.parameters.keys())

        # EXPECTED TO FAIL: Current parameter name is 'customer_message'
        # After fix, should be something like 'customer_context' or 'full_customer_context'
        assert len(param_names) == 1, "Should have exactly one parameter"

        param_name = param_names[0]

        # Parameter name should suggest full context
        context_indicators = ["context", "conversation", "messages", "full"]

        has_context_indicator = any(
            indicator in param_name.lower() for indicator in context_indicators
        )

        assert has_context_indicator, (
            f"Parameter name should suggest full context, "
            f"but got: {param_name}"
        )


class TestMultiTurnIntegration:
    """Integration tests with realistic multi-turn conversations."""

    def test_three_turn_conversation_emotional_progression(
        self, advisor_agent, sample_customer
    ):
        """Test realistic 3-turn conversation with emotional progression."""
        conversation = [
            {"role": "user", "content": "I'm overwhelmed by all the pension options"},
            {"role": "assistant", "content": "I understand. Let's break this down together."},
            {"role": "user", "content": "Okay, can you explain drawdown?"},
            {"role": "assistant", "content": "Of course. Drawdown allows you to..."},
            {"role": "user", "content": "That makes sense! I think I understand now"},
        ]

        with patch.object(
            advisor_agent, "_assess_emotional_state", wraps=advisor_agent._assess_emotional_state
        ) as mock_assess:
            advisor_agent._retrieve_context(sample_customer, conversation)

            # Verify it was called with full context
            expected_context = "\n".join([
                "I'm overwhelmed by all the pension options",
                "Okay, can you explain drawdown?",
                "That makes sense! I think I understand now",
            ])

            actual_call_arg = mock_assess.call_args[0][0]

            # EXPECTED TO FAIL until implementation is fixed
            assert actual_call_arg == expected_context

    def test_five_turn_persistent_confusion(
        self, advisor_agent, sample_customer
    ):
        """Test 5-turn conversation showing persistent confusion."""
        conversation = [
            {"role": "user", "content": "What's an annuity?"},
            {"role": "assistant", "content": "An annuity is..."},
            {"role": "user", "content": "I don't get it, what's the difference from drawdown?"},
            {"role": "assistant", "content": "The key difference is..."},
            {"role": "user", "content": "I'm still confused about the pros and cons"},
            {"role": "assistant", "content": "Let me explain more clearly..."},
            {"role": "user", "content": "Which one should I choose? I don't know"},
            {"role": "assistant", "content": "That depends on your circumstances..."},
            {"role": "user", "content": "This is so complicated, I don't understand"},
        ]

        with patch.object(
            advisor_agent, "_assess_emotional_state", wraps=advisor_agent._assess_emotional_state
        ) as mock_assess:
            advisor_agent._retrieve_context(sample_customer, conversation)

            # Get the actual argument passed
            actual_call_arg = mock_assess.call_args[0][0]

            # Should include all 5 customer messages
            assert "What's an annuity?" in actual_call_arg
            assert "I don't get it" in actual_call_arg
            assert "I'm still confused" in actual_call_arg
            assert "Which one should I choose?" in actual_call_arg
            assert "This is so complicated" in actual_call_arg

            # EXPECTED TO FAIL: Should be joined with newlines
            expected_newline_count = 4  # 5 messages = 4 newlines
            actual_newline_count = actual_call_arg.count("\n")

            assert actual_newline_count == expected_newline_count, (
                f"Expected {expected_newline_count} newlines for 5 messages, "
                f"got {actual_newline_count}"
            )


class TestEdgeCases:
    """Test edge cases in emotional arc tracking."""

    def test_messages_with_newlines_in_content(self, advisor_agent, sample_customer):
        """Test that messages containing newlines are handled correctly."""
        conversation = [
            {"role": "user", "content": "I have two questions:\n1. What's drawdown?\n2. What's an annuity?"},
            {"role": "assistant", "content": "Let me answer both..."},
            {"role": "user", "content": "Thanks!\nThat helps a lot"},
        ]

        with patch.object(
            advisor_agent, "_assess_emotional_state", return_value="neutral"
        ) as mock_assess:
            advisor_agent._retrieve_context(sample_customer, conversation)

            actual_call_arg = mock_assess.call_args[0][0]

            # Should preserve newlines within messages and add join newlines
            assert "I have two questions:\n1. What's drawdown?\n2. What's an annuity?" in actual_call_arg
            assert "Thanks!\nThat helps a lot" in actual_call_arg

    def test_very_long_conversation(self, advisor_agent, sample_customer):
        """Test that long conversations (10+ turns) are handled correctly."""
        conversation = []
        customer_messages = []

        for i in range(10):
            customer_msg = f"Customer message {i+1}"
            customer_messages.append(customer_msg)
            conversation.append({"role": "user", "content": customer_msg})
            conversation.append({"role": "assistant", "content": f"Advisor response {i+1}"})

        with patch.object(
            advisor_agent, "_assess_emotional_state", return_value="neutral"
        ) as mock_assess:
            advisor_agent._retrieve_context(sample_customer, conversation)

            expected_context = "\n".join(customer_messages)
            actual_call_arg = mock_assess.call_args[0][0]

            # EXPECTED TO FAIL until implementation is fixed
            assert actual_call_arg == expected_context
            assert actual_call_arg.count("\n") == 9  # 10 messages = 9 newlines

    def test_unicode_and_special_characters(self, advisor_agent, sample_customer):
        """Test that unicode and special characters are handled correctly."""
        conversation = [
            {"role": "user", "content": "I'm worried about my £150,000 pension 😟"},
            {"role": "assistant", "content": "Let me help you."},
            {"role": "user", "content": "What about tax—is it 25% or more?"},
        ]

        with patch.object(
            advisor_agent, "_assess_emotional_state", return_value="anxious"
        ) as mock_assess:
            advisor_agent._retrieve_context(sample_customer, conversation)

            expected_context = "I'm worried about my £150,000 pension 😟\nWhat about tax—is it 25% or more?"
            actual_call_arg = mock_assess.call_args[0][0]

            # EXPECTED TO FAIL until implementation is fixed
            assert actual_call_arg == expected_context


# Summary of expected failures
"""
EXPECTED TEST FAILURES (until implementation is fixed):

1. test_assess_emotional_state_receives_all_customer_messages
   - Currently passes only last_customer_message
   - Should pass full_customer_context (all messages joined with "\n")

2. test_filters_only_user_messages
   - Currently passes only last message
   - Should pass all customer messages

3. test_conversational_context_dict_contains_emotional_state
   - Currently passes only last message
   - Should pass full context

4. test_docstring_mentions_full_conversation_context
   - Docstring says "customer's message text" (singular)
   - Should say "full conversation context" or similar

5. test_parameter_name_reflects_full_context
   - Parameter is named 'customer_message' (singular)
   - Should be 'customer_context' or 'full_customer_context'

6. test_three_turn_conversation_emotional_progression
   - Currently passes only last message
   - Should pass all 3 customer messages joined

7. test_five_turn_persistent_confusion
   - Currently passes only last message
   - Should pass all 5 customer messages with 4 newlines

8. test_very_long_conversation
   - Currently passes only last message
   - Should pass all 10 messages with 9 newlines

9. test_unicode_and_special_characters
   - Currently passes only last message
   - Should pass both messages with unicode preserved

FIXES REQUIRED:

1. In src/guidance_agent/advisor/agent.py (_retrieve_context method):
   Change:
     last_customer_message = customer_messages[-1] if customer_messages else ""
     emotional_state = self._assess_emotional_state(last_customer_message)

   To:
     full_customer_context = "\n".join(customer_messages) if customer_messages else ""
     emotional_state = self._assess_emotional_state(full_customer_context)

2. In src/guidance_agent/advisor/agent.py (_assess_emotional_state method):
   - Update parameter name from 'customer_message' to 'customer_context' or 'full_customer_context'
   - Update docstring to reflect it receives full conversation context

   Current:
     def _assess_emotional_state(self, customer_message: str) -> str:
         "Assess the customer's emotional state from their message."

   Should be:
     def _assess_emotional_state(self, customer_context: str) -> str:
         "Assess the customer's emotional state from their full conversation context."
"""
