"""LLM configuration with Phoenix observability integration.

This module sets up automatic tracing of all LiteLLM calls to Phoenix
using OpenTelemetry instrumentation with BatchSpanProcessor for async compatibility.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Phoenix instrumentation for LiteLLM
try:
    from openinference.instrumentation.litellm import LiteLLMInstrumentor
    from phoenix.otel import register
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

    PHOENIX_AVAILABLE = True
except ImportError:
    PHOENIX_AVAILABLE = False
    print("Warning: Phoenix instrumentation not available. Install with:")
    print("  uv add arize-phoenix openinference-instrumentation-litellm")


def setup_phoenix_tracing() -> bool:
    """Set up Phoenix tracing for LiteLLM with async-compatible BatchSpanProcessor.

    Configures OpenTelemetry to automatically trace all LiteLLM calls
    to the Phoenix observability platform. Uses BatchSpanProcessor instead
    of SimpleSpanProcessor to avoid async conflicts in FastAPI.

    Returns:
        True if setup successful, False otherwise
    """
    if not PHOENIX_AVAILABLE:
        return False

    # Get Phoenix endpoint from environment
    endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:4317")
    project_name = os.getenv("PHOENIX_PROJECT_NAME", "guidance-agent")

    try:
        # Register Phoenix tracer provider
        tracer_provider = register(
            project_name=project_name,
            endpoint=endpoint,
        )

        # Create a BatchSpanProcessor for async compatibility
        # This processes spans in batches on a background thread,
        # avoiding the "socket.send() raised exception" error
        # that occurs with SimpleSpanProcessor in async contexts
        exporter = OTLPSpanExporter(
            endpoint=endpoint,
            insecure=True  # For local development
        )
        batch_processor = BatchSpanProcessor(
            exporter,
            max_queue_size=2048,
            schedule_delay_millis=5000,  # Send every 5 seconds
            max_export_batch_size=512,
        )

        # Add the batch processor to the tracer provider
        tracer_provider.add_span_processor(batch_processor)

        # Instrument LiteLLM - this automatically traces ALL LiteLLM calls!
        LiteLLMInstrumentor().instrument()

        print(f"✓ Phoenix tracing enabled (BatchSpanProcessor): {endpoint}")
        print(f"  Project: {project_name}")
        print(f"  UI: http://localhost:6006")
        return True

    except Exception as e:
        print(f"Warning: Failed to setup Phoenix tracing: {e}")
        return False


def disable_phoenix_tracing() -> None:
    """Disable Phoenix tracing."""
    if not PHOENIX_AVAILABLE:
        return

    try:
        LiteLLMInstrumentor().uninstrument()
        print("✓ Phoenix tracing disabled")
    except Exception as e:
        print(f"Warning: Failed to disable Phoenix tracing: {e}")


# Auto-setup on module import if Phoenix is available and in development environment
if (
    PHOENIX_AVAILABLE
    and os.getenv("ENVIRONMENT") == "development"
    and os.getenv("PHOENIX_AUTO_SETUP", "true").lower() == "true"
):
    setup_phoenix_tracing()
