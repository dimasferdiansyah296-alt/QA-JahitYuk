// M01 — Autentikasi & Halaman Publik
const { test, expect } = require('../lib/fixtures');
const { login } = require('./helpers');

test.describe('M01 Autentikasi & Halaman Publik', () => {

  test('TC001 Pengunjung dapat mengakses halaman beranda', async ({ page, tc, evidence }) => {
    tc({ module: 'M01', feature: 'F01', featureName: 'BERANDA', requirement: 'REQ-01', role: 'PUBLIC',
      type: 'Positive', priority: 'Medium', objective: 'Halaman publik dapat dibuka tanpa login',
      expected: 'Halaman beranda tampil dengan link Log in dan Register' });
    await page.goto('/');
    await expect(page.getByRole('link', { name: 'Log in' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Register' })).toBeVisible();
    await evidence.snap('Halaman beranda untuk pengunjung');
  });

  test('TC002 Form login menampilkan field email dan password', async ({ page, tc, evidence }) => {
    tc({ module: 'M01', feature: 'F02', featureName: 'LOGIN', requirement: 'REQ-01', role: 'PUBLIC',
      type: 'Positive', priority: 'Medium', objective: 'Form login tersedia dengan field yang benar',
      expected: 'Terdapat input email, password, dan tombol Masuk' });
    await page.goto('/login');
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Masuk' })).toBeVisible();
    await evidence.snap('Form login sebelum diisi');
  });

  test('TC003 Login dengan kredensial salah ditolak', async ({ page, tc, evidence }) => {
    tc({ module: 'M01', feature: 'F02', featureName: 'LOGIN', requirement: 'REQ-03', role: 'PUBLIC',
      type: 'Negative', priority: 'High', objective: 'Kredensial salah tidak dapat masuk',
      expected: 'Pesan "Email atau password salah." dan tetap di halaman login' });
    await page.goto('/login');
    await page.fill('input[name="email"]', 'tidakada@example.com');
    await page.fill('input[name="password"]', 'password-salah');
    await page.click('button[type="submit"]');
    await expect(page.locator('.alert-danger')).toContainText('Email atau password salah');
    await expect(page).toHaveURL(/\/login/);
    await evidence.snap('Pesan error kredensial salah');
  });

  test('TC004 Admin login berhasil dan diarahkan ke dashboard admin', async ({ page, tc, evidence }) => {
    tc({ module: 'M01', feature: 'F02', featureName: 'LOGIN', requirement: 'REQ-02', role: 'ADMIN',
      type: 'Positive', priority: 'Critical', objective: 'Admin dapat masuk ke sistem',
      expected: 'Diarahkan ke /admin/dashboard' });
    await login(page, 'ADMIN');
    await expect(page).toHaveURL(/\/admin\/dashboard/);
    await expect(page.getByText('Dashboard Admin')).toBeVisible();
    await evidence.snap('Dashboard admin setelah login');
  });

  test('TC005 Pelanggan login berhasil dan diarahkan ke dashboard pelanggan', async ({ page, tc, evidence }) => {
    tc({ module: 'M01', feature: 'F02', featureName: 'LOGIN', requirement: 'REQ-02', role: 'PELANGGAN',
      type: 'Positive', priority: 'Critical', objective: 'Pelanggan dapat masuk ke sistem',
      expected: 'Diarahkan ke /pelanggan/dashboard' });
    await login(page, 'PELANGGAN');
    await expect(page).toHaveURL(/\/pelanggan\/dashboard/);
    await expect(page.getByText(/Dashboard/)).toBeVisible();
    await evidence.snap('Dashboard pelanggan setelah login');
  });

  test('TC006 Registrasi dengan password kurang dari 8 karakter ditolak', async ({ page, tc, evidence }) => {
    tc({ module: 'M01', feature: 'F03', featureName: 'REGISTER', requirement: 'REQ-05', role: 'PUBLIC',
      type: 'Negative', priority: 'High', objective: 'Validasi panjang password minimal 8 karakter',
      expected: 'Pesan error bahwa password minimal 8 karakter' });
    await page.goto('/register');
    await page.fill('input[name="nama"]', 'Test User QA');
    await page.fill('input[name="email"]', 'testqauser@example.com');
    await page.fill('input[name="no_telepon"]', '081234567890');
    await page.fill('input[name="alamat"]', 'Jl. Test No. 1');
    await page.fill('input[name="password"]', '123');
    await page.fill('input[name="password_confirmation"]', '123');
    await page.click('button[type="submit"]');
    await expect(page.locator('.alert-danger, .invalid-feedback')).toContainText(/at least 8 characters|minimal 8/);
    await evidence.snap('Error validasi password pendek');
  });

});
