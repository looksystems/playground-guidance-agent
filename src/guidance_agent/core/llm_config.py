"""LLM configuration with Phoenix observability integration.

This module sets up automatic tracing of all LiteLLM calls to Phoenix
using OpenTelemetry instrumentation.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Phoenix instrumentation for LiteLLM
try:
    from openinference.instrumentation.litellm import LiteLLMInstrumentor
    from opentelemetry import trace as trace_api
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk import trace as trace_sdk
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor

    PHOENIX_AVAILABLE = True
except ImportError:
    PHOENIX_AVAILABLE = False
    print("Warning: Phoenix instrumentation not available. Install with:")
    print("  uv add arize-phoenix openinference-instrumentation-litellm")


def setup_phoenix_tracing() -> bool:
    """Set up Phoenix tracing for LiteLLM.

    Configures OpenTelemetry to automatically trace all LiteLLM calls
    to the Phoenix observability platform.

    Returns:
        True if setup successful, False otherwise
    """
    if not PHOENIX_AVAILABLE:
        return False

    # Get Phoenix endpoint from environment
    endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:4317")
    project_name = os.getenv("PHOENIX_PROJECT_NAME", "guidance-agent")

    try:
        # Set up OpenTelemetry tracer for Phoenix
        resource = Resource.create(attributes={"service.name": project_name})
        tracer_provider = trace_sdk.TracerProvider(resource=resource)

        # Configure OTLP exporter to send to Phoenix
        span_exporter = OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces")
        tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))

        # Set as global tracer provider
        trace_api.set_tracer_provider(tracer_provider)

        # Instrument LiteLLM - this automatically traces ALL LiteLLM calls!
        LiteLLMInstrumentor().instrument()

        print(f"✓ Phoenix tracing enabled: {endpoint}")
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
