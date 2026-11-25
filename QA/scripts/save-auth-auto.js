#!/usr/bin/env node
// Simpan sesi login otomatis untuk tiap role (memakai kredensial di .env).
// Digunakan untuk discovery & test yang memerlukan autentikasi.
const fs = require('fs');
const path = require('path');
const { chromium } = require('@playwright/test');
const { BASE_URL, VIEWPORT, AUTH_DIR, credentials } = require('../lib/env');

const roles = ['admin', 'karyawan', 'pelanggan'];

(async () => {
  fs.mkdirSync(AUTH_DIR, { recursive: true });

  for (const role of roles) {
    const { user, pass } = credentials(role.toUpperCase());
    if (!user || !pass) {
      console.log(`[SKIP] role "${role}": kredensial belum diisi di .env`);
      continue;
    }

    const browser = await chromium.launch();
    const context = await browser.newContext({ viewport: VIEWPORT, locale: 'id-ID' });
    const page = await context.newPage();

    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[name="email"]', user);
    await page.fill('input[name="password"]', pass);
    await page.click('button[type="submit"]');
    await page.waitForLoadState('networkidle').catch(() => {});

    const file = path.join(AUTH_DIR, `${role}.json`);
    await context.storageState({ path: file });
    await browser.close();
    console.log(`[OK] Sesi tersimpan: auth/${role}.json (${user})`);
  }
})().catch((e) => { console.error(e); process.exit(1); });
