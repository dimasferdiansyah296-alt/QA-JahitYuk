// M03 — Manajemen Pesanan (Sisi Admin/Karyawan)
const { test, expect } = require('../lib/fixtures');
const { login } = require('./helpers');

test.describe('M03 Manajemen Pesanan (Admin/Karyawan)', () => {

  test('TC011 Admin dapat melihat daftar semua pesanan', async ({ page, tc, evidence }) => {
    tc({ module: 'M03', feature: 'F05', featureName: 'ADMIN_PESANAN_LIST', requirement: 'REQ-11', role: 'ADMIN',
      type: 'Positive', priority: 'High', objective: 'Admin melihat seluruh pesanan',
      expected: 'Halaman manajemen pesanan tampil dengan tabel pesanan' });
    await login(page, 'ADMIN');
    await page.goto('/pesanan');
    await expect(page).toHaveURL(/\/pesanan/);
    await expect(page.getByText('Manajemen Pesanan')).toBeVisible();
    await evidence.snap('Daftar semua pesanan (admin)');
  });

  test('TC012 Admin dapat memfilter pesanan berdasarkan status', async ({ page, tc, evidence }) => {
    tc({ module: 'M03', feature: 'F05', featureName: 'ADMIN_PESANAN_FILTER', requirement: 'REQ-12', role: 'ADMIN',
      type: 'Positive', priority: 'Medium', objective: 'Filter pesanan berdasarkan status',
      expected: 'Tabel menampilkan pesanan sesuai status yang dipilih' });
    await login(page, 'ADMIN');
    await page.goto('/pesanan');
    await page.selectOption('select[name="status"]', 'baru');
    await page.getByRole('button', { name: 'Filter' }).click();
    await expect(page).toHaveURL(/status=baru/);
    await evidence.snap('Hasil filter status "baru"');
  });

  test('TC013 Admin dapat mengubah status pesanan', async ({ page, tc, evidence }) => {
    tc({ module: 'M03', feature: 'F05', featureName: 'ADMIN_PESANAN_UPDATE', requirement: 'REQ-13', role: 'ADMIN',
      type: 'Positive', priority: 'High', objective: 'Admin mengubah status pesanan',
      expected: 'Status pesanan berubah dan diarahkan ke detail dengan pesan sukses' });
    await login(page, 'ADMIN');
    await page.goto('/pesanan');
    // Buka edit pesanan pertama
    const editLink = page.locator('a[href*="/pesanan/"][href$="/edit"]').first();
    const editHref = await editLink.getAttribute('href');
    if (editHref) {
      await page.goto(editHref);
      await page.selectOption('select[name="status"]', 'diproses');
      await evidence.snap('Form edit status sebelum simpan');
      await page.getByRole('button', { name: 'Simpan Perubahan' }).click();
      await expect(page.locator('.alert-success')).toContainText('berhasil diperbarui');
      await evidence.snap('Status pesanan berhasil diubah');
    } else {
      test.skip(true, 'BLOCKED: tidak ada pesanan untuk diedit');
    }
  });

  test('TC014 Dashboard admin menampilkan statistik', async ({ page, tc, evidence }) => {
    tc({ module: 'M03', feature: 'F05', featureName: 'ADMIN_DASHBOARD', requirement: 'REQ-19', role: 'ADMIN',
      type: 'Positive', priority: 'Medium', objective: 'Dashboard admin menampilkan statistik',
      expected: 'Terdapat kartu statistik: Pelanggan, Pesanan, Karyawan, Pendapatan' });
    await login(page, 'ADMIN');
    await page.goto('/admin/dashboard');
    await expect(page.getByText('Pelanggan')).toBeVisible();
    await expect(page.locator('.card-title', { hasText: 'Pesanan' })).toBeVisible();
    await expect(page.getByText('Karyawan')).toBeVisible();
    await evidence.snap('Dashboard admin dengan statistik');
  });

});
