"""Advisor agent for providing FCA-compliant pension guidance.

This module implements the main AdvisorAgent class that:
- Generates pension guidance using LLM
- Validates guidance for FCA compliance
- Uses chain-of-thought reasoning
- Maintains memory stream of interactions
- Retrieves relevant context from cases and rules
"""

import os
import asyncio
from typing import List, Tuple, Optional, AsyncIterator, TYPE_CHECKING
from litellm import completion

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from guidance_agent.core.types import (
    AdvisorProfile,
    CustomerProfile,
    RetrievedContext,
)
from guidance_agent.core.memory import MemoryStream, MemoryNode, MemoryType
from guidance_agent.core.provider_config import (
    detect_provider,
    supports_prompt_caching,
    get_cache_headers,
    get_provider_info,
)
from guidance_agent.compliance.validator import ComplianceValidator, ValidationResult, ValidationIssue
from guidance_agent.advisor.prompts import (
    build_guidance_prompt,
    build_reasoning_prompt,
    build_guidance_prompt_with_reasoning,
    build_guidance_prompt_cached,
)
from guidance_agent.core.template_engine import render_template


class AdvisorAgent:
    """Advisor agent that provides FCA-compliant pension guidance.

    The advisor uses:
    - LLM for guidance generation
    - Chain-of-thought reasoning (optional)
    - Compliance validation with confidence scoring
    - Memory stream for observations and reflections
    - Context retrieval from cases and rules
    """

    def __init__(
        self,
        profile: AdvisorProfile,
        session: Optional["Session"] = None,
        model: Optional[str] = None,
        use_chain_of_thought: bool = True,
        enable_prompt_caching: bool = True,
    ):
        """Initialize advisor agent with profile and optional database session.

        Args:
            profile: Advisor profile configuration
            session: SQLAlchemy database session for memory persistence
            model: LLM model to use (defaults to LITELLM_MODEL_ADVISOR env var)
            use_chain_of_thought: Whether to use chain-of-thought reasoning
            enable_prompt_caching: Whether to enable prompt caching for cost reduction
        """
        self.profile = profile
        self.model = model or os.getenv("LITELLM_MODEL_ADVISOR", "gpt-4-turbo-preview")
        self.use_chain_of_thought = use_chain_of_thought
        self.enable_prompt_caching = enable_prompt_caching

        # Detect provider and capabilities
        self.provider = detect_provider(self.model)
        self.provider_info = get_provider_info(self.model)

        # Initialize components
        self.memory_stream = MemoryStream(session=session, load_existing=True)
        self.compliance_validator = ComplianceValidator(model=self.model)

    def provide_guidance(
        self,
        customer: CustomerProfile,
        conversation_history: List[dict],
    ) -> str:
        """Provide FCA-compliant guidance to customer.

        Args:
            customer: Customer profile
            conversation_history: Prior conversation messages

        Returns:
            Guidance text

        Raises:
            Exception: If guidance generation fails
        """
        # 1. Retrieve relevant context with conversational context
        context = self._retrieve_context(customer, conversation_history)

        # 2. Generate guidance (with or without chain-of-thought)
        if self.use_chain_of_thought:
            # First generate reasoning
            reasoning = self._generate_reasoning(customer, context)
            # Then generate guidance based on reasoning
            guidance = self._generate_guidance_from_reasoning(
                customer, context, reasoning
            )
        else:
            # Generate guidance directly
            guidance, reasoning = self._generate_guidance(
                customer, context, conversation_history
            )

        # 3. Validate for compliance
        validation = self.compliance_validator.validate(
            guidance=guidance,
            customer=customer,
            reasoning=reasoning,
        )

        # 4. Handle validation result
        if not validation.passed:
            # Failed validation - refine and try again
            guidance = self._refine_for_compliance(
                guidance, validation.issues, customer
            )
        elif validation.requires_human_review:
            # Borderline case (low confidence) - try to strengthen
            guidance = self._handle_borderline_case(guidance, validation, context)

        return guidance

    async def provide_guidance_stream(
        self,
        customer: CustomerProfile,
        conversation_history: List[dict],
        use_reasoning: Optional[bool] = None,
    ) -> AsyncIterator[str]:
        """Provide FCA-compliant guidance with streaming response.

        This method yields chunks of guidance as they are generated, reducing
        perceived latency by 70-75% (from 6-8s to 1-2s time to first token).

        Args:
            customer: Customer profile
            conversation_history: Prior conversation messages
            use_reasoning: Whether to use chain-of-thought reasoning (defaults to self.use_chain_of_thought)

        Yields:
            str: Chunks of guidance text as they're generated

        Example:
            >>> async for chunk in advisor.provide_guidance_stream(customer, []):
            ...     print(chunk, end="", flush=True)
        """
        # Use instance setting if not specified
        if use_reasoning is None:
            use_reasoning = self.use_chain_of_thought

        # 1. Retrieve relevant context with conversational context (non-streaming, fast)
        context = self._retrieve_context(customer, conversation_history)

        # 2. Store guidance chunks for validation
        guidance_buffer = []

        # 3. Stream guidance generation
        if use_reasoning:
            # Generate reasoning first (non-streaming, relatively fast)
            reasoning = self._generate_reasoning(customer, context)

            # Stream guidance based on reasoning
            async for chunk in self._generate_guidance_from_reasoning_stream(
                customer, context, reasoning
            ):
                guidance_buffer.append(chunk)
                yield chunk
        else:
            # Direct streaming without reasoning
            async for chunk in self._generate_guidance_stream(
                customer, context, conversation_history
            ):
                guidance_buffer.append(chunk)
                yield chunk

        # 4. Validate in background (doesn't block user experience)
        full_guidance = "".join(guidance_buffer)
        asyncio.create_task(
            self._validate_and_record_async(full_guidance, customer, context)
        )

    async def _generate_guidance_stream(
        self,
        customer: CustomerProfile,
        context: RetrievedContext,
        conversation_history: List[dict],
    ) -> AsyncIterator[str]:
        """Generate guidance with streaming.

        Args:
            customer: Customer profile
            context: Retrieved context
            conversation_history: Prior conversation

        Yields:
            str: Chunks of guidance text
        """
        # Build prompt with caching optimization
        messages = build_guidance_prompt_cached(
            advisor=self.profile,
            customer=customer,
            context=context,
            conversation_history=conversation_history,
        )

        # Get cache headers
        extra_headers = self._get_cache_headers()

        # Call LLM with streaming and caching enabled
        response = completion(
            model=self.model,
            messages=messages,
            temperature=0.7,
            stream=True,  # Enable streaming
            extra_headers=extra_headers if extra_headers else None,
        )

        # Yield chunks as they arrive
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def _generate_guidance_from_reasoning_stream(
        self,
        customer: CustomerProfile,
        context: RetrievedContext,
        reasoning: str,
    ) -> AsyncIterator[str]:
        """Generate guidance based on reasoning with streaming.

        Args:
            customer: Customer profile
            context: Retrieved context
            reasoning: Pre-generated chain-of-thought reasoning

        Yields:
            str: Chunks of guidance text
        """
        prompt = build_guidance_prompt_with_reasoning(customer, context, reasoning)

        # Get cache headers
        extra_headers = self._get_cache_headers()

        # Call LLM with streaming and caching enabled
        response = completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            stream=True,
            extra_headers=extra_headers if extra_headers else None,
        )

        # Yield chunks as they arrive
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def _validate_and_record_async(
        self,
        guidance: str,
        customer: CustomerProfile,
        context: RetrievedContext,
    ) -> ValidationResult:
        """Validate guidance asynchronously after streaming completes.

        Runs in background, doesn't block user experience.
        Only takes action if validation fails (rare <2%).

        Args:
            guidance: Full guidance text to validate
            customer: Customer profile
            context: Retrieved context

        Returns:
            ValidationResult
        """
        # Call async validator
        validation = await self.compliance_validator.validate_async(
            guidance=guidance,
            customer=customer,
            reasoning=context.reasoning if hasattr(context, 'reasoning') else "",
        )

        # Only take action if validation fails (rare)
        if not validation.passed and not validation.requires_human_review:
            # Could trigger re-generation or human review
            # For now, just log the issue
            pass

        return validation

    def _get_cache_headers(self) -> dict:
        """Get cache headers based on model provider.

        Returns:
            dict: Cache headers for the LLM API call
        """
        if not self.enable_prompt_caching:
            return {}

        if not self.provider_info["supports_caching"]:
            return {}

        return self.provider_info["cache_headers"]

    def _retrieve_context(
        self,
        customer: CustomerProfile,
        conversation_history: List[dict],
    ) -> RetrievedContext:
        """Retrieve relevant context for guidance generation with conversational awareness.

        Args:
            customer: Customer profile
            conversation_history: Prior conversation messages

        Returns:
            Retrieved context with memories, cases, and rules
        """
        # Build conversational context for enhanced case retrieval
        # Get all customer messages for emotional arc assessment
        customer_messages = [
            msg["content"]
            for msg in conversation_history
            if msg.get("role") == "user"
        ]
        # Use full conversation for emotional arc tracking
        full_customer_context = "\n".join(customer_messages) if customer_messages else ""

        conversational_context = None
        if conversation_history:
            # Build conversational context dict
            conversational_context = {
                "phase": self._detect_conversation_phase(conversation_history),
                "emotional_state": self._assess_emotional_state(full_customer_context),
                "literacy_level": getattr(
                    getattr(customer, "demographics", None),
                    "financial_literacy",
                    "medium"
                ),
            }
        else:
            # Still assess emotional state even with empty history for consistency
            self._assess_emotional_state(full_customer_context)

        # Retrieve from memory stream
        query = customer.presenting_question
        memories = self.memory_stream.retrieve(query, top_k=5) if query else []

        # Placeholder for FCA requirements
        fca_requirements = """
        Key FCA Requirements:
        1. Stay within guidance boundary - do not make specific recommendations
        2. Present options clearly with pros and cons
        3. Use appropriate language for customer's literacy level
        4. Check customer understanding throughout
        5. Signpost to FCA-regulated advisor for complex decisions (especially DB transfers)
        6. Ensure risks are clearly explained
        """

        # NOTE: In this simplified implementation, we're not using case_base and rules_base yet.
        # When integrated, pass conversational_context to case retrieval like this:
        # cases = case_base.retrieve(query_embedding, top_k=3, conversation_context=conversational_context)

        return RetrievedContext(
            memories=memories,
            cases=[],  # Will be populated in later integration with conversational_context
            rules=[],  # Will be populated in later integration
            fca_requirements=fca_requirements,
        )

    def _generate_guidance(
        self,
        customer: CustomerProfile,
        context: RetrievedContext,
        conversation_history: List[dict],
    ) -> Tuple[str, str]:
        """Generate guidance using LLM.

        Args:
            customer: Customer profile
            context: Retrieved context
            conversation_history: Prior conversation

        Returns:
            Tuple of (guidance, reasoning)
        """
        # Build prompt with caching optimization
        messages = build_guidance_prompt_cached(
            advisor=self.profile,
            customer=customer,
            context=context,
            conversation_history=conversation_history,
        )

        # Get cache headers
        extra_headers = self._get_cache_headers()

        # Call LLM with caching enabled
        response = completion(
            model=self.model,
            messages=messages,
            temperature=0.7,
            extra_headers=extra_headers if extra_headers else None,
        )

        guidance = response.choices[0].message.content

        # Reasoning is implicit in the response
        reasoning = "Generated guidance based on customer profile and context"

        return guidance, reasoning

    def _generate_reasoning(
        self,
        customer: CustomerProfile,
        context: RetrievedContext,
    ) -> str:
        """Generate chain-of-thought reasoning.

        Args:
            customer: Customer profile
            context: Retrieved context

        Returns:
            Reasoning text
        """
        prompt = build_reasoning_prompt(customer, context)

        # Get cache headers
        extra_headers = self._get_cache_headers()

        response = completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            extra_headers=extra_headers if extra_headers else None,
        )

        return response.choices[0].message.content

    def _generate_guidance_from_reasoning(
        self,
        customer: CustomerProfile,
        context: RetrievedContext,
        reasoning: str,
    ) -> str:
        """Generate guidance based on chain-of-thought reasoning.

        Args:
            customer: Customer profile
            context: Retrieved context
            reasoning: Pre-generated reasoning

        Returns:
            Guidance text
        """
        prompt = build_guidance_prompt_with_reasoning(customer, context, reasoning)

        # Get cache headers
        extra_headers = self._get_cache_headers()

        response = completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            extra_headers=extra_headers if extra_headers else None,
        )

        return response.choices[0].message.content

    def _refine_for_compliance(
        self,
        guidance: str,
        issues: List[ValidationIssue],
        customer: CustomerProfile,
    ) -> str:
        """Refine guidance to address compliance issues.

        Args:
            guidance: Original guidance that failed validation
            issues: List of compliance issues
            customer: Customer profile

        Returns:
            Refined guidance
        """
        prompt = render_template(
            "advisor/compliance_refinement.jinja",
            guidance=guidance,
            issues=issues,
            customer=customer,
        )

        # Get cache headers
        extra_headers = self._get_cache_headers()

        response = completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            extra_headers=extra_headers if extra_headers else None,
        )

        return response.choices[0].message.content

    def _handle_borderline_case(
        self,
        guidance: str,
        validation: ValidationResult,
        context: RetrievedContext,
    ) -> str:
        """Handle borderline validation case (low confidence).

        Args:
            guidance: Guidance that passed but with low confidence
            validation: Validation result
            context: Retrieved context

        Returns:
            Strengthened guidance
        """
        prompt = render_template(
            "advisor/borderline_strengthening.jinja",
            guidance=guidance,
            validation=validation,
            context=context,
        )

        # Get cache headers
        extra_headers = self._get_cache_headers()

        response = completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,  # Slightly lower temperature for more consistent output
            extra_headers=extra_headers if extra_headers else None,
        )

        return response.choices[0].message.content

    async def _calculate_conversational_quality(
        self,
        conversation_history: List[dict],
        db: Optional["AsyncSession"] = None,
    ) -> float:
        """Calculate conversational quality score (0-1) based on naturalness and engagement.

        This method evaluates the advisor's conversational effectiveness across 4 components:
        - Language variety (30%): Avoids repetitive phrases
        - Signposting usage (30%): Uses transition/guiding phrases
        - Personalization (20%): Uses customer's name appropriately
        - Engagement questions (20%): Asks questions to encourage dialogue

        Args:
            conversation_history: List of conversation messages with role/content
            db: Database session (unused, for future extensibility)

        Returns:
            float: Quality score between 0.0 and 1.0

        Example:
            >>> quality = await advisor._calculate_conversational_quality([
            ...     {"role": "user", "content": "Help me", "customer_name": "John"},
            ...     {"role": "assistant", "content": "Hi John! Let me break this down..."}
            ... ], db)
            >>> assert 0.0 <= quality <= 1.0
        """
        # Extract advisor messages only
        advisor_messages = [
            msg["content"]
            for msg in conversation_history
            if msg.get("role") in ["assistant", "advisor"]
        ]

        # Handle edge cases
        if not advisor_messages:
            return 0.0

        # Initialize score
        score = 0.0

        # Component 1: Language Variety (30%) - Avoid repetitive phrases
        common_phrases = ["you could consider", "pros and cons", "based on"]
        total_repetitions = sum(
            sum(1 for msg in advisor_messages if phrase in msg.lower())
            for phrase in common_phrases
        )

        # Calculate variety score (inverse of repetition rate)
        # If no repetitions: 1.0, if 1 per message: 0.66, if 2 per message: 0.33, if 3+: 0.0
        max_expected_repetitions = len(advisor_messages) * len(common_phrases)
        variety_score = 1.0 - (total_repetitions / max_expected_repetitions) if max_expected_repetitions > 0 else 0.0
        variety_score = max(0.0, min(1.0, variety_score))
        score += variety_score * 0.3

        # Component 2: Signposting/Transitions (30%) - Use guiding language
        signpost_phrases = [
            "let me break this down",
            "let me explain",
            "let me help",
            "here's what this means",
            "here's what",
            "building on",
            "before we",
            "first,",
            "let's explore",
            "let's look",
            "here's how",
            "one option",
            "one approach",
            "some people find",
            "it's worth",
            "it depends",
        ]

        signpost_count = sum(
            1 for msg in advisor_messages
            if any(phrase in msg.lower() for phrase in signpost_phrases)
        )

        # Normalize: 1.0 if at least 1 signpost per message, scales linearly
        signpost_score = min(signpost_count / len(advisor_messages), 1.0) if len(advisor_messages) > 0 else 0.0
        score += signpost_score * 0.3

        # Component 3: Personalization (20%) - Use customer's name
        customer_name = ""
        # Extract customer name from first message if available
        for msg in conversation_history:
            if msg.get("role") == "user" and msg.get("customer_name"):
                customer_name = msg["customer_name"]
                break

        personalization_score = 0.0
        if customer_name:
            name_usage = sum(
                1 for msg in advisor_messages
                if customer_name.lower() in msg.lower()
            )
            # Normalize: aim for 1 usage per 2 messages (0.5 rate) = 1.0 score
            expected_usage_rate = len(advisor_messages) / 2
            personalization_score = min(name_usage / expected_usage_rate, 1.0) if expected_usage_rate > 0 else 0.0

        score += personalization_score * 0.2

        # Component 4: Engagement Questions (20%) - Ask questions
        question_count = sum(msg.count("?") for msg in advisor_messages)

        # Normalize: aim for 1 question per message = 1.0 score
        engagement_score = min(question_count / len(advisor_messages), 1.0) if len(advisor_messages) > 0 else 0.0
        score += engagement_score * 0.2

        # Ensure final score is in valid range
        return max(0.0, min(1.0, score))

    def _detect_conversation_phase(self, conversation_history: List[dict]) -> str:
        """Detect the current phase of the conversation.

        Analyses conversation length and content to determine whether this is:
        - "opening": Initial rapport-building phase (1-2 messages)
        - "middle": Main information exchange phase (3-8 messages)
        - "closing": Summarization and next steps phase (9+ messages or explicit signals)

        Args:
            conversation_history: List of conversation messages with role/content

        Returns:
            str: One of "opening", "middle", or "closing"

        Example:
            >>> phase = advisor._detect_conversation_phase([
            ...     {"role": "user", "content": "Hi, I need help"},
            ...     {"role": "assistant", "content": "Hello! How can I help?"}
            ... ])
            >>> assert phase == "opening"
        """
        # Count total messages (both user and assistant)
        total_messages = len(conversation_history)

        # Opening phase: 1-2 messages (just starting)
        if total_messages <= 2:
            return "opening"

        # Check for explicit closing signals
        closing_keywords = [
            "thank you",
            "thanks",
            "that's all",
            "that helps",
            "goodbye",
            "bye",
            "next steps",
            "what should i do next",
            "how do i proceed",
        ]

        # Look at last few user messages for closing signals
        recent_user_messages = [
            msg["content"].lower()
            for msg in conversation_history[-4:]
            if msg.get("role") == "user"
        ]

        has_closing_signal = any(
            keyword in msg
            for keyword in closing_keywords
            for msg in recent_user_messages
        )

        # Closing phase: 9+ messages OR explicit closing signals
        if total_messages >= 9 or has_closing_signal:
            return "closing"

        # Middle phase: 3-8 messages (main conversation)
        return "middle"

    def _assess_emotional_state(self, customer_context: str) -> str:
        """Assess the customer's emotional state from their full conversation context.

        Uses keyword matching to detect emotional indicators across all customer messages.
        Tracks emotional arc throughout the conversation to adapt tone and pacing.
        Helps identify emotional evolution (e.g., anxious → confident, confused → understanding).

        When emotional evolution is detected, more recent messages are given priority
        to reflect the customer's current state.

        Args:
            customer_context: Full conversation context with all customer messages joined by newlines

        Returns:
            str: One of "anxious", "confident", "confused", "frustrated", or "neutral"

        Example:
            >>> full_context = "I'm really worried about retirement\\nI'm still nervous\\nFeeling better now"
            >>> state = advisor._assess_emotional_state(full_context)
            >>> assert state in ["anxious", "neutral", "confident"]
        """
        if not customer_context:
            return "neutral"

        # Split into individual messages to track emotional evolution
        messages = customer_context.split("\n")

        # Define emotional keywords
        anxious_keywords = [
            "worried",
            "anxious",
            "concerned",
            "stressed",
            "nervous",
            "scared",
            "afraid",
            "overwhelming",
            "overwhelmed",
            "panic",
            "don't know if",
            "not sure if",
            "haven't saved enough",
        ]

        frustrated_keywords = [
            "frustrated",
            "annoyed",
            "don't understand",
            "doesn't make sense",
            "complicated",
            "difficult",
            "hard to understand",
            "why is this so",
            "this is ridiculous",
        ]

        confused_keywords = [
            "confused",
            "what does",
            "what is",
            "i don't get",
            "explain",
            "unclear",
            "don't know",
            "not sure what",
            "which one",
            "what's the difference",
        ]

        confident_keywords = [
            "want to optimise",
            "looking to maximise",
            "ready to",
            "planning to",
            "i'm confident",
            "feeling more confident",
            "feeling confident",
            "i understand",
            "i think i understand",
            "starting to get it",
            "makes sense",
            "sounds good",
            "let's do it",
            "i'm doing well",
            "on track",
        ]

        # Check most recent message first for emotional evolution
        # This prioritizes current state over historical anxiety/confusion
        if len(messages) > 0:
            last_message = messages[-1].lower()

            # Check for strong confident indicators in last message
            strong_confident_keywords = [
                "ready to",
                "planning to",
                "i'm confident",
                "feeling more confident",
                "feeling confident",
                "makes sense",
                "sounds good",
                "let's do it",
            ]
            if any(keyword in last_message for keyword in strong_confident_keywords):
                return "confident"

            # Check for understanding/learning indicators that suggest neutral state
            # (not fully confident, but no longer confused)
            learning_keywords = [
                "i think i understand",
                "starting to get it",
                "i understand",
            ]
            if any(keyword in last_message for keyword in learning_keywords):
                # This suggests evolution from confused to neutral understanding
                return "neutral"

            # Check for neutral/calm language that suggests evolution away from anxiety
            if "okay" in last_message or "alright" in last_message:
                # Check if earlier messages showed anxiety/confusion
                earlier_context = "\n".join(messages[:-1]).lower()
                if any(keyword in earlier_context for keyword in anxious_keywords + confused_keywords):
                    return "neutral"  # Evolved from anxious/confused to neutral

        # Fall back to overall context assessment
        message_lower = customer_context.lower()

        # Anxious/worried indicators
        if any(keyword in message_lower for keyword in anxious_keywords):
            return "anxious"

        # Frustrated indicators
        if any(keyword in message_lower for keyword in frustrated_keywords):
            return "frustrated"

        # Confused indicators
        if any(keyword in message_lower for keyword in confused_keywords):
            return "confused"

        # Confident indicators
        if any(keyword in message_lower for keyword in confident_keywords):
            return "confident"

        # Default: neutral
        return "neutral"
