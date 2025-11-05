#!/bin/bash

# Stop Local Development Servers
# This script stops all development services

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}Stopping development services...${NC}"
echo ""

# Stop backend if running
if [ -f "$PROJECT_ROOT/.backend-dev.pid" ]; then
    BACKEND_PID=$(cat "$PROJECT_ROOT/.backend-dev.pid")
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}Stopping backend (PID: $BACKEND_PID)...${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        sleep 2
        # Force kill if still running
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            kill -9 $BACKEND_PID 2>/dev/null || true
        fi
        echo -e "${GREEN}✓ Backend stopped${NC}"
    fi
    rm "$PROJECT_ROOT/.backend-dev.pid"
fi

# Stop frontend if running
if [ -f "$PROJECT_ROOT/.frontend-dev.pid" ]; then
    FRONTEND_PID=$(cat "$PROJECT_ROOT/.frontend-dev.pid")
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}Stopping frontend (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID 2>/dev/null || true
        sleep 2
        # Force kill if still running
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            kill -9 $FRONTEND_PID 2>/dev/null || true
        fi
        echo -e "${GREEN}✓ Frontend stopped${NC}"
    fi
    rm "$PROJECT_ROOT/.frontend-dev.pid"
fi

# Stop Docker services
cd "$PROJECT_ROOT"
echo -e "${YELLOW}Stopping Docker services...${NC}"
docker-compose stop postgres phoenix 2>/dev/null || true
echo -e "${GREEN}✓ Docker services stopped${NC}"

echo ""
echo -e "${GREEN}✓ All development services stopped${NC}"
echo ""
echo -e "${YELLOW}Note:${NC} Docker containers are stopped but not removed."
echo -e "To remove containers completely, run: ${BLUE}docker-compose down${NC}"
