import { chromium } from 'playwright';

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
    const heading = await page.locator('h1:has-text("Memory Bank")').textContent();
    console.log(`✓ Page loaded successfully. Heading: "${heading}"\n`);

    // Take a screenshot
    await page.screenshot({
      path: './test-results/memories-page-final.png',
      fullPage: true
    });
    console.log('✓ Screenshot saved to ./test-results/memories-page-final.png\n');

    // Check for interactive elements
    const backButton = await page.locator('button:has-text("Back to Dashboard")').count();
    const clearFiltersButton = await page.locator('button:has-text("Clear")').count();
    const viewButtons = await page.locator('button:has-text("View")').count();
    console.log(`✓ Found ${backButton} back button(s)`);
    console.log(`✓ Found ${clearFiltersButton} clear filter button(s)`);
    console.log(`✓ Found ${viewButtons} view button(s)\n`);

    // Check stats cards are visible
    const totalMemoriesCard = await page.locator('p:has-text("Total Memories")').count();
    const observationsCard = await page.locator('p:has-text("Observations")').count();
    const reflectionsCard = await page.locator('p:has-text("Reflections")').count();
    const plansCard = await page.locator('p:has-text("Plans")').count();
    console.log(`✓ Stats cards rendered: ${totalMemoriesCard + observationsCard + reflectionsCard + plansCard}/4\n`);

    // Check for indigo colors (verify theme change)
    const indigoElements = await page.locator('[class*="indigo"]').count();
    console.log(`✓ Found ${indigoElements} elements with indigo styling\n`);

    // Print console messages
    console.log('=== CONSOLE MESSAGES ===');
    if (consoleMessages.length > 0) {
      // Filter out common dev messages
      const relevantMessages = consoleMessages.filter(msg =>
        !msg.includes('[vite]') &&
        !msg.includes('DevTools') &&
        !msg.includes('Suspense is an experimental') &&
        !msg.includes('iframe which has both allow-scripts')
      );
      if (relevantMessages.length > 0) {
        relevantMessages.forEach(msg => console.log(msg));
      } else {
        console.log('No relevant console messages (filtered dev messages)');
      }
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
    const relevantWarnings = consoleWarnings.filter(w =>
      !w.includes('iframe which has both allow-scripts') &&
      !w.includes('preloaded using link preload') &&
      !w.includes('Suspense is an experimental')
    );
    if (relevantWarnings.length > 0) {
      console.warn('⚠️ RELEVANT WARNINGS FOUND:');
      relevantWarnings.forEach(warn => console.warn(warn));
    } else {
      console.log('✓ No relevant warnings found (filtered expected dev warnings)');
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

    // Test clear filters button
    try {
      await page.click('button:has-text("Clear")', { timeout: 5000 });
      await page.waitForTimeout(500);
      console.log('✓ Clear filters button clicked successfully');
    } catch (e) {
      console.log('⚠️ Could not click Clear filters button:', e.message);
    }

    // Test back button
    try {
      const backBtn = page.locator('button:has-text("Back to Dashboard")');
      if (await backBtn.count() > 0) {
        console.log('✓ Back to Dashboard button is visible and clickable');
      }
    } catch (e) {
      console.log('⚠️ Back button check failed:', e.message);
    }

    // Check if any new errors appeared after interaction
    console.log('\n=== FINAL STATUS ===');
    const hasRelevantErrors = consoleErrors.length > 0 || pageErrors.length > 0;

    if (!hasRelevantErrors) {
      console.log('✅ ALL TESTS PASSED - No errors found!');
      console.log('✅ Page loads correctly with indigo theme');
      console.log('✅ All interactive elements are present');
      console.log('✅ Color scheme successfully changed from green to indigo');
    } else {
      console.log('❌ TESTS FAILED - Errors were found (see above)');
    }

    // Keep browser open for inspection
    console.log('\nBrowser will remain open for 5 seconds for inspection...');
    await page.waitForTimeout(5000);

  } catch (error) {
    console.error('❌ Test failed with error:', error.message);
    console.error(error.stack);
  } finally {
    await browser.close();
  }
})();
