#!/bin/bash

# ========================================
# Deployment Test Script
# ========================================

set -e

echo "=========================================="
echo "Testing Deployment"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_passed=0
test_failed=0

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=$3

    echo -n "Testing $name... "

    status=$(curl -s -o /dev/null -w "%{http_code}" $url)

    if [ "$status" == "$expected_status" ]; then
        echo -e "${GREEN}PASSED${NC} (status: $status)"
        ((test_passed++))
    else
        echo -e "${RED}FAILED${NC} (expected: $expected_status, got: $status)"
        ((test_failed++))
    fi
}

# Test health check
test_health() {
    local service=$1
    local url=$2

    echo -n "Testing $service health... "

    response=$(curl -s $url)
    status=$(echo $response | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null || echo "error")

    if [ "$status" == "healthy" ]; then
        echo -e "${GREEN}HEALTHY${NC}"
        ((test_passed++))
    else
        echo -e "${RED}UNHEALTHY${NC} (status: $status)"
        ((test_failed++))
    fi
}

echo ""
echo "1. Testing Service Health Checks"
echo "-----------------------------------"

test_health "Backend" "http://localhost:8000/health"
test_endpoint "Frontend Health" "http://localhost/health" "200"

echo ""
echo "2. Testing API Endpoints"
echo "-----------------------------------"

test_endpoint "API Root" "http://localhost:8000/" "200"
test_endpoint "API Docs" "http://localhost:8000/api/docs" "200"
test_endpoint "Customers API" "http://localhost:8000/api/customers" "200"

echo ""
echo "3. Testing Frontend"
echo "-----------------------------------"

test_endpoint "Frontend Root" "http://localhost/" "200"
test_endpoint "Frontend Assets" "http://localhost/assets" "404"

echo ""
echo "4. Testing Service Communication"
echo "-----------------------------------"

# Test if frontend can reach backend through nginx proxy
echo -n "Testing Frontend → Backend proxy... "
if docker-compose exec frontend curl -sf http://backend:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}PASSED${NC}"
    ((test_passed++))
else
    echo -e "${RED}FAILED${NC}"
    ((test_failed++))
fi

# Test if backend can reach database
echo -n "Testing Backend → Database... "
if docker-compose exec backend psql postgresql://postgres:postgres@postgres:5432/guidance_agent -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}PASSED${NC}"
    ((test_passed++))
else
    echo -e "${RED}FAILED${NC}"
    ((test_failed++))
fi

echo ""
echo "=========================================="
echo "Test Results"
echo "=========================================="
echo -e "Passed: ${GREEN}$test_passed${NC}"
echo -e "Failed: ${RED}$test_failed${NC}"
echo ""

if [ $test_failed -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
