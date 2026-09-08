# Security Audit & Hardening Sekolah — Multi-Stack (referensi nyata)

Referensi untuk Part I di SKILL.md utama. Berisi temuan & prosedur yang sudah
diverifikasi pada tiga sistem web sekolah Abu Seno (2026-09-08/09). Gunakan ini
sebagai contoh konkret saat mengaudit sistem serupa.

## Ringkasan temuan nyata per aplikasi

### 1. dashboard CBT — PHP native (`C:/laragon/www/dashboard`, db_ujian_sekolah)
- **C1 (HIGH) — bypass submit ujian.** `simpan_hasil.php` auto-set
  `$_SESSION['portal_role']='murid'` saat sesi kosong, lalu
  `Auth::guard(['murid','admin','guru'])` tanpa `isExamVerified()`. Siapa pun bisa
  POST jawaban/nilai ke `tb_hasil` tanpa login asli & tanpa token mapel. Fix: hapus
  auto-set role, wajib `Auth::guard` + `isExamVerified($id_mapel)` + bind `id_siswa`
  ke sesi.
- **C2 (MEDIUM) — baca draft siswa lain.** `get_draft.php`/`heartbeat.php` hanya
  `guard(['murid',...])`, tanpa `isExamVerified`. `get_draft.php?id_siswa=X` bisa
  dibaca siapa pun dengan sesi murid.
- **C3 (LOW) — XSS `arsip_soal.php`.** `$selected_category`/`$selected_mapel` dari
  GET di-`<?=` tanpa escape (baris 230, 259, 384, 471, 507, 508). Terbatas guru.
- **C4 (LOW) — `upload_max_filesize=2G` + `display_errors=On`** di php.ini.

Yang sudah aman (jangan re-flag): upload pakai finfo MIME whitelist,
`aksi.php` sekarang `guard(['guru','admin'])` + `requireCsrf()` + prepared
statement, router whitelist (no path traversal), nginx deny `.bak*`/`uploads/*.php`/`debug/`.

### 2. checklistharian — Laravel 11 + Filament 3 (`C:/laragon/www/checklistharian`)
- **M1 (MEDIUM) — `APP_DEBUG=true` + `APP_ENV=local` di prod.** Error page Laravel
  menampilkan stack trace/path/query env. Fix: di `C:/laragon/env/checklistharian.env`
  set `APP_ENV=production`, `APP_DEBUG=false` (env di-load di luar webroot via
  `bootstrap/app.php` → `chk_load_env()`).
- **M2 (LOW) — `autoindex on` di vhost `.test`** (hanya domain Laragon local).
- **M3 (LOW) — kredensial default di seeder** (`admin123`/`guru123`), tidak dipakai
  di DB live.
- **M4 (LOW) — `canAccessPanel()` return true** (authorization per-resource sudah ada).

Aman: `auth` middleware + `authorizeUser()` (abort 403) di semua controller report,
input di-clamp, CSRF/session otomatis Laravel.

### 3. dashboardadmin — Next.js 16 + Prisma (`C:/laragon/www/dashboardadmin`)
- **A1 (HIGH) — 14/14 server action tanpa auth.** Middleware Next hanya proteksi
  RENDER halaman, BUKAN server action. `getSiswa`, `createUser`, `deleteAllSiswa`
  bisa dipanggil tanpa login. Fix: helper `src/lib/require-auth.ts` (requireAuth +
  role guard), sisipkan `const _s = await requireAuth(); if(!_s) return {success:false,error:AUTH_DENIED_MSG};`
  di awal setiap action; role guard utk fungsi admin (`requireAuth(["admin"])`).
- **A2 (MEDIUM) — middleware cuma cek cookie ADA.** Harus verifikasi JWT
  (`jose.jwtVerify`) + redirect + hapus cookie basi.
- **A3 (LOW-MEDIUM) — JWT secret fallback hardcoded.** `process.env.JWT_SECRET ||
  "..."`. Fix: crash-loud bila env kosong.
- **Error Prisma (HIGH) — "Unknown field sumberBuku".** Client Prisma di bundle
  ketinggalan. Fix: `npx prisma generate` → `rm -rf .next` → `next build` → restart.

Aman: `.env` symlink ke luar webroot, cookie httpOnly/secure/sameSite, login bcrypt
+ Zod, `getSession()` jwtVerify.

## Prosedur fix yang aman (tervalidasi)
1. **Backup penuh**: `cp -r <app>/src C:/laragon/backups/<app>-<fix>/<TS>/src` +
   env. Verifikasi identik (`cmp`).
2. **PHP**: `php -l` tiap file. **Next**: `npx tsc --noEmit` lalu `npm run build`.
   **Laravel**: binary `C:/laragon/bin/php/php-8.3.32-Win32-vs16-x64/php.exe` artisan.
3. **Next restart**: kill PID port (`cmd /c "taskkill /F /PID <pid>"`) → start
   `background=true` → verifikasi `netstat :3100 LISTEN` + `curl /login` 200.
4. **Urutan Prisma benar**: `prisma generate` SEBELUM `rm -rf .next` + `next build`,
   lalu restart. Kalau "Unknown field" masih muncul, cek log fresh (bukan log lama).
5. **Bukti live**: domain publik via tunnel cloudflared → 200; halaman tanpa sesi →
   redirect login; log fresh 0 error. Konfirmasi ke user fix BENAR masuk live.

## Pitfalls Windows/Laragon (berulang)
- `php`/`mysql`/`node` tak di PATH di bash → pakai binary Laragon lengkap.
- `taskkill //F` (double slash) di MSYS berubah jadi path → gunakan
  `cmd /c "taskkill /F /PID <pid>"`.
- `next start` pastikan `background=true` (terminal), bukan `&`.
- Server dashboardadmin/node TIDAK auto-start setelah reboot — ingatkan pasang PM2 /
  Task Scheduler.
- Error yang "masih muncul" di log bisa jadi sisa log lama → hapus log & restart
  fresh untuk diagnosis yang benar.