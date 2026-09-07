# Security Policy — Edu Dev Toolkit

Skill ini bertema keamanan sistem sekolah (akun, nilai, dashboard ujian).
Kami serius soal itu.

## Melapor kerentanan

JANGAN buka issue publik untuk kerentanan keamanan. Laporkan privately:
- Email: (isi bila ada) atau
- Telegram ke maintainer repo ini.

Berikan:
- Langkah reproduksi.
- Dampak (apa yang bisa terjadi).
- Saran perbaikan bila ada.

Kami akan merespons dalam waktu wajar dan merilis patch sebelum detail
dibuka ke publik.

## Standar keamanan yang dijaga di skill ini

- Password: selalu `password_hash()` (bcrypt). Tidak ada plaintext/MD5/SHA1
  tanpa salt.
- SQL: seluruh query pakai prepared statement. Tidak ada string interpolation.
- CSRF: token di semua mutasi POST, validasi via `hash_equals`.
- Session: `session_regenerate_id(true)` setelah login; idle timeout.
- Authorization: cek role di server, bukan cuma sembunyi tombol di UI.
- Token ujian: diverifikasi di server (PHP), bukan cek JS di client.

## Scope

Kerentanan yang berlaku: kode di `templates/` dan `references/` yang dapat
disalin ke sistem produksi sekolah. Template bersifat contoh — keamanan final
tetap tanggung jawab sistem yang mengintegrasikannya.
