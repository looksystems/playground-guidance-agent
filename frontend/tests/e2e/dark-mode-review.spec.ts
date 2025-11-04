import { test, expect, Page } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SCREENSHOT_DIR = path.join(__dirname, '..', '..', 'screenshots', 'dark-mode-review');

// Helper function to toggle dark mode
async function toggleDarkMode(page: Page) {
  // Find and click the dark mode toggle button
  const toggleButton = page.locator('button[aria-label*="mode"]').first();
  await toggleButton.click();
  // Wait for transition to complete
  await page.waitForTimeout(500);
}

// Helper function to check if dark mode is active
async function isDarkModeActive(page: Page): Promise<boolean> {
  const html = page.locator('html');
  const classes = await html.getAttribute('class');
  return classes?.includes('dark') || false;
}

// Helper function to set dark mode
async function setDarkMode(page: Page, dark: boolean) {
  const isDark = await isDarkModeActive(page);
  if (isDark !== dark) {
    await toggleDarkMode(page);
  }
}

// Helper to take screenshot for both modes
async function captureInBothModes(page: Page, name: string) {
  // Light mode
  await setDarkMode(page, false);
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, `${name}-light.png`),
    fullPage: true
  });

  // Dark mode
  await setDarkMode(page, true);
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, `${name}-dark.png`),
    fullPage: true
  });
}

test.describe('Dark Mode Review - Customer Pages', () => {
  test('Home page - Profile form', async ({ page }) => {
    await page.goto('http://localhost:3000/');
    await page.waitForLoadState('networkidle');

    // Verify page loads
    await expect(page.locator('h1, h2').first()).toBeVisible();

    // Take screenshots in both modes
    await captureInBothModes(page, '01-customer-home');

    // Test dark mode toggle functionality
    const initialMode = await isDarkModeActive(page);
    await toggleDarkMode(page);
    const afterToggle = await isDarkModeActive(page);
    expect(initialMode).not.toBe(afterToggle);
  });

  test('History page - Consultation list', async ({ page }) => {
    await page.goto('http://localhost:3000/history');
    await page.waitForLoadState('networkidle');

    await captureInBothModes(page, '02-customer-history');
  });
});

test.describe('Dark Mode Review - Admin Dashboard', () => {
  test('Admin Dashboard - Overview', async ({ page }) => {
    await page.goto('http://localhost:3000/admin');
    await page.waitForLoadState('networkidle');

    await captureInBothModes(page, '03-admin-dashboard');

    // Verify sidebar is visible
    await expect(page.locator('aside')).toBeVisible();
  });

  test('Admin Metrics', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/metrics');
    await page.waitForLoadState('networkidle');

    await captureInBothModes(page, '04-admin-metrics');
  });

  test('Admin Settings', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/settings');
    await page.waitForLoadState('networkidle');

    await captureInBothModes(page, '05-admin-settings');
  });
});

test.describe('Dark Mode Review - Admin Consultations', () => {
  test('Consultations List', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/consultations');
    await page.waitForLoadState('networkidle');

    await captureInBothModes(page, '06-admin-consultations-list');
  });
});

test.describe('Dark Mode Review - Admin Knowledge Base', () => {
  test('FCA Knowledge List', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/knowledge/fca');
    await page.waitForLoadState('networkidle');

    await captureInBothModes(page, '07-admin-knowledge-fca-list');
  });

  test('Pension Knowledge List', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/knowledge/pension');
    await page.waitForLoadState('networkidle');

    await captureInBothModes(page, '08-admin-knowledge-pension-list');
  });
});

test.describe('Dark Mode Review - Admin Learning System', () => {
  test('Learning Rules List', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/learning/rules');
    await page.waitForLoadState('networkidle');

    await captureInBothModes(page, '09-admin-learning-rules-list');
  });
});

test.describe('Dark Mode Review - Admin Users', () => {
  test('Customers List', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/users/customers');
    await page.waitForLoadState('networkidle');

    await captureInBothModes(page, '10-admin-users-customers-list');
  });
});

test.describe('Console Errors Check', () => {
  test('Check for console errors on all pages', async ({ page }) => {
    const errors: string[] = [];
    const warnings: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(`[${msg.location().url}] ${msg.text()}`);
      } else if (msg.type() === 'warning') {
        warnings.push(`[${msg.location().url}] ${msg.text()}`);
      }
    });

    const pages = [
      'http://localhost:3000/',
      'http://localhost:3000/history',
      'http://localhost:3000/admin',
      'http://localhost:3000/admin/metrics',
      'http://localhost:3000/admin/settings',
      'http://localhost:3000/admin/consultations',
      'http://localhost:3000/admin/knowledge/fca',
      'http://localhost:3000/admin/knowledge/pension',
      'http://localhost:3000/admin/learning/rules',
      'http://localhost:3000/admin/users/customers',
    ];

    for (const url of pages) {
      await page.goto(url);
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);
    }

    console.log('Console Errors:', errors.length);
    console.log('Console Warnings:', warnings.length);

    if (errors.length > 0) {
      console.log('Errors:', errors);
    }
    if (warnings.length > 0) {
      console.log('Warnings:', warnings);
    }

    expect(errors.length, `Found ${errors.length} console errors`).toBe(0);
    expect(warnings.length, `Found ${warnings.length} console warnings`).toBe(0);
  });
});
