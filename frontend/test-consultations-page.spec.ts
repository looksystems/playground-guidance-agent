import { test, expect } from '@playwright/test';

test.describe('Admin Consultations Page QA - Indigo Color Scheme', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to admin dashboard
    await page.goto('http://localhost:3000/admin');
    await page.waitForLoadState('networkidle');
    // Wait for data to load
    await page.waitForSelector('table tbody tr', { timeout: 10000 }).catch(() => {});
  });

  test('Take full page screenshot', async ({ page }) => {
    await page.screenshot({
      path: '/tmp/admin-consultations-full.png',
      fullPage: true
    });
  });

  test('Check console for errors and warnings', async ({ page }) => {
    const errors: string[] = [];
    const warnings: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      } else if (msg.type() === 'warning') {
        warnings.push(msg.text());
      }
    });

    // Wait a bit to collect console messages
    await page.waitForTimeout(3000);

    console.log('=== CONSOLE ERRORS ===');
    console.log(errors.length > 0 ? errors.join('\n') : 'No errors found');
    console.log('\n=== CONSOLE WARNINGS ===');
    console.log(warnings.length > 0 ? warnings.join('\n') : 'No warnings found');
  });

  test('Inspect all buttons for indigo color scheme', async ({ page }) => {
    const buttons = await page.locator('button').all();
    console.log(`\n=== BUTTON INSPECTION (${buttons.length} buttons found) ===`);

    for (let i = 0; i < buttons.length; i++) {
      const button = buttons[i];
      const text = await button.textContent();
      const classes = await button.getAttribute('class');
      const bgColor = await button.evaluate(el => window.getComputedStyle(el).backgroundColor);
      const borderColor = await button.evaluate(el => window.getComputedStyle(el).borderColor);
      const color = await button.evaluate(el => window.getComputedStyle(el).color);

      console.log(`\nButton ${i + 1}: "${text?.trim() || 'No text'}"`);
      console.log(`  Classes: ${classes}`);
      console.log(`  Background: ${bgColor}`);
      console.log(`  Border: ${borderColor}`);
      console.log(`  Text Color: ${color}`);

      // Check for green colors (should be changed to indigo)
      if (bgColor.includes('34, 197, 94') || // green-500
          bgColor.includes('22, 163, 74') || // green-600
          borderColor.includes('34, 197, 94') ||
          borderColor.includes('22, 163, 74')) {
        console.log('  ⚠️  WARNING: Green color detected - should be indigo!');
      }

      // Check for indigo colors (expected)
      if (bgColor.includes('79, 70, 229') || // indigo-600
          bgColor.includes('99, 102, 241') || // indigo-500
          borderColor.includes('79, 70, 229') ||
          borderColor.includes('99, 102, 241')) {
        console.log('  ✓ Indigo color scheme detected');
      }
    }
  });

  test('Inspect badges and icons for color scheme', async ({ page }) => {
    // Check compliance badges
    const badges = await page.locator('[class*="badge"]').all();
    console.log(`\n=== BADGE INSPECTION (${badges.length} badges found) ===`);

    for (let i = 0; i < badges.length; i++) {
      const badge = badges[i];
      const text = await badge.textContent();
      const classes = await badge.getAttribute('class');
      const bgColor = await badge.evaluate(el => window.getComputedStyle(el).backgroundColor);

      console.log(`\nBadge ${i + 1}: "${text?.trim()}"`);
      console.log(`  Classes: ${classes}`);
      console.log(`  Background: ${bgColor}`);
    }

    // Check icons
    const icons = await page.locator('[class*="i-heroicons"]').all();
    console.log(`\n=== ICON INSPECTION (${icons.length} icons found) ===`);

    for (let i = 0; i < icons.length; i++) {
      const icon = icons[i];
      const classes = await icon.getAttribute('class');
      const color = await icon.evaluate(el => window.getComputedStyle(el).color);

      console.log(`\nIcon ${i + 1}:`);
      console.log(`  Classes: ${classes}`);
      console.log(`  Color: ${color}`);

      if (color.includes('34, 197, 94') || color.includes('22, 163, 74')) {
        console.log('  ⚠️  WARNING: Green color detected - should be reviewed!');
      }
    }
  });

  test('Search DOM for green color classes', async ({ page }) => {
    const html = await page.content();

    console.log('\n=== SEARCHING FOR GREEN COLOR CLASSES ===');

    const greenClasses = [
      'text-green-600', 'text-green-500', 'text-green-400',
      'bg-green-600', 'bg-green-500', 'bg-green-50', 'bg-green-900',
      'border-green-600', 'border-green-500',
      'ring-green-600', 'ring-green-500',
      'from-green-', 'to-green-'
    ];

    const found: string[] = [];
    for (const className of greenClasses) {
      if (html.includes(className)) {
        // Extract the lines containing this class
        const lines = html.split('\n').filter(line => line.includes(className));
        found.push(`\n${className}:`);
        lines.forEach(line => {
          // Trim and show first 150 chars
          const trimmed = line.trim().substring(0, 150);
          found.push(`  ${trimmed}...`);
        });
      }
    }

    if (found.length > 0) {
      console.log('⚠️  Green color classes found:');
      console.log(found.join('\n'));
    } else {
      console.log('✓ No green color classes found in DOM');
    }
  });

  test('Test all interactive elements', async ({ page }) => {
    console.log('\n=== TESTING INTERACTIVE ELEMENTS ===');

    // Test Filter button
    const filterBtn = page.locator('button:has-text("Filters")');
    if (await filterBtn.count() > 0) {
      console.log('✓ Filter button found');
      await filterBtn.screenshot({ path: '/tmp/filter-button.png' });
    }

    // Test Export button
    const exportBtn = page.locator('button:has-text("Export")');
    if (await exportBtn.count() > 0) {
      console.log('✓ Export button found');
      await exportBtn.screenshot({ path: '/tmp/export-button.png' });
    }

    // Test View buttons in table
    const viewButtons = page.locator('button:has-text("View")');
    const viewBtnCount = await viewButtons.count();
    console.log(`✓ Found ${viewBtnCount} View buttons in table`);

    if (viewBtnCount > 0) {
      await viewButtons.first().screenshot({ path: '/tmp/view-button.png' });
    }
  });

  test('Test keyboard navigation', async ({ page }) => {
    console.log('\n=== TESTING KEYBOARD NAVIGATION ===');

    // Tab through all focusable elements
    const focusableElements = await page.locator('a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])').all();
    console.log(`Found ${focusableElements.length} focusable elements`);

    // Test Tab key navigation
    await page.keyboard.press('Tab');
    let focusedElement = await page.evaluate(() => {
      const el = document.activeElement;
      return {
        tag: el?.tagName,
        text: el?.textContent?.substring(0, 30),
        classes: el?.className
      };
    });
    console.log('First Tab focus:', focusedElement);

    // Take screenshot of first focus
    await page.screenshot({ path: '/tmp/keyboard-nav-first-focus.png' });
  });

  test('Check accessibility - focus indicators', async ({ page }) => {
    console.log('\n=== CHECKING FOCUS INDICATORS ===');

    const buttons = await page.locator('button').all();

    for (let i = 0; i < Math.min(buttons.length, 5); i++) {
      await buttons[i].focus();
      const outline = await buttons[i].evaluate(el => window.getComputedStyle(el).outline);
      const boxShadow = await buttons[i].evaluate(el => window.getComputedStyle(el).boxShadow);
      const text = await buttons[i].textContent();

      console.log(`\nButton "${text?.trim()}"`);
      console.log(`  Outline: ${outline}`);
      console.log(`  Box Shadow: ${boxShadow}`);

      if (outline === 'none' && boxShadow === 'none') {
        console.log('  ⚠️  WARNING: No visible focus indicator!');
      }
    }
  });

  test('Test responsive behavior', async ({ page }) => {
    console.log('\n=== TESTING RESPONSIVE BEHAVIOR ===');

    const breakpoints = [
      { name: 'Mobile (375px)', width: 375, height: 667 },
      { name: 'Tablet (768px)', width: 768, height: 1024 },
      { name: 'Desktop (1280px)', width: 1280, height: 720 },
      { name: 'Large Desktop (1920px)', width: 1920, height: 1080 }
    ];

    for (const bp of breakpoints) {
      await page.setViewportSize({ width: bp.width, height: bp.height });
      await page.waitForTimeout(500);

      console.log(`\n${bp.name}:`);

      // Check for horizontal scroll
      const hasHorizontalScroll = await page.evaluate(() => {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
      });

      if (hasHorizontalScroll) {
        console.log('  ⚠️  WARNING: Horizontal scroll detected!');
      } else {
        console.log('  ✓ No horizontal scroll');
      }

      // Take screenshot
      await page.screenshot({
        path: `/tmp/responsive-${bp.width}px.png`,
        fullPage: true
      });
    }
  });

  test('Check metric cards for color consistency', async ({ page }) => {
    console.log('\n=== CHECKING METRIC CARDS ===');

    const metricCards = await page.locator('[data-testid="metric-card"]').all();
    console.log(`Found ${metricCards.length} metric cards`);

    for (let i = 0; i < metricCards.length; i++) {
      const card = metricCards[i];
      const text = await card.textContent();
      const title = text?.split('\n')[1]?.trim() || 'Unknown';

      console.log(`\nMetric Card ${i + 1}: ${title}`);

      // Check icon background colors
      const iconBg = card.locator('div[class*="bg-"]');
      const bgClasses = await iconBg.getAttribute('class');
      const bgColor = await iconBg.evaluate(el => window.getComputedStyle(el).backgroundColor);

      console.log(`  Icon Background Classes: ${bgClasses}`);
      console.log(`  Icon Background Color: ${bgColor}`);

      if (bgClasses?.includes('bg-green')) {
        console.log('  ⚠️  WARNING: Green background found - should it be indigo?');
      }
    }
  });

  test('Extract all computed colors from page', async ({ page }) => {
    console.log('\n=== EXTRACTING ALL COLORS FROM PAGE ===');

    const colorMap = await page.evaluate(() => {
      const colors = new Map<string, number>();
      const allElements = document.querySelectorAll('*');

      allElements.forEach(el => {
        const styles = window.getComputedStyle(el);
        const bg = styles.backgroundColor;
        const color = styles.color;
        const border = styles.borderColor;

        [bg, color, border].forEach(c => {
          if (c && c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent') {
            colors.set(c, (colors.get(c) || 0) + 1);
          }
        });
      });

      // Convert to array and sort by frequency
      return Array.from(colors.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 20) // Top 20 colors
        .map(([color, count]) => ({ color, count }));
    });

    console.log('\nTop 20 colors used on page:');
    colorMap.forEach(({ color, count }, i) => {
      console.log(`${i + 1}. ${color} (used ${count} times)`);

      // Flag green colors
      if (color.includes('34, 197, 94') || color.includes('22, 163, 74') || color.includes('16, 185, 129')) {
        console.log('   ⚠️  GREEN COLOR DETECTED');
      }

      // Flag indigo colors
      if (color.includes('79, 70, 229') || color.includes('99, 102, 241') || color.includes('67, 56, 202')) {
        console.log('   ✓ INDIGO COLOR (expected)');
      }
    });
  });
});
