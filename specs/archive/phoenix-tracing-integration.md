# Phoenix Tracing Integration Fix

## Problem Statement

Phoenix UI is accessible at http://localhost:6006 but no traces appear in the projects view, despite:
- Phoenix service running in Docker
- Dependencies installed (`arize-phoenix`, `openinference-instrumentation-litellm`)
- Environment variables configured in `.env`:
  - `PHOENIX_COLLECTOR_ENDPOINT=http://localhost:4317`
  - `PHOENIX_PROJECT_NAME=guidance-agent`

## Root Cause

The Phoenix instrumentation setup exists in `src/guidance_agent/core/llm_config.py` but **this module is never imported** anywhere in the application. Even though the module has auto-setup code at the bottom:

```python
if PHOENIX_AVAILABLE and os.getenv("PHOENIX_AUTO_SETUP", "true").lower() == "true":
    setup_phoenix_tracing()
```

This code never executes because no entry point imports the module. Therefore:
- `LiteLLMInstrumentor().instrument()` is never called
- LiteLLM calls remain uninstrumented
- No spans are exported to Phoenix

## Current State

### What's Working ✅

**Infrastructure:**
- Phoenix dependencies installed in `pyproject.toml`
- Phoenix service configured in `docker-compose.yml` (ports 4317/6006)
- Environment variables properly set
- Phoenix UI accessible

**Code:**
- Complete instrumentation setup exists in `src/guidance_agent/core/llm_config.py`
- `setup_phoenix_tracing()` function with:
  - LiteLLM auto-instrumentation
  - OTLP exporter configuration
  - OpenTelemetry tracer provider setup
- Experiment tracking in `src/guidance_agent/evaluation/experiments.py` uses OpenTelemetry

### What's Missing ❌

**Integration:**
- `llm_config.py` never imported in application entry points
- API server (`src/guidance_agent/api/main.py`) doesn't initialize tracing
- Training script (`scripts/train_advisor.py`) doesn't initialize tracing
- Auto-instrumentation never triggered
- No spans being exported to Phoenix

## LLM Call Sites (All Will Be Auto-Traced)

Once instrumentation is enabled, all these LiteLLM calls will automatically be traced:

### Advisor Agent (`src/guidance_agent/advisor/agent.py`)
- Line 218-224: Streaming guidance generation
- Line 252-259: Streaming with reasoning
- Line 376-381: Standard guidance generation
- Line 409-414: Reasoning generation
- Line 439-444: Guidance from reasoning
- Line 474-479: Compliance refinement
- Line 509-514: Borderline case handling
- **Model**: `LITELLM_MODEL_ADVISOR` (default: gpt-4-turbo-preview)

### Customer Agent (`src/guidance_agent/customer/agent.py`)
- Line 87-91: Comprehension simulation
- Line 137-141: Customer response generation
- **Model**: `LITELLM_MODEL_CUSTOMER` (default: gpt-4o-mini)

### Customer Simulator (`src/guidance_agent/customer/simulator.py`)
- Line 47-51: Outcome simulation
- **Model**: `LITELLM_MODEL_CUSTOMER` (default: gpt-4o-mini)

### Customer Generator (`src/guidance_agent/customer/generator.py`)
- Line 60-64: Demographics generation
- Line 108-112: Financial situation generation
- Line 184-188: Pension pots generation
- Line 252-256: Goals and inquiry generation
- **Model**: `LITELLM_MODEL_CUSTOMER` (default: gpt-4o-mini)

### Compliance Validator (`src/guidance_agent/compliance/validator.py`)
- Line 116-121: Compliance validation
- Line 157-162: Async compliance validation
- **Model**: `LITELLM_MODEL_COMPLIANCE` (default: gpt-4-turbo-preview)

### Embeddings (`src/guidance_agent/retrieval/embeddings.py`)
- Line 53-56: Embedding generation
- **Model**: `LITELLM_MODEL_EMBEDDINGS` (default: text-embedding-3-small)

## Implementation Steps

### 1. Update Environment-Based Setup

Modify `src/guidance_agent/core/llm_config.py` to only enable tracing in development:

```python
# Change line 83-84 from:
if PHOENIX_AVAILABLE and os.getenv("PHOENIX_AUTO_SETUP", "true").lower() == "true":
    setup_phoenix_tracing()

# To:
if (
    PHOENIX_AVAILABLE
    and os.getenv("ENVIRONMENT") == "development"
    and os.getenv("PHOENIX_AUTO_SETUP", "true").lower() == "true"
):
    setup_phoenix_tracing()
```

### 2. Initialize Tracing in API Entry Point

Add import to `src/guidance_agent/api/main.py` at the top of the file (after other imports):

```python
# Initialize Phoenix tracing before any LLM calls
from guidance_agent.core import llm_config  # noqa: F401
```

The `# noqa: F401` comment prevents linters from complaining about unused import.

### 3. Initialize Tracing in Training Script

Add import to `scripts/train_advisor.py` near the top (after other guidance_agent imports):

```python
# Initialize Phoenix tracing for training experiments
from guidance_agent.core import llm_config  # noqa: F401
```

### 4. Verify Test Isolation

Confirm that `tests/conftest.py` has the auto-use fixture that disables Phoenix for tests (already present):

```python
@pytest.fixture(autouse=True)
def disable_phoenix_tracing(monkeypatch):
    """Disable Phoenix tracing for tests to avoid external dependencies."""
    monkeypatch.setenv("PHOENIX_AUTO_SETUP", "false")
```

### 5. Restart Services

```bash
# Stop current API server
pkill -f "uvicorn guidance_agent.api.main:app"

# Restart with development environment
ENVIRONMENT=development uvicorn guidance_agent.api.main:app --reload
```

### 6. Verify Tracing is Working

1. **Make a test API request:**
   ```bash
   curl -X POST http://localhost:8000/api/consultations \
     -H "Content-Type: application/json" \
     -d '{
       "customer_profile": {
         "demographics": {"name": "Test", "age": 45},
         "financial_situation": {"annual_income": 50000},
         "pension_pots": [],
         "goals": "Test inquiry"
       }
     }'
   ```

2. **Check Phoenix UI:**
   - Open http://localhost:6006/projects
   - Should see `guidance-agent` project
   - Click to view traces with LLM spans

3. **Verify trace details should include:**
   - LLM model name
   - Prompt and completion
   - Token counts
   - Latency
   - All agent interactions (Advisor, Customer, Compliance)

## Configuration Reference

### Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `PHOENIX_COLLECTOR_ENDPOINT` | `http://localhost:4317` | OTLP endpoint for Phoenix |
| `PHOENIX_PROJECT_NAME` | `guidance-agent` | Project name in Phoenix UI |
| `ENVIRONMENT` | `development` | Required for tracing to activate |
| `PHOENIX_AUTO_SETUP` | `true` (default) | Enable/disable auto-instrumentation |

### Docker Compose

Phoenix service configuration in `docker-compose.yml`:
```yaml
phoenix:
  image: arizephoenix/phoenix:latest
  ports:
    - "6006:6006"  # UI
    - "4317:4317"  # OTLP gRPC
```

Start Phoenix:
```bash
docker-compose up phoenix
```

## Architecture Overview

### Request Flow with Tracing

1. **API Request** → `src/guidance_agent/api/routers/consultations.py`
2. **llm_config imported** → `LiteLLMInstrumentor().instrument()` called on startup
3. **AdvisorAgent created** → `src/guidance_agent/advisor/agent.py`
4. **LLM calls made** → `litellm.completion()` automatically traced
5. **Spans exported** → Phoenix OTLP endpoint (port 4317)
6. **Traces visible** → Phoenix UI (port 6006)

### What Gets Traced Automatically

With LiteLLM instrumentation enabled, each LLM call automatically captures:
- **Span attributes**: model, provider, operation type
- **Input**: prompts, messages, parameters
- **Output**: completions, token counts
- **Metadata**: latency, timestamps, status
- **Context**: parent spans for full request trace

## Testing

### Manual Testing

1. Start Phoenix: `docker-compose up phoenix`
2. Set environment: `export ENVIRONMENT=development`
3. Start API: `uvicorn guidance_agent.api.main:app --reload`
4. Make API request (see verification step above)
5. Check Phoenix UI for traces

### Automated Testing

Tests should NOT send traces (already handled):
- `tests/conftest.py` sets `PHOENIX_AUTO_SETUP=false`
- This prevents test pollution in Phoenix
- Tests run without external dependencies

## Troubleshooting

### No traces appearing after fix

1. **Check Phoenix is running:**
   ```bash
   curl http://localhost:6006
   # Should return Phoenix UI HTML
   ```

2. **Check OTLP endpoint:**
   ```bash
   curl http://localhost:4317
   # Should connect (may return binary data)
   ```

3. **Verify environment variable:**
   ```bash
   echo $ENVIRONMENT
   # Should output: development
   ```

4. **Check instrumentation initialized:**
   - Look for log output on API startup indicating Phoenix setup
   - Add debug logging to `setup_phoenix_tracing()` if needed

5. **Verify LiteLLM calls are happening:**
   - Check API logs for LLM activity
   - Ensure requests are actually triggering agent code

### Traces appearing in wrong project

- Check `PHOENIX_PROJECT_NAME` environment variable
- Restart API after changing project name

### Performance concerns

- Phoenix tracing adds minimal overhead (<1% in most cases)
- Only enabled in development environment
- Can be disabled per-request if needed by setting `PHOENIX_AUTO_SETUP=false`

## Future Enhancements

1. **Custom Spans**: Add manual spans for business logic tracing
2. **Metadata**: Enrich spans with customer context, session IDs
3. **Sampling**: Configure trace sampling for high-volume production
4. **Metrics**: Add OpenTelemetry metrics for latency, throughput
5. **Logging**: Integrate logs with traces for correlation

## References

- [Phoenix Documentation](https://docs.arize.com/phoenix)
- [LiteLLM Instrumentation](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-litellm)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
