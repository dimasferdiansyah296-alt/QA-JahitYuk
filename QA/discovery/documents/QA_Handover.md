# QA Handover — JAHITYUK!! (Sistem Manajemen Penjahitan)

> Dokumen ini adalah handover dari Tahap 1 (Application Discovery) ke Tahap 2 (QA Automation).
> Semua informasi di bawah berbasis bukti: crawler discovery (`discovery/data/`), screenshot (`discovery/screenshots/`), dan inspeksi kode sumber.

---

## 1. Profil Aplikasi

| Item | Keterangan |
|---|---|
| Nama | JAHITYUK!! — Sistem Pemesanan & Antrean Jasa Jahit |
| Teknologi | Laravel 11/12, PHP 8.4, MySQL, Bootstrap 5 |
| Base URL (uji) | http://127.0.0.1:8000 |
| Environment | local |
| Tipe aplikasi | Web aplikasi CRUD multi-role |

---

## 2. Role & Akses

| Role | Dashboard | Akses utama |
|---|---|---|
| **Pengunjung (guest)** | — | `/` (welcome), `/login`, `/register` |
| **Pelanggan** | `/pelanggan/dashboard` | Buat pesanan, lihat daftar/detail pesanan sendiri, batalkan pesanan (status `baru`) |
| **Karyawan** | `/karyawan/dashboard` | Lihat semua pesanan, ubah status & antrean pesanan |
| **Admin** | `/admin/dashboard` | Semua akses karyawan + dashboard statistik (pelanggan, pesanan, karyawan, pendapatan) |

**Aturan middleware:**
- `role:admin` → hanya admin
- `role:admin,karyawan` → admin ATAU karyawan
- `role:pelanggan` → hanya pelanggan
- Guest yang akses route `auth` → 401 (redirect ke login via middleware Laravel)
- User salah role → 403 Forbidden

---

## 3. Daftar Halaman (Page Inventory)

| Page ID | URL | Role | Fitur utama | Bukti |
|---|---|---|---|---|
| P01 | `/` | public | Halaman welcome (login/register) | discovery-public |
| P02 | `/login` | public | Form login (email, password) | discovery-public |
| P03 | `/register` | public | Form registrasi pelanggan | discovery-public |
| P04 | `/admin/dashboard` | admin | Statistik (pelanggan, pesanan, karyawan, pendapatan) | discovery-admin |
| P05 | `/karyawan/dashboard` | admin,karyawan | Dashboard karyawan | discovery-karyawan |
| P06 | `/pelanggan/dashboard` | pelanggan | Dashboard pelanggan (CTA buat pesanan) | discovery-pelanggan |
| P07 | `/pelanggan/pesanan` | pelanggan | Daftar pesanan milik pelanggan | discovery-pelanggan |
| P08 | `/pelanggan/pesanan/buat` | pelanggan | Form buat pesanan baru | discovery-pelanggan |
| P09 | `/pelanggan/pesanan/{id}` | pelanggan | Detail pesanan milik pelanggan | discovery-pelanggan |
| P10 | `/pesanan` | admin,karyawan | Daftar semua pesanan + filter/status | discovery-admin |
| P11 | `/pesanan/{id}` | admin,karyawan | Detail pesanan (admin view) | discovery-admin |
| P12 | `/pesanan/{id}/edit` | admin,karyawan | Ubah status & nomor antrean | discovery-admin |

---

## 4. Fitur Siap Uji (Ready for Testing)

### F01 — Autentikasi
- **REQ-01**: Pengunjung dapat mengakses halaman login dan register.
- **REQ-02**: User dengan kredensial valid dapat login dan diarahkan ke dashboard sesuai role.
- **REQ-03**: Login dengan kredensial salah menampilkan pesan error "Email atau password salah."
- **REQ-04**: User yang sudah login dapat logout.

### F02 — Registrasi Pelanggan
- **REQ-05**: Pengunjung dapat mendaftar sebagai pelanggan dengan data valid (nama, email, no_telepon, alamat, password min 8 karakter + konfirmasi).
- **REQ-06**: Email yang sudah terdaftar ditolak (unique).

### F03 — Pemesanan (Pelanggan)
- **REQ-07**: Pelanggan dapat membuat pesanan baru dengan field wajib: jenis_layanan, tgl_tenggat (≥ hari ini), model, ukuran, bahan, warna, rincian. Foto opsional (image, max 2 MB).
- **REQ-08**: Pesanan baru otomatis berstatus `baru`.
- **REQ-09**: Pelanggan hanya dapat melihat pesanan miliknya sendiri.
- **REQ-10**: Pelanggan dapat membatalkan (delete) pesanan hanya jika status masih `baru`.

### F04 — Manajemen Pesanan (Admin/Karyawan)
- **REQ-11**: Admin/karyawan dapat melihat daftar semua pesanan.
- **REQ-12**: Admin/karyawan dapat memfilter pesanan berdasarkan status dan mencari (model/bahan/nama pelanggan).
- **REQ-13**: Admin/karyawan dapat mengubah status pesanan (baru → diproses → dijahit → selesai → diambil).
- **REQ-14**: Admin/karyawan dapat menetapkan nomor antrean pada pesanan.

### F05 — Kontrol Akses
- **REQ-15**: Guest tidak dapat mengakses halaman yang memerlukan login (redirect ke /login).
- **REQ-16**: Pelanggan tidak dapat mengakses halaman admin/karyawan (403).
- **REQ-17**: Admin/karyawan tidak dapat mengakses dashboard pelanggan (403).
- **REQ-18**: `/dashboard` mengarahkan ke dashboard sesuai role user yang login.

---

## 5. Business Rules

1. **Status pesanan** hanya boleh: `baru`, `diproses`, `dijahit`, `selesai`, `diambil`.
2. **Jenis layanan** hanya: Jahit Baju, Jahit Celana, Jahit Rok, Jahit Gaun, Jahit Jas, Permak, Lainnya.
3. **Tanggal tenggat** harus ≥ hari ini (`after_or_equal:today`).
4. **Hapus pesanan** hanya boleh jika status `baru`.
5. **Password register** minimal 8 karakter dan harus dikonfirmasi.
6. **Foto pesanan** opsional; format jpeg/jpg/png/webp, maks 2 MB.

---

## 6. Preconditions untuk Test

- Aplikasi berjalan di http://127.0.0.1:8000
- Database `jahityuk` sudah ter-migrate + seed (ada akun admin, karyawan, pelanggan)
- Akun uji tersimpan di `QA/.env` (ADMIN_*, KARYAWAN_*, PELANGGAN_*)
- Sesi auth tersimpan di `QA/auth/{role}.json`

---

## 7. Keterbatasan Pengujian

- Karyawan dashboard saat ini hanya menampilkan halaman sederhana tanpa navigasi ke manajemen pesanan (perlu akses langsung via URL `/pesanan`).
- Tidak ada modul pembayaran aktif di UI (tabel `pembayaran` ada tapi belum ada halaman transaksi).
- Tidak ada modul antrean CRUD di UI (antrean hanya dipilih dari dropdown yang sudah ada).
- Halaman welcome (`/`) masih menggunakan default Laravel, belum branding JAHITYUK sepenuhnya.

---

## 8. Hal yang Butuh Konfirmasi dari Pemilik Proyek

1. Apakah karyawan seharusnya bisa mengakses `/karyawan/dashboard` dengan navigasi ke manajemen pesanan?
2. Apakah ada alur pembayaran yang perlu diuji?
3. Apakah admin boleh mengakses `/pelanggan/dashboard`? (saat ini ditolak 403)
