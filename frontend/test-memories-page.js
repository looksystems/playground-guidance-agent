const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  const consoleMessages = [];
  const consoleErrors = [];
  const consoleWarnings = [];
  const pageErrors = [];

  // Listen to all console messages
  page.on('console', msg => {
    const text = msg.text();
    const type = msg.type();
    consoleMessages.push(`[${type}] ${text}`);

    if (type === 'error') {
      consoleErrors.push(text);
    } else if (type === 'warning') {
      consoleWarnings.push(text);
    }
  });

  // Listen to page errors
  page.on('pageerror', error => {
    pageErrors.push(`Page Error: ${error.message}\n${error.stack}`);
  });

  try {
    console.log('Navigating to http://localhost:3000/admin/learning/memories...\n');
    await page.goto('http://localhost:3000/admin/learning/memories', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    // Wait for the page to fully render
    await page.waitForTimeout(3000);

    // Check if the main heading is present
    const heading = await page.locator('h1').textContent();
    console.log(`✓ Page loaded successfully. Heading: "${heading}"\n`);

    // Take a screenshot
    await page.screenshot({
      path: './test-results/memories-page-screenshot.png',
      fullPage: true
    });
    console.log('✓ Screenshot saved to ./test-results/memories-page-screenshot.png\n');

    // Check for interactive elements
    const backButton = await page.locator('button:has-text("Back to Dashboard")').count();
    const clearFiltersButton = await page.locator('button:has-text("Clear")').count();
    console.log(`✓ Found ${backButton} back button(s)`);
    console.log(`✓ Found ${clearFiltersButton} clear filter button(s)\n`);

    // Print console messages
    console.log('=== CONSOLE MESSAGES ===');
    if (consoleMessages.length > 0) {
      consoleMessages.forEach(msg => console.log(msg));
    } else {
      console.log('No console messages');
    }

    console.log('\n=== CONSOLE ERRORS ===');
    if (consoleErrors.length > 0) {
      console.error('❌ ERRORS FOUND:');
      consoleErrors.forEach(err => console.error(err));
    } else {
      console.log('✓ No console errors found');
    }

    console.log('\n=== CONSOLE WARNINGS ===');
    if (consoleWarnings.length > 0) {
      console.warn('⚠️ WARNINGS FOUND:');
      consoleWarnings.forEach(warn => console.warn(warn));
    } else {
      console.log('✓ No console warnings found');
    }

    console.log('\n=== PAGE ERRORS ===');
    if (pageErrors.length > 0) {
      console.error('❌ PAGE ERRORS FOUND:');
      pageErrors.forEach(err => console.error(err));
    } else {
      console.log('✓ No page errors found');
    }

    // Test filter interactions
    console.log('\n=== TESTING INTERACTIONS ===');

    // Test memory type filter
    await page.click('div:has-text("Memory Type") + div button');
    await page.waitForTimeout(500);
    console.log('✓ Memory Type filter clicked');

    // Test clear filters button
    await page.click('button:has-text("Clear")');
    await page.waitForTimeout(500);
    console.log('✓ Clear filters button clicked');

    // Check if any new errors appeared
    console.log('\n=== FINAL STATUS ===');
    if (consoleErrors.length === 0 && pageErrors.length === 0) {
      console.log('✅ ALL TESTS PASSED - No errors found!');
    } else {
      console.log('❌ TESTS FAILED - Errors were found (see above)');
    }

    // Keep browser open for inspection
    console.log('\nBrowser will remain open for 10 seconds for inspection...');
    await page.waitForTimeout(10000);

  } catch (error) {
    console.error('❌ Test failed with error:', error.message);
    console.error(error.stack);
  } finally {
    await browser.close();
  }
})();
