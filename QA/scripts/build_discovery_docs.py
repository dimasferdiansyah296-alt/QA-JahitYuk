#!/usr/bin/env python3
"""PHASE 3-4 Discovery: bangun dokumen discovery (DOCX/XLSX) dari data crawler nyata.

Sumber data (tidak ada yang dikarang):
  - discovery/data/discovery-{public,admin,karyawan,pelanggan}.json  (bukti crawler + screenshot)
  - discovery/documents/QA_Handover.md                               (baseline requirement)

Hasil:
  - discovery/documents/Application_Overview.docx
  - discovery/documents/Feature_Inventory.xlsx
  - discovery/documents/Role_Permission_Matrix.xlsx
  - discovery/documents/QA_Requirement_Specification.docx
  - discovery/diagrams/*.mmd

Jalankan ulang: python scripts/build_discovery_docs.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Cm
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "discovery" / "data"
DOCS = ROOT / "discovery" / "documents"
DIAGRAMS = ROOT / "discovery" / "diagrams"
BASE_URL = "http://127.0.0.1:8000"

ROLES = ["public", "admin", "karyawan", "pelanggan"]

# --- Inventaris halaman global (URL unik) -----------------------------------
# evidence: berkas screenshot hasil crawler (relatif terhadap QA/).
PAGES = [
    ("PG01", "/", "Halaman beranda pengunjung", "Pengunjung",
     "P001_PUBLIC_home.png", "Observed"),
    ("PG02", "/login", "Form login (email, password, ingat saya)", "Pengunjung",
     "P002_PUBLIC_login.png", "Observed"),
    ("PG03", "/register", "Form registrasi pelanggan", "Pengunjung",
     "P003_PUBLIC_register.png", "Observed"),
    ("PG04", "/dashboard", "Redirect ke dashboard sesuai role", "Semua user login",
     "P001_ADMIN_admin-dashboard.png", "Verified (semua role diarahkan sesuai role)"),
    ("PG05", "/admin/dashboard", "Dashboard admin + statistik", "Admin",
     "P001_ADMIN_admin-dashboard.png", "Observed"),
    ("PG06", "/karyawan/dashboard", "Dashboard karyawan", "Admin, Karyawan",
     "P001_KARYAWAN_karyawan-dashboard.png", "Observed"),
    ("PG07", "/pelanggan/dashboard", "Dashboard pelanggan", "Pelanggan",
     "P001_PELANGGAN_pelanggan-dashboard.png", "Observed"),
    ("PG08", "/pelanggan/pesanan", "Daftar pesanan milik pelanggan", "Pelanggan",
     "P004_PELANGGAN_pelanggan-pesanan.png", "Observed"),
    ("PG09", "/pelanggan/pesanan/buat", "Form buat pesanan baru", "Pelanggan",
     "P003_PELANGGAN_pelanggan-pesanan-buat.png", "Observed"),
    ("PG10", "/pelanggan/pesanan/{id}", "Detail pesanan milik pelanggan", "Pelanggan",
     "P005_PELANGGAN_pelanggan-pesanan-11.png", "Observed"),
    ("PG11", "/pesanan", "Daftar semua pesanan + filter & pencarian", "Admin, Karyawan",
     "P003_ADMIN_pesanan.png", "Observed"),
    ("PG12", "/pesanan/{id}", "Detail pesanan (tampilan admin)", "Admin, Karyawan",
     "P005_ADMIN_pesanan-11.png", "Observed"),
    ("PG13", "/pesanan/{id}/edit", "Ubah status pesanan & nomor antrean", "Admin, Karyawan",
     "P006_ADMIN_pesanan-11-edit.png", "Observed"),
]

# --- Inventaris fitur -------------------------------------------------------
FEATURES = [
    ("F01", "BERANDA", "M01", "Pengunjung", "REQ-01",
     "PG01", "Observed"),
    ("F02", "LOGIN / LOGOUT", "M01", "Pengunjung, Semua role", "REQ-01, REQ-02, REQ-03, REQ-04",
     "PG02, PG04", "Verified (login per role diuji)"),
    ("F03", "REGISTER", "M01", "Pengunjung", "REQ-05, REQ-06",
     "PG03", "Observed (form teramati; validasi belum diuji)"),
    ("F04", "PESANAN_PELANGGAN", "M02", "Pelanggan", "REQ-07, REQ-08, REQ-09, REQ-10",
     "PG08, PG09, PG10", "Observed"),
    ("F05", "MANAJEMEN_PESANAN", "M03", "Admin, Karyawan", "REQ-11, REQ-12, REQ-13, REQ-14, REQ-19",
     "PG05, PG11, PG12, PG13", "Observed"),
    ("F06", "KONTROL_AKSES", "M04", "Semua role", "REQ-15, REQ-16, REQ-17, REQ-18",
     "Semua halaman terproteksi", "Verified (redirect & 403 diuji)"),
]

# --- Requirement ------------------------------------------------------------
REQUIREMENTS = [
    ("REQ-01", "M01", "F01", "Pengunjung dapat mengakses halaman login dan register", "Fungsional",
     "Tinggi", "PG02, PG03", "Observed", "Crawler publik + HTTP 200"),
    ("REQ-02", "M01", "F02", "User dengan kredensial valid diarahkan ke dashboard sesuai role", "Fungsional",
     "Kritis", "PG02, PG04", "Verified", "Crawler: /dashboard -> /admin|karyawan|pelanggan/dashboard"),
    ("REQ-03", "M01", "F02", "Login dengan kredensial salah menampilkan pesan \"Email atau password salah.\"", "Negatif",
     "Tinggi", "PG02", "Documented", "AuthController::login"),
    ("REQ-04", "M01", "F02", "User yang sudah login dapat logout", "Fungsional",
     "Sedang", "PG02", "Documented", "Form POST /logout pada layout"),
    ("REQ-05", "M01", "F03", "Pengunjung dapat mendaftar sebagai pelanggan dengan data valid", "Fungsional",
     "Tinggi", "PG03", "Observed", "Crawler form register (6 field)"),
    ("REQ-06", "M01", "F03", "Email yang sudah terdaftar ditolak (unique)", "Negatif",
     "Sedang", "PG03", "Documented", "AuthController::register (unique:users,email)"),
    ("REQ-07", "M02", "F04", "Pelanggan dapat membuat pesanan dengan field wajib terisi", "Fungsional",
     "Kritis", "PG09", "Observed", "Crawler form buat pesanan (8 field)"),
    ("REQ-08", "M02", "F04", "Pesanan baru otomatis berstatus \"baru\"", "Fungsional",
     "Tinggi", "PG09, PG10", "Documented", "Catatan pada form + PesananController"),
    ("REQ-09", "M02", "F04", "Pelanggan hanya melihat pesanan miliknya sendiri", "Akses",
     "Kritis", "PG08, PG10", "Observed", "Daftar pesanan ter-scope per pelanggan"),
    ("REQ-10", "M02", "F04", "Pesanan hanya dapat dihapus saat status masih \"baru\"", "Akses",
     "Tinggi", "PG08, PG10", "Documented", "PesananController::destroy"),
    ("REQ-11", "M03", "F05", "Admin/karyawan dapat melihat daftar semua pesanan", "Fungsional",
     "Kritis", "PG11", "Observed", "Crawler /pesanan (tabel pesanan)"),
    ("REQ-12", "M03", "F05", "Admin/karyawan dapat memfilter status dan mencari pesanan", "Fungsional",
     "Sedang", "PG11", "Observed", "Crawler form filter (select status + input cari)"),
    ("REQ-13", "M03", "F05", "Admin/karyawan dapat mengubah status pesanan (baru->diambil)", "Fungsional",
     "Kritis", "PG13", "Observed", "Crawler form edit (select status)"),
    ("REQ-14", "M03", "F05", "Admin/karyawan dapat menetapkan nomor antrean", "Fungsional",
     "Sedang", "PG13", "Observed", "Crawler form edit (select id_antrean)"),
    ("REQ-15", "M04", "F06", "Guest tidak dapat mengakses halaman yang perlu login", "Akses",
     "Kritis", "Semua halaman auth", "Documented", "Middleware auth"),
    ("REQ-16", "M04", "F06", "Pelanggan tidak dapat mengakses halaman admin/karyawan (403)", "Akses",
     "Kritis", "PG05, PG06, PG11-PG13", "Documented", "Middleware role:admin / role:admin,karyawan"),
    ("REQ-17", "M04", "F06", "Admin/karyawan tidak dapat mengakses dashboard pelanggan (403)", "Akses",
     "Tinggi", "PG07", "Documented", "Middleware role:pelanggan"),
    ("REQ-18", "M04", "F06", "Halaman /dashboard mengarahkan sesuai role user", "Fungsional",
     "Sedang", "PG04", "Verified", "Crawler: redirect per role teramati"),
    ("REQ-19", "M03", "F05", "Dashboard admin menampilkan kartu statistik", "Fungsional",
     "Sedang", "PG05", "Observed", "Crawler /admin/dashboard (kartu statistik)"),
]

# --- Matriks izin (Verifikasi dari crawler + inspeksi route/middleware) ------
# nilai: "Akses" | "403" | "Redirect login" | "Redirect dashboard"
PERMISSION = [
    ("/", "Akses", "Akses", "Akses", "Akses", "Route publik"),
    ("/login", "Akses", "Redirect dashboard", "Redirect dashboard", "Redirect dashboard", "Middleware guest"),
    ("/register", "Akses", "Redirect dashboard", "Redirect dashboard", "Redirect dashboard", "Middleware guest"),
    ("/dashboard", "Redirect login", "Redirect dashboard", "Redirect dashboard", "Redirect dashboard", "Route /dashboard match(role)"),
    ("/admin/dashboard", "Redirect login", "Dashboard pelanggan", "403", "Akses", "role:admin"),
    ("/karyawan/dashboard", "Redirect login", "403", "Akses", "Akses", "role:admin,karyawan"),
    ("/pelanggan/dashboard", "Redirect login", "Akses", "403", "403", "role:pelanggan"),
    ("/pelanggan/pesanan", "Redirect login", "Akses", "403", "403", "role:pelanggan"),
    ("/pelanggan/pesanan/buat", "Redirect login", "Akses", "403", "403", "role:pelanggan"),
    ("/pelanggan/pesanan/{id}", "Redirect login", "Akses (milik sendiri)", "403", "403", "role:pelanggan + scope pemilik"),
    ("/pesanan", "Redirect login", "403", "Akses", "Akses", "role:admin,karyawan"),
    ("/pesanan/{id}", "Redirect login", "403", "Akses", "Akses", "role:admin,karyawan"),
    ("/pesanan/{id}/edit", "Redirect login", "403", "Akses", "Akses", "role:admin,karyawan"),
    ("/logout", "Redirect login", "Akses", "Akses", "Akses", "auth"),
]

# --- Skenario turunan per requirement ---------------------------------------
SCENARIOS = {
    "REQ-02": [("Positif", "Login admin dengan kredensial valid", "Diarahkan ke /admin/dashboard"),
               ("Positif", "Login pelanggan dengan kredensial valid", "Diarahkan ke /pelanggan/dashboard"),
               ("Positif", "Login karyawan dengan kredensial valid", "Diarahkan ke /karyawan/dashboard")],
    "REQ-03": [("Negatif", "Login dengan password salah", "Pesan \"Email atau password salah.\", tetap di /login"),
               ("Negatif", "Login dengan email tidak terdaftar", "Pesan \"Email atau password salah.\""),
               ("Boundary", "Submit form login kosong", "Validasi field wajib email & password")],
    "REQ-05": [("Positif", "Registrasi pelanggan dengan data valid", "Akun dibuat & diarahkan ke dashboard pelanggan"),
               ("Boundary", "Password 7 karakter", "Ditolak: minimal 8 karakter"),
               ("Boundary", "Password 8 karakter", "Diterima"),
               ("Negatif", "Konfirmasi password tidak sama", "Ditolak: konfirmasi tidak cocok")],
    "REQ-06": [("Negatif", "Registrasi dengan email yang sudah terdaftar", "Ditolak: email sudah digunakan")],
    "REQ-07": [("Positif", "Buat pesanan dengan semua field wajib terisi", "Pesanan tersimpan, status \"baru\""),
               ("Negatif", "Buat pesanan tanpa mengisi field wajib", "Validasi field wajib muncul"),
               ("Boundary", "Tanggal tenggat sebelum hari ini", "Ditolak: harus >= hari ini"),
               ("Boundary", "Upload foto > 2 MB", "Ditolak: maksimal 2 MB")],
    "REQ-09": [("Akses", "Pelanggan membuka detail pesanan milik pelanggan lain", "Akses ditolak / tidak menemukan data")],
    "REQ-10": [("Positif", "Hapus pesanan berstatus \"baru\"", "Pesanan terhapus"),
               ("Negatif", "Hapus pesanan yang sedang diproses", "Ditolak")],
    "REQ-12": [("Positif", "Filter status \"selesai\"", "Hanya pesanan berstatus selesai tampil"),
               ("Positif", "Cari berdasarkan nama model", "Hanya pesanan yang cocok tampil"),
               ("Boundary", "Kata kunci tidak ditemukan", "Tabel kosong tanpa error")],
    "REQ-13": [("Positif", "Ubah status baru -> diproses", "Status tersimpan & tampil pada daftar"),
               ("Workflow", "Ubah status berurutan hingga \"diambil\"", "Setiap perubahan tersimpan")],
    "REQ-15": [("Akses", "Guest membuka /pesanan", "Redirect ke /login"),
               ("Akses", "Guest membuka /admin/dashboard", "Redirect ke /login")],
    "REQ-16": [("Akses", "Pelanggan membuka /pesanan", "403 Forbidden"),
               ("Akses", "Pelanggan membuka /admin/dashboard", "403 Forbidden")],
    "REQ-17": [("Akses", "Admin membuka /pelanggan/dashboard", "403 Forbidden"),
               ("Akses", "Karyawan membuka /pelanggan/dashboard", "403 Forbidden")],
    "REQ-18": [("Positif", "Admin membuka /dashboard", "Redirect ke /admin/dashboard"),
               ("Positif", "Karyawan membuka /dashboard", "Redirect ke /karyawan/dashboard"),
               ("Positif", "Pelanggan membuka /dashboard", "Redirect ke /pelanggan/dashboard")],
}

HDR_FILL = PatternFill("solid", fgColor="1F4E79")
HDR_FONT = Font(color="FFFFFF", bold=True, size=10)
BODY_FONT = Font(size=10)


def load_discovery() -> dict:
    out = {}
    for role in ROLES:
        f = DATA / f"discovery-{role}.json"
        if f.exists():
            out[role] = json.loads(f.read_text(encoding="utf-8"))
    return out


def style_doc(doc: Document) -> None:
    st = doc.styles["Normal"]
    st.font.name = "Arial"
    st.font.size = Pt(10)
    for s in doc.sections:
        s.left_margin = s.right_margin = Cm(2.0)


def add_footer(doc: Document, text: str) -> None:
    for s in doc.sections:
        p = s.footer.paragraphs[0]
        p.text = f"{text} | Halaman "
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.style.font.size = Pt(8)
        run = p.add_run()
        fld = run._r.makeelement(
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fldSimple",
            {"{http://schemas.openxmlformats.org/wordprocessingml/2006/main}instr": "PAGE"},
        )
        run._r.append(fld)


def add_table(doc: Document, headers: list[str], rows: list[list[str]], widths=None) -> None:
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        c._tc.get_or_add_tcPr().append(_shade("1F4E79"))
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(v))
            r.font.size = Pt(9)
    doc.add_paragraph()


def _shade(color: str):
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), color)
    return shd


def build_overview(discovery: dict) -> None:
    stamp = datetime.now(timezone.utc).astimezone().strftime("%d %B %Y")
    doc = Document()
    style_doc(doc)
    add_footer(doc, "JAHITYUK — Application Overview (Discovery)")

    h = doc.add_heading("JAHITYUK!! — Application Overview", level=0)
    doc.add_paragraph("Dokumen Discovery (Tahap 1) — berbasis bukti crawler read-only Playwright.")

    doc.add_heading("1. Profil Aplikasi", level=1)
    add_table(doc, ["Item", "Keterangan"], [
        ["Nama aplikasi", "JAHITYUK!! — Sistem Pemesanan & Antrean Jasa Jahit"],
        ["Jenis aplikasi", "Web aplikasi CRUD multi-role (server-rendered)"],
        ["Teknologi", "Laravel (PHP), Blade, Bootstrap 5, MySQL, Session driver = file"],
        ["Base URL pengujian", BASE_URL],
        ["Environment", "local"],
        ["Tanggal discovery", stamp],
        ["Metode", "Crawler read-only (traversal tautan, tanpa submit form) + inspeksi route/controller"],
        ["Role", "Pengunjung (guest), Pelanggan, Karyawan, Admin"],
    ])

    doc.add_heading("2. Tujuan & Pengguna", level=1)
    doc.add_paragraph(
        "JAHITYUK adalah aplikasi pengelolaan jasa penjahitan. Pelanggan membuat pesanan jahit "
        "(jenis layanan, model, ukuran, bahan, warna, rincian, foto acuan), lalu admin/karyawan "
        "memprosesnya melalui alur status: Baru -> Diproses -> Dijahit -> Selesai -> Diambil, "
        "serta menetapkan nomor antrean."
    )
    add_table(doc, ["Role", "Kebutuhan utama"], [
        ["Pengunjung", "Melihat beranda, login, dan mendaftar akun pelanggan"],
        ["Pelanggan", "Membuat & memantau pesanan sendiri, membatalkan pesanan berstatus baru"],
        ["Karyawan", "Melihat & memproses semua pesanan (status, antrean)"],
        ["Admin", "Semua akses karyawan + dashboard statistik"],
    ])

    doc.add_heading("3. Model Akses", level=1)
    doc.add_paragraph(
        "Kontrol akses ditegakkan pada sisi server melalui middleware Laravel: `auth` untuk semua "
        "route privat, dan `role:<daftar>` untuk pembatasan per-role. Ringkasan lengkap pada "
        "Role_Permission_Matrix.xlsx."
    )
    add_table(doc, ["Middleware", "Cakupan route"], [
        ["guest", "/login, /register"],
        ["auth", "/logout, /dashboard, seluruh route di bawah"],
        ["role:admin", "/admin/dashboard"],
        ["role:admin,karyawan", "/karyawan/dashboard, /pesanan/*"],
        ["role:pelanggan", "/pelanggan/dashboard, /pelanggan/pesanan/*"],
    ])

    doc.add_heading("4. Cakupan Discovery", level=1)
    add_table(doc, ["Role crawl", "Jumlah halaman", "Berkas bukti"], [
        [r.upper(), str(len(discovery[r]["pages"])), f"discovery/data/discovery-{r}.json"] for r in ROLES
        if r in discovery
    ])
    doc.add_paragraph(
        "Crawler hanya mengikuti tautan <a href>, tidak mengisi/mengirim form, serta melewati URL "
        "yang mengandung pola: logout, keluar, delete, hapus, destroy, remove."
    )

    doc.add_heading("5. Label Kepercayaan Bukti", level=1)
    add_table(doc, ["Label", "Arti"], [
        ["Verified", "Perilaku sudah dibuktikan melalui eksekusi test nyata"],
        ["Observed", "Halaman/fitur teramati pada crawler, belum diuji perilakunya"],
        ["Documented", "Berasal dari dokumen/kode sumber, belum diuji di browser"],
        ["Inferred", "Kesimpulan tidak langsung, perlu verifikasi"],
        ["Unknown", "Belum ada informasi"],
    ])

    doc.add_heading("6. Keterbatasan Discovery", level=1)
    for x in [
        "Kontrol akses hanya boleh disimpulkan dari perilaku server; tampilan menu di frontend tidak "
        "cukup sebagai bukti penegakan hak akses.",
        "Dashboard karyawan tidak menyediakan tautan ke manajemen pesanan sehingga crawler hanya "
        "menemukan 2 halaman; akses /pesanan perlu dilakukan langsung melalui URL.",
        "Belum ada UI modul pembayaran dan CRUD antrean (tabel ada, halaman belum tersedia).",
        "Halaman beranda (/) masih memakai template bawaan Laravel (judul 'Laravel'), belum branding JAHITYUK.",
        "Data pesanan berasal dari data seed; nomor pesanan pada screenshot dapat berbeda antar run.",
    ]:
        doc.add_paragraph(x, style="List Bullet")

    DOCS.mkdir(parents=True, exist_ok=True)
    doc.save(DOCS / "Application_Overview.docx")


def build_feature_inventory(discovery: dict) -> None:
    wb = Workbook()

    ws = wb.active
    ws.title = "Halaman"
    ws.append(["Page ID", "URL", "Deskripsi", "Role pengakses", "Bukti screenshot", "Status bukti"])
    for row in PAGES:
        ws.append(list(row))

    ws2 = wb.create_sheet("Fitur")
    ws2.append(["Feature ID", "Nama fitur", "Module ID", "Role", "Requirement",
                "Halaman terkait", "Status bukti"])
    for row in FEATURES:
        ws2.append(list(row))

    ws3 = wb.create_sheet("Form & Field")
    ws3.append(["Role crawler", "Page ID", "URL", "Form#", "Method", "Action",
                "Field name", "Tipe", "Wajib", "Label/Placeholder", "Opsi"])
    for role, data in discovery.items():
        for p in data["pages"]:
            for f in p.get("forms") or []:
                if not f.get("fields"):
                    continue
                for fl in f["fields"]:
                    ws3.append([
                        role.upper(), p["page_id"], p.get("final_url") or p["requested_url"],
                        f["form_index"], f.get("method"), f.get("action"),
                        fl.get("name"), fl.get("type"), "Ya" if fl.get("required") else "Tidak",
                        fl.get("label") or fl.get("placeholder") or "",
                        " | ".join(fl.get("options") or [])[:200],
                    ])

    ws4 = wb.create_sheet("Ringkasan Crawl")
    ws4.append(["Role", "Base URL", "Waktu crawl", "Jumlah halaman", "Console error", "HTTP >= 400"])
    for role, data in discovery.items():
        errs = sum(len(p.get("console_errors") or []) for p in data["pages"])
        bad = sum(1 for p in data["pages"] if (p.get("http_status") or 0) >= 400)
        ws4.append([role.upper(), data["base_url"], data["generated_at"], len(data["pages"]), errs, bad])

    for sheet in wb.worksheets:
        for c in sheet[1]:
            c.fill = HDR_FILL
            c.font = HDR_FONT
            c.alignment = Alignment(vertical="center")
        for col in sheet.columns:
            letter = col[0].column_letter
            width = min(60, max(12, max(len(str(c.value or "")) for c in col) + 2))
            sheet.column_dimensions[letter].width = width
        sheet.freeze_panes = "A2"

    DOCS.mkdir(parents=True, exist_ok=True)
    wb.save(DOCS / "Feature_Inventory.xlsx")


def build_permission_matrix() -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Role Permission Matrix"
    ws.append(["Resource / Route", "Pengunjung", "Pelanggan", "Karyawan", "Admin",
               "Sumber penegakan", "Bukti"])
    evidence = {
        "/dashboard": "discovery-{role}.json P001 (redirected=true)",
        "/admin/dashboard": "discovery-admin.json P001",
        "/karyawan/dashboard": "discovery-karyawan.json P001",
        "/pelanggan/dashboard": "discovery-pelanggan.json P001",
        "/pelanggan/pesanan": "discovery-pelanggan.json P004",
        "/pelanggan/pesanan/buat": "discovery-pelanggan.json P003",
        "/pelanggan/pesanan/{id}": "discovery-pelanggan.json P005-P006",
        "/pesanan": "discovery-admin.json P003",
        "/pesanan/{id}": "discovery-admin.json P005, P007 ...",
        "/pesanan/{id}/edit": "discovery-admin.json P006, P008 ...",
    }
    for row in PERMISSION:
        ws.append(list(row) + [evidence.get(row[0], "routes/web.php + status crawler")])

    ws.append([])
    ws.append(["Catatan: 403/redirect diverifikasi ulang melalui test kontrol akses (M05) pada Tahap 2."])

    for c in ws[1]:
        c.fill = HDR_FILL
        c.font = HDR_FONT
    ws.column_dimensions["A"].width = 28
    for col in "BCDE":
        ws.column_dimensions[col].width = 20
    ws.column_dimensions["F"].width = 30
    ws.column_dimensions["G"].width = 40

    DOCS.mkdir(parents=True, exist_ok=True)
    wb.save(DOCS / "Role_Permission_Matrix.xlsx")


def build_requirement_spec() -> None:
    doc = Document()
    style_doc(doc)
    add_footer(doc, "JAHITYUK — QA Requirement Specification")

    doc.add_heading("QA Requirement Specification — JAHITYUK!!", level=0)
    doc.add_paragraph(
        "Daftar requirement yang dapat diuji, diturunkan dari hasil discovery (crawler + inspeksi kode). "
        "Setiap requirement menjadi dasar penelusuran Requirement -> Test Case -> Bukti -> Bug."
    )

    doc.add_heading("1. Daftar Requirement", level=1)
    add_table(doc,
              ["REQ ID", "Module", "Feature", "Requirement", "Tipe", "Prioritas", "Halaman", "Status bukti", "Sumber"],
              [[r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8]] for r in REQUIREMENTS])

    doc.add_heading("2. Skenario Turunan", level=1)
    doc.add_paragraph("Skenario positif, negatif, boundary, workflow, dan akses yang diturunkan dari requirement.")
    rows = []
    for req_id, sc in SCENARIOS.items():
        for tipe, langkah, hasil in sc:
            rows.append([req_id, tipe, langkah, hasil])
    add_table(doc, ["REQ ID", "Tipe skenario", "Langkah / kondisi", "Expected result"], rows)

    doc.add_heading("3. Business Rules", level=1)
    for x in [
        "Status pesanan hanya: baru, diproses, dijahit, selesai, diambil.",
        "Jenis layanan: Jahit Baju, Jahit Celana, Jahit Rok, Jahit Gaun, Jahit Jas, Permak, Lainnya.",
        "Ukuran: S, M, L, XL, XXL.",
        "Tanggal tenggat harus >= hari ini (after_or_equal:today).",
        "Hapus pesanan hanya jika status masih 'baru'.",
        "Password register minimal 8 karakter dan harus dikonfirmasi.",
        "Foto pesanan opsional; format jpeg/jpg/png/webp, maksimal 2 MB.",
    ]:
        doc.add_paragraph(x, style="List Bullet")

    doc.add_heading("4. Hal yang Perlu Konfirmasi", level=1)
    for x in [
        "Apakah karyawan seharusnya memiliki navigasi ke manajemen pesanan dari dashboard-nya?",
        "Apakah alur pembayaran (tabel pembayaran) perlu diuji pada iterasi ini?",
        "Apakah admin seharusnya boleh mengakses /pelanggan/dashboard? (saat ini 403)",
    ]:
        doc.add_paragraph(x, style="List Number")

    DOCS.mkdir(parents=True, exist_ok=True)
    doc.save(DOCS / "QA_Requirement_Specification.docx")


DIAGRAM_FILES = {
    "alur-login.mmd": """flowchart TD
    A[Pengunjung buka /login] --> B[Isi email & password]
    B --> C{Kredensial valid?}
    C -- Tidak --> D[Tampilkan 'Email atau password salah.']
    D --> B
    C -- Ya --> E{Role user}
    E -- admin --> F[/admin/dashboard/]
    E -- karyawan --> G[/karyawan/dashboard/]
    E -- pelanggan --> H[/pelanggan/dashboard/]
""",
    "alur-buat-pesanan.mmd": """flowchart TD
    A[Pelanggan login] --> B[/pelanggan/dashboard/]
    B --> C[/pelanggan/pesanan/buat/]
    C --> D[Isi jenis_layanan, tgl_tenggat, model, ukuran, bahan, warna, rincian]
    D --> E[Foto acuan opsional maks 2MB]
    E --> F{Validasi lolos?}
    F -- Tidak --> G[Tampilkan error validasi]
    G --> D
    F -- Ya --> H[POST /pelanggan/pesanan]
    H --> I[Pesanan tersimpan status 'baru']
    I --> J[/pelanggan/pesanan/]
""",
    "alur-ubah-status-pesanan.mmd": """flowchart TD
    A[Admin/Karyawan login] --> B[/pesanan/]
    B --> C{Filter status / cari}
    C --> D[/pesanan/{id}/edit/]
    D --> E[Ubah status & nomor antrean]
    E --> F[PUT /pesanan/{id}]
    F --> G[Status tersimpan]
    G --> B
    subgraph Alur status
      S1[baru] --> S2[diproses] --> S3[dijahit] --> S4[selesai] --> S5[diambil]
    end
""",
    "alur-registrasi-pelanggan.mmd": """flowchart TD
    A[Pengunjung buka /register] --> B[Isi nama, email, no_telepon, alamat, password, konfirmasi]
    B --> C{Validasi lolos?}
    C -- Tidak --> D[Tampilkan error validasi]
    D --> B
    C -- Ya --> E[POST /register]
    E --> F[User + Pelanggan dibuat]
    F --> G[Auto login -> /pelanggan/dashboard]
""",
}


def build_diagrams() -> None:
    DIAGRAMS.mkdir(parents=True, exist_ok=True)
    for name, content in DIAGRAM_FILES.items():
        (DIAGRAMS / name).write_text(content, encoding="utf-8")


def main() -> None:
    discovery = load_discovery()
    print(f"[discovery] role terbaca: {', '.join(discovery)}")
    build_overview(discovery)
    build_feature_inventory(discovery)
    build_permission_matrix()
    build_requirement_spec()
    build_diagrams()
    print("[discovery] dokumen dibuat:")
    for f in sorted(DOCS.glob("*")):
        print(f"  - {f.relative_to(ROOT)}")
    for f in sorted(DIAGRAMS.glob("*.mmd")):
        print(f"  - {f.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
