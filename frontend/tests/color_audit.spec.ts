import { test, expect } from '@playwright/test';
import { chromium } from '@playwright/test';

test.describe('Comprehensive Color Audit - Green vs Indigo', () => {
  test('audit all pages for color usage', async ({ page }) => {
    // Set viewport for consistent screenshots
    await page.setViewportSize({ width: 1920, height: 1080 });

    // 1. Home/Chat Interface
    console.log('\n=== 1. HOME/CHAT INTERFACE (/) ===');
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: '/tmp/audit-01-home-chat.png', fullPage: true });
    console.log('✓ Screenshot saved: audit-01-home-chat.png');

    // 2. Consultation History
    console.log('\n=== 2. CONSULTATION HISTORY (/history) ===');
    await page.goto('http://localhost:3000/history');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: '/tmp/audit-02-history.png', fullPage: true });
    console.log('✓ Screenshot saved: audit-02-history.png');

    // 3. Admin Dashboard
    console.log('\n=== 3. ADMIN DASHBOARD (/admin) ===');
    await page.goto('http://localhost:3000/admin');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: '/tmp/audit-03-admin-dashboard.png', fullPage: true });
    console.log('✓ Screenshot saved: audit-03-admin-dashboard.png');

    // 4. FCA Knowledge
    console.log('\n=== 4. FCA KNOWLEDGE (/admin/fca-knowledge) ===');
    await page.goto('http://localhost:3000/admin/fca-knowledge');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: '/tmp/audit-04-fca-knowledge.png', fullPage: true });
    console.log('✓ Screenshot saved: audit-04-fca-knowledge.png');

    // 5. Pension Knowledge
    console.log('\n=== 5. PENSION KNOWLEDGE (/admin/pension-knowledge) ===');
    await page.goto('http://localhost:3000/admin/pension-knowledge');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: '/tmp/audit-05-pension-knowledge.png', fullPage: true });
    console.log('✓ Screenshot saved: audit-05-pension-knowledge.png');

    // 6. Memories
    console.log('\n=== 6. MEMORIES (/admin/memories) ===');
    await page.goto('http://localhost:3000/admin/memories');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: '/tmp/audit-06-memories.png', fullPage: true });
    console.log('✓ Screenshot saved: audit-06-memories.png');

    // 7. Cases
    console.log('\n=== 7. CASES (/admin/cases) ===');
    await page.goto('http://localhost:3000/admin/cases');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: '/tmp/audit-07-cases.png', fullPage: true });
    console.log('✓ Screenshot saved: audit-07-cases.png');

    // 8. Rules
    console.log('\n=== 8. RULES (/admin/rules) ===');
    await page.goto('http://localhost:3000/admin/rules');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: '/tmp/audit-08-rules.png', fullPage: true });
    console.log('✓ Screenshot saved: audit-08-rules.png');

    // 9. Customers
    console.log('\n=== 9. CUSTOMERS (/admin/customers) ===');
    await page.goto('http://localhost:3000/admin/customers');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: '/tmp/audit-09-customers.png', fullPage: true });
    console.log('✓ Screenshot saved: audit-09-customers.png');

    // 10. Consultations
    console.log('\n=== 10. CONSULTATIONS (/admin/consultations) ===');
    await page.goto('http://localhost:3000/admin/consultations');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: '/tmp/audit-10-consultations.png', fullPage: true });
    console.log('✓ Screenshot saved: audit-10-consultations.png');

    // 11. System Settings
    console.log('\n=== 11. SYSTEM SETTINGS (/admin/settings) ===');
    await page.goto('http://localhost:3000/admin/settings');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: '/tmp/audit-11-settings.png', fullPage: true });
    console.log('✓ Screenshot saved: audit-11-settings.png');

    console.log('\n=== SCREENSHOT CAPTURE COMPLETE ===');
    console.log('All 11 screenshots saved to /tmp/');
  });
});
