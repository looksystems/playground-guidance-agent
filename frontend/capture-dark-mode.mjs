import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SCREENSHOT_DIR = path.join(__dirname, 'screenshots', 'dark-mode-review');

// Ensure screenshot directory exists
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

const pages = [
  { url: '/', name: '01-customer-home', title: 'Home - Profile Form' },
  { url: '/history', name: '02-customer-history', title: 'History - Consultation List' },
  { url: '/admin', name: '03-admin-dashboard', title: 'Admin Dashboard' },
  { url: '/admin/metrics', name: '04-admin-metrics', title: 'Admin Metrics' },
  { url: '/admin/settings', name: '05-admin-settings', title: 'Admin Settings' },
  { url: '/admin/consultations', name: '06-admin-consultations', title: 'Admin Consultations List' },
  { url: '/admin/knowledge/fca', name: '07-admin-fca-knowledge', title: 'FCA Knowledge List' },
  { url: '/admin/knowledge/pension', name: '08-admin-pension-knowledge', title: 'Pension Knowledge List' },
  { url: '/admin/learning/rules', name: '09-admin-learning-rules', title: 'Learning Rules List' },
  { url: '/admin/users/customers', name: '10-admin-customers', title: 'Customers List' },
];

async function captureScreenshots() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });
  const page = await context.newPage();

  console.log('Starting dark mode review...\n');

  const errors = [];
  const warnings = [];

  // Collect console messages
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      errors.push(`${msg.text()}`);
    } else if (msg.type() === 'warning') {
      warnings.push(`${msg.text()}`);
    }
  });

  for (const pageInfo of pages) {
    console.log(`📸 Capturing: ${pageInfo.title}`);

    try {
      await page.goto(`http://localhost:3000${pageInfo.url}`, { waitUntil: 'networkidle' });
      await page.waitForTimeout(1000); // Wait for any transitions

      // Check if dark mode toggle exists
      const toggleExists = await page.locator('button[aria-label*="mode"]').count() > 0;
      console.log(`   Toggle button found: ${toggleExists}`);

      // Capture LIGHT mode
      const htmlClasses = await page.locator('html').getAttribute('class') || '';
      const currentlyDark = htmlClasses.includes('dark');
      console.log(`   Currently in ${currentlyDark ? 'DARK' : 'LIGHT'} mode`);

      if (currentlyDark) {
        // Switch to light mode first
        if (toggleExists) {
          await page.locator('button[aria-label*="mode"]').first().click();
          await page.waitForTimeout(500);
        }
      }

      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${pageInfo.name}-light.png`),
        fullPage: true
      });
      console.log(`   ✓ Light mode captured`);

      // Capture DARK mode
      if (toggleExists) {
        await page.locator('button[aria-label*="mode"]').first().click();
        await page.waitForTimeout(500);

        const htmlClassesAfter = await page.locator('html').getAttribute('class') || '';
        const nowDark = htmlClassesAfter.includes('dark');
        console.log(`   After toggle: ${nowDark ? 'DARK' : 'LIGHT'} mode`);

        await page.screenshot({
          path: path.join(SCREENSHOT_DIR, `${pageInfo.name}-dark.png`),
          fullPage: true
        });
        console.log(`   ✓ Dark mode captured`);
      } else {
        console.log(`   ⚠️  No dark mode toggle found - skipping dark mode capture`);
      }

      console.log('');
    } catch (error) {
      console.error(`   ❌ Error capturing ${pageInfo.title}:`, error.message);
      console.log('');
    }
  }

  console.log('\n📊 Console Analysis:');
  console.log(`   Errors: ${errors.length}`);
  console.log(`   Warnings: ${warnings.length}`);

  if (errors.length > 0) {
    console.log('\n🔴 Console Errors:');
    const uniqueErrors = [...new Set(errors)];
    uniqueErrors.slice(0, 10).forEach((err, i) => {
      console.log(`   ${i + 1}. ${err.substring(0, 150)}`);
    });
  }

  if (warnings.length > 0) {
    console.log('\n⚠️  Console Warnings (unique):');
    const uniqueWarnings = [...new Set(warnings)];
    uniqueWarnings.slice(0, 10).forEach((warn, i) => {
      console.log(`   ${i + 1}. ${warn.substring(0, 150)}`);
    });
  }

  await browser.close();
  console.log('\n✅ Screenshot capture complete!');
}

captureScreenshots().catch(console.error);
