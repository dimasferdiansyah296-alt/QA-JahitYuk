// Helper login untuk aplikasi JAHITYUK.
const { credentials, BASE_URL } = require('../lib/env');

/**
 * Login ke JAHITYUK sebagai role tertentu.
 * @param {import('@playwright/test').Page} page
 * @param {'ADMIN'|'KARYAWAN'|'PELANGGAN'} role
 */
async function login(page, role) {
  const { user, pass } = credentials(role);
  await page.goto('/login');
  await page.fill('input[name="email"]', user);
  await page.fill('input[name="password"]', pass);
  await page.click('button[type="submit"]');
  await page.waitForLoadState('networkidle').catch(() => {});
}

module.exports = { login };
