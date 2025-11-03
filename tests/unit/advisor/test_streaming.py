"""Unit tests for streaming functionality in AdvisorAgent.

Tests for:
- provide_guidance_stream() async generator
- _generate_guidance_stream() async generator
- _generate_guidance_from_reasoning_stream() async generator
- _validate_and_record_async() parallel validation
- Time to first token (TTFT) performance
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import AsyncIterator

from guidance_agent.core.types import (
    AdvisorProfile,
    CustomerProfile,
    CustomerDemographics,
    FinancialSituation,
    PensionPot,
    RetrievedContext,
)
from guidance_agent.advisor.agent import AdvisorAgent
from guidance_agent.compliance.validator import ValidationResult, ValidationIssue


class TestProvideGuidanceStream:
    """Tests for provide_guidance_stream async generator method."""

    @pytest.fixture
    def advisor_profile(self):
        """Create an advisor profile."""
        return AdvisorProfile(
            name="Sarah",
            description="Experienced pension guidance specialist",
        )

    @pytest.fixture
    def customer_profile(self):
        """Create a customer profile."""
        return CustomerProfile(
            demographics=CustomerDemographics(
                age=55,
                gender="M",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            financial=FinancialSituation(
                annual_income=50000,
                total_assets=200000,
                total_debt=10000,
                dependents=0,
                risk_tolerance="medium",
            ),
            pensions=[
                PensionPot(
                    pot_id="pot1",
                    provider="Provider A",
                    pot_type="defined_contribution",
                    current_value=100000,
                    projected_value=120000,
                    age_accessible=55,
                )
            ],
            goals="Understanding withdrawal options",
            presenting_question="Can I access my pension now?",
        )

    @pytest.mark.asyncio
    async def test_provide_guidance_stream_exists(self, advisor_profile, customer_profile):
        """Test that provide_guidance_stream method exists."""
        agent = AdvisorAgent(profile=advisor_profile)

        # Method should exist
        assert hasattr(agent, "provide_guidance_stream")

        # Should be an async generator function
        import inspect
        assert inspect.isasyncgenfunction(agent.provide_guidance_stream)

    @pytest.mark.asyncio
    async def test_provide_guidance_stream_yields_chunks(self, advisor_profile, customer_profile):
        """Test that streaming yields multiple chunks."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)
        conversation = []

        # Mock the streaming generator to return test chunks
        async def mock_stream(*args, **kwargs):
            test_chunks = ["Hello ", "there ", "from ", "streaming!"]
            for chunk in test_chunks:
                yield chunk

        with patch.object(agent, "_generate_guidance_stream", mock_stream):
            chunks = []
            async for chunk in agent.provide_guidance_stream(customer_profile, conversation, use_reasoning=False):
                chunks.append(chunk)
                assert isinstance(chunk, str)
                assert len(chunk) > 0

            # Verify we got multiple chunks
            assert len(chunks) > 1

            # Verify full guidance is coherent
            full_guidance = "".join(chunks)
            assert len(full_guidance) > 0

    @pytest.mark.asyncio
    async def test_provide_guidance_stream_with_reasoning(self, advisor_profile, customer_profile):
        """Test streaming with chain-of-thought reasoning."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=True)
        conversation = []

        # Mock reasoning generation
        async def mock_generate_reasoning(*args, **kwargs):
            return "Customer is 55 and can access pension..."

        # Mock streaming with reasoning
        async def mock_stream_with_reasoning(*args, **kwargs):
            test_chunks = ["Based ", "on ", "your ", "situation..."]
            for chunk in test_chunks:
                yield chunk

        with patch.object(agent, "_generate_reasoning", mock_generate_reasoning):
            with patch.object(agent, "_generate_guidance_from_reasoning_stream", mock_stream_with_reasoning):
                chunks = []
                async for chunk in agent.provide_guidance_stream(customer_profile, conversation):
                    chunks.append(chunk)

                # Verify we got chunks
                assert len(chunks) > 0
                full_guidance = "".join(chunks)
                assert len(full_guidance) > 0

    @pytest.mark.asyncio
    async def test_provide_guidance_stream_triggers_async_validation(self, advisor_profile, customer_profile):
        """Test that streaming triggers background validation."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)
        conversation = []

        # Mock streaming
        async def mock_stream(*args, **kwargs):
            yield "Test guidance chunk"

        # Mock async validation
        mock_validate_async = AsyncMock(return_value=ValidationResult(
            passed=True,
            confidence=0.95,
            issues=[],
            requires_human_review=False,
        ))

        with patch.object(agent, "_generate_guidance_stream", mock_stream):
            with patch.object(agent, "_validate_and_record_async", mock_validate_async):
                chunks = []
                async for chunk in agent.provide_guidance_stream(customer_profile, conversation, use_reasoning=False):
                    chunks.append(chunk)

                # Give async task time to execute
                await asyncio.sleep(0.1)

                # Verify validation was called asynchronously
                assert mock_validate_async.called


class TestGenerateGuidanceStream:
    """Tests for _generate_guidance_stream async generator method."""

    @pytest.fixture
    def advisor_profile(self):
        """Create an advisor profile."""
        return AdvisorProfile(name="Sarah", description="Test advisor")

    @pytest.fixture
    def customer_profile(self):
        """Create a customer profile."""
        return CustomerProfile(
            demographics=CustomerDemographics(
                age=55,
                gender="M",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            presenting_question="Can I access my pension?",
        )

    @pytest.fixture
    def context(self):
        """Create a retrieved context."""
        return RetrievedContext(
            memories=[],
            cases=[],
            rules=[],
            fca_requirements="Stay within guidance boundary",
        )

    @pytest.mark.asyncio
    async def test_generate_guidance_stream_exists(self, advisor_profile):
        """Test that _generate_guidance_stream method exists."""
        agent = AdvisorAgent(profile=advisor_profile)

        assert hasattr(agent, "_generate_guidance_stream")
        import inspect
        assert inspect.isasyncgenfunction(agent._generate_guidance_stream)

    @pytest.mark.asyncio
    async def test_generate_guidance_stream_calls_llm_with_streaming(
        self, advisor_profile, customer_profile, context
    ):
        """Test that stream calls LLM with stream=True."""
        agent = AdvisorAgent(profile=advisor_profile)
        conversation = []

        # Mock streaming LLM response
        class MockStreamResponse:
            def __iter__(self):
                chunks = [
                    MagicMock(choices=[MagicMock(delta=MagicMock(content="Test "))]),
                    MagicMock(choices=[MagicMock(delta=MagicMock(content="stream"))]),
                    MagicMock(choices=[MagicMock(delta=MagicMock(content=None))]),  # End of stream
                ]
                return iter(chunks)

        with patch("guidance_agent.advisor.agent.completion") as mock_completion:
            mock_completion.return_value = MockStreamResponse()

            chunks = []
            async for chunk in agent._generate_guidance_stream(
                customer_profile, context, conversation
            ):
                chunks.append(chunk)

            # Verify LLM was called with stream=True
            assert mock_completion.called
            call_kwargs = mock_completion.call_args.kwargs
            assert call_kwargs.get("stream") == True

    @pytest.mark.asyncio
    async def test_generate_guidance_stream_yields_content_only(
        self, advisor_profile, customer_profile, context
    ):
        """Test that stream yields only content chunks, not None."""
        agent = AdvisorAgent(profile=advisor_profile)
        conversation = []

        # Mock streaming response with some None content
        class MockStreamResponse:
            def __iter__(self):
                chunks = [
                    MagicMock(choices=[MagicMock(delta=MagicMock(content="Hello"))]),
                    MagicMock(choices=[MagicMock(delta=MagicMock(content=None))]),  # Should be skipped
                    MagicMock(choices=[MagicMock(delta=MagicMock(content=" world"))]),
                ]
                return iter(chunks)

        with patch("guidance_agent.advisor.agent.completion") as mock_completion:
            mock_completion.return_value = MockStreamResponse()

            chunks = []
            async for chunk in agent._generate_guidance_stream(
                customer_profile, context, conversation
            ):
                chunks.append(chunk)

            # Should only have 2 chunks (None should be filtered out)
            assert len(chunks) == 2
            assert chunks[0] == "Hello"
            assert chunks[1] == " world"


class TestStreamingPerformance:
    """Tests for streaming performance metrics (TTFT)."""

    @pytest.fixture
    def advisor_profile(self):
        """Create an advisor profile."""
        return AdvisorProfile(name="Sarah", description="Test advisor")

    @pytest.fixture
    def customer_profile(self):
        """Create a customer profile."""
        return CustomerProfile(
            demographics=CustomerDemographics(
                age=55,
                gender="M",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            presenting_question="Can I access my pension?",
        )

    @pytest.mark.asyncio
    async def test_streaming_time_to_first_token_is_fast(
        self, advisor_profile, customer_profile
    ):
        """Test that first token arrives quickly (< 2s target)."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)
        conversation = []

        # Mock streaming with delayed chunks to simulate real LLM
        async def mock_stream(*args, **kwargs):
            # First chunk arrives quickly
            yield "First chunk"
            await asyncio.sleep(0.1)
            yield "Second chunk"

        with patch.object(agent, "_generate_guidance_stream", mock_stream):
            start_time = time.time()
            first_token_time = None

            async for chunk in agent.provide_guidance_stream(customer_profile, conversation, use_reasoning=False):
                if first_token_time is None:
                    first_token_time = time.time()
                    # Only check first chunk then break
                    break

            # Verify first token arrived quickly (should be nearly instant with mock)
            time_to_first_token = first_token_time - start_time
            assert time_to_first_token < 2.0, f"TTFT too high: {time_to_first_token}s"

    @pytest.mark.asyncio
    async def test_streaming_buffers_guidance_for_validation(
        self, advisor_profile, customer_profile
    ):
        """Test that streaming collects chunks for post-stream validation."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)
        conversation = []

        # Track what was sent to validation
        validation_guidance = None

        async def mock_validate_async(guidance, customer, context):
            nonlocal validation_guidance
            validation_guidance = guidance
            return ValidationResult(passed=True, confidence=0.95, issues=[], requires_human_review=False)

        async def mock_stream(*args, **kwargs):
            yield "Chunk 1 "
            yield "Chunk 2 "
            yield "Chunk 3"

        with patch.object(agent, "_generate_guidance_stream", mock_stream):
            with patch.object(agent, "_validate_and_record_async", mock_validate_async):
                chunks = []
                async for chunk in agent.provide_guidance_stream(customer_profile, conversation, use_reasoning=False):
                    chunks.append(chunk)

                # Give async validation time to run
                await asyncio.sleep(0.1)

                # Verify full guidance was passed to validation
                expected_full = "Chunk 1 Chunk 2 Chunk 3"
                assert validation_guidance == expected_full


class TestParallelValidation:
    """Tests for parallel/async validation during streaming."""

    @pytest.fixture
    def advisor_profile(self):
        """Create an advisor profile."""
        return AdvisorProfile(name="Sarah", description="Test advisor")

    @pytest.fixture
    def customer_profile(self):
        """Create a customer profile."""
        return CustomerProfile(
            demographics=CustomerDemographics(
                age=55,
                gender="M",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            presenting_question="Can I access my pension?",
        )

    @pytest.mark.asyncio
    async def test_validate_and_record_async_exists(self, advisor_profile):
        """Test that _validate_and_record_async method exists."""
        agent = AdvisorAgent(profile=advisor_profile)

        assert hasattr(agent, "_validate_and_record_async")
        assert asyncio.iscoroutinefunction(agent._validate_and_record_async)

    @pytest.mark.asyncio
    async def test_validate_and_record_async_calls_validator(
        self, advisor_profile, customer_profile
    ):
        """Test that async validation calls the compliance validator."""
        agent = AdvisorAgent(profile=advisor_profile)
        context = RetrievedContext()
        guidance = "Test guidance text"

        # Mock the async validator
        mock_validate_async = AsyncMock(return_value=ValidationResult(
            passed=True,
            confidence=0.95,
            issues=[],
            requires_human_review=False,
        ))

        with patch.object(agent.compliance_validator, "validate_async", mock_validate_async):
            result = await agent._validate_and_record_async(guidance, customer_profile, context)

            # Verify validator was called
            assert mock_validate_async.called
            call_args = mock_validate_async.call_args
            assert call_args.kwargs["guidance"] == guidance

    @pytest.mark.asyncio
    async def test_validate_and_record_async_returns_validation_result(
        self, advisor_profile, customer_profile
    ):
        """Test that async validation returns ValidationResult."""
        agent = AdvisorAgent(profile=advisor_profile)
        context = RetrievedContext()
        guidance = "Test guidance"

        expected_result = ValidationResult(
            passed=True,
            confidence=0.90,
            issues=[],
            requires_human_review=False,
        )

        mock_validate_async = AsyncMock(return_value=expected_result)

        with patch.object(agent.compliance_validator, "validate_async", mock_validate_async):
            result = await agent._validate_and_record_async(guidance, customer_profile, context)

            assert result == expected_result
            assert result.passed == True
            assert result.confidence == 0.90

    @pytest.mark.asyncio
    async def test_parallel_validation_during_streaming(
        self, advisor_profile, customer_profile
    ):
        """Test that validation runs in parallel with streaming."""
        agent = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)
        conversation = []

        # Track timing
        stream_start = None
        validation_start = None
        validation_called = asyncio.Event()

        async def mock_stream(*args, **kwargs):
            nonlocal stream_start
            stream_start = time.time()
            for i in range(3):
                yield f"Chunk {i} "
                await asyncio.sleep(0.05)  # Simulate streaming delay

        async def mock_validate(*args, **kwargs):
            nonlocal validation_start
            validation_start = time.time()
            validation_called.set()
            await asyncio.sleep(0.05)  # Simulate validation work
            return ValidationResult(passed=True, confidence=0.95, issues=[], requires_human_review=False)

        with patch.object(agent, "_generate_guidance_stream", mock_stream):
            with patch.object(agent, "_validate_and_record_async", mock_validate):
                chunks = []
                async for chunk in agent.provide_guidance_stream(customer_profile, conversation, use_reasoning=False):
                    chunks.append(chunk)

                # Wait for validation to be called
                await asyncio.wait_for(validation_called.wait(), timeout=1.0)

                # Validation should have started after stream completed
                assert validation_start is not None
                assert stream_start is not None
