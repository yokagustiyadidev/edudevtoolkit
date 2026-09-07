# Contributing — Edu Dev Toolkit

Terima kasih mau menyumbang. Skill ini untuk tenaga kependidikan Indonesia,
jadi kontribusi harus tetap sederhana dan langsung berguna (prinsip Ponytail:
solusi paling pendek yang tetap bekerja).

## Cara mulai

1. Fork repo ini.
2. Clone fork ke lokal: `git clone <fork-url>`
3. Buat branch per fitur/perbaikan: `git checkout -b fix/nama-perubahan`
   Jangan edit langsung di `main`.
4. Commit dengan pesan jelas (bahasa Indonesia atau Inggris, konsisten).
5. Push branch, lalu buka Pull Request ke `main`.

## Standar wajib

- **Template PHP**: wajib prepared statement (`mysqli_prepare`/`PDO`), token
  CSRF di tiap mutasi POST, password pakai `password_hash()`. Tidak ada
  interpolasi string mentah ke query. Skill ini bertema keamanan — contoh
  kode tidak boleh vulnerable.
- **Kurikulum Merdeka**: rujukan ke platform resmi Kemdikbud
  (merdekamengajar.kemdikbud.go.id). Jangan mencantumkan angka/aturan pasti
  tanpa catatan "verifikasi ke platform resmi".
- **Bahasa**: konten pengguna akhir berbahasa Indonesia. Komentar kode bisa
  Indonesia/Inggris, asal konsisten per file.
- **Generic**: contoh tabel/kolom generik (`tb_users`, `tb_hasil`). Jangan
  hardcode ke sistem sekolah tertentu kecuali sebagai contoh hasil (lihat
  `templates/Modul_Ajar_Informatika_Kelas6.docx`).
- **Dokumentasi**: setiap file baru di `references/` atau `templates/` wajib
  dicantumkan di `SKILL.md` dan `README.md` (struktur tree).

## Review checklist (reviewer)

- [ ] Tidak ada SQL injection (prepared statement).
- [ ] CSRF & session guard untuk mutasi.
- [ ] README/SKILL.md sudah sync daftar file.
- [ ] Tidak ada file yatim (tidak dirujuk dokumentasi).
- [ ] Bahasa & gaya konsisten.

## Lisensi

Dengan berkontribusi, kamu setuju karyamu dirilis di bawah lisensi MIT (lihat
`LICENSE`).
