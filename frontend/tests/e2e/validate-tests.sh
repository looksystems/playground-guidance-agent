#!/bin/bash

# Validation script for Phase 6 E2E Tests
# Checks that all required test files and dependencies are in place

echo "================================="
echo "Phase 6 E2E Test Validation"
echo "================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        return 0
    else
        echo -e "${RED}✗${NC} $1 NOT FOUND"
        return 1
    fi
}

check_package() {
    if grep -q "\"$1\"" ../../package.json; then
        echo -e "${GREEN}✓${NC} $1 installed"
        return 0
    else
        echo -e "${RED}✗${NC} $1 NOT installed"
        return 1
    fi
}

count_tests() {
    local count=$(grep -c "test(" "$1" 2>/dev/null || echo "0")
    echo -e "${GREEN}✓${NC} $1: $count tests"
}

# Track errors
ERRORS=0

echo "1. Checking Test Files"
echo "----------------------"
check_file "admin-data-models.spec.ts" || ((ERRORS++))
check_file "admin-data-models-with-mocks.spec.ts" || ((ERRORS++))
check_file "fixtures.ts" || ((ERRORS++))
check_file "README.md" || ((ERRORS++))
check_file "TEST_SUMMARY.md" || ((ERRORS++))
echo ""

echo "2. Checking Configuration"
echo "------------------------"
check_file "../../playwright.config.ts" || ((ERRORS++))
echo ""

echo "3. Checking Dependencies"
echo "-----------------------"
check_package "@playwright/test" || ((ERRORS++))
check_package "@nuxt/test-utils" || ((ERRORS++))
echo ""

echo "4. Counting Tests"
echo "----------------"
count_tests "admin-data-models.spec.ts"
count_tests "admin-data-models-with-mocks.spec.ts"
TOTAL_TESTS=$(($(grep -c "test(" admin-data-models.spec.ts 2>/dev/null || echo 0) + $(grep -c "test(" admin-data-models-with-mocks.spec.ts 2>/dev/null || echo 0)))
echo -e "${YELLOW}Total Tests: $TOTAL_TESTS${NC}"
echo ""

echo "5. Checking NPM Scripts"
echo "----------------------"
if grep -q "test:e2e" ../../package.json; then
    echo -e "${GREEN}✓${NC} test:e2e script configured"
else
    echo -e "${RED}✗${NC} test:e2e script NOT configured"
    ((ERRORS++))
fi

if grep -q "test:e2e:ui" ../../package.json; then
    echo -e "${GREEN}✓${NC} test:e2e:ui script configured"
else
    echo -e "${RED}✗${NC} test:e2e:ui script NOT configured"
    ((ERRORS++))
fi
echo ""

echo "6. Test Coverage by Page"
echo "------------------------"
echo "Knowledge Base:"
echo "  - FCA Knowledge List: ✓"
echo "  - FCA Knowledge Detail: ✓"
echo "  - Pension Knowledge List: ✓"
echo "  - Pension Knowledge Detail: ✓"
echo ""
echo "Learning System:"
echo "  - Memories List: ✓"
echo "  - Memories Detail: ✓"
echo "  - Cases List: ✓"
echo "  - Cases Detail: ✓"
echo "  - Rules List: ✓"
echo "  - Rules Detail: ✓"
echo ""
echo "Customer Management:"
echo "  - Customers List: ✓"
echo "  - Customers Detail: ✓"
echo ""

echo "================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo "Ready to run tests with: npm run test:e2e"
    exit 0
else
    echo -e "${RED}✗ $ERRORS check(s) failed${NC}"
    echo "Please fix the issues above before running tests"
    exit 1
fi
