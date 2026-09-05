---
name: edu-dev-toolkit
description: "Educator toolkit: school ops, ponytail code, Obsidian notes."
version: "1.0.0"
author: Hermes Agent
license: MIT
hermes:
  tags: [education, school, users, report, dashboard, ponytail, obsidian, notes]
  related_skills: []
metadata:
  hermes:
    tags: [education, school, users, report, dashboard, ponytail, obsidian, notes]
    related_skills: []
category: edu-dev
---

# Edu Dev Toolkit

Toolkit terpadu untuk pendidik yang merawat sistem web sekolah: operasikan data sekolah,
bangun fitur dengan cara paling simpel, dan dokumentasikan pengetahuan. Tiga pilar:

- **Part A — School Operations**: kelola akun guru/staf, buat laporan, jalankan dashboard aman.
- **Part B — Build Simply (Ponytail)**: filosofi kode paling pendek yang tetap bekerja.
- **Part C — Knowledge & Notes (Obsidian)**: simpan & cari catatan di vault.

Gunakan saat: mengelola akun sekolah, membuat rekap nilai/absen, mengaudit keamanan
dashboard, menulis/menyederhanakan kode fitur sekolah, atau mendokumentasikan sistem.

## When to Use
- Mengelola akun guru/staf, reset password, nonaktifkan user (Part A1).
- Membuat rekap nilai/absen atau export laporan (A2).
- Menjalankan dashboard per role atau audit keamanan (A3).
- Menulis/menyederhanakan kode sistem sekolah (Part B / Ponytail).
- Mendokumentasikan arsitektur/SOP/audit di vault (Part C / Obsidian).

======================================================================
## PART A — SCHOOL OPERATIONS
======================================================================

### A1. Manajemen Akun Guru & Staf (CRUD `tb_users`)
Siklus hidup akun guru & tenaga kependidikan. Generik — sesuaikan nama tabel/kolom.

Data model minimal:
- `id` int PK
- `nama` varchar (wajib)
- `username`/`nip` varchar UNIK (cek duplikat sebelum insert)
- `role` enum: `admin` | `guru` | `staf`
- `password` varchar — SELALU `password_hash()`, jangan plaintext/MD5
- `status` tinyint: 1=aktif, 0=nonaktif (soft delete)
- `created_at`/`updated_at` timestamp

CREATE: validasi (nama wajib, username unik, role valid) → hash password → insert `status=1`
→ verifikasi kolom password berisi hash (`$2y$...`), bukan teks asli.

EDIT: update nama/role/foto langsung. Password HANYA di-rehash kalau field diisi.
Waspada eskalasi peran (guru→admin butuh konfirmasi eksplisit).

DEACTIVATE (prefer) vs DELETE: soft delete `UPDATE tb_users SET status=0` menyelamatkan
data relasional. Hard delete hanya bila tak ada FK. SAFETY: backup, hitung baris
before/after, scope persis.

RESET PASSWORD: hash baru + flag `must_change_pw=1`. Jangan tulis plaintext ke log.

### A2. Laporan Sekolah (Rekap Nilai / Absen)
Sumber: `tb_hasil`/`tb_nilai` (id_siswa, id_mapel, poin, tipe_soal), `tb_siswa`,
`tb_mapel` (bobot), `tb_absen` (status: hadir/izin/sakit/alpa).

Pola: `AVG(poin) GROUP BY id_siswa, id_mapel`. Bobot tipe (PG=1, isian=3, essay=5)
SIMPAN di DB, JANGAN hardcode di query.

```sql
SELECT s.nama, m.nama_mapel, ROUND(AVG(h.poin),2) AS rata2, COUNT(*) AS jumlah
FROM tb_hasil h
JOIN tb_siswa s ON s.id=h.id_siswa
JOIN tb_mapel m ON m.id=h.id_mapel
WHERE h.id_mapel=? AND s.kelas=?
GROUP BY s.id, m.id ORDER BY rata2 DESC;
```

Output: CSV (`fputcsv`), HTML table, atau PDF (TCPDF/Dompdf/print CSS).
Pitfalls: AVG null → tampilkan `-`; filter tanggal pakai `DATE()` + WIB (Asia/Jakarta);
agregasi di SQL (jangan N+1 loop). Verifikasi: total laporan == jumlah raw baris per siswa.

### A3. Dashboard Runbook & Security Baseline
Role matrix (least privilege): `admin` (user/mapel/token/rekap/backup), `guru`
(CRUD materi/soal, mulai ujian, koreksi, rekap), `staf` (rekap/absen, TIDAK ubah soal/token).

Cara benar: login pakai `session_regenerate_id(true)` (anti fixation); token ujian
verifikasi SERVER-SIDE (PHP), bukan cek JS (mudah bypass); koreksi simpan poin per
tipe sesuai bobot DB; rekap agregasi di DB.

Security baseline (audit): CSRF token di semua POST; `session_regenerate_id(true)`
setelah login; idle timeout (30 mnt); password hash; backup `tb_hasil` & `tb_users`
sebelum modifikasi massal.

Operational runbook (ubah data/code): 1) backup dulu, 2) staging bila bisa,
3) verifikasi baris before/after, 4) deploy & konfirmasi live, 5) catat audit.

======================================================================
## PART B — BUILD SIMPLY (Ponytail)
======================================================================
Lazy senior dev: solusi paling pendek yang tetap bekerja. YAGNI, stdlib dulu,
tanpa abstraksi yang tak diminta.

Ladder (berhenti di rung pertama yang cukup):
1. Perlu ada? Spekulatif = skip, sebut satu baris.
2. Stdlib cukup? Pakai.
3. Fitur native platform cukup? `<input type=date>` > picker lib, CSS > JS, constraint DB > app code.
4. Dependency terpasang cukup? Pakai. Jangan tambah baru untuk yang beberapa baris bisa.
5. Bisa satu baris? Satu baris.
6. Baru: kode minimum yang bekerja.

Rules: tanpa abstraksi tak diminta (interface/factory/config untuk satu implementasi);
deletion > addition; fewest files; diff terpendek menang. Tandai penyederhanaan sengaja
dengan `// ponytail: ...` (sebut batas & jalur upgrade).

Output: kode dulu, lalu ≤3 baris (apa di-skip, kapan tambah). Pola:
`[code] → skipped: X, add when Y.`

Intensity: `lite` (sebut alternatif lebih malas 1 baris), `full` (ladder enforced, default),
`ultra` (YAGNI ekstrem, tantang sisa requirement).

JANGAN disederhanakan: validasi input di trust boundary, error handling cegah data loss,
security, accessibility, apa pun yang diminta eksplisit. Non-trivial logic (branch/loop/
parser/money/security) tinggalkan SATU runnable check (`assert`/`__main__`/test kecil).

======================================================================
## PART C — KNOWLEDGE & NOTES (Obsidian)
======================================================================
Vault filesystem-first: baca, cari, buat, edit catatan Markdown.

Vault path: resolusi `OBSIDIAN_VAULT_PATH` (dari `${HERMES_HOME:-~/.hermes}/.env`);
fallback `~/Documents/Obsidian Vault`. Resolve dulu ke path absolut sebelum pakai file tools
(path boleh mengandung spasi).

- Read: `read_file` (path absolut).
- List: `search_files` target=`files`, `pattern:"*.md"` di path vault/subfolder.
- Search: `search_files` target=`content`, `pattern` regex, `file_glob:"*.md"`.
- Create: `write_file` dengan konten markdown lengkap.
- Append/edit: `read_file` → `patch` (anchor stabil) atau `write_file` bila lebih jelas.
- Wikilinks: tautkan dengan `[[Note Name]]` saat membuat catatan.

Gunakan Obsidian untuk mendokumentasikan arsitektur dashboard, catatan audit, dan
SOP sekolah — lalu tautkan ke sesi kerja di Part A.

======================================================================
## Catatan Penggunaan
======================================================================
- Tiga pilar independen: pakai yang relevan. Mau CRUD akun → A1. Refactor kode → B.
  Catat temuan → C.
- Semua contoh generik (PHP/MySQL). Sesuaikan nama tabel/kolom dengan sistemmu.
- Keamanan & backup mutlak di Part A; jangan "ponytail" away validasi/backup.

======================================================================
## Reference & Template Files (di folder skill)
======================================================================
File pendukung siap pakai (copy-paste, lalu sesuaikan):

### references/
- `references/db_schema.sql` — skema contoh `tb_users`/`tb_siswa`/`tb_mapel`/
  `tb_hasil`/`tb_absen` (InnoDB, utf8mb4, FK). Dasar untuk Part A1/A2.
- `references/security_checklist.md` — checklist audit keamanan dashboard (Part A3).
  Centang tiap item sebelum rilis / setelah perubahan.
- `references/ponytail_examples.md` — before/after refactor kode sekolah (Part B).

### templates/
- `templates/user_crud.php` — template CRUD akun guru/staf (hash password, soft
  delete, guard role, reset password). Tambahkan CSRF per Part A3.
- `templates/report_nilai.sql` — query rekap nilai berbobot & absen (bobot dari DB).
- `templates/obsidian_note.md` — template catatan audit/SOP Obsidian (dengan wikilink).

Cara pakai: saat tugas masuk, baca file di atas via skill_manage(file_path=...) lalu
sesuaikan ke sistem sekolahmu.
