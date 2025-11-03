# Docker Setup Guide

This guide explains how to set up and run the Pension Guidance Agent using Docker.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB of available RAM
- At least 10GB of disk space

## Quick Start

1. **Clone the repository and navigate to the project directory**

```bash
cd guidance-agent
```

2. **Create environment file**

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
OPENAI_API_KEY=sk-your-key-here
# or
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

3. **Deploy the application**

```bash
./scripts/deploy.sh
```

This will:
- Build all Docker images
- Start all services (Postgres, Phoenix, Backend, Frontend)
- Run database migrations
- Perform health checks

4. **Access the application**

- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs
- Phoenix Observability: http://localhost:6006

## Architecture

The Docker setup consists of 4 services:

### 1. PostgreSQL with pgvector
- Database for storing consultations, customers, and embeddings
- Includes pgvector extension for vector similarity search
- Port: 5432
- Data persisted in `postgres_data` volume

### 2. Phoenix (Arize)
- LLM observability and tracing
- Monitors all LLM interactions
- Port: 6006 (UI), 4317 (OTLP)
- Data persisted in `phoenix_data` volume

### 3. Backend (FastAPI)
- Python 3.11 application
- Runs with Uvicorn server
- Port: 8000
- Auto-runs database migrations on startup

### 4. Frontend (Vue.js + Nginx)
- Multi-stage build (Node.js → Nginx)
- SPA with client-side routing
- Port: 80
- Proxies API requests to backend

## Service Management

### Start Services

```bash
docker-compose up -d
```

### Stop Services

```bash
docker-compose down
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart Service

```bash
docker-compose restart backend
```

### Rebuild Service

```bash
docker-compose build --no-cache backend
docker-compose up -d backend
```

## Health Checks

All services have health check endpoints:

### Backend Health
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "database": true,
  "llm": true,
  "timestamp": "2025-11-02T12:00:00"
}
```

### Frontend Health
```bash
curl http://localhost/health
```

## Environment Variables

### Backend Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | `postgresql://postgres:postgres@postgres:5432/guidance_agent` |
| `OPENAI_API_KEY` | OpenAI API key | Yes* | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | Yes* | - |
| `LITELLM_MODEL_ADVISOR` | Model for advisor agent | No | `gpt-4-turbo-preview` |
| `LITELLM_MODEL_CUSTOMER` | Model for customer simulation | No | `gpt-3.5-turbo` |
| `LITELLM_MODEL_EMBEDDINGS` | Embeddings model | No | `text-embedding-3-small` |
| `EMBEDDING_DIMENSION` | Embedding vector size | No | `1536` |
| `PHOENIX_COLLECTOR_ENDPOINT` | Phoenix OTLP endpoint | No | `http://phoenix:4317` |
| `ENVIRONMENT` | Application environment | No | `production` |
| `LOG_LEVEL` | Logging level | No | `INFO` |

*At least one LLM API key is required

### Frontend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:8000` |
| `VITE_APP_TITLE` | Application title | `Pension Guidance Chat` |
| `VITE_ENVIRONMENT` | Environment name | `production` |

## Database Management

### Run Migrations

```bash
./scripts/migrate.sh
```

Or manually:
```bash
docker-compose exec backend alembic upgrade head
```

### Create New Migration

```bash
docker-compose exec backend alembic revision --autogenerate -m "Description"
```

### Rollback Migration

```bash
docker-compose exec backend alembic downgrade -1
```

### Database Backup

```bash
./scripts/backup.sh
```

Backups are stored in `backups/` directory with timestamp.

### Restore Database

```bash
gunzip backups/guidance_agent_20251102_120000.sql.gz
docker-compose exec -T postgres psql -U postgres guidance_agent < backups/guidance_agent_20251102_120000.sql
```

## Seed Demo Data

```bash
./scripts/seed.sh
```

This will load the pension knowledge base into the vector database.

## Development vs Production

### Development Mode

For development, you can mount source code as volumes:

**Backend** (already configured in docker-compose.yml):
```yaml
volumes:
  - ./src:/app/src:ro
```

**Frontend** (add to docker-compose.yml):
```yaml
volumes:
  - ./frontend/src:/app/src:ro
```

Then restart services:
```bash
docker-compose restart backend frontend
```

### Production Mode

For production:
1. Remove volume mounts from docker-compose.yml
2. Use environment-specific .env file
3. Enable SSL/TLS with reverse proxy
4. Use managed database service
5. Enable proper logging and monitoring

## Troubleshooting

### Services Not Starting

1. Check logs:
```bash
docker-compose logs backend
```

2. Check health status:
```bash
docker-compose ps
```

3. Verify environment variables:
```bash
docker-compose config
```

### Database Connection Issues

1. Ensure Postgres is healthy:
```bash
docker-compose exec postgres pg_isready -U postgres
```

2. Check database exists:
```bash
docker-compose exec postgres psql -U postgres -l
```

3. Test connection from backend:
```bash
docker-compose exec backend python -c "from guidance_agent.core.database import get_session; get_session().execute('SELECT 1')"
```

### Build Failures

1. Clear Docker cache:
```bash
docker-compose build --no-cache
```

2. Remove old images:
```bash
docker system prune -a
```

3. Check disk space:
```bash
docker system df
```

### Frontend Not Loading

1. Check nginx logs:
```bash
docker-compose logs frontend
```

2. Verify built assets:
```bash
docker-compose exec frontend ls -la /usr/share/nginx/html
```

3. Test nginx config:
```bash
docker-compose exec frontend nginx -t
```

## Testing the Deployment

Run the comprehensive test script:

```bash
./scripts/test-deployment.sh
```

This tests:
- Health checks for all services
- API endpoints
- Frontend accessibility
- Service communication
- Database connectivity

## Cleanup

### Stop and Remove All Containers

```bash
docker-compose down
```

### Remove Volumes (WARNING: Deletes all data)

```bash
docker-compose down -v
```

### Remove Images

```bash
docker-compose down --rmi all
```

## Performance Optimization

### Backend

1. **Increase workers**:
```bash
CMD ["uvicorn", "guidance_agent.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

2. **Enable caching**:
Add Redis service and configure application caching

3. **Connection pooling**:
Configure SQLAlchemy pool size in database settings

### Frontend

1. **CDN for static assets**:
Upload built assets to CDN and update nginx config

2. **Enable caching**:
Already configured in nginx.conf for static assets

3. **Compression**:
Gzip already enabled in nginx.conf

## Security Considerations

1. **Change default passwords**:
Update Postgres password in production

2. **Use secrets management**:
Use Docker secrets or external vault for API keys

3. **Enable HTTPS**:
Add SSL certificates and configure nginx for HTTPS

4. **Network isolation**:
Use Docker networks to isolate services

5. **Read-only filesystem**:
Add `read_only: true` to service definitions where possible

## Monitoring

### Service Status

```bash
docker-compose ps
```

### Resource Usage

```bash
docker stats
```

### Health Checks

```bash
curl http://localhost:8000/health
curl http://localhost/health
```

### Phoenix Observability

Access Phoenix UI at http://localhost:6006 to view:
- LLM traces and spans
- Performance metrics
- Token usage
- Error tracking

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Review documentation
3. Open an issue on GitHub
