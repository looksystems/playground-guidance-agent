# Phoenix Tracing Setup

This document describes the Phoenix tracing setup for the guidance-agent application.

## Current Status

✅ **Phoenix tracing fully functional with async compatibility**
- Using `BatchSpanProcessor` for async-compatible trace export
- No more "socket.send() raised exception" errors
- Comprehensive test suite in `tests/integration/test_phoenix_tracing.py`
- Phoenix UI accessible at http://localhost:6006/projects
- LiteLLM instrumentation properly configured
- Works seamlessly with FastAPI backend

## Working Configuration

Phoenix tracing is configured with `BatchSpanProcessor` for async compatibility:

```python
from phoenix.otel import register
from openinference.instrumentation.litellm import LiteLLMInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Register Phoenix tracer provider
tracer_provider = register(
    project_name="guidance-agent",
    endpoint="http://localhost:4317",
)

# Add BatchSpanProcessor for async compatibility
exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",
    insecure=True
)
batch_processor = BatchSpanProcessor(
    exporter,
    max_queue_size=2048,
    schedule_delay_millis=5000,  # Send every 5 seconds
    max_export_batch_size=512,
)
tracer_provider.add_span_processor(batch_processor)

# Instrument LiteLLM
LiteLLMInstrumentor().instrument()
```

This configuration is implemented in `src/guidance_agent/core/llm_config.py:27-79`.

## Solution: BatchSpanProcessor

**Problem:** Phoenix's `register()` uses `SimpleSpanProcessor` by default, which sends spans synchronously and conflicts with FastAPI's async event loop, causing "socket.send() raised exception" errors.

**Solution:** We now use `BatchSpanProcessor` which:
1. Processes spans in batches on a background thread
2. Avoids blocking async operations
3. Provides better performance by batching traces
4. Eliminates socket errors in FastAPI

## Configuration Options

### Enable/Disable Phoenix Tracing

Add to `.env`:
```bash
# Enable Phoenix tracing (default in development)
PHOENIX_AUTO_SETUP=true
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:4317
PHOENIX_PROJECT_NAME=guidance-agent
ENVIRONMENT=development
```

Or disable it:
```bash
PHOENIX_AUTO_SETUP=false
```

### BatchSpanProcessor Settings

The current configuration uses these settings (in `llm_config.py:59-64`):

- `max_queue_size=2048`: Maximum spans to queue before dropping
- `schedule_delay_millis=5000`: Send batches every 5 seconds
- `max_export_batch_size=512`: Maximum spans per batch

These can be tuned based on your needs:
- **Lower latency**: Reduce `schedule_delay_millis` (e.g., 1000ms)
- **Higher throughput**: Increase batch size and queue size
- **Lower memory**: Decrease queue size

## Testing

### Comprehensive Test Suite

We have a full integration test suite in `tests/integration/test_phoenix_tracing.py`:

```bash
# 1. Start Phoenix
docker-compose up phoenix

# 2. Run Phoenix integration tests
pytest tests/integration/test_phoenix_tracing.py -v

# 3. Run streaming test with Phoenix tracing
PHOENIX_AUTO_SETUP=true pytest tests/integration/test_streaming.py::test_streaming_with_phoenix_tracing -v
```

The test suite verifies:
- Basic LiteLLM call tracing
- Multiple sequential calls
- Custom span creation
- Async compatibility (critical for FastAPI)

### Quick Manual Test

Use the standalone test script:

```bash
python test_phoenix_integration.py
```

Then check Phoenix UI at http://localhost:6006/projects for traces.

### What to Verify

After running tests, check the Phoenix UI:
1. Navigate to http://localhost:6006/projects
2. Look for the "test-phoenix-integration" or "guidance-agent" project
3. Verify traces appear with LiteLLM call details
4. Check that there are no "socket.send()" errors in logs

## Environment Variables

```bash
# Phoenix Configuration
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:4317  # Phoenix gRPC endpoint
PHOENIX_PROJECT_NAME=guidance-agent              # Project name in Phoenix UI
PHOENIX_AUTO_SETUP=true                          # Auto-setup on import (set to false to disable)

# Application Settings
ENVIRONMENT=development  # Phoenix only auto-starts in development mode
```

## Key Files

- **`src/guidance_agent/core/llm_config.py:27-79`** - Phoenix tracing setup with BatchSpanProcessor
- **`tests/integration/test_phoenix_tracing.py`** - Comprehensive integration test suite
- **`tests/integration/test_streaming.py:243-292`** - Streaming with Phoenix tracing test
- **`test_phoenix_integration.py`** - Standalone manual test script (legacy)
- **`.env`** - Configuration

## Architecture Notes

### Auto-Setup Behavior

Phoenix tracing auto-setup triggers when (`llm_config.py:95-100`):
1. Phoenix packages are installed (`PHOENIX_AVAILABLE = True`)
2. `ENVIRONMENT=development`
3. `PHOENIX_AUTO_SETUP=true` (default)

This happens automatically when `llm_config` module is imported.

### Test Suite Configuration

Tests disable Phoenix by default (`tests/conftest.py:52-71`):
- Session-scoped fixture sets `PHOENIX_AUTO_SETUP=false`
- Individual Phoenix tests can override this
- Prevents interference with regular test runs

### FastAPI Integration

The application imports `llm_config` early in the FastAPI startup:
- Phoenix tracing starts before any LLM calls
- All LiteLLM calls are automatically traced
- BatchSpanProcessor ensures no async conflicts

## Troubleshooting

### "socket.send() raised exception" Errors

**Fixed!** This was caused by `SimpleSpanProcessor`. We now use `BatchSpanProcessor`.

If you still see these errors:
1. Verify you're using the updated `llm_config.py`
2. Check that BatchSpanProcessor is being used (look for "BatchSpanProcessor" in startup logs)
3. Ensure Phoenix is running: `docker-compose up phoenix`

### Traces Not Appearing in Phoenix UI

1. Check Phoenix is running: http://localhost:6006
2. Verify `PHOENIX_AUTO_SETUP=true` in `.env`
3. Check `ENVIRONMENT=development` in `.env`
4. Look for "✓ Phoenix tracing enabled (BatchSpanProcessor)" in logs
5. Wait 5 seconds for batch export (or check the `schedule_delay_millis` setting)

### Import Errors

If you see "Phoenix instrumentation not available":
```bash
uv add arize-phoenix openinference-instrumentation-litellm
```

## Production Recommendations

### Disable in Production

Set in `.env.production`:
```bash
PHOENIX_AUTO_SETUP=false
ENVIRONMENT=production
```

### Or Use Phoenix Cloud

For production observability, consider [Phoenix Cloud](https://app.phoenix.arize.com):
- Managed infrastructure
- Better security
- Advanced analytics
- No local setup required

Update endpoint:
```bash
PHOENIX_COLLECTOR_ENDPOINT=https://app.phoenix.arize.com/v1/traces
PHOENIX_API_KEY=your-api-key
```

## Support

- Phoenix Docs: https://docs.arize.com/phoenix
- GitHub Issues: https://github.com/Arize-ai/phoenix/issues
- This implementation: See `PHOENIX_TRACING.md` in the repository
