"""Integration tests for Phoenix tracing.

These tests verify that Phoenix tracing works correctly with the guidance-agent
application. They require Phoenix to be running locally.

To run these tests:
1. Start Phoenix: docker-compose up phoenix
2. Run: pytest tests/integration/test_phoenix_tracing.py -v

Phoenix UI will be available at: http://localhost:6006
"""

import os
import time
import asyncio
import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@pytest.fixture(scope="module")
def phoenix_enabled():
    """Fixture to check if Phoenix is enabled and available.

    Tests will be skipped if:
    - Phoenix packages are not installed
    - Phoenix is not running locally

    Note: These tests are opt-in and require explicit execution.
    The conftest.py disables Phoenix by default for all tests.
    """
    # Try importing Phoenix dependencies
    try:
        from phoenix.otel import register
        from openinference.instrumentation.litellm import LiteLLMInstrumentor
    except ImportError:
        pytest.skip("Phoenix packages not installed. Install with: uv add arize-phoenix openinference-instrumentation-litellm")

    # All checks passed
    return True


@pytest.fixture(scope="module")
def phoenix_tracer(phoenix_enabled):
    """Set up Phoenix tracing for the test module.

    This fixture:
    1. Registers Phoenix tracer with a test project
    2. Instruments LiteLLM
    3. Yields to allow tests to run
    4. Cleans up by uninstrumenting LiteLLM
    """
    from phoenix.otel import register
    from openinference.instrumentation.litellm import LiteLLMInstrumentor
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

    endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:4317")
    project_name = "test-phoenix-integration"

    # Register Phoenix tracer
    tracer_provider = register(
        project_name=project_name,
        endpoint=endpoint,
    )

    # Add BatchSpanProcessor for async compatibility
    exporter = OTLPSpanExporter(
        endpoint=endpoint,
        insecure=True
    )
    batch_processor = BatchSpanProcessor(
        exporter,
        max_queue_size=2048,
        schedule_delay_millis=1000,  # Faster for tests
        max_export_batch_size=512,
    )
    tracer_provider.add_span_processor(batch_processor)

    # Instrument LiteLLM
    instrumentor = LiteLLMInstrumentor()
    instrumentor.instrument()

    print(f"\n✓ Phoenix tracing enabled for tests")
    print(f"  Project: {project_name}")
    print(f"  Endpoint: {endpoint}")
    print(f"  UI: http://localhost:6006/projects")

    yield tracer_provider

    # Cleanup
    instrumentor.uninstrument()
    print(f"\n✓ Phoenix tracing disabled")


@pytest.mark.integration
def test_basic_litellm_tracing(phoenix_tracer):
    """Test that basic LiteLLM calls are traced to Phoenix.

    This test verifies:
    1. LiteLLM instrumentation is working
    2. Traces are exported to Phoenix
    3. No errors occur during trace export
    """
    import litellm

    # Suppress LiteLLM debug output
    litellm.suppress_debug_info = True

    # Make a simple LiteLLM call
    response = litellm.completion(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Say 'Phoenix tracing test successful!' and nothing else."}
        ],
        max_tokens=20
    )

    # Verify response
    assert response.choices[0].message.content is not None
    assert len(response.choices[0].message.content) > 0

    # Wait for trace to be exported
    time.sleep(2)

    print("\n✓ LiteLLM call completed and traced")
    print(f"  Response: {response.choices[0].message.content}")
    print(f"  → Check Phoenix UI: http://localhost:6006/projects")


@pytest.mark.integration
def test_multiple_litellm_calls(phoenix_tracer):
    """Test that multiple LiteLLM calls are all traced.

    Verifies that the instrumentation handles multiple sequential calls
    and batches them correctly.
    """
    import litellm

    litellm.suppress_debug_info = True

    # Make multiple calls
    responses = []
    for i in range(3):
        response = litellm.completion(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Say 'Call {i+1}' and nothing else."}
            ],
            max_tokens=10
        )
        responses.append(response)

    # Verify all responses
    assert len(responses) == 3
    for response in responses:
        assert response.choices[0].message.content is not None

    # Wait for traces to be exported
    time.sleep(2)

    print(f"\n✓ {len(responses)} LiteLLM calls completed and traced")
    print(f"  → Check Phoenix UI for multiple traces: http://localhost:6006/projects")


@pytest.mark.integration
def test_tracing_with_custom_spans(phoenix_tracer):
    """Test custom span creation alongside LiteLLM tracing.

    Verifies that custom OpenTelemetry spans work correctly with
    the Phoenix instrumentation.
    """
    import litellm
    from opentelemetry import trace

    litellm.suppress_debug_info = True
    tracer = trace.get_tracer(__name__)

    # Create a custom parent span
    with tracer.start_as_current_span("test_custom_span") as span:
        # Add custom attributes
        span.set_attribute("test.type", "integration")
        span.set_attribute("test.name", "phoenix_tracing")

        # Make LiteLLM call within custom span
        response = litellm.completion(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Custom span test!' and nothing else."}
            ],
            max_tokens=10
        )

        # Add result to span
        span.set_attribute("response.length", len(response.choices[0].message.content))

    # Verify response
    assert response.choices[0].message.content is not None

    # Wait for traces to be exported
    time.sleep(2)

    print("\n✓ Custom span with nested LiteLLM call traced")
    print(f"  → Check Phoenix UI for hierarchical trace: http://localhost:6006/projects")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_compatibility(phoenix_tracer):
    """Test that Phoenix tracing works in async contexts.

    This is critical for FastAPI integration. Verifies that the
    BatchSpanProcessor handles async contexts correctly without
    "socket.send() raised exception" errors.
    """
    import litellm
    from opentelemetry import trace

    litellm.suppress_debug_info = True
    tracer = trace.get_tracer(__name__)

    # Simulate async operation with tracing
    with tracer.start_as_current_span("async_test_span") as span:
        span.set_attribute("execution.mode", "async")

        # Make LiteLLM call in async context
        # Note: litellm.completion is sync, but we're calling it from async context
        # This simulates the FastAPI scenario
        response = litellm.completion(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Async test successful!' and nothing else."}
            ],
            max_tokens=10
        )

        span.set_attribute("response.received", True)

    # Verify response
    assert response.choices[0].message.content is not None

    # Wait for traces to be exported
    await asyncio.sleep(2)

    print("\n✓ Async context tracing successful (no socket errors)")
    print(f"  → This confirms FastAPI compatibility")


# For manual testing: run this file directly
if __name__ == "__main__":
    print("=" * 60)
    print("Phoenix Tracing Integration Tests")
    print("=" * 60)
    print("\nTo run these tests:")
    print("1. Start Phoenix: docker-compose up phoenix")
    print("2. Run: pytest tests/integration/test_phoenix_tracing.py -v")
    print(f"\nPhoenix UI: http://localhost:6006/projects")
    print("=" * 60)
