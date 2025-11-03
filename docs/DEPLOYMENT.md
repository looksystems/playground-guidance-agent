# Deployment Guide

This guide covers deploying the Pension Guidance Agent to production environments.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Production Checklist](#production-checklist)
- [Deployment Options](#deployment-options)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Monitoring and Logging](#monitoring-and-logging)
- [Backup and Recovery](#backup-and-recovery)
- [Scaling](#scaling)
- [Security Hardening](#security-hardening)

## Overview

The application consists of:
- **Frontend**: Vue.js SPA served by Nginx
- **Backend**: FastAPI application with Uvicorn
- **Database**: PostgreSQL with pgvector extension
- **Observability**: Phoenix for LLM tracing

## Prerequisites

### Required
- Docker Engine 20.10+
- Docker Compose 2.0+
- Valid LLM API keys (OpenAI or Anthropic)
- Domain name with DNS configured
- SSL/TLS certificates

### Recommended
- Reverse proxy (Nginx/Traefik/Caddy)
- Managed PostgreSQL service
- Log aggregation service
- Monitoring/alerting system
- Backup solution

## Production Checklist

Before deploying to production:

### Security
- [ ] Change default database password
- [ ] Use secrets management for API keys
- [ ] Enable HTTPS with valid certificates
- [ ] Configure CORS for production domain
- [ ] Enable rate limiting
- [ ] Set up firewall rules
- [ ] Review and update security headers
- [ ] Disable debug mode
- [ ] Remove development tools

### Infrastructure
- [ ] Set up managed database (or configure backups)
- [ ] Configure DNS records
- [ ] Set up SSL certificates
- [ ] Configure reverse proxy
- [ ] Set up monitoring
- [ ] Configure log aggregation
- [ ] Set up backup automation
- [ ] Configure alerts

### Application
- [ ] Review environment variables
- [ ] Test all API endpoints
- [ ] Run database migrations
- [ ] Load knowledge base data
- [ ] Test health checks
- [ ] Configure CORS origins
- [ ] Set appropriate log levels
- [ ] Configure rate limits

### Testing
- [ ] Run integration tests
- [ ] Load testing
- [ ] Security scanning
- [ ] SSL/TLS validation
- [ ] Backup/restore testing
- [ ] Disaster recovery testing

## Deployment Options

### Option 1: Docker Compose (Simple)

Best for: Small deployments, single server

1. **Prepare server**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. **Deploy application**
```bash
git clone <repository-url>
cd guidance-agent
cp .env.production .env
# Edit .env with production values
./scripts/deploy.sh
```

3. **Configure reverse proxy**
See [SSL/TLS Configuration](#ssltls-configuration)

### Option 2: Docker Swarm (Medium Scale)

Best for: Multi-server deployments, high availability

1. **Initialize Swarm**
```bash
docker swarm init
```

2. **Create docker-compose.prod.yml**
```yaml
version: '3.8'

services:
  backend:
    image: guidance-agent-backend:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
    # ... rest of config
```

3. **Deploy stack**
```bash
docker stack deploy -c docker-compose.prod.yml guidance
```

### Option 3: Kubernetes (Large Scale)

Best for: Large deployments, cloud platforms

See `docs/kubernetes/` for Helm charts and manifests.

### Option 4: Cloud Platforms

#### AWS

**Using ECS**:
1. Build and push images to ECR
2. Create ECS task definitions
3. Configure ALB for load balancing
4. Use RDS for PostgreSQL
5. Use Secrets Manager for credentials

**Using EKS**:
Use Kubernetes deployment option with EKS

#### Google Cloud

**Using Cloud Run**:
1. Build images
2. Push to Container Registry
3. Deploy to Cloud Run
4. Use Cloud SQL for PostgreSQL
5. Use Secret Manager

#### Azure

**Using Container Apps**:
1. Create Container Registry
2. Build and push images
3. Deploy to Container Apps
4. Use Azure Database for PostgreSQL
5. Use Key Vault for secrets

## Environment Configuration

### Production Environment Variables

Create `.env` file:

```bash
# ========================================
# API Keys - USE SECRETS MANAGEMENT
# ========================================
OPENAI_API_KEY=<from-secrets-manager>
ANTHROPIC_API_KEY=<from-secrets-manager>

# ========================================
# Database - USE MANAGED SERVICE
# ========================================
DATABASE_URL=postgresql://user:password@db.example.com:5432/guidance_agent

# ========================================
# LLM Configuration
# ========================================
LITELLM_MODEL_ADVISOR=gpt-4-turbo-preview
LITELLM_MODEL_CUSTOMER=gpt-3.5-turbo
LITELLM_MODEL_EMBEDDINGS=text-embedding-3-small
EMBEDDING_DIMENSION=1536

# ========================================
# Phoenix Configuration
# ========================================
PHOENIX_COLLECTOR_ENDPOINT=http://phoenix:4317
PHOENIX_PROJECT_NAME=guidance-agent-prod

# ========================================
# Application Settings
# ========================================
ENVIRONMENT=production
LOG_LEVEL=WARNING

# ========================================
# Frontend Configuration
# ========================================
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_APP_TITLE=Pension Guidance Chat
VITE_ENVIRONMENT=production
```

### Secrets Management

#### Using Docker Secrets

1. Create secrets:
```bash
echo "your-openai-key" | docker secret create openai_api_key -
echo "your-db-password" | docker secret create db_password -
```

2. Update docker-compose.yml:
```yaml
services:
  backend:
    secrets:
      - openai_api_key
      - db_password
    environment:
      OPENAI_API_KEY_FILE: /run/secrets/openai_api_key

secrets:
  openai_api_key:
    external: true
  db_password:
    external: true
```

#### Using Vault (HashiCorp)

```bash
# Store secrets
vault kv put secret/guidance-agent \
  openai_api_key=sk-... \
  db_password=...

# Retrieve in application
vault kv get -field=openai_api_key secret/guidance-agent
```

## Database Setup

### Option 1: Managed PostgreSQL

**AWS RDS**:
```bash
# Create RDS instance with pgvector
aws rds create-db-instance \
  --db-instance-identifier guidance-agent-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15 \
  --allocated-storage 100 \
  --master-username postgres \
  --master-user-password <password>

# Install pgvector extension
psql -h <rds-endpoint> -U postgres -c "CREATE EXTENSION vector;"
```

**Google Cloud SQL**:
```bash
gcloud sql instances create guidance-agent-db \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-8192 \
  --region=us-central1

gcloud sql databases create guidance_agent \
  --instance=guidance-agent-db
```

### Option 2: Self-Managed PostgreSQL

1. **Install PostgreSQL**:
```bash
apt-get install postgresql-15 postgresql-15-pgvector
```

2. **Configure for production**:
```bash
# /etc/postgresql/15/main/postgresql.conf
max_connections = 100
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
```

3. **Enable pgvector**:
```sql
CREATE EXTENSION vector;
```

4. **Set up replication** (optional):
See PostgreSQL streaming replication documentation

## SSL/TLS Configuration

### Option 1: Nginx Reverse Proxy with Let's Encrypt

1. **Install Certbot**:
```bash
apt-get install certbot python3-certbot-nginx
```

2. **Obtain certificate**:
```bash
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

3. **Configure Nginx**:
```nginx
# /etc/nginx/sites-available/guidance-agent
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Frontend
    location / {
        proxy_pass http://localhost:80;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

4. **Enable and test**:
```bash
ln -s /etc/nginx/sites-available/guidance-agent /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### Option 2: Traefik

1. **Create traefik.yml**:
```yaml
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@yourdomain.com
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web
```

2. **Update docker-compose.yml**:
```yaml
services:
  traefik:
    image: traefik:v2.10
    command:
      - --providers.docker=true
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
      - --certificatesresolvers.letsencrypt.acme.email=admin@yourdomain.com
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./letsencrypt:/letsencrypt

  frontend:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`yourdomain.com`)"
      - "traefik.http.routers.frontend.entrypoints=websecure"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
```

## Monitoring and Logging

### Application Monitoring

1. **Health checks**:
```bash
# Add to cron
*/5 * * * * curl -f http://localhost:8000/health || alert-script.sh
```

2. **Phoenix observability**:
Access at http://yourdomain.com:6006

3. **Add Prometheus metrics** (optional):
```python
# Add to backend
from prometheus_client import Counter, Histogram
requests_total = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')
```

### Logging

1. **Configure log aggregation**:

**Using ELK Stack**:
```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Using Loki**:
```yaml
services:
  loki:
    image: grafana/loki:2.9.0

  promtail:
    image: grafana/promtail:2.9.0
    volumes:
      - /var/log:/var/log
```

2. **Application logging**:
```python
# Update LOG_LEVEL in production
LOG_LEVEL=WARNING
```

## Backup and Recovery

### Automated Backups

1. **Set up backup cron job**:
```bash
# /etc/cron.d/guidance-agent-backup
0 2 * * * /path/to/guidance-agent/scripts/backup.sh >> /var/log/backup.log 2>&1
```

2. **Backup to S3**:
```bash
#!/bin/bash
# Add to backup.sh
aws s3 cp $BACKUP_FILE s3://backup-bucket/guidance-agent/
```

### Disaster Recovery

1. **Document recovery procedure**:
```bash
# 1. Restore database
gunzip backup.sql.gz
psql < backup.sql

# 2. Restart services
docker-compose up -d

# 3. Verify health
curl http://localhost:8000/health
```

2. **Test recovery regularly**:
```bash
# Monthly DR test
./scripts/test-disaster-recovery.sh
```

## Scaling

### Horizontal Scaling

1. **Backend replicas**:
```yaml
services:
  backend:
    deploy:
      replicas: 3
    environment:
      - WORKERS=1  # Use 1 worker per container
```

2. **Load balancer**:
Use nginx/haproxy/cloud LB to distribute traffic

### Vertical Scaling

1. **Increase resources**:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

### Database Scaling

1. **Read replicas**:
Set up PostgreSQL streaming replication

2. **Connection pooling**:
Use PgBouncer between application and database

## Security Hardening

### Application

1. **Update CORS origins**:
```python
# src/guidance_agent/api/main.py
allow_origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

2. **Enable rate limiting**:
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.get("/api/consultations")
@limiter.limit("10/minute")
async def get_consultations():
    ...
```

3. **Input validation**:
Already implemented via Pydantic

### Infrastructure

1. **Firewall rules**:
```bash
# Only allow necessary ports
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

2. **Container security**:
```yaml
services:
  backend:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
```

3. **Network isolation**:
```yaml
networks:
  frontend-network:
    internal: false
  backend-network:
    internal: true
```

## Post-Deployment

### Verification

1. Run deployment tests:
```bash
./scripts/test-deployment.sh
```

2. Verify SSL:
```bash
curl https://yourdomain.com/health
```

3. Check logs:
```bash
docker-compose logs -f
```

### Monitoring

1. Set up alerts for:
   - Service downtime
   - High error rates
   - Database issues
   - Disk space
   - Memory usage

2. Monitor Phoenix dashboard

3. Review logs regularly

## Rollback

If deployment fails:

1. **Revert to previous version**:
```bash
docker-compose down
git checkout <previous-tag>
docker-compose up -d
```

2. **Restore database**:
```bash
./scripts/restore-backup.sh <backup-file>
```

## Support

For production issues:
1. Check health endpoints
2. Review logs
3. Check Phoenix traces
4. Consult documentation
5. Contact support team
