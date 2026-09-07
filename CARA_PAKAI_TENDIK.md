# Cara Pakai Edu Dev Toolkit untuk Tendik (Non-Teknis)

Panduan ini untuk tenaga kependidikan (admin, operator sekolah) yang bukan
programmer. Tidak perlu paham coding. Ikuti langkah nomor saja.

---

## 1. Apa itu toolkit ini?

Kumpulan "cara kerja" untuk Hermes Agent supaya bisa bantu kerjaan sekolah:
tambah akun guru, rekap nilai, audit keamanan dashboard, bikin modul ajar
Kurikulum Merdeka, dan menjawab pertanyaan guru/siswa secara rasional.

Toolkit ini bukan aplikasi dengan tombol klik. Ia adalah "buku pintar" yang
dibaca Hermes saat kamu memberi perintah. Jadi kamu butuh Hermes sebagai
antarmukanya.

---

## 2. Prasyarat (sekali saja, biasanya sudah dibantu admin IT)

- Hermes Agent sudah terpasang (CLI di laptop, atau lewat Telegram).
- Folder `edu-dev-toolkit/` sudah ada di dalam folder `skills/` profil Hermes.
  Cara paling mudah: clone repo ini ke folder skills, atau copy foldernya.

```
# Contoh (minta admin IT kalau belum paham):
git clone https://github.com/yokagustiyadidev/edudevtoolkit.git \
  ~/.hermes/skills/edu-dev-toolkit
```

---

## 3. Cara pakai sehari-hari

Buka Hermes (chat Telegram ke bot, atau terminal CLI), lalu ketik perintah
dengan bahasa sehari-hari. Hermes akan otomatis memakai toolkit ini.

Contoh langsung:

    Tambah akun guru baru: nama Budi Santoso, username budi, role guru,
    password awal rahasia123.

    Buat rekap nilai mapel Matematika kelas VI A periode September 2026,
    export ke CSV.

    Reset password guru yang lupa: username siti.

    Audit keamanan dashboard ujian sekolah kami.

---

## 4. Malas mikir kata? Pakai prompt siap-salin

Buka file `references/prompt_tendik.md`. Di sana ada 10 blok perintah siap
pakai. Copy satu blok, ganti teks dalam [ ], lalu kirim ke Hermes. Selesai.

---

## 5. Hal yang harus diingat (keamanan)

- JANGAN kirim password asli, NIK, atau data pribadi siswa ke chat publik.
- Data sensitif tetap di server sekolah; Hermes hanya memproses perintah.
- Template butuh koneksi database yang sudah diatur admin IT di awal.
  Tendik tidak perlu mengatur sendiri.

---

## 6. Kalau bermasalah

- Hermes tidak paham perintah? Ulangi dengan kalimat lebih jelas, sebut
  mapel/kelas/nama dengan spesifik.
- Hasil tidak keluar? Pastikan folder skill sudah benar di `skills/`.
- Butuh fitur baru? Minta admin IT atau buat issue di GitHub repo ini.

---

Dokumentasi lengkap ada di `README.md` dan `SKILL.md`. Untuk tenaga kependidikan,
file ini dan `references/prompt_tendik.md` sudah cukup.
