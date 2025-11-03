#!/bin/bash

# ========================================
# Database Seeding Script
# ========================================

set -e

echo "=========================================="
echo "Seeding Database with Demo Data"
echo "=========================================="

# Check if backend is running
if ! docker-compose ps backend | grep -q "Up"; then
    echo "ERROR: Backend service is not running!"
    echo "Please start services with: docker-compose up -d"
    exit 1
fi

echo "Loading pension knowledge base..."
docker-compose exec backend python -m scripts.load_knowledge

echo ""
echo "Seeding complete!"
echo "You can now access the application with demo data."
