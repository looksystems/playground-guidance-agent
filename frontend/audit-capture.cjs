const { chromium } = require('playwright');

const pages = [
  ['01-home-chat', '/', 'Home/Chat Interface'],
  ['02-history', '/history', 'Consultation History'],
  ['03-admin-dashboard', '/admin', 'Admin Dashboard'],
  ['04-fca-knowledge', '/admin/fca-knowledge', 'FCA Knowledge'],
  ['05-pension-knowledge', '/admin/pension-knowledge', 'Pension Knowledge'],
  ['06-memories', '/admin/memories', 'Memories'],
  ['07-cases', '/admin/cases', 'Cases'],
  ['08-rules', '/admin/rules', 'Rules'],
  ['09-customers', '/admin/customers', 'Customers'],
  ['10-consultations', '/admin/consultations', 'Consultations'],
  ['11-settings', '/admin/settings', 'System Settings'],
];

(async () => {
  console.log('\n' + '='.repeat(80));
  console.log('COMPREHENSIVE COLOR AUDIT - Screenshot Capture');
  console.log('='.repeat(80));

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });

  for (let i = 0; i < pages.length; i++) {
    const [filename, url, title] = pages[i];
    console.log(`\n[${i + 1}/11] ${title}`);
    console.log(`  URL: ${url}`);

    try {
      const fullUrl = `http://localhost:3000${url}`;
      await page.goto(fullUrl, { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(1000);

      const screenshotPath = `/tmp/audit-${filename}.png`;
      await page.screenshot({ path: screenshotPath, fullPage: true });
      console.log(`  ✓ Screenshot saved: ${screenshotPath}`);
    } catch (e) {
      console.log(`  ✗ Error: ${e.message}`);
    }
  }

  await browser.close();

  console.log('\n' + '='.repeat(80));
  console.log('SCREENSHOT CAPTURE COMPLETE');
  console.log('='.repeat(80));
})();
