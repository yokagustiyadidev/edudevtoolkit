# Security Checklist — Dashboard Sekolah (Part A3 + Part I)

Audit dashboard sebelum rilis / setelah perubahan. Centang tiap item.
Berlaku lintas stack: PHP native, Laravel, Next.js.

## Autentikasi & Sesi
- [ ] `session_regenerate_id(true)` dipanggil SETELAH login sukses (anti session fixation) — PHP
- [ ] Idle timeout aktif (mis. 30 menit) — sesi guru/admin tidak awet terus
- [ ] Password disimpan dengan `password_hash()` (PHP) / bcrypt (Laravel/Next) — bukan plaintext/MD5/SHA1 tanpa salt
- [ ] Reset password menghash ulang & men-set `must_change_pw=1`
- [ ] Role dicek di server (`Auth::guard(['admin','guru'])` PHP / `auth` middleware Laravel / `requireAuth()` Next.js), bukan cuma sembunyi tombol di UI
- [ ] **Next.js khusus**: middleware verifikasi JWT (`jose.jwtVerify`), bukan cuma cek cookie ADA. Server actions WAJIB mulai dengan `requireAuth()`. Middleware tidak proteksi server action.

## CSRF & Input
- [ ] Token CSRF dihasilkan (`bin2hex(random_bytes(32))`) & divalidasi di semua POST — PHP native
- [ ] CSRF otomatis Laravel (`@csrf` di form, `VerifyCsrfToken` middleware) — cek tidak di-disable
- [ ] GET tidak mengubah state (unsafe method ditolak / dilewati CSRF)
- [ ] Input numerik di-cast `(int)`; string di-escape / prepared statement
- [ ] Token ujian diverifikasi SERVER-SIDE (PHP), bukan cek JS di client (mudah bypass)
- [ ] **Next.js**: server action validasi input dengan Zod/schema sebelum proses
- [ ] **Laravel**: input di-clamp/validate via FormRequest, bukan langsung `$request->all()`

## Otorisasi (least privilege)
- [ ] `admin`: user / mapel / token / rekap / backup
- [ ] `guru`: CRUD materi & soal sendiri, mulai ujian, koreksi, rekap — TIDAK ubah user lain
- [ ] `staf`: rekap / absen saja — TIDAK ubah soal / token
- [ ] Eskalasi guru → admin butuh konfirmasi eksplisit
- [ ] **Laravel**: controller report pakai `authorizeUser()` (abort 403), bukan cuma `auth`
- [ ] **Next.js**: role guard di server action (`requireAuth(["admin"])`) untuk fungsi admin

## SQL Injection
- [ ] PHP native: prepared statement (`mysqli_prepare`/`bind_param` atau PDO) — TIDAK ada interpolasi `"...$_GET..."`
- [ ] Laravel: Eloquent/Query Builder sudah parameterized — cek tidak ada `DB::raw()` dengan input mentah
- [ ] Next.js: Prisma parameterized — cek tidak ada `$queryRaw` dengan input mentah
- [ ] Cek: `grep -rnE '\b(mysqli_query|->query)\s*\(\$conn, ".*\$_(GET|POST)' public/`

## XSS
- [ ] PHP: echo `$_GET/$_POST` wajib `htmlspecialchars` — cek short-echo `<?=`
- [ ] Laravel: Blade `{{ }}` auto-escape — cek `{!! !!}` (raw) hanya untuk data terpercaya
- [ ] Next.js: React auto-escape — cek `dangerouslySetInnerHTML`

## RCE / File Upload
- [ ] Upload pakai `finfo` MIME whitelist + whitelist ext + rename `uniqid()` — bukan trust ext dari user
- [ ] Nginx/Apache: deny `.php` di folder uploads
- [ ] Laravel: validation `mimes:` + store dengan nama generated

## Secret & Config Leak
- [ ] `.env`/config di luar webroot (PHP: `C:/laragon/env/`, Next: symlink ke luar)
- [ ] TIDAK ada JWT secret fallback hardcoded (`process.env.JWT_SECRET || "..."`) — crash-loud bila env kosong
- [ ] TIDAK ada API key/password di source code / git history
- [ ] `.bak`/`.orig`/`.sql` tidak ada di webroot — deny di nginx
- [ ] `APP_DEBUG=true` / `display_errors=On` → set ke `false`/`Off` di production
- [ ] Laravel: `APP_ENV=production` di env live

## Data & Backup
- [ ] Backup `tb_hasil` & `tb_users` SEBELUM modifikasi massal
- [ ] Soft delete (`status=0`) untuk nonaktif user, bukan hard delete
- [ ] Verifikasi baris before/after setiap perubahan data
- [ ] Deploy lewat staging bila memungkinkan, lalu konfirmasi masuk live

## Operasional
- [ ] Setiap perubahan dicatat (siapa / apa / kapan) — audit log
- [ ] Rollback terbukti bisa (tes restore dari backup)
- [ ] **Next.js**: `prisma generate` → `rm -rf .next` → `next build` → restart (urutan wajib)
- [ ] **Windows/Laragon**: pakai binary lengkap (`C:/laragon/bin/php/php-8.3.../php.exe`), bukan `php` di PATH
- [ ] Server Node/Next TIDAK auto-start setelah reboot — pasang PM2/Task Scheduler
