---
name: edu-dev-toolkit
description: "Educator toolkit: school ops, build apps, reasoning, Kurikulum Merdeka."
version: "2.0.0"
author: Hermes Agent
license: MIT
hermes:
  tags: [education, school, users, report, dashboard, ponytail, obsidian, notes, build, reasoning, kurikulum-merdeka]
  related_skills: []
metadata:
  hermes:
    tags: [education, school, users, report, dashboard, ponytail, obsidian, notes, build, reasoning, kurikulum-merdeka]
    related_skills: []
category: edu-dev
---

# Edu Dev Toolkit

Toolkit terpadu untuk pendidik yang merawat sistem web sekolah DAN membantu proses
belajar-mengajar. Enam pilar:

- **Part A — School Operations**: kelola akun guru/staf, buat laporan, jalankan dashboard aman.
- **Part B — Build Simply (Ponytail)**: filosofi kode paling pendek yang tetap bekerja.
- **Part C — Knowledge & Notes (Obsidian)**: simpan & cari catatan di vault.
- **Part D — Building Educational Apps**: rancang & bangun aplikasi/web pembelajaran simpel & berdampak.
- **Part E — Reasoning & Thinking**: berpikir terstruktur, jawab pertanyaan pedagogik & teknis dengan relevan.
- **Part F — Kurikulum Merdeka (Indonesia)**: rujukan saat ditanya kebijakan, struktur, & implementasi Kurmer.

Gunakan saat: mengelola akun sekolah, membuat rekap nilai/absen, mengaudit keamanan
dashboard, menulis/menyederhanakan kode fitur sekolah, mendokumentasikan sistem,
membangun aplikasi pembelajaran, menjawab pertanyaan guru/siswa secara rasional, atau
menjawab soal seputar Kurikulum Merdeka.

## When to Use
- Mengelola akun guru/staf, reset password, nonaktifkan user (Part A1).
- Membuat rekap nilai/absen atau export laporan (A2).
- Menjalankan dashboard per role atau audit keamanan (A3).
- Menulis/menyederhanakan kode sistem sekolah (Part B / Ponytail).
- Mendokumentasikan arsitektur/SOP/audit di vault (Part C / Obsidian).
- Merancang/membangun aplikasi atau fitur pembelajaran (Part D).
- Menjawab pertanyaan guru/siswa dengan penalaran jelas & relevan (Part E).
- Menjawab pertanyaan seputar Kurikulum Merdeka (Part F).

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
## PART D — BUILDING EDUCATIONAL APPS
======================================================================
Membangun aplikasi/fitur pembelajaran yang simpel, berdampak, dan mudah dirawat.
Gabungkan dengan Part B (Ponytail) agar tidak over-engineered.

### Prinsip
- Mulai dari masalah nyata guru/siswa, bukan fitur yang "keren". Ukur dulu, bangun
  sesudahnya. (Ponytail rung 1: perlu ada?)
- Satu fitur = satu alur kerja. Jangan gabungkan modul yang tak berkaitan.
- Gunakan stack yang sudah dikuasai sekolah (di kasus ini: PHP native + MySQL/Laragon).
  Jangan pindah framework hanya demi tren.
- UI jelas untuk pengguna non-teknis: guru & siswa SD. Hindari jargon, tombol besar,
  alur linear.

### Siklus build (ringkas)
1. **Tentukan scope**: input → proses → output. Tulis 1 paragraf.
2. **Sketsa data**: tabel apa yang perlu ada (rujuk `references/db_schema.sql`).
3. **Bangun MVP**: 1 halaman kerja > 5 halaman setengah jadi.
4. **Uji dengan data nyata**: 1 siswa beneran > 100 baris unit test palsu.
5. **Deploy staging → live** (ikuti runbook Part A3).

### Contoh fitur edukasi siap bangun
- Kuis interaktif per mapel (PG/isian/essay) — lihat `templates/user_crud.php` pola.
- Game edukatif (ular tangga, kuis papan) — motifasi siswa, simpan skor di `tb_hasil`.
- Rekap nilai otomatis (Part A2) dengan export PDF/CSV untuk wali murid.
- Modul projek penguatan profil pelajar (Pancasila) — lihat Part F.

### Pitfalls
- Bangun LMS lengkap padahal butuh cuma 1 form. (YAGNI)
- Stack baru yang tak ada yang bisa rawat di sekolah.
- UI dibuat untuk developer, bukan guru SD.

======================================================================
## PART E — REASONING & THINKING
======================================================================
Berpikir terstruktur & memberi jawaban relevan saat guru/siswa bertanya — baik soal
pedagogik maupun teknis. Hindari jawaban normatif yang tak berguna.

### Kerangka jawab (saat ditanya)
1. **Klarifikasi konteks** singkat bila ambigu (kelas? mapel? tujuan?). Jangan tebak
   langsung bila salah arah merugikan.
2. **Pisahkan fakta vs opini**. Kalau kebijakan (mis. Kurmer), sebut sumber/landasan.
3. **Berikan jawaban langsung dulu**, lalu penjelasan. Jangan berputar sebelum poin.
4. **Berikan langkah konkret** (bukan "sebaiknya"). Kalau bisa jadi kode/query/template,
   berikan.
5. **Sebut batasan** — kapan pendekatan ini salah, apa yang tak dicover.

### Pola penalaran
- **Cause→Effect**: "X terjadi karena Y, maka perbaikinya dengan Z."
- **Trade-off**: "Opsi A lebih simpel tapi X; opsi B cover X tapi lebih berat. Untuk
  sekolah kecil, pilih A."
- **First-principles**: turunkan dari tujuan belajar, bukan dari apa yang sudah ada.

### Jangan
- Jawab "tergantung" tanpa memberi kriteria keputusan.
- Beri validasi kosong ("ide bagus!") tanpa substansi.
- Campur opini tak berbasis bukti ke dalam fakta kebijakan.

### Untuk siswa (penjelasan sederhana)
Gunakan analogi kehidupan nyata, kalimat pendek, hindari istilah asing tanpa penjelasan.
Sesuai tahap SD/SMP.

======================================================================
## PART F — KURIKULUM MERDEKA (INDONESIA)
======================================================================
Rujukan saat ditanya kebijakan, struktur, & implementasi Kurikulum Merdeka (Kurmer).
Gunakan dengan Part E (reasoning) — beri jawaban berbasis landasan, bukan asumsi.

### Konsep kunci (fakta, bukan opini)
- **Paradigma**: dari konten sentral ke **kompetensi & profil pelajar Pancasila**.
- **Pembelajaran**: berbasis **projek** (P5 = Projek Penguatan Profil Pelajar Pancasila),
  bukan hanya mata pelajaran kognitif.
- **Inti struktur**:
  - **CP** (Capaian Pembelajaran) — apa yang diharapkan capai di akhir fase.
  - **TP** (Tujuan Pembelajaran) — turunan harian/mingguan dari CP.
  - **ATP** (Alur Tujuan Pembelajaran) — urutan capaian per fase.
  - **Modul Ajar** & **Elemen Capaian** per mata pelajaran.
- **Fase**, bukan kelas: Fase A (RA), B (SD 1-2), C (SD 3-4), D (SD 5-6), E (SMP), F (SMA).
- **Rapor**: narasi + profil pelajar, bukan cuma angka. Asesmen formatif > sumatif.
- **Platform resmi**: [Merdeka Mengajar](https://merdekamengajar.kemdikbud.go.id),
  [PMM /kurikulum.kemdikbud.go.id](https://kurikulum.kemdikbud.go.id).

### Saat guru bertanya "bagaimana menerapkan X di Kurmer"
1. Petakan ke CP/TP mata pelajaran & fase terkait.
2. Sarankan projek nyata (P5) bila memungkinkan — belajar lewat pengalaman.
3. Untuk asesmen: pakai formatif, beri umpan balik, jangan cuma angka.
4. Hindari "menghapus K13 langsung" — transisi bertahap, sekolah bisa pilih
   (Kurmer/Mandiri, Mandiri Berubah, Mandiri Berbagi, dll).

### Bantuan teknis untuk Kurmer
- Template modul ajar & TP bisa didokumentasikan di Obsidian (Part C).
- Rekap projek P5 → simpan di `tb_hasil` dengan `tipe_soal='essay'`/projek (rujuk A2).
- Aplikasi sekolah (dashboard/nilai) tetap relevan: tampilkan profil pelajar, bukan
  hanya nilai angka (lihat Part D).

### Batasan
- Aturan Kurmer bisa berubah per regulasi Kemdikbud. Verifikasi ke platform resmi
  sebelum memberi angka pasti ke guru. Skill ini ringkasan, bukan pengganti regulasi.

======================================================================
## Catatan Penggunaan
======================================================================
- Enam pilar independen: pakai yang relevan. CRUD akun → A1. Refactor → B. Catat → C.
  Bangun app → D. Jawab pertanyaan → E. Kurmer → F.
- Semua contoh generik (PHP/MySQL). Sesuaikan nama tabel/kolom dengan sistemmu.
- Keamanan & backup mutlak di Part A; jangan "ponytail" away validasi/backup.
- Part E berlaku untuk semua pilar: jawab langsung, beri langkah konkret, sebut batas.

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
- `references/kurikulum_merdeka.md` — ringkasan konsep & istilah Kurmer untuk rujukan cepat (Part F).
- `references/build_app_checklist.md` — checklist rancang & bangun aplikasi edukasi (Part D).

### templates/
- `templates/user_crud.php` — template CRUD akun guru/staf (hash password, soft
  delete, guard role, reset password). Tambahkan CSRF per Part A3.
- `templates/report_nilai.sql` — query rekap nilai berbobot & absen (bobot dari DB).
- `templates/obsidian_note.md` — template catatan audit/SOP Obsidian (dengan wikilink).
- `templates/modul_ajar.md` — template modul ajar / TP Kurikulum Merdeka (Part F).

Cara pakai: saat tugas masuk, baca file di atas via skill_manage(file_path=...) lalu
sesuaikan ke sistem sekolahmu.
