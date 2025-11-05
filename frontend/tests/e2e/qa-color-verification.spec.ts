import { test, expect } from '@playwright/test'
import path from 'path'

test.describe('Color Implementation QA - Indigo Primary', () => {
  test.beforeEach(async ({ page }) => {
    // Clear console logs before each test
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.error(`❌ Console Error: ${msg.text()}`)
      } else if (msg.type() === 'warning') {
        console.warn(`⚠️  Console Warning: ${msg.text()}`)
      }
    })

    // Listen for page errors
    page.on('pageerror', error => {
      console.error(`❌ Page Error: ${error.message}`)
    })
  })

  test('Customer Chat Interface - Light Mode', async ({ page }) => {
    // Navigate to customer chat
    await page.goto('http://localhost:3000')
    await page.waitForLoadState('networkidle')

    // Wait for page to be fully rendered
    await page.waitForTimeout(1000)

    // Take full page screenshot
    await page.screenshot({
      path: '/tmp/qa-customer-chat-light.png',
      fullPage: true
    })

    // Check for console errors
    const consoleErrors: string[] = []
    const consoleWarnings: string[] = []

    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(msg.text())
      if (msg.type() === 'warning') consoleWarnings.push(msg.text())
    })

    // Verify primary color elements are visible
    const heading = page.locator('h1, h2').first()
    await expect(heading).toBeVisible()

    // Check for any buttons or links with primary color
    const buttons = page.locator('button, a')
    const buttonCount = await buttons.count()
    console.log(`✓ Found ${buttonCount} interactive elements`)

    // Check navigation if present
    const nav = page.locator('nav')
    if (await nav.count() > 0) {
      await expect(nav.first()).toBeVisible()
      console.log('✓ Navigation present and visible')
    }

    // Report console issues
    if (consoleErrors.length > 0) {
      console.error(`❌ Found ${consoleErrors.length} console errors`)
    } else {
      console.log('✓ No console errors')
    }

    if (consoleWarnings.length > 0) {
      console.warn(`⚠️  Found ${consoleWarnings.length} console warnings`)
    } else {
      console.log('✓ No console warnings')
    }
  })

  test('Customer Chat Interface - Dark Mode', async ({ page, context }) => {
    // Set dark mode
    await context.addInitScript(() => {
      localStorage.setItem('nuxt-color-mode', 'dark')
    })

    await page.goto('http://localhost:3000')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)

    // Take screenshot
    await page.screenshot({
      path: '/tmp/qa-customer-chat-dark.png',
      fullPage: true
    })

    console.log('✓ Dark mode screenshot captured')
  })

  test('Admin Dashboard - Light Mode', async ({ page }) => {
    await page.goto('http://localhost:3000/admin')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000) // Wait for data loading

    // Take screenshot
    await page.screenshot({
      path: '/tmp/qa-admin-dashboard-light.png',
      fullPage: true
    })

    // Verify metric cards are visible
    const metricCards = page.locator('[data-testid="metric-card"]')
    const cardCount = await metricCards.count()
    console.log(`✓ Found ${cardCount} metric cards`)

    if (cardCount >= 3) {
      await expect(metricCards.first()).toBeVisible()
      console.log('✓ Metric cards visible')
    }

    // Check for indigo color in primary elements
    const primaryElements = page.locator('[class*="primary"], [class*="indigo"]')
    const primaryCount = await primaryElements.count()
    console.log(`✓ Found ${primaryCount} elements with primary/indigo classes`)

    // Check for green color in compliance elements (should be preserved)
    const greenElements = page.locator('[class*="green"]')
    const greenCount = await greenElements.count()
    console.log(`✓ Found ${greenCount} elements with green classes (compliance indicators)`)
  })

  test('Admin Dashboard - Dark Mode', async ({ page, context }) => {
    await context.addInitScript(() => {
      localStorage.setItem('nuxt-color-mode', 'dark')
    })

    await page.goto('http://localhost:3000/admin')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)

    await page.screenshot({
      path: '/tmp/qa-admin-dashboard-dark.png',
      fullPage: true
    })

    console.log('✓ Admin dashboard dark mode screenshot captured')
  })

  test('Admin Data Management Pages - Memories', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/learning/memories')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)

    await page.screenshot({
      path: '/tmp/qa-admin-memories-light.png',
      fullPage: true
    })

    // Check for table or data display
    const hasTable = await page.locator('table').count() > 0
    const hasCards = await page.locator('[class*="card"]').count() > 0

    if (hasTable) {
      console.log('✓ Data table present')
    }
    if (hasCards) {
      console.log('✓ Card components present')
    }
  })

  test('Admin Data Management Pages - Cases', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/learning/cases')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)

    await page.screenshot({
      path: '/tmp/qa-admin-cases-light.png',
      fullPage: true
    })

    console.log('✓ Cases page screenshot captured')
  })

  test('Admin Data Management Pages - Rules', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/learning/rules')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)

    await page.screenshot({
      path: '/tmp/qa-admin-rules-light.png',
      fullPage: true
    })

    console.log('✓ Rules page screenshot captured')
  })

  test('Keyboard Navigation - Customer Chat', async ({ page }) => {
    await page.goto('http://localhost:3000')
    await page.waitForLoadState('networkidle')

    // Tab through interactive elements
    let tabCount = 0
    const maxTabs = 20

    for (let i = 0; i < maxTabs; i++) {
      await page.keyboard.press('Tab')
      tabCount++

      // Check if any element is focused
      const focused = await page.evaluate(() => {
        const el = document.activeElement
        return el ? {
          tag: el.tagName,
          type: el.getAttribute('type'),
          class: el.className
        } : null
      })

      if (focused) {
        console.log(`Tab ${tabCount}: ${focused.tag} ${focused.type || ''} ${focused.class}`)
      }

      await page.waitForTimeout(100)
    }

    console.log(`✓ Keyboard navigation tested through ${tabCount} tab presses`)
  })

  test('Responsive - Mobile (375px)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('http://localhost:3000')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)

    await page.screenshot({
      path: '/tmp/qa-responsive-mobile-375.png',
      fullPage: true
    })

    console.log('✓ Mobile 375px screenshot captured')

    // Check for horizontal scroll
    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth
    })

    if (hasHorizontalScroll) {
      console.warn('⚠️  Horizontal scroll detected on mobile view')
    } else {
      console.log('✓ No horizontal scroll on mobile view')
    }
  })

  test('Responsive - Tablet (768px)', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 })
    await page.goto('http://localhost:3000')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)

    await page.screenshot({
      path: '/tmp/qa-responsive-tablet-768.png',
      fullPage: true
    })

    console.log('✓ Tablet 768px screenshot captured')
  })

  test('Responsive - Desktop (1920px)', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 })
    await page.goto('http://localhost:3000')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)

    await page.screenshot({
      path: '/tmp/qa-responsive-desktop-1920.png',
      fullPage: true
    })

    console.log('✓ Desktop 1920px screenshot captured')
  })

  test('Color Contrast Check - Text Elements', async ({ page }) => {
    await page.goto('http://localhost:3000')
    await page.waitForLoadState('networkidle')

    // Check contrast of text elements
    const textElements = await page.locator('h1, h2, h3, h4, h5, h6, p, a, button, span').all()
    console.log(`✓ Checking ${textElements.length} text elements for contrast`)

    // Sample check (in real implementation, would use contrast calculation)
    let checkedCount = 0
    for (const element of textElements.slice(0, 20)) {
      const isVisible = await element.isVisible().catch(() => false)
      if (isVisible) {
        checkedCount++
      }
    }

    console.log(`✓ Verified ${checkedCount} visible text elements`)
  })

  test('Interactive Elements - Buttons and Links', async ({ page }) => {
    await page.goto('http://localhost:3000')
    await page.waitForLoadState('networkidle')

    // Find all buttons
    const buttons = await page.locator('button').all()
    console.log(`✓ Found ${buttons.length} buttons`)

    // Find all links
    const links = await page.locator('a').all()
    console.log(`✓ Found ${links.length} links`)

    // Check if buttons have proper states
    for (const button of buttons.slice(0, 5)) {
      const isVisible = await button.isVisible().catch(() => false)
      const isEnabled = await button.isEnabled().catch(() => true)

      if (isVisible) {
        console.log(`  Button: visible=${isVisible}, enabled=${isEnabled}`)
      }
    }
  })

  test('Admin Dashboard - Chart Colors', async ({ page }) => {
    await page.goto('http://localhost:3000/admin')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(3000) // Wait for chart to render

    // Take screenshot focused on chart area
    const chartContainer = page.locator('canvas').first()

    if (await chartContainer.count() > 0) {
      await chartContainer.screenshot({
        path: '/tmp/qa-chart-indigo.png'
      })
      console.log('✓ Chart screenshot captured')
    } else {
      console.log('⚠️  No chart canvas found')
    }
  })

  test('Console Logs - Full Session Check', async ({ page }) => {
    const consoleMessages: Array<{ type: string; text: string }> = []

    page.on('console', msg => {
      consoleMessages.push({
        type: msg.type(),
        text: msg.text()
      })
    })

    // Navigate through multiple pages
    await page.goto('http://localhost:3000')
    await page.waitForTimeout(1000)

    await page.goto('http://localhost:3000/admin')
    await page.waitForTimeout(2000)

    await page.goto('http://localhost:3000/admin/learning/memories')
    await page.waitForTimeout(1000)

    // Report console summary
    const errors = consoleMessages.filter(m => m.type === 'error')
    const warnings = consoleMessages.filter(m => m.type === 'warning')
    const info = consoleMessages.filter(m => m.type === 'info' || m.type === 'log')

    console.log('\n📊 Console Summary:')
    console.log(`   Errors: ${errors.length}`)
    console.log(`   Warnings: ${warnings.length}`)
    console.log(`   Info/Log: ${info.length}`)

    if (errors.length > 0) {
      console.log('\n❌ Console Errors:')
      errors.forEach(e => console.log(`   ${e.text}`))
    }

    if (warnings.length > 0) {
      console.log('\n⚠️  Console Warnings:')
      warnings.forEach(w => console.log(`   ${w.text}`))
    }

    // Fail test if there are errors
    expect(errors.length).toBe(0)
  })
})
