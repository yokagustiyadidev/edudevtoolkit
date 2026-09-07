# Changelog

## [2.2.0] - 2026-09-07
### Added
- **Part G — Automation: Info Dinas → Spreadsheet**. Hermes mencatat info dari
  Dinas Pendidikan / Kemendikdasmen ke `info_dinas.xlsx` lokal (append per baris).
- `scripts/catat_info_dinas.py`: script append baris ke Excel via openpyxl.
  Terima JSON di stdin (field: isi, tanggal_info, sumber, kategori,
  tindak_lanjut, status, pj, xlsx). Path default env `INFO_DINAS_XLSX` /
  `D:/2026-2027/info_dinas.xlsx`. Bukan JSON → seluruh teks = isi.
- Kolom sheet: No | Tanggal Catat | Tanggal Info | Sumber | Kategori |
  Isi Info | Tindak Lanjut | Status | PJ.

### Changed
- SKILL.md: tambah Part G; version → 2.2.0.

## [2.1.0] - 2026-09-05
### Added
- `references/prompt_tendik.md`: 10 prompt siap-salin berbahasa Indonesia untuk
  tenaga kependidikan non-teknis.
- `CARA_PAKAI_TENDIK.md`: panduan 1 halaman cara pakai untuk tendik.
- `CONTRIBUTING.md`: panduan kontribusi + standar wajib (security, Kurmer).
- `SECURITY.md`: kebijakan pelaporan kerentanan & standar keamanan.
- `CHANGELOG.md`: file ini.
- `templates/Modul_Ajar_Informatika_Kelas6.docx` + `modul_ajar_informatika_spec.json`:
  dipindah ke `templates/` dari root (sebelumnya file yatim tak dirujuk).

### Changed
- `templates/user_crud.php`: ditulis ulang total menjadi production-ready —
  prepared statement di seluruh query, token CSRF, guard role self-contained
  (session PHP, tanpa dependency eksternal), mutasi state wajib POST.
- `SKILL.md` / `README.md`: sinkronisasi daftar file; perbaiki `tb_nilai`
  → `tb_hasil` di Part A2.

## [2.0.0] - 2026 (sebelumnya)
- Edu Dev Toolkit v2: school ops + Ponytail + Obsidian + building apps +
  reasoning + Kurikulum Merdeka (6 pilar).
- LICENSE MIT.
