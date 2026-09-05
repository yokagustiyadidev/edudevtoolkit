# Build App Checklist — Aplikasi Edukasi (Part D)

Centang sebelum & sesudah membangun fitur/aplikasi pembelajaran. Gandeng Part B
(Ponytail) agar tidak over-engineered.

## Sebelum Bangun
- [ ] Masalah nyata diidentifikasi (guru/siswa butuh apa? bukan "fitur keren")
- [ ] Scope 1 paragraf: input → proses → output
- [ ] Tabel/data sketsa siap (rujuk `references/db_schema.sql`)
- [ ] Stack = yang dikuasai sekolah (PHP native + MySQL di sini) — bukan tren baru
- [ ] UI untuk non-teknis: tombol besar, alur linear, bahasa guru/SD

## Saat Bangun (MVP)
- [ ] 1 halaman kerja dulu > 5 halaman setengah jadi
- [ ] Pakai stdlib/native dulu (Ponytail rung 2-3)
- [ ] Tanpa abstraksi tak perlu (factory/interface untuk 1 implementasi = skip)
- [ ] Validasi input di boundary (jangan "ponytail away" security)

## Sesudah Bangun
- [ ] Uji dengan 1 siswa nyata (bukan 100 test palsu)
- [ ] Backup data sebelum deploy (Part A3 runbook)
- [ ] Deploy staging → konfirmasi live
- [ ] Catat di audit log / Obsidian (Part C)

## Contoh fitur siap bangun
- Kuis interaktif (PG/isian/essay) → simpan di `tb_hasil`
- Game edukatif (ular tangga/kuis papan) → skor di `tb_hasil`
- Rekap nilai otomatis + export PDF/CSV (Part A2)
- Modul P5 / profil pelajar (Part F) → tampil di dashboard

## Pitfalls
- LMS lengkap padahal butuh 1 form (YAGNI).
- Ganti framework hanya demi tren → tak ada yang bisa rawat.
- UI buat developer, bukan guru SD.
