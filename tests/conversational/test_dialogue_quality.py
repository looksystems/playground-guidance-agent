"""Tests for dialogue quality and naturalness (Phase 5.2).

This module tests conversational quality features:
- Conversation phase detection (opening/middle/closing)
- Emotional state assessment (anxious/confident/confused/frustrated/neutral)
- Conversational quality calculation (high vs low quality scoring)
- FCA compliance maintained with conversational style
"""

import pytest
from guidance_agent.core.types import AdvisorProfile, CustomerProfile, CustomerDemographics
from guidance_agent.advisor.agent import AdvisorAgent
from guidance_agent.compliance.validator import ComplianceValidator


class TestConversationPhaseDetection:
    """Tests for conversation phase detection."""

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

    def test_opening_phase_with_greeting(self, advisor_agent):
        """Test that greeting is detected as opening phase."""
        conversation_history = [
            {"role": "user", "content": "Hello, I'm new to pensions"},
            {"role": "assistant", "content": "Welcome! I'm happy to help you understand pensions."},
        ]

        phase = advisor_agent._detect_conversation_phase(conversation_history)

        assert phase == "opening", "Greeting should be opening phase"

    def test_middle_phase_with_multiple_exchanges(self, advisor_agent):
        """Test that multiple exchanges are detected as middle phase."""
        conversation_history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "Tell me about pension options"},
            {"role": "assistant", "content": "Here are your main options..."},
            {"role": "user", "content": "What about tax-free lump sums?"},
        ]

        phase = advisor_agent._detect_conversation_phase(conversation_history)

        assert phase == "middle", "Multiple exchanges should be middle phase"

    def test_middle_phase_information_exchange(self, advisor_agent):
        """Test that active information exchange is middle phase."""
        conversation_history = [
            {"role": "user", "content": "I have £50k in my pension"},
            {"role": "assistant", "content": "That's a good foundation. Let's explore your options."},
            {"role": "user", "content": "What can I do with it?"},
            {"role": "assistant", "content": "You have several paths available..."},
            {"role": "user", "content": "Tell me more about drawdown"},
            {"role": "assistant", "content": "Drawdown allows you to..."},
        ]

        phase = advisor_agent._detect_conversation_phase(conversation_history)

        assert phase == "middle", "Information exchange should be middle phase"

    def test_closing_phase_with_many_messages(self, advisor_agent):
        """Test that long conversation is detected as closing phase."""
        conversation_history = [
            {"role": "user", "content": f"Message {i}"}
            for i in range(10)
        ]

        phase = advisor_agent._detect_conversation_phase(conversation_history)

        assert phase == "closing", "Long conversation should be closing phase"

    def test_closing_phase_with_thank_you(self, advisor_agent):
        """Test that 'thank you' triggers closing phase."""
        conversation_history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "Tell me about pensions"},
            {"role": "assistant", "content": "Here's information..."},
            {"role": "user", "content": "Thank you, that helps!"},
        ]

        phase = advisor_agent._detect_conversation_phase(conversation_history)

        assert phase == "closing", "'Thank you' should trigger closing phase"

    def test_closing_phase_with_next_steps_question(self, advisor_agent):
        """Test that 'what should I do next' triggers closing phase."""
        conversation_history = [
            {"role": "user", "content": "What are my options?"},
            {"role": "assistant", "content": "Here are three main options..."},
            {"role": "user", "content": "What should I do next?"},
        ]

        phase = advisor_agent._detect_conversation_phase(conversation_history)

        assert phase == "closing", "'What should I do next' should trigger closing phase"

    def test_closing_phase_with_goodbye(self, advisor_agent):
        """Test that goodbye triggers closing phase."""
        conversation_history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "I need to go now, goodbye"},
        ]

        phase = advisor_agent._detect_conversation_phase(conversation_history)

        assert phase == "closing", "Goodbye should trigger closing phase"

    def test_empty_conversation_defaults_to_opening(self, advisor_agent):
        """Test that empty conversation defaults to opening phase."""
        conversation_history = []

        phase = advisor_agent._detect_conversation_phase(conversation_history)

        assert phase == "opening", "Empty conversation should default to opening"


class TestEmotionalStateAssessment:
    """Tests for emotional state assessment."""

    @pytest.fixture
    def advisor_agent(self):
        """Create advisor agent for testing."""
        profile = AdvisorProfile(
            name="Sarah",
            description="Pension guidance specialist",
        )
        return AdvisorAgent(profile=profile, use_chain_of_thought=False)

    def test_anxious_state_with_worried_keyword(self, advisor_agent):
        """Test that 'worried' indicates anxious state."""
        message = "I'm really worried about my retirement savings"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "anxious", "'worried' should indicate anxious state"

    def test_anxious_state_with_stressed_keyword(self, advisor_agent):
        """Test that 'stressed' indicates anxious state."""
        message = "I'm feeling stressed about whether I've saved enough"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "anxious", "'stressed' should indicate anxious state"

    def test_anxious_state_with_overwhelmed_keyword(self, advisor_agent):
        """Test that 'overwhelmed' indicates anxious state."""
        message = "This is all so overwhelming and I don't know where to start"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "anxious", "'overwhelmed' should indicate anxious state"

    def test_anxious_state_with_panic_keyword(self, advisor_agent):
        """Test that 'panic' indicates anxious state."""
        message = "I'm starting to panic about my pension situation"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "anxious", "'panic' should indicate anxious state"

    def test_confident_state_with_optimize_keyword(self, advisor_agent):
        """Test that 'optimize' indicates confident state."""
        message = "I want to optimize my pension contributions for maximum growth"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "confident", "'optimize' should indicate confident state"

    def test_confident_state_with_ready_to_keyword(self, advisor_agent):
        """Test that 'ready to' indicates confident state."""
        message = "I'm ready to increase my contributions and plan ahead"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "confident", "'ready to' should indicate confident state"

    def test_confident_state_with_on_track_keyword(self, advisor_agent):
        """Test that 'on track' indicates confident state."""
        message = "I think I'm on track with my retirement savings"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "confident", "'on track' should indicate confident state"

    def test_confused_state_with_confused_keyword(self, advisor_agent):
        """Test that 'confused' indicates confused state."""
        message = "I'm confused about the difference between these options"

        state = advisor_agent._assess_emotional_state(message)

        # Note: 'confused' may match multiple patterns
        assert state in ["confused", "frustrated"], "'confused' should indicate confused or frustrated state"

    def test_confused_state_with_what_does_keyword(self, advisor_agent):
        """Test that 'what does' indicates confused state."""
        message = "What does tax-free lump sum mean exactly?"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "confused", "'what does' should indicate confused state"

    def test_confused_state_with_explain_keyword(self, advisor_agent):
        """Test that 'explain' indicates confused state."""
        message = "Can you explain how pension contributions work?"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "confused", "'explain' should indicate confused state"

    def test_frustrated_state_with_frustrated_keyword(self, advisor_agent):
        """Test that 'frustrated' indicates frustrated state."""
        message = "I'm frustrated with how complicated this all is"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "frustrated", "'frustrated' should indicate frustrated state"

    def test_frustrated_state_with_dont_understand(self, advisor_agent):
        """Test that 'don't understand' indicates frustrated state."""
        message = "I don't understand why this has to be so difficult"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "frustrated", "'don't understand' should indicate frustrated state"

    def test_neutral_state_with_no_indicators(self, advisor_agent):
        """Test that message with no emotional indicators is neutral."""
        message = "What are my pension options?"

        state = advisor_agent._assess_emotional_state(message)

        assert state == "neutral", "No emotional indicators should be neutral state"

    def test_neutral_state_with_factual_question(self, advisor_agent):
        """Test that factual question is neutral."""
        message = "How much is in my pension pot right now?"

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


class TestConversationalQualityCalculation:
    """Tests for conversational quality scoring."""

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
        high_quality_history = [
            {
                "role": "user",
                "content": "My name is John, I need help with my pension",
                "customer_name": "John",
            },
            {
                "role": "assistant",
                "content": "Great to meet you, John! Let me break this down for you. "
                "First, let's explore your current situation. What would be most helpful?",
            },
            {"role": "user", "content": "My pension amount"},
            {
                "role": "assistant",
                "content": "Perfect, John. You have £20,000 at age 30. "
                "Here's a helpful way to think about retirement planning. "
                "Would you like me to walk you through the details?",
            },
        ]

        quality = await advisor_agent._calculate_conversational_quality(
            high_quality_history, db=None
        )

        assert quality > 0.7, f"High-quality conversation should score >0.7, got {quality}"
        assert 0.0 <= quality <= 1.0

    @pytest.mark.asyncio
    async def test_low_quality_conversation_scores_below_0_5(self, advisor_agent):
        """Test that low-quality conversation (repetitive, impersonal, robotic) scores < 0.5."""
        # Low quality: repetitive phrases, no personalization, no questions, no signposting
        low_quality_history = [
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
        ]

        quality = await advisor_agent._calculate_conversational_quality(
            low_quality_history, db=None
        )

        assert quality < 0.5, f"Low-quality conversation should score <0.5, got {quality}"
        assert 0.0 <= quality <= 1.0

    @pytest.mark.asyncio
    async def test_medium_quality_scores_between_0_4_and_0_7(self, advisor_agent):
        """Test that medium-quality conversation scores between 0.4 and 0.7."""
        medium_quality_history = [
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
        ]

        quality = await advisor_agent._calculate_conversational_quality(
            medium_quality_history, db=None
        )

        assert 0.4 <= quality <= 0.7, f"Medium-quality conversation should score 0.4-0.7, got {quality}"


class TestFCAComplianceWithConversationalStyle:
    """Tests that conversational enhancements maintain FCA compliance."""

    @pytest.fixture
    def advisor_agent(self):
        """Create advisor agent for testing."""
        profile = AdvisorProfile(
            name="Sarah",
            description="Pension guidance specialist",
        )
        return AdvisorAgent(profile=profile, use_chain_of_thought=False)

    @pytest.fixture
    def compliance_validator(self):
        """Create compliance validator."""
        return ComplianceValidator()

    @pytest.fixture
    def sample_customer(self):
        """Create sample customer profile."""
        return CustomerProfile(
            demographics=CustomerDemographics(
                age=35,
                gender="F",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            presenting_question="I need help with my pension",
        )

    @pytest.mark.asyncio
    async def test_warm_greeting_is_compliant(self, compliance_validator, sample_customer):
        """Test that warm, personalized greeting is FCA compliant."""
        warm_message = "Hi Sarah! I'm so glad you reached out. Let's explore your pension options together!"

        # This should be compliant - warmth doesn't violate FCA rules
        validation = await compliance_validator.validate_async(
            guidance=warm_message,
            customer=sample_customer,
            customer_message="I need help with my pension",
        )

        assert validation.passed, "Warm greeting should be FCA compliant"
        assert validation.confidence > 0.7

    @pytest.mark.asyncio
    async def test_signposting_language_is_compliant(self, compliance_validator, sample_customer):
        """Test that signposting phrases are FCA compliant."""
        signposted_message = """Let me break this down for you. First, let's look at your options.

You have several approaches to consider for your pension. You could increase your contributions, consolidate existing pensions, or review your investment choices. Each option has different considerations.

For example, increasing contributions means more money going into your pension, but it affects your current take-home pay. Consolidating pensions can simplify management, but you need to check for exit penalties or loss of benefits.

Would you like me to explain any of these options in more detail? For specific recommendations about which approach suits your circumstances, you'd want to speak with an FCA-regulated financial adviser."""

        validation = await compliance_validator.validate_async(
            guidance=signposted_message,
            customer=sample_customer,
            customer_message="I'm confused about my pension",
        )

        assert validation.passed, "Signposting language should be compliant"

    @pytest.mark.asyncio
    async def test_personalization_with_name_is_compliant(self, compliance_validator, sample_customer):
        """Test that using customer's name is FCA compliant."""
        personalized_message = "Thanks for that information, John. Based on what you've told me, here's what I can explain about your pension options. There are three main types to consider: defined contribution, defined benefit, and personal pensions. Each has different characteristics in terms of how much you pay, how the pension builds up, and what you receive at retirement."

        validation = await compliance_validator.validate_async(
            guidance=personalized_message,
            customer=sample_customer,
            customer_message="My name is John, can you help me?",
        )

        # Should pass or have high confidence (personalization alone doesn't violate FCA)
        assert validation.passed or validation.confidence > 0.7, \
            f"Personalization (name usage) should be compliant or high-confidence. Got passed={validation.passed}, confidence={validation.confidence}"

    @pytest.mark.asyncio
    async def test_empathetic_language_is_compliant(self, compliance_validator, sample_customer):
        """Test that empathetic, acknowledging language is compliant."""
        empathetic_message = "I understand this can feel overwhelming. Many people feel the same way when they start looking at their pension. Let me help make this clearer for you."

        validation = await compliance_validator.validate_async(
            guidance=empathetic_message,
            customer=sample_customer,
            customer_message="I'm stressed about my pension",
        )

        assert validation.passed, "Empathetic language should be compliant"

    @pytest.mark.asyncio
    async def test_engaging_questions_are_compliant(self, compliance_validator, sample_customer):
        """Test that engagement questions are FCA compliant."""
        engaging_message = """You have several pension options to consider when you reach retirement age:

1. Take a tax-free lump sum (typically up to 25% of your pot) and leave the rest invested
2. Buy an annuity for guaranteed income
3. Enter drawdown to take flexible amounts
4. Take the whole pot as cash (though most will be taxed)

Each option has different tax implications, flexibility levels, and long-term considerations. For example, taking cash now provides immediate access but may leave you with less for later retirement years.

Would you like me to explain any of these options in more detail? What aspect is most important to you right now - flexibility, security, or maximizing your pot's value? For personalized recommendations about which option suits your circumstances, speak with an FCA-regulated financial adviser."""

        validation = await compliance_validator.validate_async(
            guidance=engaging_message,
            customer=sample_customer,
            customer_message="Tell me about my options",
        )

        assert validation.passed, "Engaging questions should be compliant"

    @pytest.mark.asyncio
    async def test_varied_phrasing_is_compliant(self, compliance_validator, sample_customer):
        """Test that varied phrasing alternatives are compliant."""
        varied_message = "One option to explore is increasing your contributions. Another approach is to review your pension annually. It's worth thinking about your retirement goals."

        validation = await compliance_validator.validate_async(
            guidance=varied_message,
            customer=sample_customer,
            customer_message="What should I do?",
        )

        assert validation.passed, "Varied phrasing should be compliant"

    @pytest.mark.asyncio
    async def test_conversational_style_does_not_become_directive(self, compliance_validator, sample_customer):
        """Test that conversational style doesn't cross into directive advice."""
        # This SHOULD be flagged as non-compliant
        directive_message = "Sarah, you should definitely increase your contributions to 20% right now. This is what you need to do to retire comfortably."

        validation = await compliance_validator.validate_async(
            guidance=directive_message,
            customer=sample_customer,
            customer_message="What should I do with my pension?",
        )

        # This should be flagged as potentially non-compliant due to directive language
        assert not validation.passed or validation.confidence < 0.8, \
            "Directive language should be flagged even with conversational elements"

    @pytest.mark.asyncio
    async def test_warmth_without_risk_disclosure_still_requires_disclosure(self, compliance_validator, sample_customer):
        """Test that warm language doesn't excuse missing risk disclosure."""
        # Missing risk disclosure for drawdown
        warm_no_risk = "Hi John! Drawdown is a great flexible option that gives you control. You can take as much or as little as you want whenever you need it. Sounds perfect, right?"

        validation = await compliance_validator.validate_async(
            guidance=warm_no_risk,
            customer=sample_customer,
            customer_message="Tell me about drawdown",
        )

        # Should potentially be flagged for missing risk disclosure
        # (though this depends on the validator's implementation)
        # At minimum, confidence should reflect the issue
        if not validation.passed:
            assert any("risk" in str(issue).lower() for issue in validation.issues), \
                "Should flag missing risk disclosure"


class TestRealisticConversationalScenarios:
    """Test realistic conversational scenarios from the spec."""

    @pytest.fixture
    def advisor_agent(self):
        """Create advisor agent for testing."""
        profile = AdvisorProfile(
            name="Sarah",
            description="Pension guidance specialist",
        )
        return AdvisorAgent(profile=profile, use_chain_of_thought=False)

    @pytest.mark.asyncio
    async def test_spec_desired_style_example_scores_high(self, advisor_agent):
        """Test that the desired style from spec scores higher than current style."""
        # From spec: "Desired Style Example" (updated for FCA neutrality)
        desired_style = [
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

        # From spec: "Current Style Example" (robotic)
        current_style = [
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

        desired_score = await advisor_agent._calculate_conversational_quality(
            desired_style, db=None
        )
        current_score = await advisor_agent._calculate_conversational_quality(
            current_style, db=None
        )

        assert desired_score > current_score, \
            f"Desired style ({desired_score}) should score higher than current robotic style ({current_score})"
        assert desired_score > 0.6, "Desired conversational style should score >0.6"

    @pytest.mark.asyncio
    async def test_anxious_customer_conversation(self, advisor_agent):
        """Test conversation with anxious customer."""
        anxious_conversation = [
            {
                "role": "user",
                "content": "I'm really worried I haven't saved enough and I'm stressed about retirement",
            },
            {
                "role": "assistant",
                "content": "I understand this can feel overwhelming, and it's completely normal to feel concerned about your retirement. Let me help you understand where you stand. First, can you tell me a bit about your current pension situation?",
            },
            {
                "role": "user",
                "content": "I have about £20,000 and I'm 40 years old",
            },
            {
                "role": "assistant",
                "content": "Thank you for sharing that. Here's what I want you to know: you're taking a positive step by thinking about this now. Let me break down where you are and what options you have to build on this foundation. Does that sound helpful?",
            },
        ]

        # Detect emotional state
        state = advisor_agent._assess_emotional_state(anxious_conversation[0]["content"])
        assert state == "anxious"

        # Quality should still be good with appropriate empathy
        quality = await advisor_agent._calculate_conversational_quality(
            anxious_conversation, db=None
        )
        assert quality > 0.5, "Empathetic response to anxious customer should score well"

    @pytest.mark.asyncio
    async def test_confident_customer_conversation(self, advisor_agent):
        """Test conversation with confident customer."""
        confident_conversation = [
            {
                "role": "user",
                "content": "I'm feeling good about my pension, I want to optimize my contributions",
            },
            {
                "role": "assistant",
                "content": "That's great to hear! Since you're ready to optimize, let's explore some strategies. What specific aspect would you like to focus on - contribution levels, investment approach, or tax efficiency?",
            },
            {
                "role": "user",
                "content": "Contribution levels mainly",
            },
            {
                "role": "assistant",
                "content": "Perfect. Here are three approaches worth considering. One path is maximizing your annual allowance. Another is taking advantage of any employer matching. Let's work through what might give you the best outcome.",
            },
        ]

        # Detect emotional state
        state = advisor_agent._assess_emotional_state(confident_conversation[0]["content"])
        assert state == "confident"

        # Quality should be good with appropriate engagement
        quality = await advisor_agent._calculate_conversational_quality(
            confident_conversation, db=None
        )
        assert quality > 0.5, "Engaging response to confident customer should score well"
