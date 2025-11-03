#!/bin/bash

# ========================================
# Deployment Script for Pension Guidance Agent
# ========================================

set -e

echo "=========================================="
echo "Deploying Pension Guidance Agent"
echo "=========================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and fill in your values"
    exit 1
fi

# Source environment variables
source .env

# Check required environment variables
if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: No LLM API keys found!"
    echo "Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env"
    exit 1
fi

echo ""
echo "Step 1: Pulling latest images..."
docker-compose pull postgres phoenix

echo ""
echo "Step 2: Building application images..."
docker-compose build --no-cache

echo ""
echo "Step 3: Stopping existing containers..."
docker-compose down

echo ""
echo "Step 4: Starting services..."
docker-compose up -d

echo ""
echo "Step 5: Waiting for services to be healthy..."
sleep 10

# Wait for postgres
echo -n "Waiting for Postgres..."
until docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo " Ready!"

# Wait for backend
echo -n "Waiting for Backend..."
until curl -sf http://localhost:8000/health > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo " Ready!"

# Wait for frontend
echo -n "Waiting for Frontend..."
until curl -sf http://localhost/health > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo " Ready!"

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Services:"
echo "  Frontend: http://localhost"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/api/docs"
echo "  Phoenix UI: http://localhost:6006"
echo ""
echo "Health Checks:"
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop services: docker-compose down"
echo "=========================================="
