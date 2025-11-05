#!/bin/bash

# Start Local Development Servers
# This script starts all necessary services for local development
# - PostgreSQL & Phoenix in Docker
# - Backend locally with uvicorn
# - Frontend locally with npm

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Default options
START_BACKEND=true
START_FRONTEND=true
START_PHOENIX=true
DETACHED=true

# Parse command line arguments
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Start local development servers for Pension Guidance Chat"
    echo ""
    echo "Options:"
    echo "  -b, --backend-only      Start only backend services (postgres, backend, phoenix)"
    echo "  -f, --frontend-only     Start only frontend (requires backend running)"
    echo "  -n, --no-phoenix        Skip Phoenix observability"
    echo "  -a, --attached          Run in attached mode (show logs, blocks terminal)"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                      # Start everything (default)"
    echo "  $0 --backend-only       # Start only backend stack"
    echo "  $0 --no-phoenix         # Start without Phoenix"
    echo "  $0 --attached           # Start with logs visible (blocks)"
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--backend-only)
            START_FRONTEND=false
            shift
            ;;
        -f|--frontend-only)
            START_BACKEND=false
            START_PHOENIX=false
            shift
            ;;
        -n|--no-phoenix)
            START_PHOENIX=false
            shift
            ;;
        -a|--attached)
            DETACHED=false
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            exit 1
            ;;
    esac
done

# Print banner
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║        Pension Guidance Chat - Development Setup          ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker daemon is not running${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker is available${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: docker-compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ docker-compose is available${NC}"

# Check uv (for backend)
if [ "$START_BACKEND" = true ]; then
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}Error: uv is not installed${NC}"
        echo -e "${YELLOW}Install with: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ uv is available${NC}"
fi

# Check Node.js (for frontend)
if [ "$START_FRONTEND" = true ]; then
    if ! command -v node &> /dev/null; then
        echo -e "${RED}Error: Node.js is not installed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Node.js is available ($(node --version))${NC}"
fi

# Check if .env exists
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    if [ -f "$PROJECT_ROOT/.env.example" ]; then
        echo -e "${YELLOW}Creating .env from .env.example...${NC}"
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        echo -e "${RED}Please configure .env with your API keys before proceeding${NC}"
        exit 1
    else
        echo -e "${RED}Error: No .env.example found${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ .env file exists${NC}"
echo ""

# Start Docker services (PostgreSQL + Phoenix)
if [ "$START_BACKEND" = true ]; then
    echo -e "${BLUE}Starting Docker services (PostgreSQL + Phoenix)...${NC}"

    cd "$PROJECT_ROOT"

    # Build services list for Docker
    DOCKER_SERVICES="postgres"
    if [ "$START_PHOENIX" = true ]; then
        DOCKER_SERVICES="$DOCKER_SERVICES phoenix"
    fi

    # Start Docker services
    docker-compose up -d $DOCKER_SERVICES

    # Wait for PostgreSQL to be ready
    echo -n "  PostgreSQL... "
    RETRIES=30
    while [ $RETRIES -gt 0 ]; do
        if docker-compose exec -T postgres pg_isready -U postgres &> /dev/null; then
            echo -e "${GREEN}✓${NC}"
            break
        fi
        RETRIES=$((RETRIES-1))
        if [ $RETRIES -eq 0 ]; then
            echo -e "${RED}✗ (timeout)${NC}"
            exit 1
        fi
        sleep 1
    done

    # Check Phoenix if enabled
    if [ "$START_PHOENIX" = true ]; then
        echo -n "  Phoenix... "
        RETRIES=30
        while [ $RETRIES -gt 0 ]; do
            if curl -s http://localhost:6006 &> /dev/null; then
                echo -e "${GREEN}✓${NC}"
                break
            fi
            RETRIES=$((RETRIES-1))
            if [ $RETRIES -eq 0 ]; then
                echo -e "${YELLOW}⚠ (timeout - may still be starting)${NC}"
                break
            fi
            sleep 1
        done
    fi

    echo ""
    echo -e "${GREEN}✓ Docker services started${NC}"
    echo ""

    # Sync dependencies with uv
    echo -e "${BLUE}Syncing Python dependencies with uv...${NC}"
    cd "$PROJECT_ROOT"
    uv sync
    # Install the package itself in editable mode
    uv pip install -e .
    echo -e "${GREEN}✓ Dependencies synced${NC}"
    echo ""

    # Start backend locally with uvicorn
    echo -e "${BLUE}Starting backend (uvicorn)...${NC}"

    if [ "$DETACHED" = true ]; then
        # Run in background
        uv run uvicorn guidance_agent.api.main:app --reload --host 0.0.0.0 --port 8000 > "$PROJECT_ROOT/backend-dev.log" 2>&1 &
        BACKEND_PID=$!
        echo $BACKEND_PID > "$PROJECT_ROOT/.backend-dev.pid"

        # Wait for backend to be ready
        echo -n "  Backend API... "
        RETRIES=60
        while [ $RETRIES -gt 0 ]; do
            if curl -s http://localhost:8000/health &> /dev/null; then
                echo -e "${GREEN}✓${NC}"
                break
            fi
            RETRIES=$((RETRIES-1))
            if [ $RETRIES -eq 0 ]; then
                echo -e "${RED}✗ (timeout)${NC}"
                echo -e "${YELLOW}Backend may still be starting. Check logs: tail -f backend-dev.log${NC}"
                break
            fi
            sleep 1
        done
    else
        # Will run in foreground later
        echo -e "${YELLOW}Backend will start in attached mode...${NC}"
    fi

    echo ""
    echo -e "${GREEN}✓ Backend started${NC}"
    echo ""
fi

# Start frontend
if [ "$START_FRONTEND" = true ]; then
    echo -e "${BLUE}Starting frontend (Nuxt)...${NC}"

    cd "$FRONTEND_DIR"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}node_modules not found. Running npm install...${NC}"
        npm install
    fi

    # Start frontend dev server
    if [ "$DETACHED" = true ]; then
        # Run in background
        npm run dev > "$PROJECT_ROOT/frontend-dev.log" 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > "$PROJECT_ROOT/.frontend-dev.pid"

        # Wait for frontend to be ready
        echo -n "  Nuxt dev server... "
        RETRIES=60
        while [ $RETRIES -gt 0 ]; do
            if curl -s http://localhost:3000 &> /dev/null; then
                echo -e "${GREEN}✓${NC}"
                break
            fi
            RETRIES=$((RETRIES-1))
            if [ $RETRIES -eq 0 ]; then
                echo -e "${RED}✗ (timeout)${NC}"
                echo -e "${YELLOW}Frontend may still be starting. Check logs: tail -f frontend-dev.log${NC}"
                break
            fi
            sleep 1
        done
    else
        # Will run in foreground later
        echo -e "${YELLOW}Frontend will start in attached mode...${NC}"
    fi

    echo ""
    echo -e "${GREEN}✓ Frontend started${NC}"
    echo ""
fi

# Print service URLs
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Services Running                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$START_FRONTEND" = true ]; then
    echo -e "  ${GREEN}Frontend (Nuxt 3):${NC}"
    echo -e "    ${BLUE}http://localhost:3000${NC}"
    echo ""
fi

if [ "$START_BACKEND" = true ]; then
    echo -e "  ${GREEN}Backend (FastAPI):${NC}"
    echo -e "    ${BLUE}http://localhost:8000${NC}"
    echo -e "    API Docs: ${BLUE}http://localhost:8000/api/docs${NC}"
    echo ""

    if [ "$START_PHOENIX" = true ]; then
        echo -e "  ${GREEN}Phoenix (Observability):${NC}"
        echo -e "    ${BLUE}http://localhost:6006${NC}"
        echo ""
    fi

    echo -e "  ${GREEN}PostgreSQL:${NC}"
    echo -e "    ${BLUE}localhost:5432${NC} (guidance_agent)"
    echo ""
fi

# Print useful commands
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Useful Commands                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$DETACHED" = true ]; then
    echo -e "  ${YELLOW}View logs:${NC}"
    if [ "$START_BACKEND" = true ]; then
        echo "    tail -f backend-dev.log           # Backend logs"
        echo "    docker-compose logs -f postgres   # Database logs"
        if [ "$START_PHOENIX" = true ]; then
            echo "    docker-compose logs -f phoenix    # Phoenix logs"
        fi
    fi
    if [ "$START_FRONTEND" = true ]; then
        echo "    tail -f frontend-dev.log          # Frontend logs"
    fi
    echo ""

    echo -e "  ${YELLOW}Stop services:${NC}"
    echo "    $SCRIPT_DIR/stop-dev.sh           # Stop all services"
    echo ""
fi

echo -e "  ${YELLOW}Run tests:${NC}"
if [ "$START_BACKEND" = true ]; then
    echo "    pytest                            # Backend tests"
fi
if [ "$START_FRONTEND" = true ]; then
    echo "    cd frontend && npm test           # Frontend tests"
fi
echo ""

echo -e "  ${YELLOW}Database:${NC}"
echo "    docker-compose exec postgres psql -U postgres -d guidance_agent"
echo ""

echo -e "${GREEN}✓ Development environment is ready!${NC}"
echo ""

# If running in attached mode, start services in foreground
if [ "$DETACHED" = false ]; then
    echo -e "${YELLOW}Running in attached mode. Press Ctrl+C to stop all services${NC}"
    echo ""

    # Trap Ctrl+C to cleanup
    cleanup() {
        echo -e "\n${YELLOW}Stopping services...${NC}"
        if [ ! -z "$BACKEND_PID" ]; then
            kill $BACKEND_PID 2>/dev/null || true
        fi
        if [ ! -z "$FRONTEND_PID" ]; then
            kill $FRONTEND_PID 2>/dev/null || true
        fi
        docker-compose stop postgres phoenix 2>/dev/null || true
        exit 0
    }
    trap cleanup INT TERM

    # Start backend in foreground if needed
    if [ "$START_BACKEND" = true ]; then
        cd "$PROJECT_ROOT"
        uv run uvicorn guidance_agent.api.main:app --reload --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
    fi

    # Start frontend in foreground if needed
    if [ "$START_FRONTEND" = true ]; then
        cd "$FRONTEND_DIR"
        npm run dev &
        FRONTEND_PID=$!
    fi

    # Wait for any process to exit
    wait
fi
