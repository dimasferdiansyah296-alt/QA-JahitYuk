// M04 — Kontrol Akses (Role-based)
const { test, expect } = require('../lib/fixtures');
const { login } = require('./helpers');

test.describe('M04 Kontrol Akses', () => {

  test('TC015 Guest dialihkan ke login saat mengakses halaman terlindungi', async ({ page, tc, evidence }) => {
    tc({ module: 'M04', feature: 'F06', featureName: 'AKSES', requirement: 'REQ-15', role: 'PUBLIC',
      type: 'Access Control', priority: 'Critical', objective: 'Halaman internal terlindungi dari guest',
      expected: 'Diarahkan ke halaman login' });
    await page.goto('/pesanan');
    await expect(page).toHaveURL(/\/login/);
    await evidence.snap('Guest dialihkan ke login');
  });

  test('TC016 Pelanggan ditolak mengakses halaman manajemen pesanan admin', async ({ page, tc, evidence }) => {
    tc({ module: 'M04', feature: 'F06', featureName: 'AKSES', requirement: 'REQ-16', role: 'PELANGGAN',
      type: 'Access Control', priority: 'High', objective: 'Pelanggan tidak boleh akses /pesanan',
      expected: 'Mendapat halaman 403 Forbidden' });
    await login(page, 'PELANGGAN');
    await page.goto('/pesanan');
    await expect(page.locator('body')).toContainText(/403|Forbidden|Akses ditolak/);
    await evidence.snap('Pelanggan ditolak akses /pesanan (403)');
  });

  test('TC017 Admin ditolak mengakses dashboard pelanggan', async ({ page, tc, evidence }) => {
    tc({ module: 'M04', feature: 'F06', featureName: 'AKSES', requirement: 'REQ-17', role: 'ADMIN',
      type: 'Access Control', priority: 'Medium', objective: 'Admin tidak boleh akses /pelanggan/dashboard',
      expected: 'Mendapat halaman 403 Forbidden' });
    await login(page, 'ADMIN');
    await page.goto('/pelanggan/dashboard');
    await expect(page.locator('body')).toContainText(/403|Forbidden|Akses ditolak/);
    await evidence.snap('Admin ditolak akses /pelanggan/dashboard (403)');
  });

  test('TC018 /dashboard mengarahkan ke dashboard sesuai role', async ({ page, tc, evidence }) => {
    tc({ module: 'M04', feature: 'F06', featureName: 'AKSES', requirement: 'REQ-18', role: 'ADMIN',
      type: 'Positive', priority: 'Medium', objective: 'Route /dashboard redirect sesuai role',
      expected: 'Admin diarahkan ke /admin/dashboard' });
    await login(page, 'ADMIN');
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/admin\/dashboard/);
    await evidence.snap('Redirect /dashboard ke admin dashboard');
  });

});
