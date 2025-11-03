# E2E Tests for Admin Data Models - Phase 6

## Overview

Comprehensive Playwright E2E tests for all 12 admin data model pages implemented in Phase 6.

## Pages Tested

### Knowledge Base (4 pages)
1. `/admin/knowledge/fca` - FCA Knowledge list page
2. `/admin/knowledge/fca/[id]` - FCA Knowledge detail page
3. `/admin/knowledge/pension` - Pension Knowledge list page
4. `/admin/knowledge/pension/[id]` - Pension Knowledge detail page

### Learning System (6 pages)
5. `/admin/learning/memories` - Memories list page
6. `/admin/learning/memories/[id]` - Memory detail page
7. `/admin/learning/cases` - Cases list page
8. `/admin/learning/cases/[id]` - Case detail page
9. `/admin/learning/rules` - Rules list page
10. `/admin/learning/rules/[id]` - Rule detail page

### Customer Management (2 pages)
11. `/admin/users/customers` - Customers list page
12. `/admin/users/customers/[id]` - Customer detail page

## Test Files

- **`admin-data-models.spec.ts`** - Main test suite without API mocking (tests against real backend or empty states)
- **`admin-data-models-with-mocks.spec.ts`** - Tests with mocked API responses for consistent data
- **`fixtures.ts`** - Mock data and API response helpers

## Test Coverage

### List Pages
- ✅ Page loads successfully with correct heading
- ✅ Stats cards display with correct data
- ✅ FilterBar is present and functional
- ✅ DataTable displays items
- ✅ Pagination controls work
- ✅ Filter changes update displayed data
- ✅ Loading state displays initially
- ✅ Empty state displays when no data
- ✅ Error state displays on API failure
- ✅ Back to Dashboard button works

### Detail Pages
- ✅ Page loads successfully
- ✅ Breadcrumb and back button present
- ✅ Main content card displays all fields
- ✅ Copy-to-clipboard for ID field
- ✅ Metadata section displays
- ✅ Vector indicator shows correct status
- ✅ Navigation back to list works
- ✅ 404 handling for invalid ID
- ✅ Loading state displays initially
- ✅ Error state displays on API failure

### Additional Coverage
- ✅ Cross-page navigation
- ✅ Accessibility (heading hierarchy, keyboard navigation)
- ✅ Network error handling
- ✅ Search functionality with debouncing
- ✅ Date filtering
- ✅ Clear filters functionality
- ✅ Sorting controls
- ✅ Color coding for importance/confidence scores

## Installation

Install Playwright and dependencies:

```bash
npm install
```

Install Playwright browsers (first time only):

```bash
npx playwright install
```

## Running Tests

### Run all E2E tests (headless)
```bash
npm run test:e2e
```

### Run tests with UI mode (interactive)
```bash
npm run test:e2e:ui
```

### Run tests in headed mode (see browser)
```bash
npm run test:e2e:headed
```

### Run tests in debug mode
```bash
npm run test:e2e:debug
```

### Run specific test file
```bash
npx playwright test admin-data-models.spec.ts
```

### Run tests for specific page
```bash
npx playwright test -g "FCA Knowledge"
```

### View test report
```bash
npm run test:e2e:report
```

## Configuration

Test configuration is in `playwright.config.ts`:

- **Base URL**: `http://localhost:3000` (configurable via `BASE_URL` env var)
- **Timeout**: 30 seconds per test
- **Retries**: 2 retries in CI, 0 locally
- **Browsers**: Chromium (Firefox and WebKit can be enabled)
- **Screenshots**: Captured on failure
- **Videos**: Retained on failure
- **Traces**: Captured on first retry

## Test Strategy

### Without Mocks (`admin-data-models.spec.ts`)
- Tests pages against real backend or empty states
- Verifies actual API integration
- May require backend to be running
- Tests are more lenient and handle various data states

### With Mocks (`admin-data-models-with-mocks.spec.ts`)
- Uses fixtures to provide consistent test data
- Tests specific UI behaviors with known data
- Faster execution (no backend required)
- Tests edge cases like empty states and 404 errors

## Running Backend for Tests

If testing against real backend, start both services:

```bash
# Terminal 1: Start backend API
cd ../..
python -m uvicorn src.guidance_agent.api.main:app --reload

# Terminal 2: Start frontend dev server
cd frontend
npm run dev

# Terminal 3: Run tests
npm run test:e2e
```

## Mock Data

Test fixtures in `fixtures.ts` provide:

- Sample data for all 6 models
- Paginated responses
- Empty state responses
- 404 error responses
- Network error simulation

You can customize mock data by editing `fixtures.ts`.

## Test Helpers

### `waitForPageLoad(page)`
Waits for page to finish loading, including skeleton loaders.

### `checkStatsCards(page, expectedCount)`
Verifies stats cards are displayed.

### `checkFilterBar(page)`
Verifies filter controls are present.

### `checkDataDisplay(page)`
Verifies table or list displays data.

### `checkPagination(page)`
Verifies pagination controls exist.

### API Mock Helpers (from fixtures.ts)

- `setupAPIMocks(page, mockResponses)` - Setup specific endpoint mocks
- `setupAllAPIMocks(page)` - Setup mocks for all admin endpoints
- `setupEmptyStateMocks(page)` - Setup empty state responses
- `setup404Mocks(page)` - Setup 404 error responses
- `setupNetworkErrorMocks(page)` - Simulate network failures

## Test Results

Test results are saved in:
- **HTML Report**: `playwright-report/index.html`
- **JSON Results**: `test-results/results.json`
- **Screenshots**: `test-results/` (on failure)
- **Videos**: `test-results/` (on failure)

## Continuous Integration

Tests are configured for CI with:
- Retry logic (2 retries)
- Single worker for stability
- Automatic browser installation
- Comprehensive reporting

## Troubleshooting

### Tests fail with "Page not found"
- Ensure backend is running on `http://localhost:8000`
- Ensure frontend dev server is running on `http://localhost:3000`
- Check `BASE_URL` in configuration

### Tests timeout
- Increase timeout in `playwright.config.ts`
- Check if backend is responding slowly
- Try running tests with `--headed` to see what's happening

### Flaky tests
- Tests include wait strategies to minimize flakiness
- If tests are flaky, check network latency
- Consider using mocked tests for more stability

### Mock data not working
- Verify fixtures.ts exports are correct
- Check route matching in setupAPIMocks
- Enable `trace: 'on'` to debug API calls

## Adding New Tests

To add tests for new pages:

1. Add mock data to `fixtures.ts`
2. Create test describe block in spec file
3. Test list page features
4. Test detail page features
5. Test edge cases (404, empty, errors)

Example:

```typescript
test.describe('New Model - List Page', () => {
  test('should load successfully', async ({ page }) => {
    await page.goto('/admin/new-model')
    await waitForPageLoad(page)
    await expect(page.getByRole('heading', { name: /New Model/i })).toBeVisible()
  })

  test('should display stats cards', async ({ page }) => {
    await page.goto('/admin/new-model')
    await waitForPageLoad(page)
    await checkStatsCards(page, 2)
  })

  // Add more tests...
})
```

## Test Statistics

- **Total Test Files**: 3
- **Total Tests**: 80+
- **Pages Covered**: 12 (6 models × 2 pages)
- **Test Categories**:
  - List page tests: 50+
  - Detail page tests: 15+
  - Navigation tests: 5+
  - Error handling tests: 5+
  - Accessibility tests: 5+

## Resources

- [Playwright Documentation](https://playwright.dev)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Phase 6 Specification](../../../specs/PHASE6_ADMIN_DATA_MODELS.md)
