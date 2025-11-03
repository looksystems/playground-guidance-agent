# Docker Quick Start Guide

## What Works Right Now

The backend, database, and observability services are fully functional and ready to deploy.

## Quick Deploy (Backend Services)

```bash
# 1. Configure environment
cp .env.example .env

# 2. Add your API key (choose one)
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
# OR
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env

# 3. Start services
docker-compose up -d postgres phoenix backend

# 4. Wait for services to be ready (30 seconds)
sleep 30

# 5. Check health
curl http://localhost:8000/health
```

## Access Services

After deployment, access:

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Phoenix Observability**: http://localhost:6006
- **Health Check**: http://localhost:8000/health

## Test the API

```bash
# Health check
curl http://localhost:8000/health

# Get API info
curl http://localhost:8000/

# List customers
curl http://localhost:8000/api/customers

# API documentation
open http://localhost:8000/api/docs
```

## View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f phoenix
```

## Stop Services

```bash
docker-compose down
```

## Database Management

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Check migration status
docker-compose exec backend alembic current

# Backup database
./scripts/backup.sh

# Seed demo data
./scripts/seed.sh
```

## Known Issue: Frontend

The frontend service is blocked by a Tailwind CSS v4 compatibility issue in the existing codebase. This does NOT affect backend functionality.

**To use the full UI, you can:**
1. Run frontend locally: `cd frontend && npm run dev`
2. Access backend API directly via http://localhost:8000/api/docs
3. Wait for frontend team to fix Tailwind CSS issues

## Production Deployment

For production deployment, see:
- `/docs/DOCKER_SETUP.md` - Complete Docker guide
- `/docs/DEPLOYMENT.md` - Production deployment guide
- `/docs/PRODUCTION_CHECKLIST.md` - Deployment checklist

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Verify .env file
cat .env | grep API_KEY

# Check Docker is running
docker ps
```

### Database connection fails
```bash
# Wait for PostgreSQL to be ready
docker-compose exec postgres pg_isready -U postgres

# Check database exists
docker-compose exec postgres psql -U postgres -l
```

### API returns errors
```bash
# Check backend logs
docker-compose logs backend

# Verify environment variables
docker-compose exec backend env | grep -E "DATABASE|API_KEY"
```

## Next Steps

1. **Test the API**: http://localhost:8000/api/docs
2. **View traces**: http://localhost:6006
3. **Run training**: Use existing Python scripts
4. **Monitor health**: http://localhost:8000/health

For complete documentation, see `/docs/DOCKER_SETUP.md`
