# Testing Guide - Pension Guidance Chat

This document provides comprehensive guidance for testing the Pension Guidance Chat application, including E2E, integration, unit, and accessibility tests.

## Table of Contents

1. [Overview](#overview)
2. [Test Structure](#test-structure)
3. [E2E Testing with Playwright](#e2e-testing-with-playwright)
4. [Integration Testing](#integration-testing)
5. [Unit Testing](#unit-testing)
6. [Accessibility Testing](#accessibility-testing)
7. [Running Tests](#running-tests)
8. [CI/CD Integration](#cicd-integration)
9. [Test Data and Fixtures](#test-data-and-fixtures)
10. [Troubleshooting](#troubleshooting)

## Overview

The Pension Guidance Chat application uses a comprehensive testing strategy:

- **E2E Tests**: Full-stack testing using Playwright (Frontend + Backend + Database)
- **Integration Tests**: Backend API and database integration tests using pytest
- **Unit Tests**: Component and function-level tests for both frontend (Vitest) and backend (pytest)
- **Accessibility Tests**: Automated accessibility testing using axe-core/playwright

### Testing Framework Selection

**Playwright** was chosen for E2E testing because of:
- Excellent cross-browser support (Chromium, Firefox, WebKit)
- Built-in waiting and auto-retry mechanisms
- Better TypeScript support than Cypress
- Faster execution and better CI/CD integration
- Native support for multiple test projects (browsers/devices)

## Test Structure

```
guidance-agent/
├── frontend/
│   ├── e2e/
│   │   ├── fixtures/         # Test data (customers, messages, consultations)
│   │   ├── pages/            # Page Object Models
│   │   └── tests/            # E2E test suites
│   ├── src/
│   │   └── __tests__/        # Unit tests for components
│   └── playwright.config.ts  # Playwright configuration
├── tests/
│   ├── unit/                 # Backend unit tests
│   ├── integration/          # Backend integration tests
│   └── api/                  # API endpoint tests
└── pytest.ini                # Pytest configuration
```

## E2E Testing with Playwright

### Installation

```bash
cd frontend
npm install -D @playwright/test @axe-core/playwright
npx playwright install
```

### Test Suites

#### 1. Customer Flow Tests (`customer-flow.spec.ts`)
Tests the complete customer journey from homepage to chat to history.

```bash
npm run test:e2e:chromium -- customer-flow.spec.ts
```

**Scenarios:**
- Complete customer journey (home → chat → history)
- Send multiple messages in chat
- Chat input validation
- Profile form submission

#### 2. Admin Flow Tests (`admin-flow.spec.ts`)
Tests admin dashboard and consultation review functionality.

```bash
npm run test:e2e:chromium -- admin-flow.spec.ts
```

**Scenarios:**
- Dashboard loads with metrics
- View consultations table
- Click on consultation to view details
- Export functionality
- Filter functionality

#### 3. Consultation History Tests (`consultation-history.spec.ts`)
Tests the consultation history page with filtering and search.

```bash
npm run test:e2e:chromium -- consultation-history.spec.ts
```

**Scenarios:**
- Page loads correctly
- Filter by status (all, active, completed)
- Search consultations
- Empty state display
- Load more functionality

#### 4. Error Handling Tests (`error-handling.spec.ts`)
Tests error scenarios and edge cases.

```bash
npm run test:e2e:chromium -- error-handling.spec.ts
```

**Scenarios:**
- 404 page for invalid routes
- Invalid consultation ID handling
- Network error simulation
- Server error responses (500)
- API timeout handling
- Malformed JSON responses
- Special characters in input

#### 5. Accessibility Tests (`accessibility.spec.ts`)
Tests WCAG 2.1 AA compliance using axe-core.

```bash
npm run test:e2e:chromium -- accessibility.spec.ts
```

**Scenarios:**
- No accessibility violations on key pages
- Keyboard navigation
- Form labels and ARIA attributes
- Focus indicators
- Color contrast
- Heading hierarchy
- Screen reader compatibility

#### 6. Streaming Tests (`streaming.spec.ts`)
Tests Server-Sent Events (SSE) streaming functionality.

```bash
npm run test:e2e:chromium -- streaming.spec.ts
```

**Scenarios:**
- Streaming indicator appears
- Messages stream in real-time
- Streaming completes successfully
- Multiple sequential messages
- Connection error handling
- Compliance badge appearance
- Advisor status updates

### Page Object Models

Page Object Models (POMs) provide a clean interface to interact with pages:

- **HomePage**: Homepage interactions
- **ChatPage**: Chat interface and messaging
- **ConsultationHistoryPage**: History page with filters
- **AdminDashboardPage**: Admin dashboard metrics and table
- **ConsultationReviewPage**: Detailed consultation review

Example usage:

```typescript
import { ChatPage } from '../pages/ChatPage';

test('send message in chat', async ({ page }) => {
  const chatPage = new ChatPage(page);
  await chatPage.goto('consultation-123');

  await chatPage.sendMessage('Hello, I have a question');
  await chatPage.waitForResponse();

  const messages = await chatPage.getMessages();
  expect(messages.length).toBeGreaterThan(0);
});
```

### Running E2E Tests

```bash
# Run all E2E tests
npm run test:e2e

# Run with UI mode (interactive)
npm run test:e2e:ui

# Run in headed mode (see browser)
npm run test:e2e:headed

# Run in debug mode
npm run test:e2e:debug

# Run specific browser
npm run test:e2e:chromium
npm run test:e2e:firefox
npm run test:e2e:webkit

# Run specific test file
npm run test:e2e -- customer-flow.spec.ts

# Run with specific tag
npm run test:e2e -- --grep @smoke
```

## Integration Testing

### Backend Integration Tests

Located in `tests/integration/`, these tests verify the full consultation workflow with real database interactions.

#### Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/ -v -m integration

# Run specific integration test
pytest tests/integration/test_full_consultation.py -v

# Run with coverage
pytest tests/integration/ --cov=src --cov-report=html
```

#### Key Integration Tests

**test_full_consultation.py**:
- Complete consultation workflow (create → message → stream → end)
- Compliance validation during consultation
- Learning system data capture
- Multiple concurrent consultations
- Error handling for invalid operations
- Pagination of consultation list
- Long conversation handling (stress test)

### Test Environment

Integration tests use a separate test database configured in `docker-compose.test.yml`:

```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run integration tests against test environment
DATABASE_URL=postgresql://postgres:test_password@localhost:5433/guidance_agent_test \
pytest tests/integration/ -v

# Stop test environment
docker-compose -f docker-compose.test.yml down -v
```

## Unit Testing

### Frontend Unit Tests (Vitest)

```bash
cd frontend

# Run unit tests
npm run test

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage
```

### Backend Unit Tests (pytest)

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific module
pytest tests/unit/advisor/ -v
pytest tests/unit/compliance/ -v
pytest tests/unit/learning/ -v

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=html
```

## Accessibility Testing

### Automated Accessibility Testing

We use @axe-core/playwright for automated WCAG 2.1 AA compliance testing:

```typescript
import AxeBuilder from '@axe-core/playwright';

test('page has no accessibility violations', async ({ page }) => {
  await page.goto('/');

  const accessibilityScanResults = await new AxeBuilder({ page }).analyze();

  expect(accessibilityScanResults.violations).toEqual([]);
});
```

### Manual Accessibility Testing

1. **Keyboard Navigation**: Ensure all functionality is accessible via keyboard
2. **Screen Reader**: Test with NVDA (Windows) or VoiceOver (macOS)
3. **Color Contrast**: Use browser devtools to verify contrast ratios
4. **Focus Management**: Verify logical focus order and visible focus indicators

### Running Accessibility Tests Only

```bash
npm run test:e2e -- accessibility.spec.ts
```

## Running Tests

### Local Development

```bash
# Frontend E2E tests (starts dev server automatically)
cd frontend
npm run test:e2e

# Backend integration tests (requires database)
docker-compose up -d postgres
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/guidance_agent \
pytest tests/integration/ -v

# All unit tests
npm run test  # Frontend
pytest tests/unit/ -v  # Backend
```

### Full Test Suite

```bash
# Start all services
docker-compose up -d

# Run frontend E2E tests
cd frontend && npm run test:e2e

# Run backend tests
pytest tests/ -v

# Stop services
docker-compose down
```

### CI/CD Test Execution

Tests are automatically run on every push and pull request via GitHub Actions:

```bash
# View workflow
.github/workflows/e2e-tests.yml

# Workflow jobs:
# 1. e2e-tests: Full E2E tests with Playwright
# 2. integration-tests: Backend integration tests
# 3. accessibility-tests: Accessibility-only tests
```

## CI/CD Integration

### GitHub Actions Workflow

The CI/CD pipeline runs three parallel test jobs:

1. **E2E Tests** (ubuntu-latest):
   - Sets up Node.js and Python
   - Installs dependencies
   - Starts PostgreSQL test database
   - Runs database migrations
   - Starts backend server
   - Starts frontend dev server
   - Runs Playwright tests
   - Uploads test artifacts (reports, screenshots, videos)

2. **Integration Tests** (ubuntu-latest):
   - Sets up Python
   - Starts test database
   - Runs backend integration tests
   - Uploads coverage reports

3. **Accessibility Tests** (ubuntu-latest):
   - Runs only accessibility tests
   - Uploads accessibility reports

### Viewing Test Results

Test results are available as CI/CD artifacts:
- **playwright-report**: HTML report with screenshots and videos
- **test-results**: Raw test results in JSON format
- **accessibility-report**: Accessibility test results
- **integration-test-coverage**: Backend code coverage

## Test Data and Fixtures

### Fixture Files

Located in `frontend/e2e/fixtures/`:

**customers.json**:
```json
[
  {
    "id": "customer-1",
    "name": "John Smith",
    "age": 52,
    "email": "john.smith@example.com"
  }
]
```

**messages.json**:
```json
[
  {
    "id": "msg-1",
    "content": "Hello, I have a question about my pension options.",
    "type": "customer"
  }
]
```

**consultations.json**:
```json
[
  {
    "id": "test-consultation-1",
    "customerName": "John Smith",
    "topic": "Pension Consolidation Guidance",
    "status": "active"
  }
]
```

### Using Fixtures in Tests

```typescript
import customers from '../fixtures/customers.json' with { type: 'json' };

test('create consultation with customer data', async ({ page }) => {
  const customer = customers[0];
  // Use customer.name, customer.age, etc.
});
```

## Troubleshooting

### Common Issues

#### 1. Tailwind CSS Errors

**Error**: `Cannot apply unknown utility class`

**Solution**: Check that custom Tailwind classes are properly configured in `tailwind.config.js`.

#### 2. Tests Timing Out

**Error**: `Test timeout of 30000ms exceeded`

**Solution**:
- Increase timeout in playwright.config.ts
- Check if backend is running
- Verify database connections

#### 3. Flaky Tests

**Solution**:
- Use Playwright's built-in waiting mechanisms
- Avoid hard-coded waits (`page.waitForTimeout`)
- Use `page.waitForSelector` or `expect().toBeVisible()`
- Enable retries in CI: `retries: process.env.CI ? 2 : 0`

#### 4. Database Connection Issues

**Error**: `Connection refused` or `Database does not exist`

**Solution**:
```bash
# Ensure database is running
docker-compose ps

# Run migrations
alembic upgrade head

# Check connection string
echo $DATABASE_URL
```

#### 5. Port Conflicts

**Error**: `Port 5173 already in use`

**Solution**:
```bash
# Kill process using port
lsof -ti:5173 | xargs kill -9

# Or use different port
VITE_PORT=5174 npm run dev
```

### Debug Mode

```bash
# Run tests in debug mode (pauses at breakpoints)
npm run test:e2e:debug

# Run with verbose output
npm run test:e2e -- --reporter=list --workers=1

# Generate trace for failed tests
npm run test:e2e -- --trace on

# View trace
npx playwright show-trace trace.zip
```

### Test Coverage

```bash
# Frontend coverage
npm run test:coverage

# Backend coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Best Practices

### Writing Tests

1. **Use Page Object Models**: Encapsulate page interactions
2. **Avoid Hard-Coded Waits**: Use Playwright's auto-waiting
3. **Independent Tests**: Each test should be isolated
4. **Descriptive Names**: Test names should describe what they verify
5. **Arrange-Act-Assert**: Follow AAA pattern
6. **Clean Up**: Ensure tests clean up after themselves

### Test Data

1. **Use Fixtures**: Store test data in JSON files
2. **Generate Unique IDs**: Use UUIDs to avoid conflicts
3. **Reset State**: Clean database between test runs
4. **Mock External Services**: Don't rely on external APIs

### Performance

1. **Parallel Execution**: Run tests in parallel when possible
2. **Skip Expensive Operations**: Mock LLM calls in tests
3. **Use Test Database**: Separate from development database
4. **Minimize Network Calls**: Use mocks and stubs

## Next Steps

1. **Increase Coverage**: Add more edge case tests
2. **Visual Regression**: Add visual diff testing
3. **Performance Tests**: Add load and stress tests
4. **Security Tests**: Add penetration and security tests
5. **Mobile Testing**: Add mobile-specific test scenarios

## Resources

- [Playwright Documentation](https://playwright.dev/)
- [Vitest Documentation](https://vitest.dev/)
- [Pytest Documentation](https://docs.pytest.org/)
- [axe-core Documentation](https://github.com/dequelabs/axe-core)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

## Support

For issues or questions about testing:
1. Check this documentation
2. Review existing tests for examples
3. Check CI/CD logs for error details
4. Open an issue with test failure details
