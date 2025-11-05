"""LLM configuration with Phoenix observability integration.

This module sets up automatic tracing of all LiteLLM calls to Phoenix
using OpenTelemetry instrumentation with BatchSpanProcessor for async compatibility.
"""

import os
import logging
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Import Phoenix instrumentation for LiteLLM
try:
    from openinference.instrumentation.litellm import LiteLLMInstrumentor
    from phoenix.otel import register
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

    PHOENIX_AVAILABLE = True
except ImportError as e:
    PHOENIX_AVAILABLE = False
    logger.warning(f"Phoenix instrumentation not available: {e}")
    logger.warning("Install with: uv add arize-phoenix openinference-instrumentation-litellm")


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
        # Register Phoenix tracer provider (creates the base tracer)
        tracer_provider = register(
            project_name=project_name,
            endpoint=endpoint,
        )

        # Create OTLP exporter with explicit settings
        # insecure=True allows HTTP instead of HTTPS
        exporter = OTLPSpanExporter(
            endpoint=endpoint,
            insecure=True  # Required for HTTP endpoints
        )

        # Add BatchSpanProcessor for async compatibility
        # This batches spans before sending to reduce overhead
        batch_processor = BatchSpanProcessor(
            exporter,
            max_queue_size=2048,
            schedule_delay_millis=5000,  # Send every 5 seconds
            max_export_batch_size=512,
        )
        tracer_provider.add_span_processor(batch_processor)

        # Instrument LiteLLM - this automatically traces ALL LiteLLM calls!
        instrumentor = LiteLLMInstrumentor()
        instrumentor.instrument()

        logger.info(f"✓ Phoenix tracing enabled (BatchSpanProcessor): {endpoint}")
        logger.info(f"  Project: {project_name}")
        logger.info(f"  UI: http://localhost:6006")
        logger.info("  LiteLLM instrumentation: ACTIVE")

        # Create a test span to verify tracing works
        from opentelemetry import trace
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("phoenix-test-span") as span:
            span.set_attribute("test.type", "initialization")
            span.set_attribute("test.success", True)
            logger.info("  ✓ Test span created - should appear in Phoenix UI")

        return True

    except Exception as e:
        logger.error(f"Failed to setup Phoenix tracing: {e}", exc_info=True)
        return False


def disable_phoenix_tracing() -> None:
    """Disable Phoenix tracing."""
    if not PHOENIX_AVAILABLE:
        return

    try:
        LiteLLMInstrumentor().uninstrument()
        logger.info("✓ Phoenix tracing disabled")
    except Exception as e:
        logger.warning(f"Failed to disable Phoenix tracing: {e}", exc_info=True)


# Auto-setup on module import if Phoenix is available and in development environment
if (
    PHOENIX_AVAILABLE
    and os.getenv("ENVIRONMENT") == "development"
    and os.getenv("PHOENIX_AUTO_SETUP", "true").lower() == "true"
):
    setup_phoenix_tracing()
