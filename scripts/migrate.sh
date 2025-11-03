#!/bin/bash

# ========================================
# Database Migration Script
# ========================================

set -e

echo "=========================================="
echo "Running Database Migrations"
echo "=========================================="

# Check if backend is running
if ! docker-compose ps backend | grep -q "Up"; then
    echo "ERROR: Backend service is not running!"
    echo "Please start services with: docker-compose up -d"
    exit 1
fi

echo "Running migrations..."
docker-compose exec backend alembic upgrade head

echo ""
echo "Current migration status:"
docker-compose exec backend alembic current

echo ""
echo "Migrations complete!"
