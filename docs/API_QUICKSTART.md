# API Quick Start Guide

## Prerequisites

- Python 3.11+
- PostgreSQL database running
- Environment variables configured

## Installation

```bash
# Install dependencies
uv sync

# Or with pip
pip install -e .
```

## Configuration

Create a `.env` file:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/guidance_agent

# LLM
LITELLM_MODEL_ADVISOR=gpt-4-turbo-preview
OPENAI_API_KEY=your-key-here

# Admin
ADMIN_TOKEN=your-secure-token
```

## Running the API

### Development Mode

```bash
# With uvicorn directly
uvicorn guidance_agent.api.main:app --reload --port 8000

# With Python module
python -m guidance_agent.api.main
```

### Access Interactive Documentation

```bash
# Swagger UI
open http://localhost:8000/api/docs

# ReDoc
open http://localhost:8000/api/redoc
```

## Quick API Tour

### 1. Create a Consultation

```bash
curl -X POST http://localhost:8000/api/consultations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Smith",
    "age": 52,
    "initial_query": "I have 4 different pensions from old jobs. Can I combine them?"
  }'
```

Response:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "customer_id": "223e4567-e89b-12d3-a456-426614174001",
  "advisor_name": "Sarah",
  "status": "active",
  "created_at": "2025-11-02T10:30:00Z"
}
```

### 2. Send a Customer Message

```bash
curl -X POST http://localhost:8000/api/consultations/{consultation_id}/messages \
  -H "Content-Type: application/json" \
  -d '{
    "content": "I am not sure what type they are"
  }'
```

### 3. Stream Advisor Response (SSE)

```bash
curl -N http://localhost:8000/api/consultations/{consultation_id}/stream
```

Response (Server-Sent Events):
```
data: {"type":"chunk","content":"I understand "}

data: {"type":"chunk","content":"why managing "}

data: {"type":"chunk","content":"multiple pensions "}

data: {"type":"chunk","content":"feels complicated. "}

data: {"type":"complete","compliance_score":0.97,"compliance_confidence":0.97,"full_message":"I understand why managing multiple pensions feels complicated. ..."}
```

### 4. Get Consultation Details

```bash
curl http://localhost:8000/api/consultations/{consultation_id}
```

### 5. Admin: View Compliance Metrics

```bash
curl http://localhost:8000/api/admin/metrics/compliance?days=30 \
  -H "Authorization: Bearer admin-token"
```

Response:
```json
{
  "total_consultations": 45,
  "avg_compliance_score": 0.96,
  "compliant_percentage": 95.6,
  "avg_satisfaction": 8.3,
  "period_start": "2025-10-03T00:00:00Z",
  "period_end": "2025-11-02T00:00:00Z"
}
```

## Frontend Integration Example

### JavaScript/TypeScript

```typescript
// Create consultation
const response = await fetch('http://localhost:8000/api/consultations', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'John Smith',
    age: 52,
    initial_query: 'Can I combine my pensions?',
  }),
});
const consultation = await response.json();

// Send message
await fetch(`http://localhost:8000/api/consultations/${consultation.id}/messages`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ content: 'Tell me more' }),
});

// Stream response
const eventSource = new EventSource(
  `http://localhost:8000/api/consultations/${consultation.id}/stream`
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'chunk') {
    // Append chunk to display
    displayText += data.content;
  } else if (data.type === 'complete') {
    // Show compliance badge
    showComplianceBadge(data.compliance_score);
    eventSource.close();
  } else if (data.type === 'error') {
    // Handle error
    console.error(data.error);
    eventSource.close();
  }
};
```

## Testing

```bash
# Run all API tests
pytest tests/api/ -v

# Run specific test file
pytest tests/api/test_consultations.py -v

# Run with coverage
pytest tests/api/ --cov=guidance_agent.api --cov-report=html

# Open coverage report
open htmlcov/index.html
```

## Common Issues

### Issue: CORS errors from frontend

**Solution**: Add your frontend URL to CORS origins in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://your-frontend-url",  # Add this
    ],
    ...
)
```

### Issue: Database connection errors

**Solution**: Verify PostgreSQL is running and DATABASE_URL is correct:

```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### Issue: SSE connection drops

**Solution**: Add keep-alive headers and increase timeout:

```python
# In nginx config
proxy_read_timeout 300s;
proxy_http_version 1.1;
proxy_set_header Connection "";
```

## API Endpoints Reference

### Consultations

- `POST /api/consultations` - Create consultation
- `GET /api/consultations/{id}` - Get consultation details
- `GET /api/consultations` - List consultations (paginated)
- `POST /api/consultations/{id}/messages` - Send message
- `GET /api/consultations/{id}/stream` - Stream guidance (SSE)
- `POST /api/consultations/{id}/end` - End consultation
- `GET /api/consultations/{id}/metrics` - Get metrics

### Customers

- `GET /api/customers/{id}` - Get customer profile
- `GET /api/customers/{id}/consultations` - List customer consultations

### Admin (requires auth)

- `GET /api/admin/consultations` - List with filters
- `GET /api/admin/consultations/{id}` - Detailed review
- `GET /api/admin/metrics/compliance` - Compliance metrics
- `GET /api/admin/metrics/time-series` - Time-series data
- `GET /api/admin/consultations/{id}/export` - Export consultation

### Utility

- `GET /health` - Health check
- `GET /` - API information

## Production Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .

CMD ["uvicorn", "guidance_agent.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### With Gunicorn + Uvicorn Workers

```bash
gunicorn guidance_agent.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## Next Steps

1. **Build Frontend**: Start Phase 4 - Vue.js chat interface
2. **Add Monitoring**: Integrate logging and metrics
3. **Enhance Auth**: Replace simple token with JWT
4. **Add Rate Limiting**: Prevent API abuse
5. **Enable Caching**: Use Redis for frequently accessed data

## Support

- **Documentation**: See `docs/API_INTEGRATION.md` for detailed integration guide
- **Tests**: See `tests/api/` for usage examples
- **Interactive Docs**: Visit `/api/docs` for live API exploration
