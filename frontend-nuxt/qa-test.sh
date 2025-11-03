#!/bin/bash

# Frontend QA Test Suite
# Comprehensive testing script for all frontend aspects

set -e  # Exit on error

echo "=========================================="
echo "Frontend QA Test Suite"
echo "=========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
ISSUES=()

# Function to report test result
report_test() {
    local test_name="$1"
    local status="$2"
    local message="$3"

    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✓${NC} $test_name"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $test_name"
        echo -e "  ${RED}Error: $message${NC}"
        ISSUES+=("$test_name: $message")
        ((TESTS_FAILED++))
    fi
}

# Function to run a test with error handling
run_test() {
    local test_name="$1"
    local command="$2"

    echo -e "\n${YELLOW}Running: $test_name${NC}"

    if eval "$command" > /tmp/qa_test_output.txt 2>&1; then
        report_test "$test_name" "PASS" ""
        return 0
    else
        local error_msg=$(cat /tmp/qa_test_output.txt | tail -20)
        report_test "$test_name" "FAIL" "$error_msg"
        return 1
    fi
}

echo "1. TypeScript Type Checking"
echo "----------------------------"
if npx vue-tsc --noEmit 2>&1 | tee /tmp/tsc_output.txt; then
    if grep -q "error TS" /tmp/tsc_output.txt; then
        error_count=$(grep -c "error TS" /tmp/tsc_output.txt || echo "0")
        report_test "TypeScript type checking" "FAIL" "Found $error_count type errors"
    else
        report_test "TypeScript type checking" "PASS" ""
    fi
else
    report_test "TypeScript type checking" "FAIL" "Type checking failed"
fi

echo ""
echo "2. Unit Tests"
echo "-------------"
if npm test -- --run 2>&1 | tee /tmp/vitest_output.txt; then
    # Check if all tests passed - look for the summary line
    if grep -q "Test Files.*passed" /tmp/vitest_output.txt && grep -q "Tests.*passed" /tmp/vitest_output.txt; then
        # Verify no failures
        if ! grep -q "failed" /tmp/vitest_output.txt; then
            report_test "Unit tests" "PASS" ""
        else
            report_test "Unit tests" "FAIL" "Some tests failed"
        fi
    else
        report_test "Unit tests" "FAIL" "Some tests failed"
    fi
else
    # Even if the command exits with non-zero, check if tests actually passed
    if grep -q "Test Files.*passed" /tmp/vitest_output.txt && ! grep -q "failed" /tmp/vitest_output.txt; then
        report_test "Unit tests" "PASS" ""
    else
        report_test "Unit tests" "FAIL" "Test suite failed to run"
    fi
fi

echo ""
echo "3. Build Process"
echo "----------------"
if npm run build 2>&1 | tee /tmp/build_output.txt; then
    if grep -qi "error" /tmp/build_output.txt && ! grep -q "0 errors" /tmp/build_output.txt; then
        report_test "Production build" "FAIL" "Build completed with errors"
    else
        report_test "Production build" "PASS" ""
    fi
else
    report_test "Production build" "FAIL" "Build failed"
fi

echo ""
echo "4. Code Quality Checks"
echo "----------------------"

# Check for console.log statements (excluding test files)
if find app -type f \( -name "*.vue" -o -name "*.ts" \) ! -path "*/node_modules/*" -exec grep -l "console\.log" {} \; > /tmp/console_logs.txt 2>&1; then
    if [ -s /tmp/console_logs.txt ]; then
        log_count=$(wc -l < /tmp/console_logs.txt)
        report_test "No debug console.log statements" "FAIL" "Found console.log in $log_count files"
    else
        report_test "No debug console.log statements" "PASS" ""
    fi
else
    report_test "No debug console.log statements" "PASS" ""
fi

# Check for TODO/FIXME comments
if find app -type f \( -name "*.vue" -o -name "*.ts" \) ! -path "*/node_modules/*" -exec grep -l "TODO\|FIXME" {} \; > /tmp/todos.txt 2>&1; then
    if [ -s /tmp/todos.txt ]; then
        todo_count=$(wc -l < /tmp/todos.txt)
        echo -e "${YELLOW}ℹ${NC} Found TODO/FIXME comments in $todo_count files (informational)"
    fi
fi

echo ""
echo "5. File Structure Validation"
echo "-----------------------------"

# Check if all components have tests
missing_tests=()
for component in app/components/**/*.vue; do
    component_name=$(basename "$component" .vue)
    component_dir=$(dirname "$component" | sed 's|app/||')
    test_file="tests/$component_dir/$component_name.test.ts"

    if [ ! -f "$test_file" ]; then
        missing_tests+=("$component_name")
    fi
done

if [ ${#missing_tests[@]} -eq 0 ]; then
    report_test "All components have tests" "PASS" ""
else
    report_test "All components have tests" "FAIL" "Missing tests for: ${missing_tests[*]}"
fi

# Check if all pages have tests
missing_page_tests=()
for page in app/pages/**/*.vue app/pages/*.vue; do
    [ -f "$page" ] || continue
    page_name=$(basename "$page" .vue)
    page_dir=$(dirname "$page" | sed 's|app/pages||' | sed 's|^/||')

    if [ -n "$page_dir" ]; then
        test_file="tests/pages/$page_dir/$page_name.test.ts"
    else
        test_file="tests/pages/$page_name.test.ts"
    fi

    if [ ! -f "$test_file" ]; then
        missing_page_tests+=("$page")
    fi
done

if [ ${#missing_page_tests[@]} -eq 0 ]; then
    report_test "All pages have tests" "PASS" ""
else
    report_test "All pages have tests" "FAIL" "Missing tests for: ${missing_page_tests[*]}"
fi

echo ""
echo "6. Dependencies Check"
echo "---------------------"

# Check for outdated critical dependencies
if npm outdated 2>&1 | tee /tmp/npm_outdated.txt; then
    echo -e "${YELLOW}ℹ${NC} Dependency status saved (informational)"
fi

# Check for security vulnerabilities
if npm audit --audit-level=moderate 2>&1 | tee /tmp/npm_audit.txt; then
    report_test "No moderate/high security vulnerabilities" "PASS" ""
else
    if grep -q "vulnerabilities" /tmp/npm_audit.txt; then
        vuln_summary=$(grep "vulnerabilities" /tmp/npm_audit.txt | head -1)
        report_test "No moderate/high security vulnerabilities" "FAIL" "$vuln_summary"
    else
        report_test "No moderate/high security vulnerabilities" "FAIL" "Security audit failed"
    fi
fi

echo ""
echo "=========================================="
echo "QA Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -gt 0 ]; then
    echo "Issues Found:"
    echo "-------------"
    for issue in "${ISSUES[@]}"; do
        echo -e "${RED}✗${NC} $issue"
    done
    echo ""
    exit 1
else
    echo -e "${GREEN}All QA tests passed! ✓${NC}"
    exit 0
fi
