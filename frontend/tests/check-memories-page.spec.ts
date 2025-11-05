import { test, expect } from '@playwright/test'

test('Check memories page for console errors', async ({ page }) => {
  const consoleMessages: string[] = []
  const consoleErrors: string[] = []
  const consoleWarnings: string[] = []

  // Listen to all console messages
  page.on('console', msg => {
    const text = msg.text()
    consoleMessages.push(`[${msg.type()}] ${text}`)

    if (msg.type() === 'error') {
      consoleErrors.push(text)
    } else if (msg.type() === 'warning') {
      consoleWarnings.push(text)
    }
  })

  // Listen to page errors
  page.on('pageerror', error => {
    consoleErrors.push(`Page Error: ${error.message}`)
  })

  // Navigate to the memories page
  await page.goto('http://localhost:3000/admin/learning/memories', {
    waitUntil: 'networkidle'
  })

  // Wait a bit for any async errors
  await page.waitForTimeout(2000)

  // Take a screenshot
  await page.screenshot({
    path: '/Users/adrian/Work/guidance-agent/frontend/test-results/memories-page.png',
    fullPage: true
  })

  // Log all console messages
  console.log('\n=== ALL CONSOLE MESSAGES ===')
  consoleMessages.forEach(msg => console.log(msg))

  console.log('\n=== CONSOLE ERRORS ===')
  if (consoleErrors.length > 0) {
    consoleErrors.forEach(err => console.log(err))
  } else {
    console.log('No console errors found')
  }

  console.log('\n=== CONSOLE WARNINGS ===')
  if (consoleWarnings.length > 0) {
    consoleWarnings.forEach(warn => console.log(warn))
  } else {
    console.log('No console warnings found')
  }

  // Check if page loaded successfully
  await expect(page.locator('h1')).toContainText('Memory Bank')

  // This test should pass even if there are console errors
  // We just want to see what they are
})
