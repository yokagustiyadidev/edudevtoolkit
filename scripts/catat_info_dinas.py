#!/usr/bin/env python3
"""
catat_info_dinas.py — Append satu baris info dari Dinas Pendidikan / Kemendikdasmen
ke spreadsheet Excel (.xlsx) lokal.

Cara pakai (dari Hermes / command line):
  echo '{"isi":"Surat edaran UN mendatang","sumber":"Kemendikdasmen","kategori":"Surat Edaran"}' \
    | python scripts/catat_info_dinas.py

Input: JSON di stdin dengan field opsional:
  isi            (wajib) — isi info surat/pengumuman
  tanggal_info   — tanggal tertulis di surat (kosong = "-")
  sumber         — default "Dinas/Kemendikdasmen"
  kategori       — Surat Edaran | Juknis | Lomba | Kalender | Lainnya (default Lainnya)
  tindak_lanjut  — rencana sekolah (default "-")
  status         — Belum ditindak | Proses | Selesai (default Belum ditindak)
  pj             — penanggung jawab (default "-")
  xlsx           — override path file (default env INFO_DINAS_XLSX atau D:/2026-2027/info_dinas.xlsx)

Output: JSON {"ok":true,"no":N,"path":"...","tanggal_catat":"..."}

Bila stdin bukan JSON, seluruh teks dianggap field `isi`.
Path opsional disimpan di env INFO_DINAS_XLSX agar portable antar sekolah.
"""
import sys
import os
import json
import datetime

from openpyxl import Workbook, load_workbook

DEFAULT_PATH = os.environ.get("INFO_DINAS_XLSX", r"D:/2026-2027/info_dinas.xlsx")
HEADERS = ["No", "Tanggal Catat", "Tanggal Info", "Sumber", "Kategori",
           "Isi Info", "Tindak Lanjut", "Status", "PJ"]


def _wib_now():
    # WIB = UTC+7
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))


def main():
    raw = sys.stdin.read().strip()
    if not raw:
        print(json.dumps({"ok": False, "error": "stdin kosong"}))
        sys.exit(1)

    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            data = {"isi": str(data)}
    except Exception:
        # Bukan JSON -> anggap seluruh teks adalah isi info
        data = {"isi": raw}

    path = data.get("xlsx") or DEFAULT_PATH

    if os.path.exists(path):
        wb = load_workbook(path)
        ws = wb.active
    else:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        wb = Workbook()
        ws = wb.active
        ws.append(HEADERS)

    data_rows = max(ws.max_row - 1, 0)
    no = data_rows + 1
    tcatat = _wib_now().strftime("%Y-%m-%d %H:%M")

    row = [
        no,
        tcatat,
        data.get("tanggal_info") or "-",
        data.get("sumber") or "Dinas/Kemendikdasmen",
        data.get("kategori") or "Lainnya",
        data.get("isi") or "",
        data.get("tindak_lanjut") or "-",
        data.get("status") or "Belum ditindak",
        data.get("pj") or "-",
    ]
    ws.append(row)
    wb.save(path)

    print(json.dumps({
        "ok": True,
        "no": no,
        "path": path,
        "tanggal_catat": tcatat,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
