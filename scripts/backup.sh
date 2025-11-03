#!/bin/bash

# ========================================
# Database Backup Script
# ========================================

set -e

BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/guidance_agent_$TIMESTAMP.sql"

echo "=========================================="
echo "Database Backup"
echo "=========================================="

# Create backup directory
mkdir -p $BACKUP_DIR

echo "Backing up database to $BACKUP_FILE..."
docker-compose exec -T postgres pg_dump -U postgres guidance_agent > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

echo "Backup complete: ${BACKUP_FILE}.gz"

# Keep only last 7 backups
echo "Cleaning old backups..."
ls -t $BACKUP_DIR/*.gz | tail -n +8 | xargs -r rm

echo "Done!"
