import { chromium } from 'playwright';

async function runQA() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  console.log('=== ADMIN CONSULTATIONS PAGE QA REPORT ===\n');

  try {
    // Navigate to admin dashboard
    console.log('Navigating to http://localhost:3000/admin...');
    await page.goto('http://localhost:3000/admin', { waitUntil: 'networkidle' });
    console.log('✓ Page loaded\n');

    // Collect console messages
    const errors = [];
    const warnings = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
      else if (msg.type() === 'warning') warnings.push(msg.text());
    });

    // Wait for data to load
    await page.waitForSelector('table tbody tr', { timeout: 10000 }).catch(() => {
      console.log('⚠️  No table rows found - data may not be loaded\n');
    });

    // 1. TAKE SCREENSHOTS
    console.log('=== 1. SCREENSHOTS ===');
    await page.screenshot({ path: '/tmp/admin-consultations-full.png', fullPage: true });
    console.log('✓ Full page screenshot saved to /tmp/admin-consultations-full.png\n');

    // 2. CONSOLE ERRORS/WARNINGS
    await page.waitForTimeout(2000); // Wait to collect messages
    console.log('=== 2. CONSOLE ERRORS & WARNINGS ===');
    if (errors.length > 0) {
      console.log(`❌ ERRORS (${errors.length}):`);
      errors.forEach((e, i) => console.log(`  ${i + 1}. ${e}`));
    } else {
      console.log('✓ No console errors');
    }
    if (warnings.length > 0) {
      console.log(`⚠️  WARNINGS (${warnings.length}):`);
      warnings.forEach((w, i) => console.log(`  ${i + 1}. ${w}`));
    } else {
      console.log('✓ No console warnings');
    }
    console.log('');

    // 3. INSPECT BUTTONS
    console.log('=== 3. BUTTON COLOR INSPECTION ===');
    const buttons = await page.locator('button').all();
    console.log(`Found ${buttons.length} buttons\n`);

    let greenButtonsFound = 0;
    let indigoButtonsFound = 0;

    for (let i = 0; i < buttons.length; i++) {
      const button = buttons[i];
      const text = await button.textContent();
      const isVisible = await button.isVisible().catch(() => false);

      if (!isVisible) continue;

      const bgColor = await button.evaluate(el => window.getComputedStyle(el).backgroundColor);
      const borderColor = await button.evaluate(el => window.getComputedStyle(el).borderColor);
      const textColor = await button.evaluate(el => window.getComputedStyle(el).color);

      const hasGreen =
        bgColor.includes('34, 197, 94') || bgColor.includes('22, 163, 74') ||
        borderColor.includes('34, 197, 94') || borderColor.includes('22, 163, 74');

      const hasIndigo =
        bgColor.includes('79, 70, 229') || bgColor.includes('99, 102, 241') ||
        borderColor.includes('79, 70, 229') || borderColor.includes('99, 102, 241');

      if (hasGreen || hasIndigo || text?.trim()) {
        console.log(`Button: "${text?.trim() || 'No text'}"`);
        console.log(`  Background: ${bgColor}`);
        console.log(`  Border: ${borderColor}`);
        console.log(`  Text: ${textColor}`);

        if (hasGreen) {
          console.log('  ❌ GREEN COLOR DETECTED - SHOULD BE INDIGO!');
          greenButtonsFound++;
        }
        if (hasIndigo) {
          console.log('  ✓ Indigo color scheme');
          indigoButtonsFound++;
        }
        console.log('');
      }
    }

    console.log(`Summary: ${indigoButtonsFound} buttons with indigo, ${greenButtonsFound} buttons with green\n`);

    // 4. SEARCH FOR GREEN CLASSES
    console.log('=== 4. GREEN COLOR CLASS SEARCH ===');
    const html = await page.content();
    const greenClasses = [
      'text-green-600', 'text-green-500', 'text-green-400',
      'bg-green-600', 'bg-green-500', 'bg-green-50', 'bg-green-900',
      'border-green-600', 'border-green-500'
    ];

    const foundClasses = [];
    for (const className of greenClasses) {
      if (html.includes(className)) {
        foundClasses.push(className);
      }
    }

    if (foundClasses.length > 0) {
      console.log('❌ Green color classes found in DOM:');
      foundClasses.forEach(c => console.log(`  - ${c}`));
    } else {
      console.log('✓ No green color classes found in DOM');
    }
    console.log('');

    // 5. METRIC CARDS INSPECTION
    console.log('=== 5. METRIC CARDS INSPECTION ===');
    const metricCards = await page.locator('[data-testid="metric-card"]').all();
    console.log(`Found ${metricCards.length} metric cards\n`);

    for (let i = 0; i < metricCards.length; i++) {
      const card = metricCards[i];
      const text = await card.textContent();
      const lines = text?.split('\n').filter(l => l.trim());
      const title = lines?.[0]?.trim() || `Card ${i + 1}`;

      console.log(`Metric Card: ${title}`);

      // Check icon background
      const iconBg = card.locator('div[class*="bg-"]').first();
      const bgClasses = await iconBg.getAttribute('class').catch(() => '');
      const bgColor = await iconBg.evaluate(el => window.getComputedStyle(el).backgroundColor).catch(() => '');

      console.log(`  Background classes: ${bgClasses}`);
      console.log(`  Background color: ${bgColor}`);

      if (bgClasses.includes('bg-green')) {
        console.log('  ⚠️  Green background - should this be indigo?');
      } else if (bgClasses.includes('bg-primary') || bgClasses.includes('bg-indigo')) {
        console.log('  ✓ Using primary/indigo color');
      }

      // Check icons
      const icons = await card.locator('[class*="text-green"]').all();
      if (icons.length > 0) {
        console.log(`  ❌ Found ${icons.length} green icon(s)`);
      }

      console.log('');
    }

    // 6. TOP COLORS ANALYSIS
    console.log('=== 6. TOP COLORS USED ON PAGE ===');
    const colorMap = await page.evaluate(() => {
      const colors = new Map();
      const allElements = document.querySelectorAll('*');

      allElements.forEach(el => {
        const styles = window.getComputedStyle(el);
        [styles.backgroundColor, styles.color, styles.borderColor].forEach(c => {
          if (c && c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent') {
            colors.set(c, (colors.get(c) || 0) + 1);
          }
        });
      });

      return Array.from(colors.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15)
        .map(([color, count]) => ({ color, count }));
    });

    colorMap.forEach(({ color, count }, i) => {
      let flag = '';
      if (color.includes('34, 197, 94') || color.includes('22, 163, 74')) {
        flag = ' ❌ GREEN';
      } else if (color.includes('79, 70, 229') || color.includes('99, 102, 241')) {
        flag = ' ✓ INDIGO';
      }
      console.log(`${i + 1}. ${color} (${count} uses)${flag}`);
    });
    console.log('');

    // 7. INTERACTIVE ELEMENTS TEST
    console.log('=== 7. INTERACTIVE ELEMENTS TEST ===');

    const filterBtn = page.locator('button:has-text("Filters")');
    const filterCount = await filterBtn.count();
    console.log(`Filter button: ${filterCount > 0 ? '✓ Found' : '❌ Not found'}`);

    const exportBtn = page.locator('button:has-text("Export")');
    const exportCount = await exportBtn.count();
    console.log(`Export button: ${exportCount > 0 ? '✓ Found' : '❌ Not found'}`);

    const viewButtons = page.locator('button:has-text("View")');
    const viewCount = await viewButtons.count();
    console.log(`View buttons in table: ${viewCount > 0 ? `✓ Found ${viewCount}` : '❌ Not found'}`);
    console.log('');

    // 8. RESPONSIVE TEST
    console.log('=== 8. RESPONSIVE BEHAVIOR ===');
    const breakpoints = [
      { name: 'Mobile', width: 375, height: 667 },
      { name: 'Tablet', width: 768, height: 1024 },
      { name: 'Desktop', width: 1280, height: 720 }
    ];

    for (const bp of breakpoints) {
      await page.setViewportSize({ width: bp.width, height: bp.height });
      await page.waitForTimeout(300);

      const hasHScroll = await page.evaluate(() => {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
      });

      console.log(`${bp.name} (${bp.width}px): ${hasHScroll ? '❌ Horizontal scroll detected' : '✓ No horizontal scroll'}`);

      await page.screenshot({ path: `/tmp/responsive-${bp.width}px.png`, fullPage: false });
    }
    console.log('');

    // 9. ACCESSIBILITY CHECK
    console.log('=== 9. ACCESSIBILITY - FOCUS INDICATORS ===');
    await page.setViewportSize({ width: 1280, height: 720 });
    const allButtons = await page.locator('button:visible').all();

    let noFocusIndicator = 0;
    for (let i = 0; i < Math.min(allButtons.length, 5); i++) {
      await allButtons[i].focus();
      const outline = await allButtons[i].evaluate(el => window.getComputedStyle(el).outline);
      const boxShadow = await allButtons[i].evaluate(el => window.getComputedStyle(el).boxShadow);

      if (outline === 'none' && boxShadow === 'none') {
        noFocusIndicator++;
      }
    }

    if (noFocusIndicator > 0) {
      console.log(`⚠️  ${noFocusIndicator} buttons have no visible focus indicator`);
    } else {
      console.log('✓ All tested buttons have focus indicators');
    }
    console.log('');

    // FINAL SUMMARY
    console.log('=== FINAL SUMMARY ===');
    const issues = [];
    if (errors.length > 0) issues.push(`${errors.length} console error(s)`);
    if (warnings.length > 0) issues.push(`${warnings.length} console warning(s)`);
    if (greenButtonsFound > 0) issues.push(`${greenButtonsFound} button(s) with green colors`);
    if (foundClasses.length > 0) issues.push(`${foundClasses.length} green color class(es) in DOM`);
    if (noFocusIndicator > 0) issues.push(`${noFocusIndicator} button(s) without focus indicators`);

    if (issues.length === 0) {
      console.log('✅ NO ISSUES FOUND - Page is ready!');
    } else {
      console.log('❌ ISSUES FOUND:');
      issues.forEach((issue, i) => console.log(`  ${i + 1}. ${issue}`));
    }

    console.log('\n=== QA REPORT COMPLETE ===');

  } catch (error) {
    console.error('Error during QA:', error);
  } finally {
    await browser.close();
  }
}

runQA();
