import { test, expect, Page } from '@playwright/test'

/**
 * E2E Tests for Validation Reasoning Display Feature
 *
 * Tests the expandable compliance reasoning section in consultation detail page
 * Following TDD approach - these tests are written BEFORE implementation
 *
 * Test Coverage:
 * - Reasoning section hidden by default
 * - Toggle functionality shows/hides reasoning
 * - Proper display of compliance issues
 * - Pass/fail badge display
 * - Severity color coding
 * - Graceful handling of missing reasoning data (backward compatibility)
 * - Review flag display
 */

// Test helper to wait for page load
async function waitForPageLoad(page: Page) {
  await page.waitForLoadState('networkidle')
  await page.waitForSelector('[data-testid="skeleton"]', { state: 'hidden', timeout: 10000 }).catch(() => {
    // Skeletons might not exist, that's okay
  })
}

/**
 * Setup mock consultation data with reasoning
 */
async function setupMockConsultation(page: Page) {
  // Intercept API call and return mock data with compliance reasoning
  await page.route('**/api/admin/consultations/*', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'test-consultation-123',
        customer_name: 'Test Customer',
        customer_age: 55,
        conversation: [
          {
            role: 'customer',
            content: 'I want to withdraw my entire pension pot.',
            timestamp: '2025-11-03T10:00:00Z'
          },
          {
            role: 'advisor',
            content: 'I understand you are considering withdrawing your entire pension pot. Before proceeding, it is important to understand the implications...',
            timestamp: '2025-11-03T10:01:00Z',
            compliance_score: 0.92,
            compliance_confidence: 0.92,
            compliance_reasoning: `# Compliance Analysis

## 1. Guidance Boundary (Score: 0.95)
The advisor correctly stays within regulated guidance boundaries by explaining implications without making personal recommendations.

## 2. Risk Disclosure (Score: 0.90)
Adequate risk disclosure provided, including tax implications and sustainability concerns.

## 3. Neutrality (Score: 0.93)
The response maintains neutrality by presenting options without bias.

## 4. Comprehension (Score: 0.88)
Language is clear but could be more tailored to customer understanding level.

## 5. Documentation (Score: 0.95)
Response is well-documented and traceable.

## Overall Assessment
The advisor's response demonstrates strong compliance with FCA guidance requirements. Minor improvements could be made in comprehension checking.`,
            compliance_issues: [
              {
                category: 'comprehension',
                severity: 'minor',
                description: 'Could include more comprehension checks to ensure customer understanding'
              }
            ],
            compliance_passed: true,
            requires_human_review: false
          },
          {
            role: 'customer',
            content: 'Should I invest in stocks?',
            timestamp: '2025-11-03T10:02:00Z'
          },
          {
            role: 'advisor',
            content: 'You should definitely invest in tech stocks right now!',
            timestamp: '2025-11-03T10:03:00Z',
            compliance_score: 0.35,
            compliance_confidence: 0.35,
            compliance_reasoning: `# Compliance Analysis - CRITICAL FAILURE

## 1. Guidance Boundary (Score: 0.10)
**CRITICAL VIOLATION**: This response crosses into regulated advice territory by making specific investment recommendations.

## 2. Risk Disclosure (Score: 0.20)
Inadequate risk disclosure - no mention of risks associated with stock investments.

## 3. Neutrality (Score: 0.30)
The recommendation shows bias toward specific investment types.

## 4. Comprehension (Score: 0.50)
No assessment of customer's investment knowledge or risk tolerance.

## 5. Documentation (Score: 0.60)
Response lacks proper context and reasoning.

## Overall Assessment
**FAILED** - This response constitutes regulated investment advice and violates FCA guidance boundaries. Immediate correction required.`,
            compliance_issues: [
              {
                category: 'guidance_boundary',
                severity: 'critical',
                description: 'Response provides specific investment advice, crossing into regulated territory'
              },
              {
                category: 'risk_disclosure',
                severity: 'major',
                description: 'Missing risk disclosure for investment recommendations'
              },
              {
                category: 'neutrality',
                severity: 'major',
                description: 'Recommendation shows bias and lacks balanced perspective'
              }
            ],
            compliance_passed: false,
            requires_human_review: true
          }
        ],
        metrics: {
          avg_compliance_score: 0.635
        },
        outcome: {
          retrieved_cases: 3,
          applied_rules: [
            'FCA COBS 9.2: Assess client suitability',
            'FCA COBS 4.2: Communicate clearly'
          ]
        }
      })
    })
  })
}

/**
 * Setup mock consultation WITHOUT reasoning (backward compatibility test)
 */
async function setupMockConsultationWithoutReasoning(page: Page) {
  await page.route('**/api/admin/consultations/*', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'test-consultation-old',
        customer_name: 'Old Customer',
        customer_age: 60,
        conversation: [
          {
            role: 'advisor',
            content: 'This is an old consultation without reasoning data.',
            timestamp: '2025-11-01T10:00:00Z',
            compliance_score: 0.85,
            compliance_confidence: 0.85
            // No compliance_reasoning, compliance_issues, compliance_passed, requires_human_review
          }
        ],
        metrics: {
          avg_compliance_score: 0.85
        }
      })
    })
  })
}

test.describe('Validation Reasoning Display', () => {

  test.describe('Basic Display and Toggle Functionality', () => {
    test('should NOT show reasoning section by default (collapsed state)', async ({ page }) => {
      await setupMockConsultation(page)
      await page.goto('/admin/consultations/test-123')
      await waitForPageLoad(page)

      // Find the first advisor message with compliance score
      const advisorMessage = page.locator('[class*="border-orange"]').first()
      await expect(advisorMessage).toBeVisible()

      // Compliance badge should be visible
      const complianceBadge = advisorMessage.locator('[class*="badge"]', { hasText: /\d+%/ })
      await expect(complianceBadge.first()).toBeVisible()

      // Reasoning section should NOT be visible initially
      const reasoningSection = page.getByText(/Detailed Analysis/i)
      await expect(reasoningSection).not.toBeVisible()
    })

    test('should show reasoning section when compliance badge is clicked', async ({ page }) => {
      await setupMockConsultation(page)
      await page.goto('/admin/consultations/test-123')
      await waitForPageLoad(page)

      // Click the compliance badge to expand reasoning
      const complianceBadge = page.locator('[data-testid="compliance-badge"]').first()
      await complianceBadge.click()

      // Reasoning section should now be visible
      const reasoningSection = page.getByText(/Detailed Analysis/i)
      await expect(reasoningSection).toBeVisible({ timeout: 2000 })
    })

    test('should toggle reasoning section on multiple clicks', async ({ page }) => {
      await setupMockConsultation(page)
      await page.goto('/admin/consultations/test-123')
      await waitForPageLoad(page)

      const complianceBadge = page.locator('[data-testid="compliance-badge"]').first()
      const reasoningSection = page.getByText(/Detailed Analysis/i)

      // Expand
      await complianceBadge.click()
      await expect(reasoningSection).toBeVisible()

      // Collapse
      await complianceBadge.click()
      await expect(reasoningSection).not.toBeVisible()

      // Expand again
      await complianceBadge.click()
      await expect(reasoningSection).toBeVisible()
    })

    test('should show chevron icon indicating expandable state', async ({ page }) => {
      await setupMockConsultation(page)
      await page.goto('/admin/consultations/test-123')
      await waitForPageLoad(page)

      // Should have chevron-down icon when collapsed
      const chevronDown = page.locator('[class*="i-heroicons-chevron-down"]').first()
      await expect(chevronDown).toBeVisible()

      // Click to expand
      const complianceBadge = page.locator('[data-testid="compliance-badge"]').first()
      await complianceBadge.click()

      // Should have chevron-up icon when expanded
      const chevronUp = page.locator('[class*="i-heroicons-chevron-up"]').first()
      await expect(chevronUp).toBeVisible()
    })
  })

  test.describe('Compliance Status Display', () => {
    test('should display PASSED badge for compliant messages', async ({ page }) => {
      await setupMockConsultation(page)
      await page.goto('/admin/consultations/test-123')
      await waitForPageLoad(page)

      // Expand first advisor message (which passes)
      const firstBadge = page.locator('[data-testid="compliance-badge"]').first()
      await firstBadge.click()

      // Should show PASSED badge
      const passedBadge = page.getByText('PASSED')
      await expect(passedBadge).toBeVisible()

      // PASSED badge should be green
      await expect(passedBadge).toHaveClass(/green|success/i)
    })

    test('should display FAILED badge for non-compliant messages', async ({ page }) => {
      await setupMockConsultation(page)
      await page.goto('/admin/consultations/test-123')
      await waitForPageLoad(page)

      // Expand second advisor message (which fails)
      const secondBadge = page.locator('[data-testid="compliance-badge"]').nth(1)
      await secondBadge.click()

      // Should show FAILED badge
      const failedBadge = page.getByText('FAILED')
      await expect(failedBadge).toBeVisible()

      // FAILED badge should be red
      await expect(failedBadge).toHaveClass(/red|error|danger/i)
    })

    test('should display "Requires Review" badge when flagged', async ({ page }) => {
      await setupMockConsultation(page)
      await page.goto('/admin/consultations/test-123')
      await waitForPageLoad(page)

      // Expand second advisor message (which requires review)
      const secondBadge = page.locator('[data-testid="compliance-badge"]').nth(1)
      await secondBadge.click()

      // Should show Requires Review badge
      const reviewBadge = page.getByText(/Requires Review/i)
      await expect(reviewBadge).toBeVisible()

      // Review badge should be orange/warning
      await expect(reviewBadge).toHaveClass(/orange|warning/i)
    })

    test('should NOT display "Requires Review" badge when not flagged', async ({ page }) => {
      await setupMockConsultation(page)
      await page.goto('/admin/consultations/test-123')
      await waitForPageLoad(page)

      // Expand first advisor message (which doesn't require review)
      const firstBadge = page.locator('[data-testid="compliance-badge"]').first()
      await firstBadge.click()

      // Should NOT show Requires Review badge
      const reviewBadge = page.getByText(/Requires Review/i)
      await expect(reviewBadge).not.toBeVisible()
    })
  })

  test.describe('Compliance Issues Display', () => {
    test('should display list of compliance issues when present', async ({ page }) => {
      await setupMockConsultation(page)
      await page.goto('/admin/consultations/test-123')
      await waitForPageLoad(page)

      // Expand second advisor message (which has multiple issues)
      const secondBadge = page.locator('[data-testid="compliance-badge"]').nth(1)
      await secondBadge.click()

      // Should show "Issues Found" section
      await expect(page.getByText(/Issues Found/i)).toBeVisible()

      // Should display all three issues
      await expect(page.getByText(/Response provides specific investment advice/i)).toBeVisible()
      await expect(page.getByText(/Missing risk disclosure/i)).toBeVisible()
      await expect(page.getByText(/Recommendation shows bias/i)).toBeVisible()
    })

    test('should display severity badges with correct colors', async ({ page }) => {
      await setupMockConsultation(page)
      await page.goto('/admin/consultations/test-123')
      await waitForPageLoad(page)

      // Expand second advisor message
      const secondBadge = page.locator('[data-testid="compliance-badge"]').nth(1)
      await secondBadge.click()

      // Critical severity should be red
      const criticalBadge = page.getByText('critical')
      await expect(criticalBadge).toBeVisible()
      await expect(criticalBadge).toHaveClass(/red|error|danger/i)

      // Major severity should be orange
      const majorBadges = page.getByText('major')
      await expect(majorBadges.first()).toBeVisible()
      await expect(majorBadges.first()).toHaveClass(/orange|warning/i)
    })

    test('should display minor severity issues with yellow badge', async ({ page }) => {
      await setupMockConsultation(page)
      await page.goto('/admin/consultations/test-123')
      await waitForPageLoad(page)

      // Expand first advisor message (has minor issue)
      const firstBadge = page.locator('[data-testid="compliance-badge"]').first()
      await firstBadge.click()

      // Minor severity should be yellow
      const minorBadge = page.getByText('minor')
      await expect(minorBadge).toBeVisible()
      await expect(minorBadge).toHaveClass(/yellow|warning/i)
    })

    test('should NOT display issues section when no issues present', async ({ page }) => {
      // Setup mock with no issues
      await page.route('**/api/admin/consultations/*', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            conversation: [
              {
                role: 'advisor',
                content: 'Perfect response.',
                timestamp: '2025-11-03T10:00:00Z',
                compliance_score: 1.0,
                compliance_reasoning: 'All compliance areas scored 1.0.',
                compliance_issues: [], // Empty issues array
                compliance_passed: true,
                requires_human_review: false
              }
            ],
            customer_name: 'Test',
            customer_age: 50,
            metrics: { avg_compliance_score: 1.0 }
          })
        })
      })

      await page.goto('/admin/consultations/test-123')
      await waitForPageLoad(page)

      const badge = page.locator('[data-testid="compliance-badge"]').first()
      await badge.click()

      // Should NOT show "Issues Found" section
      await expect(page.getByText(/Issues Found/i)).not.toBeVisible()
    })
  })

  test.describe('Detailed Reasoning Display', () => {
    test('should display full compliance reasoning text', async ({ page }) => {
      await setupMockConsultation(page)
      await page.goto('/admin/consultations/test-123')
      await waitForPageLoad(page)

      // Expand first advisor message
      const firstBadge = page.locator('[data-testid="compliance-badge"]').first()
      await firstBadge.click()

      // Should show detailed analysis section
      await expect(page.getByText(/Detailed Analysis/i)).toBeVisible()

      // Should display parts of the reasoning
      await expect(page.getByText(/Guidance Boundary/i)).toBeVisible()
      await expect(page.getByText(/Risk Disclosure/i)).toBeVisible()
      await expect(page.getByText(/Overall Assessment/i)).toBeVisible()
    })

    test('should preserve formatting in reasoning text', async ({ page }) => {
      await setupMockConsultation(page)
      await page.goto('/admin/consultations/test-123')
      await waitForPageLoad(page)

      const firstBadge = page.locator('[data-testid="compliance-badge"]').first()
      await firstBadge.click()

      // Reasoning should be in a <pre> tag to preserve formatting
      const reasoningPre = page.locator('pre', { hasText: /Compliance Analysis/i })
      await expect(reasoningPre).toBeVisible()
    })
  })

  test.describe('Backward Compatibility', () => {
    test('should gracefully handle messages without reasoning data', async ({ page }) => {
      await setupMockConsultationWithoutReasoning(page)
      await page.goto('/admin/consultations/test-old')
      await waitForPageLoad(page)

      // Page should load successfully
      await expect(page.getByRole('heading', { name: /Consultation Review/i })).toBeVisible()

      // Should still show compliance score
      const complianceBadge = page.locator('[class*="badge"]', { hasText: /85%|0\.85/i })
      const badgeCount = await complianceBadge.count()
      expect(badgeCount).toBeGreaterThan(0)

      // Should NOT show expandable reasoning (no chevron, not clickable)
      const chevron = page.locator('[class*="chevron"]')
      await expect(chevron).not.toBeVisible()
    })

    test('should NOT crash when clicking badge without reasoning data', async ({ page }) => {
      await setupMockConsultationWithoutReasoning(page)
      await page.goto('/admin/consultations/test-old')
      await waitForPageLoad(page)

      // Try clicking the badge (should do nothing gracefully)
      const badge = page.locator('[class*="badge"]').first()
      if (await badge.isVisible()) {
        await badge.click().catch(() => {
          // It's okay if badge is not clickable
        })
      }

      // Page should still be functional
      await expect(page.getByRole('heading', { name: /Consultation Review/i })).toBeVisible()
    })

    test('should only show expandable UI for messages with reasoning', async ({ page }) => {
      // Setup mixed data
      await page.route('**/api/admin/consultations/*', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            conversation: [
              {
                role: 'advisor',
                content: 'Old message without reasoning.',
                timestamp: '2025-11-01T10:00:00Z',
                compliance_score: 0.85
                // No reasoning data
              },
              {
                role: 'advisor',
                content: 'New message with reasoning.',
                timestamp: '2025-11-03T10:00:00Z',
                compliance_score: 0.90,
                compliance_reasoning: 'Full reasoning here.',
                compliance_issues: [],
                compliance_passed: true,
                requires_human_review: false
              }
            ],
            customer_name: 'Test',
            customer_age: 50,
            metrics: { avg_compliance_score: 0.875 }
          })
        })
      })

      await page.goto('/admin/consultations/test-mixed')
      await waitForPageLoad(page)

      // First message should NOT have expandable UI
      const advisorMessages = page.locator('[class*="border-orange"]')
      const firstMessage = advisorMessages.first()
      const firstChevron = firstMessage.locator('[class*="chevron"]')
      await expect(firstChevron).not.toBeVisible()

      // Second message SHOULD have expandable UI
      const secondMessage = advisorMessages.nth(1)
      const secondChevron = secondMessage.locator('[class*="chevron"]')
      await expect(secondChevron).toBeVisible()
    })
  })

  test.describe('Visual Design and UX', () => {
    test('should style reasoning section differently from main content', async ({ page }) => {
      await setupMockConsultation(page)
      await page.goto('/admin/consultations/test-123')
      await waitForPageLoad(page)

      const firstBadge = page.locator('[data-testid="compliance-badge"]').first()
      await firstBadge.click()

      // Reasoning card should have distinct background
      const reasoningCard = page.locator('[class*="bg-gray"]', { hasText: /Detailed Analysis/i })
      await expect(reasoningCard).toBeVisible()
    })

    test('should show cursor pointer on compliance badge when clickable', async ({ page }) => {
      await setupMockConsultation(page)
      await page.goto('/admin/consultations/test-123')
      await waitForPageLoad(page)

      // Badge should have cursor-pointer class
      const badge = page.locator('[data-testid="compliance-badge"]').first()
      await expect(badge).toHaveClass(/cursor-pointer/i)
    })

    test('should display issues in a readable list format', async ({ page }) => {
      await setupMockConsultation(page)
      await page.goto('/admin/consultations/test-123')
      await waitForPageLoad(page)

      const secondBadge = page.locator('[data-testid="compliance-badge"]').nth(1)
      await secondBadge.click()

      // Issues should be in a list
      const issuesList = page.locator('ul', { has: page.locator('li', { hasText: /Response provides specific/i }) })
      await expect(issuesList).toBeVisible()

      // Each issue should have severity badge and description
      const issueItems = issuesList.locator('li')
      const count = await issueItems.count()
      expect(count).toBe(3) // Three issues in mock data
    })
  })

  test.describe('Multiple Messages', () => {
    test('should independently toggle reasoning for each message', async ({ page }) => {
      await setupMockConsultation(page)
      await page.goto('/admin/consultations/test-123')
      await waitForPageLoad(page)

      // Expand first message
      const firstBadge = page.locator('[data-testid="compliance-badge"]').first()
      await firstBadge.click()

      const firstReasoning = page.locator('[class*="border-orange"]').first().getByText(/Detailed Analysis/i)
      await expect(firstReasoning).toBeVisible()

      // Expand second message
      const secondBadge = page.locator('[data-testid="compliance-badge"]').nth(1)
      await secondBadge.click()

      const secondReasoning = page.locator('[class*="border-orange"]').nth(1).getByText(/Detailed Analysis/i)
      await expect(secondReasoning).toBeVisible()

      // Both should be visible simultaneously
      await expect(firstReasoning).toBeVisible()
      await expect(secondReasoning).toBeVisible()

      // Collapse first message
      await firstBadge.click()
      await expect(firstReasoning).not.toBeVisible()

      // Second should still be visible
      await expect(secondReasoning).toBeVisible()
    })
  })
})
