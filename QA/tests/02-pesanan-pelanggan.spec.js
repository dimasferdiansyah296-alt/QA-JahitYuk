// M02 — Pemesanan (Sisi Pelanggan)
const { test, expect } = require('../lib/fixtures');
const { login } = require('./helpers');

test.describe('M02 Pemesanan (Pelanggan)', () => {

  test('TC007 Pelanggan dapat melihat daftar pesanan miliknya', async ({ page, tc, evidence }) => {
    tc({ module: 'M02', feature: 'F04', featureName: 'PESANAN_LIST', requirement: 'REQ-09', role: 'PELANGGAN',
      type: 'Positive', priority: 'High', objective: 'Pelanggan melihat daftar pesanannya sendiri',
      expected: 'Halaman daftar pesanan tampil dengan tabel atau pesan kosong' });
    await login(page, 'PELANGGAN');
    await page.goto('/pelanggan/pesanan');
    await expect(page).toHaveURL(/\/pelanggan\/pesanan/);
    await expect(page.getByText(/Daftar Pesanan|Pesanan Saya/)).toBeVisible();
    await evidence.snap('Daftar pesanan pelanggan');
  });

  test('TC008 Pelanggan dapat membuat pesanan baru dengan data valid', async ({ page, tc, evidence }) => {
    tc({ module: 'M02', feature: 'F04', featureName: 'PESANAN_CREATE', requirement: 'REQ-07', role: 'PELANGGAN',
      type: 'Positive', priority: 'Critical', objective: 'Pelanggan membuat pesanan jahit baru',
      expected: 'Pesanan tersimpan dan diarahkan ke daftar pesanan dengan pesan sukses' });
    await login(page, 'PELANGGAN');
    await page.goto('/pelanggan/pesanan/buat');
    await evidence.snap('Form buat pesanan sebelum diisi');

    await page.selectOption('select[name="jenis_layanan"]', 'Jahit Baju');
    await page.fill('input[name="tgl_tenggat"]', '2026-12-31');
    await page.fill('input[name="model"]', 'Kemeja Formal');
    await page.selectOption('select[name="ukuran"]', 'L');
    await page.fill('input[name="bahan"]', 'Katun');
    await page.fill('input[name="warna"]', 'Biru');
    await page.fill('textarea[name="rincian"]', 'Lengan panjang, kerah kemeja, saku dada');
    await evidence.snap('Form buat pesanan terisi lengkap');

    await page.getByRole('button', { name: 'Kirim Pesanan' }).click();
    await expect(page).toHaveURL(/\/pelanggan\/pesanan$/);
    await expect(page.locator('.alert-success')).toContainText('berhasil dibuat');
    await evidence.snap('Pesanan berhasil dibuat');
  });

  test('TC009 Buat pesanan tanpa field wajib menampilkan validasi', async ({ page, tc, evidence }) => {
    tc({ module: 'M02', feature: 'F04', featureName: 'PESANAN_CREATE', requirement: 'REQ-07', role: 'PELANGGAN',
      type: 'Negative', priority: 'High', objective: 'Validasi field wajib pada form pesanan',
      expected: 'Form tidak tersubmit; pesan error field wajib muncul' });
    await login(page, 'PELANGGAN');
    await page.goto('/pelanggan/pesanan/buat');
    await page.getByRole('button', { name: 'Kirim Pesanan' }).click();
    // Tetap di halaman buat (ada error validasi)
    await expect(page).toHaveURL(/\/pelanggan\/pesanan\/buat/);
    await evidence.snap('Validasi field wajib pesanan');
  });

  test('TC010 Pelanggan dapat melihat detail pesanannya', async ({ page, tc, evidence }) => {
    tc({ module: 'M02', feature: 'F04', featureName: 'PESANAN_SHOW', requirement: 'REQ-09', role: 'PELANGGAN',
      type: 'Positive', priority: 'Medium', objective: 'Pelanggan melihat detail pesanannya',
      expected: 'Halaman detail pesanan tampil dengan info pesanan' });
    await login(page, 'PELANGGAN');
    await page.goto('/pelanggan/pesanan');
    await evidence.snap('Daftar pesanan sebelum pilih detail');
    // Link detail pesanan: /pelanggan/pesanan/{id} (angka), bukan /buat
    const detailLink = page.locator('a[href*="/pelanggan/pesanan/"]').filter({ hasText: /Detail|Lihat|\d+/ }).first();
    const count = await detailLink.count();
    if (count > 0) {
      await detailLink.click();
      await expect(page).toHaveURL(/\/pelanggan\/pesanan\/\d+/);
      await expect(page.getByText(/Detail Pesanan/)).toBeVisible();
      await evidence.snap('Detail pesanan pelanggan');
    } else {
      test.skip(true, 'BLOCKED: tidak ada pesanan untuk pelanggan ini');
    }
  });

});
