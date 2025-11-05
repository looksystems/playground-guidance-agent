"""Integration tests for streaming functionality.

Tests complete consultation flow with streaming:
- End-to-end streaming with real LLM calls (when enabled)
- Multi-turn conversations with streaming
- Phoenix tracing verification for streaming metrics
- Performance benchmarks (TTFT, total time)
"""

import pytest
import asyncio
import time
from typing import List

from guidance_agent.core.types import (
    AdvisorProfile,
    CustomerProfile,
    CustomerDemographics,
    FinancialSituation,
    PensionPot,
)
from guidance_agent.advisor.agent import AdvisorAgent


@pytest.fixture
def advisor_profile():
    """Create advisor profile for integration tests."""
    return AdvisorProfile(
        name="Sarah Chen",
        description="Experienced FCA-regulated pension guidance specialist with 10 years of experience.",
    )


@pytest.fixture
def test_customer():
    """Create a test customer profile."""
    return CustomerProfile(
        demographics=CustomerDemographics(
            age=58,
            gender="F",
            location="Manchester",
            employment_status="employed",
            financial_literacy="medium",
        ),
        financial=FinancialSituation(
            annual_income=45000,
            total_assets=180000,
            total_debt=15000,
            dependents=0,
            risk_tolerance="medium",
        ),
        pensions=[
            PensionPot(
                pot_id="pot1",
                provider="Aviva",
                pot_type="defined_contribution",
                current_value=120000,
                projected_value=150000,
                age_accessible=55,
            )
        ],
        goals="Plan for retirement in 2 years",
        presenting_question="I'm thinking about retiring early at 60. What are my options for accessing my pension?",
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_consultation_with_streaming(advisor_profile, test_customer):
    """Test complete consultation flow with streaming."""
    advisor = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=True)

    conversation = []

    # Simulate customer inquiry
    inquiry = test_customer.presenting_question
    conversation.append({"role": "customer", "content": inquiry})

    # Advisor responds with streaming
    response_chunks: List[str] = []
    chunk_count = 0

    async for chunk in advisor.provide_guidance_stream(test_customer, conversation):
        response_chunks.append(chunk)
        chunk_count += 1
        # Verify each chunk is a string
        assert isinstance(chunk, str)

    # Verify we got multiple chunks
    assert chunk_count > 1, f"Expected multiple chunks, got {chunk_count}"

    # Verify guidance is complete and coherent
    guidance = "".join(response_chunks)
    assert len(guidance) > 200, "Guidance should be substantive"
    conversation.append({"role": "advisor", "content": guidance})

    # Follow-up question
    test_customer.presenting_question = "What about tax implications?"
    conversation.append({"role": "customer", "content": test_customer.presenting_question})

    # Stream second response
    response_chunks_2: List[str] = []
    async for chunk in advisor.provide_guidance_stream(test_customer, conversation):
        response_chunks_2.append(chunk)

    guidance_2 = "".join(response_chunks_2)
    assert len(guidance_2) > 100, "Follow-up guidance should be substantive"
    assert len(response_chunks_2) > 1, "Should stream multiple chunks"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_streaming_performance_metrics(advisor_profile, test_customer):
    """Test streaming performance meets targets."""
    advisor = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)

    # Measure streaming performance
    start_time = time.time()
    first_token_time = None
    last_token_time = None
    chunk_count = 0
    total_length = 0

    async for chunk in advisor.provide_guidance_stream(test_customer, []):
        chunk_count += 1
        total_length += len(chunk)

        if first_token_time is None:
            first_token_time = time.time()

        last_token_time = time.time()

    # Calculate metrics
    ttft = first_token_time - start_time  # Time to first token
    total_time = last_token_time - start_time

    # Performance assertions (targets from spec)
    assert ttft < 2.0, f"TTFT should be < 2s, got {ttft:.2f}s"
    assert total_time < 20.0, f"Total time should be reasonable, got {total_time:.2f}s"
    assert chunk_count > 3, f"Should receive multiple chunks, got {chunk_count}"
    assert total_length > 100, "Should receive substantive content"

    # Log performance metrics
    print(f"\nStreaming Performance:")
    print(f"  Time to First Token: {ttft:.2f}s")
    print(f"  Total Time: {total_time:.2f}s")
    print(f"  Chunks: {chunk_count}")
    print(f"  Total Characters: {total_length}")
    print(f"  Chars/Second: {total_length/total_time:.1f}")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_streaming_with_different_complexity(advisor_profile):
    """Test streaming performance with different question complexities."""
    advisor = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)

    # Simple question
    simple_customer = CustomerProfile(
        demographics=CustomerDemographics(
            age=55,
            gender="M",
            location="London",
            employment_status="employed",
            financial_literacy="high",
        ),
        presenting_question="What is pension freedom?",
    )

    simple_chunks = []
    simple_start = time.time()
    simple_first = None

    async for chunk in advisor.provide_guidance_stream(simple_customer, []):
        if simple_first is None:
            simple_first = time.time()
        simple_chunks.append(chunk)

    simple_ttft = simple_first - simple_start

    # Complex question
    complex_customer = CustomerProfile(
        demographics=CustomerDemographics(
            age=58,
            gender="F",
            location="Bristol",
            employment_status="employed",
            financial_literacy="low",
        ),
        financial=FinancialSituation(
            annual_income=40000,
            total_assets=250000,
            total_debt=50000,
            dependents=2,
            risk_tolerance="low",
        ),
        pensions=[
            PensionPot(
                pot_id="pot1",
                provider="Scottish Widows",
                pot_type="defined_contribution",
                current_value=150000,
                projected_value=180000,
                age_accessible=55,
            ),
            PensionPot(
                pot_id="pot2",
                provider="Standard Life",
                pot_type="defined_benefit",
                current_value=200000,
                projected_value=200000,
                age_accessible=60,
                is_db_scheme=True,
                db_guaranteed_amount=12000,
            ),
        ],
        presenting_question="I have both DB and DC pensions. Should I transfer my DB pension to access it earlier?",
    )

    complex_chunks = []
    complex_start = time.time()
    complex_first = None

    async for chunk in advisor.provide_guidance_stream(complex_customer, []):
        if complex_first is None:
            complex_first = time.time()
        complex_chunks.append(chunk)

    complex_ttft = complex_first - complex_start

    # Both should have good TTFT
    assert simple_ttft < 2.0, f"Simple question TTFT too high: {simple_ttft:.2f}s"
    assert complex_ttft < 2.0, f"Complex question TTFT too high: {complex_ttft:.2f}s"

    # Complex question likely has more chunks
    print(f"\nComplexity Comparison:")
    print(f"  Simple - TTFT: {simple_ttft:.2f}s, Chunks: {len(simple_chunks)}")
    print(f"  Complex - TTFT: {complex_ttft:.2f}s, Chunks: {len(complex_chunks)}")


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.skip(reason="Requires Phoenix setup - enable when Phoenix is running")
async def test_streaming_with_phoenix_tracing(advisor_profile, test_customer):
    """Verify Phoenix captures streaming traces correctly.

    This test requires Phoenix to be running and configured.
    It verifies that Phoenix captures:
    1. Parent span for the streaming operation
    2. Child spans for each LLM call
    3. Streaming metadata (TTFT, chunk count, tokens/sec)
    """
    from opentelemetry import trace

    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("test_streaming_consultation") as span:
        advisor = AdvisorAgent(profile=advisor_profile)

        chunks = []
        start_time = time.time()
        first_token_time = None

        async for chunk in advisor.provide_guidance_stream(test_customer, []):
            if first_token_time is None:
                first_token_time = time.time()
            chunks.append(chunk)

        end_time = time.time()

        # Add custom metrics to span
        span.set_attribute("chunk_count", len(chunks))
        span.set_attribute("ttft", first_token_time - start_time)
        span.set_attribute("total_time", end_time - start_time)
        span.set_attribute("customer_id", test_customer.customer_id if hasattr(test_customer, 'customer_id') else 'test')

    # Phoenix should capture:
    # - The parent span "test_streaming_consultation"
    # - Child spans for LLM calls (with streaming=True)
    # - Metrics like TTFT, tokens/sec, chunk count
    # Manual verification in Phoenix UI


@pytest.mark.asyncio
@pytest.mark.integration
async def test_streaming_backwards_compatibility(advisor_profile, test_customer):
    """Test that non-streaming methods still work (backwards compatibility)."""
    advisor = AdvisorAgent(profile=advisor_profile, use_chain_of_thought=False)

    # Old blocking method should still work
    guidance = advisor.provide_guidance(test_customer, [])

    assert isinstance(guidance, str)
    assert len(guidance) > 100

    # Compare with streaming method
    chunks = []
    async for chunk in advisor.provide_guidance_stream(test_customer, []):
        chunks.append(chunk)

    streaming_guidance = "".join(chunks)

    # Both should produce valid guidance
    assert len(guidance) > 0
    assert len(streaming_guidance) > 0
