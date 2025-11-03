import { Page } from '@playwright/test'

/**
 * Test Fixtures for Admin Data Model E2E Tests
 *
 * Provides mock data and API response handlers for testing
 */

// ====================
// Mock Data
// ====================

export const mockFCAKnowledge = {
  items: [
    {
      id: '11111111-1111-1111-1111-111111111111',
      content: 'FCA requires pension advisors to assess suitability before making recommendations.',
      source: 'FCA Handbook COBS 9.2',
      category: 'Suitability',
      has_embedding: true,
      meta: { importance: 'high' },
      created_at: '2025-01-15T10:00:00Z'
    },
    {
      id: '22222222-2222-2222-2222-222222222222',
      content: 'Client agreements must be provided before conducting regulated activities.',
      source: 'FCA Handbook COBS 8.1',
      category: 'Client Agreement',
      has_embedding: true,
      meta: {},
      created_at: '2025-01-16T10:00:00Z'
    }
  ],
  total: 45,
  page: 1,
  page_size: 20,
  pages: 3
}

export const mockPensionKnowledge = {
  items: [
    {
      id: '33333333-3333-3333-3333-333333333333',
      content: 'State Pension age is currently 66 for both men and women.',
      category: 'State Pension',
      subcategory: 'Age',
      has_embedding: true,
      meta: {},
      created_at: '2025-01-15T10:00:00Z'
    }
  ],
  total: 78,
  page: 1,
  page_size: 20,
  pages: 4
}

export const mockMemories = {
  items: [
    {
      id: '44444444-4444-4444-4444-444444444444',
      description: 'Customer asked about pension transfer from defined benefit scheme',
      timestamp: '2025-01-20T14:30:00Z',
      last_accessed: '2025-01-21T09:15:00Z',
      importance: 0.85,
      memory_type: 'observation',
      has_embedding: true,
      meta: {},
      created_at: '2025-01-20T14:30:00Z'
    },
    {
      id: '55555555-5555-5555-5555-555555555555',
      description: 'Reflected on importance of checking transfer value analysis',
      timestamp: '2025-01-20T15:00:00Z',
      last_accessed: '2025-01-20T15:00:00Z',
      importance: 0.65,
      memory_type: 'reflection',
      has_embedding: true,
      meta: {},
      created_at: '2025-01-20T15:00:00Z'
    }
  ],
  total: 234,
  page: 1,
  page_size: 20,
  pages: 12
}

export const mockCases = {
  items: [
    {
      id: '66666666-6666-6666-6666-666666666666',
      task_type: 'Pension Transfer',
      customer_situation: 'Customer aged 58 with DB pension, considering transfer',
      guidance_provided: 'Advised to obtain transfer value analysis and consider guarantees',
      outcome: { satisfied: true, compliant: true },
      has_embedding: true,
      meta: {},
      created_at: '2025-01-15T10:00:00Z'
    }
  ],
  total: 89,
  page: 1,
  page_size: 20,
  pages: 5
}

export const mockRules = {
  items: [
    {
      id: '77777777-7777-7777-7777-777777777777',
      principle: 'Always check transfer value before advising on DB to DC transfers',
      domain: 'Pension Transfers',
      confidence: 0.92,
      supporting_evidence: ['case1', 'case2', 'case3'],
      evidence_count: 3,
      has_embedding: true,
      meta: {},
      created_at: '2025-01-10T10:00:00Z',
      updated_at: '2025-01-20T10:00:00Z'
    }
  ],
  total: 56,
  page: 1,
  page_size: 20,
  pages: 3
}

export const mockCustomers = {
  items: [
    {
      customer_id: '88888888-8888-8888-8888-888888888888',
      total_consultations: 3,
      first_consultation: '2024-12-01T10:00:00Z',
      last_consultation: '2025-01-20T14:30:00Z',
      avg_compliance_score: 0.95,
      avg_satisfaction: 4.5,
      topics: ['Pension Transfer', 'Retirement Planning'],
      customer_profile: {
        age: 58,
        retirement_goal_age: 65
      },
      recent_consultations: []
    }
  ],
  total: 125,
  page: 1,
  page_size: 20,
  pages: 7,
  stats: {
    total_customers: 125,
    active_customers_30d: 45,
    avg_consultations_per_customer: 2.3
  }
}

// ====================
// API Mock Helpers
// ====================

/**
 * Setup API mocks for a page with mock data
 */
export async function setupAPIMocks(page: Page, mockResponses: Record<string, any>) {
  for (const [endpoint, response] of Object.entries(mockResponses)) {
    await page.route(`**/api/admin/${endpoint}**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(response)
      })
    })
  }
}

/**
 * Setup API mocks for all admin data models
 */
export async function setupAllAPIMocks(page: Page) {
  await setupAPIMocks(page, {
    'fca-knowledge': mockFCAKnowledge,
    'fca-knowledge/*': mockFCAKnowledge.items[0],
    'pension-knowledge': mockPensionKnowledge,
    'pension-knowledge/*': mockPensionKnowledge.items[0],
    'memories': mockMemories,
    'memories/*': mockMemories.items[0],
    'cases': mockCases,
    'cases/*': mockCases.items[0],
    'rules': mockRules,
    'rules/*': mockRules.items[0],
    'customers': mockCustomers,
    'customers/*': mockCustomers.items[0]
  })
}

/**
 * Setup empty state mocks (no data)
 */
export async function setupEmptyStateMocks(page: Page) {
  const emptyResponse = {
    items: [],
    total: 0,
    page: 1,
    page_size: 20,
    pages: 0
  }

  await page.route('**/api/admin/**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(emptyResponse)
    })
  })
}

/**
 * Setup 404 error mocks
 */
export async function setup404Mocks(page: Page) {
  await page.route('**/api/admin/**', async (route) => {
    await route.fulfill({
      status: 404,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Not found' })
    })
  })
}

/**
 * Setup network error mocks
 */
export async function setupNetworkErrorMocks(page: Page) {
  await page.route('**/api/admin/**', async (route) => {
    await route.abort('failed')
  })
}
