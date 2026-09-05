# Security Checklist — Dashboard Sekolah (Part A3)

Audit dashboard sebelum rilis / setelah perubahan. Centang tiap item.

## Autentikasi & Sesi
- [ ] `session_regenerate_id(true)` dipanggil SETELAH login sukses (anti session fixation)
- [ ] Idle timeout aktif (mis. 30 menit) — sesi guru/admin tidak awet terus
- [ ] Password disimpan dengan `password_hash()` (bukan plaintext / MD5 / SHA1 tanpa salt)
- [ ] Reset password menghash ulang & men-set `must_change_pw=1`
- [ ] Role dicek di server (`Auth::guard(['admin','guru'])`), bukan cuma sembunyi tombol di UI

## CSRF & Input
- [ ] Token CSRF dihasilkan (`bin2hex(random_bytes(32))`) & divalidasi di semua POST
- [ ] GET tidak mengubah state (unsafe method ditolak / dilewati CSRF)
- [ ] Input numerik di-cast `(int)`; string di-escape / prepared statement
- [ ] Token ujian diverifikasi SERVER-SIDE (PHP), bukan cek JS di client (mudah bypass)

## Otorisasi (least privilege)
- [ ] `admin`: user / mapel / token / rekap / backup
- [ ] `guru`: CRUD materi & soal sendiri, mulai ujian, koreksi, rekap — TIDAK ubah user lain
- [ ] `staf`: rekap / absen saja — TIDAK ubah soal / token
- [ ] Eskalasi guru → admin butuh konfirmasi eksplisit

## Data & Backup
- [ ] Backup `tb_hasil` & `tb_users` SEBELUM modifikasi massal
- [ ] Soft delete (`status=0`) untuk nonaktif user, bukan hard delete
- [ ] Verifikasi baris before/after setiap perubahan data
- [ ] Deploy lewat staging bila memungkinkan, lalu konfirmasi masuk live

## Operasional
- [ ] Setiap perubahan dicatat (siapa / apa / kapan) — audit log
- [ ] Rollback terbukti bisa (tes restore dari backup)
