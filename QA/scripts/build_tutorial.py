#!/usr/bin/env python3
"""PHASE 10 User Tutorial: bangun reports/Website_User_Tutorial.docx.

Sumber:
  - screenshots/*.png              (bukti aktual hasil eksekusi test)
  - discovery/screenshots/*.png    (tangkapan crawler discovery)
  - metadata test case (tests/*.spec.js, via build_test_catalogue.parse_specs)

Prinsip:
  - Menggunakan nama menu/istilah aktual aplikasi.
  - TIDAK menyertakan kredensial.
  - Membedakan langkah terverifikasi (dibuktikan test PASS) dan yang belum diverifikasi.

Jalankan ulang: python scripts/build_tutorial.py
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
BASE_URL = "http://127.0.0.1:8000"

HEADER_FILL = "1F4E79"
VERIFIED = "[Terverifikasi]"          # dibuktikan test PASS
UNVERIFIED = "[Belum diverifikasi]"   # belum diuji otomatis


def style_doc(doc: Document) -> None:
    st = doc.styles["Normal"]
    st.font.name = "Arial"
    st.font.size = Pt(10.5)
    st.paragraph_format.space_after = Pt(6)
    for s in doc.sections:
        s.page_width = Cm(21.0)
        s.page_height = Cm(29.7)
        s.top_margin = Cm(2.2)
        s.bottom_margin = Cm(2.0)
        s.left_margin = Cm(2.2)
        s.right_margin = Cm(2.0)


def add_header_footer(doc: Document, text: str) -> None:
    for s in doc.sections:
        hp = s.header.paragraphs[0]
        hp.text = text
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hp.runs[0].font.size = Pt(8)
        hp.runs[0].font.color.rgb = RGBColor(0x55, 0x55, 0x55)
        fp = s.footer.paragraphs[0]
        fp.text = f"{text} | Halaman "
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fp.runs[0].font.size = Pt(8)
        run = fp.add_run()
        fld = OxmlElement("w:fldSimple")
        fld.set(qn("w:instr"), "PAGE")
        run._r.append(fld)


def add_toc(doc: Document) -> None:
    p = doc.add_paragraph()
    run = p.add_run()
    begin = OxmlElement("w:fldChar"); begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve")
    instr.text = 'TOC \\o "1-3" \\h \\z \\u'
    sep = OxmlElement("w:fldChar"); sep.set(qn("w:fldCharType"), "separate")
    txt = OxmlElement("w:t"); txt.text = 'Klik kanan lalu pilih "Update Field" untuk memuat daftar isi.'
    end = OxmlElement("w:fldChar"); end.set(qn("w:fldCharType"), "end")
    for el in (begin, instr, sep, txt, end):
        run._r.append(el)


def _shade(color: str):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), color)
    return shd


def add_table(doc: Document, headers, rows) -> None:
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(str(h))
        r.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        c._tc.get_or_add_tcPr().append(_shade(HEADER_FILL))
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(v))
            r.font.size = Pt(9)
    doc.add_paragraph()


def add_steps(doc: Document, steps: list[str]) -> None:
    for s in steps:
        doc.add_paragraph(s, style="List Number")


def add_figure(doc: Document, rel_path: str, caption: str, width_cm: float = 14.5) -> None:
    img = ROOT / rel_path
    if not img.exists():
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(img), width=Cm(width_cm))
    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cp.add_run(caption)
    r.italic = True
    r.font.size = Pt(8)
    r.font.color.rgb = RGBColor(0x44, 0x44, 0x44)


def build() -> None:
    stamp = datetime.now(timezone.utc).astimezone().strftime("%d %B %Y")
    apps = "JAHITYUK!! — Sistem Manajemen Penjahitan"

    doc = Document()
    style_doc(doc)
    add_header_footer(doc, "JAHITYUK — Panduan Pengguna")

    # ===== Cover =====
    t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run("\n\n\nPanduan Pengguna")
    r.bold = True; r.font.size = Pt(28)
    sub = doc.add_paragraph(); sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rs = sub.add_run(apps); rs.font.size = Pt(14); rs.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    doc.add_paragraph()
    m = doc.add_paragraph(); m.alignment = WD_ALIGN_PARAGRAPH.CENTER
    m.add_run(
        "Dokumen Tutorial (User Documentation)\n"
        f"Base URL: {BASE_URL}\n"
        f"Tanggal: {stamp}"
    ).font.size = Pt(11)
    doc.add_page_break()

    doc.add_heading("Daftar Isi", level=1)
    add_toc(doc)
    doc.add_page_break()

    # ===== 1. Pendahuluan =====
    doc.add_heading("1. Pendahuluan", level=1)
    doc.add_paragraph(
        "JAHITYUK adalah aplikasi pengelolaan jasa penjahitan. Pengunjung dapat melihat beranda dan "
        "mendaftar akun; pelanggan membuat dan memantau pesanan jahit; admin dan karyawan memproses "
        "pesanan melalui alur status serta menetapkan nomor antrean."
    )
    add_table(doc, ["Item", "Keterangan"], [
        ["Nama aplikasi", apps],
        ["Tujuan", "Mengelola pesanan jasa jahit dari pemesanan hingga pengambilan"],
        ["Pengguna sasaran", "Pelanggan, Karyawan, Admin"],
        ["Persyaratan penggunaan", "Perangkat dengan browser modern (mis. Chrome/Edge) dan koneksi ke server aplikasi"],
        ["Alamat aplikasi", BASE_URL],
    ])
    doc.add_paragraph(
        "Catatan verifikasi: langkah yang ditandai [Terverifikasi] telah diuji otomatis dan lulus "
        "(PASS). Langkah [Belum diverifikasi] belum diuji otomatis pada iterasi ini dan disarankan "
        "dikonfirmasi manual."
    )

    # ===== 2. Memulai =====
    doc.add_heading("2. Memulai (Getting Started)", level=1)
    doc.add_heading("2.1 Membuka Aplikasi", level=2)
    add_steps(doc, [
        f"Buka browser dan akses {BASE_URL}.",
        "Halaman beranda menampilkan tautan Log in dan Register.",
    ])
    add_figure(doc, "screenshots/TC001_PUBLIC_BERANDA_STEP01_PASS.png",
               "Gambar 1. Halaman beranda untuk pengunjung (TC001, PASS).")

    doc.add_heading("2.2 Masuk (Login) " + VERIFIED, level=2)
    add_steps(doc, [
        "Klik Log in pada halaman beranda.",
        "Isi kolom email dan password.",
        "Klik tombol Masuk.",
        "Jika kredensial valid, Anda diarahkan ke dashboard sesuai role.",
    ])
    add_figure(doc, "screenshots/TC002_PUBLIC_LOGIN_STEP01_PASS.png",
               "Gambar 2. Form login dengan field email dan password (TC002, PASS).")
    doc.add_paragraph(
        "Jika email/password salah, sistem menampilkan pesan 'Email atau password salah.' dan Anda "
        "tetap berada di halaman login (TC003, PASS)."
    )
    add_figure(doc, "screenshots/TC003_PUBLIC_LOGIN_STEP01_PASS.png",
               "Gambar 3. Pesan error saat kredensial salah (TC003, PASS).")

    doc.add_heading("2.3 Mendaftar (Register) " + VERIFIED, level=2)
    add_steps(doc, [
        "Dari halaman beranda, klik Register.",
        "Isi nama, email, no. telepon, alamat, password, dan konfirmasi password.",
        "Klik tombol daftar.",
        "Validasi memastikan password minimal 8 karakter.",
    ])
    add_figure(doc, "screenshots/TC006_PUBLIC_REGISTER_STEP01_PASS.png",
               "Gambar 4. Validasi password pendek pada form registrasi (TC006, PASS).")
    doc.add_paragraph(
        f"{UNVERIFIED} Registrasi dengan data lengkap sampai akun berhasil dibuat dan otomatis masuk "
        "belum diuji otomatis pada iterasi ini."
    )

    doc.add_heading("2.4 Keluar (Logout) " + UNVERIFIED, level=2)
    doc.add_paragraph(
        "Tombol keluar tersedia pada menu pengguna setelah login. Alur logout belum diuji otomatis "
        "(REQ-04 belum tercakup test case); disarankan memverifikasi secara manual."
    )

    # ===== 3. Navigasi =====
    doc.add_heading("3. Navigasi Aplikasi", level=1)
    doc.add_paragraph(
        "Setelah login, setiap role diarahkan ke dashboard-nya masing-masing melalui halaman /dashboard:"
    )
    add_table(doc, ["Role", "Dashboard", "Menu utama"], [
        ["Pelanggan", "/pelanggan/dashboard", "Pesanan Saya (daftar pesanan), Buat Pesanan"],
        ["Karyawan", "/karyawan/dashboard", "Akses Manajemen Pesanan via /pesanan"],
        ["Admin", "/admin/dashboard", "Statistik (Pelanggan, Pesanan, Karyawan, Pendapatan) dan Manajemen Pesanan"],
    ])
    add_figure(doc, "discovery/screenshots/P001_KARYAWAN_karyawan-dashboard.png",
               "Gambar 5. Dashboard karyawan (hasil discovery).")

    # ===== 4. Pengunjung =====
    doc.add_heading("4. Panduan untuk Pengunjung", level=1)
    doc.add_paragraph(
        "Pengunjung (belum login) dapat mengakses beranda, melihat form login, dan mendaftar akun "
        "pelanggan. Fitur yang memerlukan login akan mengalihkan ke halaman login (TC015, PASS)."
    )

    # ===== 5. Pelanggan =====
    doc.add_heading("5. Panduan untuk Pelanggan", level=1)
    add_figure(doc, "screenshots/TC005_PELANGGAN_LOGIN_STEP01_PASS.png",
               "Gambar 6. Dashboard pelanggan setelah login (TC005, PASS).")

    doc.add_heading("5.1 Melihat Daftar Pesanan " + VERIFIED, level=2)
    add_steps(doc, [
        "Login sebagai pelanggan.",
        "Buka menu Pesanan Saya / Daftar Pesanan.",
        "Aplikasi menampilkan daftar pesanan milik Anda (hanya pesanan Anda sendiri).",
    ])
    add_figure(doc, "screenshots/TC007_PELANGGAN_PESANAN_LIST_STEP01_PASS.png",
               "Gambar 7. Daftar pesanan pelanggan (TC007, PASS).")

    doc.add_heading("5.2 Membuat Pesanan " + VERIFIED, level=2)
    add_steps(doc, [
        "Buka menu Buat Pesanan.",
        "Pilih jenis layanan, isi tanggal tenggat (>= hari ini), model, ukuran, bahan, warna, dan rincian.",
        "Opsional: unggah foto acuan (jpeg/jpg/png/webp, maksimal 2 MB).",
        "Klik tombol Kirim Pesanan.",
        "Pesanan tersimpan dengan status 'baru' dan diarahkan ke daftar pesanan dengan pesan sukses.",
    ])
    add_figure(doc, "screenshots/TC008_PELANGGAN_PESANAN_CREATE_STEP01_PASS.png",
               "Gambar 8. Form buat pesanan sebelum diisi (TC008, PASS).")
    add_figure(doc, "screenshots/TC008_PELANGGAN_PESANAN_CREATE_STEP02_PASS.png",
               "Gambar 9. Form buat pesanan terisi lengkap (TC008, PASS).")
    doc.add_paragraph(
        "Jika kolom wajib belum diisi, form tidak tersubmit dan pesan validasi muncul (TC009, PASS)."
    )
    add_figure(doc, "screenshots/TC009_PELANGGAN_PESANAN_CREATE_STEP01_PASS.png",
               "Gambar 10. Validasi kolom wajib pada form pesanan (TC009, PASS).")

    doc.add_heading("5.3 Melihat Detail Pesanan " + VERIFIED, level=2)
    add_steps(doc, [
        "Dari daftar pesanan, klik tautan detail pada salah satu pesanan.",
        "Halaman Detail Pesanan menampilkan informasi pesanan tersebut.",
    ])
    add_figure(doc, "screenshots/TC010_PELANGGAN_PESANAN_SHOW_STEP02_PASS.png",
               "Gambar 11. Detail pesanan pelanggan (TC010, PASS).")

    doc.add_heading("5.4 Membatalkan / Menghapus Pesanan " + UNVERIFIED, level=2)
    doc.add_paragraph(
        "Pesanan hanya dapat dihapus saat statusnya masih 'baru'. Alur ini belum diuji otomatis "
        "(REQ-10 belum tercakup); disarankan memverifikasi manual."
    )

    # ===== 6. Karyawan =====
    doc.add_heading("6. Panduan untuk Karyawan", level=1)
    doc.add_paragraph(
        f"{UNVERIFIED} Login khusus role Karyawan belum diuji otomatis pada iterasi ini. Karyawan "
        "memiliki akses yang sama dengan admin untuk manajemen pesanan."
    )
    doc.add_paragraph(
        "Catatan: dashboard karyawan belum menyediakan tautan langsung ke Manajemen Pesanan; "
        "manajemen pesanan diakses melalui alamat /pesanan."
    )
    doc.add_heading("6.1 Manajemen Pesanan " + VERIFIED + " (via akun admin)", level=2)
    doc.add_paragraph(
        "Langkah pada Bab 7 (Admin) berlaku sama untuk karyawan pada halaman /pesanan. Halaman "
        "Manajemen Pesanan menampilkan seluruh pesanan dengan filter status dan pencarian."
    )

    # ===== 7. Admin =====
    doc.add_heading("7. Panduan untuk Admin", level=1)
    add_figure(doc, "screenshots/TC004_ADMIN_LOGIN_STEP01_PASS.png",
               "Gambar 12. Dashboard admin setelah login (TC004, PASS).")

    doc.add_heading("7.1 Dashboard Statistik " + VERIFIED, level=2)
    doc.add_paragraph(
        "Dashboard admin menampilkan kartu statistik: Pelanggan, Pesanan, Karyawan, dan Pendapatan "
        "(TC014, PASS)."
    )
    add_figure(doc, "screenshots/TC014_ADMIN_ADMIN_DASHBOARD_STEP01_PASS.png",
               "Gambar 13. Dashboard admin dengan kartu statistik (TC014, PASS).")

    doc.add_heading("7.2 Melihat Daftar Semua Pesanan " + VERIFIED, level=2)
    add_steps(doc, [
        "Buka menu Manajemen Pesanan (/pesanan).",
        "Halaman menampilkan tabel seluruh pesanan dari semua pelanggan.",
    ])
    add_figure(doc, "screenshots/TC011_ADMIN_ADMIN_PESANAN_LIST_STEP01_PASS.png",
               "Gambar 14. Daftar semua pesanan (TC011, PASS).")

    doc.add_heading("7.3 Memfilter Pesanan " + VERIFIED, level=2)
    add_steps(doc, [
        "Pada halaman Manajemen Pesanan, pilih status pada dropdown filter (mis. 'baru').",
        "Klik tombol Filter.",
        "Tabel menampilkan pesanan sesuai status yang dipilih.",
    ])
    add_figure(doc, "screenshots/TC012_ADMIN_ADMIN_PESANAN_FILTER_STEP01_PASS.png",
               "Gambar 15. Hasil filter status 'baru' (TC012, PASS).")

    doc.add_heading("7.4 Mengubah Status Pesanan " + VERIFIED, level=2)
    add_steps(doc, [
        "Pada daftar pesanan, klik aksi ubah/edit pada pesanan yang dituju.",
        "Pilih status baru (baru → diproses → dijahit → selesai → diambil).",
        "Klik tombol Simpan Perubahan.",
        "Status tersimpan dan muncul pesan sukses.",
    ])
    add_figure(doc, "screenshots/TC013_ADMIN_ADMIN_PESANAN_UPDATE_STEP01_PASS.png",
               "Gambar 16. Form ubah status sebelum disimpan (TC013, PASS).")
    add_figure(doc, "screenshots/TC013_ADMIN_ADMIN_PESANAN_UPDATE_STEP02_PASS.png",
               "Gambar 17. Status pesanan berhasil diubah (TC013, PASS).")
    doc.add_paragraph(
        f"{UNVERIFIED} Penetapan nomor antrean pada form edit belum diuji otomatis (REQ-14)."
    )

    # ===== 8. Alur Bisnis =====
    doc.add_heading("8. Alur Bisnis (Business Workflow)", level=1)
    doc.add_paragraph("Urutan proses pemesanan hingga pengambilan:")
    add_table(doc, ["Tahap", "Aktor", "Aktivitas", "Status pesanan"], [
        ["1", "Pelanggan", "Membuat pesanan jahit", "baru"],
        ["2", "Admin/Karyawan", "Menetapkan nomor antrean & memproses", "diproses"],
        ["3", "Admin/Karyawan", "Proses penjahitan", "dijahit"],
        ["4", "Admin/Karyawan", "Pesanan selesai dikerjakan", "selesai"],
        ["5", "Admin/Karyawan", "Pesanan diambil pelanggan", "diambil"],
    ])
    doc.add_paragraph(
        "Kondisi: pesanan hanya dapat dihapus oleh pelanggan saat berstatus 'baru'. Foto acuan "
        "opsional (maksimal 2 MB)."
    )

    # ===== 9. Troubleshooting =====
    doc.add_heading("9. Troubleshooting", level=1)
    add_table(doc, ["Gejala", "Kemungkinan penyebab", "Solusi"], [
        ["Diarahkan ke halaman login saat membuka menu",
         "Belum login atau sesi berakhir", "Masuk kembali dengan akun yang sesuai (TC015)."],
        ["Pesan 'Email atau password salah.'",
         "Email/password keliru", "Periksa kembali kredensial Anda (TC003)."],
        ["Pesan validasi pada form pesanan",
         "Kolom wajib belum diisi / tanggal tenggat < hari ini", "Lengkapi kolom wajib dan pilih tanggal >= hari ini (TC009)."],
        ["Akses ditolak (403 Forbidden)",
         "Membuka halaman di luar role akun", "Gunakan akun dengan role yang tepat (TC016, TC017)."],
        ["Berkas foto pesanan ditolak",
         "Format/ukuran tidak sesuai",
         "Gunakan jpeg/jpg/png/webp dengan ukuran maksimal 2 MB. " + UNVERIFIED],
    ])

    # ===== 10. Informasi Tambahan =====
    doc.add_heading("10. Informasi Tambahan", level=1)
    doc.add_paragraph(
        "Dokumen ini disusun berdasarkan aplikasi aktual dan hasil pengujian. Tanda verifikasi:"
    )
    add_table(doc, ["Tanda", "Arti"], [
        [VERIFIED, "Langkah telah diuji otomatis dan lulus (PASS)."],
        [UNVERIFIED, "Langkah belum diuji otomatis; perlu konfirmasi manual."],
    ])
    doc.add_paragraph("Bukti screenshot mengacu pada ID test case, mis. TC008 = pembuatan pesanan.")

    REPORTS.mkdir(parents=True, exist_ok=True)
    out = REPORTS / "Website_User_Tutorial.docx"
    doc.save(out)
    print(f"[tutorial] -> {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build()
