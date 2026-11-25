#!/usr/bin/env python3
"""PHASE 3 Test Case Catalogue: bangun reports/Test_Case_Catalogue.xlsx dari spec Playwright.

Sumber data: berkas di tests/*.spec.js (judul test + metadata tc({...})).
Tidak ada test case yang dikarang; seluruh baris berasal dari spec yang benar-benar ada.

Jalankan ulang: python scripts/build_test_catalogue.py
"""
from __future__ import annotations

import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests"
REPORTS = ROOT / "reports"

HDR_FILL = PatternFill("solid", fgColor="1F4E79")
HDR_FONT = Font(color="FFFFFF", bold=True, size=10)

TEST_RE = re.compile(r"test\(\s*'(TC\d+[^']*)'", re.S)
TC_META_RE = re.compile(r"tc\(\s*\{(.*?)\}\s*\)", re.S)
FIELD_RE = re.compile(r"(\w+)\s*:\s*'((?:[^'\\]|\\.)*)'")
SKIP_EXTS = {"latihan"}

PRECOND = {
    "PUBLIC": "Aplikasi berjalan di BASE_URL; tanpa login",
    "ADMIN": "Login sebagai ADMIN (kredensial dari .env)",
    "KARYAWAN": "Login sebagai KARYAWAN (kredensial dari .env)",
    "PELANGGAN": "Login sebagai PELANGGAN (kredensial dari .env)",
}


def parse_specs() -> list[dict]:
    cases = []
    for spec in sorted(TESTS.rglob("*.spec.js")):
        if SKIP_EXTS & set(part for part in spec.relative_to(TESTS).parts[:-1]):
            continue
        text = spec.read_text(encoding="utf-8")
        for m in TEST_RE.finditer(text):
            title = m.group(1).strip()
            tc_id, _, desc = title.partition(" ")
            block = text[m.end(): m.end() + 900]
            meta = {}
            mm = TC_META_RE.search(block)
            if mm:
                for k, v in FIELD_RE.findall(mm.group(1)):
                    meta[k] = v.replace("\\'", "'")
            cases.append({
                "tc_id": tc_id,
                "title": desc,
                "module": meta.get("module", ""),
                "feature": meta.get("feature", ""),
                "feature_name": meta.get("featureName", ""),
                "requirement": meta.get("requirement", ""),
                "role": meta.get("role", ""),
                "type": meta.get("type", ""),
                "priority": meta.get("priority", ""),
                "objective": meta.get("objective", title),
                "expected": meta.get("expected", ""),
                "source": f"tests/{spec.relative_to(TESTS).as_posix()}",
            })
    return cases


def build(cases: list[dict]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Katalog Test Case"
    headers = ["Test Case ID", "Judul", "Module ID", "Feature ID", "Feature Name",
               "Requirement ID", "Role", "Type", "Priority", "Objective",
               "Preconditions", "Expected Result", "Sumber (spec)"]
    ws.append(headers)
    for c in cases:
        ws.append([
            c["tc_id"], c["title"], c["module"], c["feature"], c["feature_name"],
            c["requirement"], c["role"], c["type"], c["priority"], c["objective"],
            PRECOND.get(c["role"], f"Login sebagai {c['role']}" if c["role"] else "-"),
            c["expected"], c["source"],
        ])

    # Cakupan per fitur
    ws2 = wb.create_sheet("Cakupan Fitur")
    ws2.append(["Feature ID", "Nama fitur", "Module ID", "Requirement", "Jumlah TC",
                "Role", "Status"])
    cover: dict[str, dict] = {}
    for c in cases:
        if not c["feature"]:
            continue
        row = cover.setdefault(c["feature"], {
            "name": c["feature_name"], "module": c["module"],
            "req": set(), "roles": set(), "count": 0,
        })
        row["count"] += 1
        if c["requirement"] and c["requirement"] != "-":
            row["req"].add(c["requirement"])
        if c["role"]:
            row["roles"].add(c["role"])
    for fid in sorted(cover):
        r = cover[fid]
        ws2.append([fid, r["name"], r["module"], ", ".join(sorted(r["req"])),
                    r["count"], ", ".join(sorted(r["roles"])), "Ready for Testing"])

    for sheet in wb.worksheets:
        for cell in sheet[1]:
            cell.fill = HDR_FILL
            cell.font = HDR_FONT
            cell.alignment = Alignment(vertical="center", wrap_text=True)
        for col in sheet.columns:
            width = min(48, max(12, max(len(str(c.value or "")) for c in col) + 2))
            sheet.column_dimensions[col[0].column_letter].width = width
        sheet.freeze_panes = "A2"

    REPORTS.mkdir(parents=True, exist_ok=True)
    out = REPORTS / "Test_Case_Catalogue.xlsx"
    wb.save(out)
    print(f"[katalog] {len(cases)} test case -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    build(parse_specs())
