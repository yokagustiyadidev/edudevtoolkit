# Cara Pakai Edu Dev Toolkit untuk Tendik (Non-Teknis)

Panduan ini untuk tenaga kependidikan (admin, operator sekolah) yang bukan
programmer. Tidak perlu paham coding. Ikuti langkah nomor saja.

---

## 1. Apa itu toolkit ini?

Kumpulan "cara kerja" untuk Hermes Agent supaya bisa bantu kerjaan sekolah:
tambah akun guru, rekap nilai, audit keamanan dashboard, bikin modul ajar
Kurikulum Merdeka, catat info dinas, peta struktur kode, remote hosting,
dan menjawab pertanyaan guru/siswa secara rasional.

Toolkit ini punya 10 pilar (A sampai J):

| Pilar | Untuk apa |
|-------|-----------|
| A — School Operations | Kelola akun, rekap nilai/absen, dashboard |
| B — Ponytail | Sederhanakan kode yang ruwet |
| C — Obsidian | Catat SOP/dokumentasi |
| D — Build Apps | Bikin aplikasi pembelajaran |
| E — Reasoning | Jawab pertanyaan guru/siswa |
| F — Kurikulum Merdeka | Rujukan kebijakan Kurmer |
| G — Info Dinas | Catat info dinas ke spreadsheet |
| H — Graphify | Peta hubungan kode sekolah |
| I — Security Audit | Audit keamanan multi-stack |
| J — Hostinger Remote | Kendalikan hosting via SSH |

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

    Catat info dinas: Surat edaran UN mendatang dari Kemendikdasmen.

    Buat graph dari folder dashboard untuk lihat file yang paling banyak dipakai.

    Cek status hosting sekolah via SSH alias hostinger.

---

## 4. Malas mikir kata? Pakai prompt siap-salin

Buka file `references/prompt_tendik.md`. Di sana ada 14 blok perintah siap
pakai (copy-paste ke Hermes, ganti teks dalam [ ]). Selesai.

---

## 5. Hal yang harus diingat (keamanan)

- JANGAN kirim password asli, NIK, atau data pribadi siswa ke chat publik.
- Data sensitif tetap di server sekolah; Hermes hanya memproses perintah.
- Template butuh koneksi database yang sudah diatur admin IT di awal.
  Tendik tidak perlu mengatur sendiri.
- Untuk SSH/hosting (Part J): kredensial sudah disimpan di laptop (key-based).
  Tidak perlu ketik password di chat. Cukup sebut "ssh hostinger" atau pakai
  prompt no. 14.

---

## 6. Kalau bermasalah

- Hermes tidak paham perintah? Ulangi dengan kalimat lebih jelas, sebut
  mapel/kelas/nama dengan spesifik.
- Hasil tidak keluar? Pastikan folder skill sudah benar di `skills/`.
- Script info dinas error? Cek: file Excel sedang dibuka di aplikasi lain
  (tutup dulu), atau install openpyxl (`pip install openpyxl`).
- Scraper dinas tidak ketemu item? Struktur situs mungkin berubah — minta
  admin IT kalibrasi ulang selektor di `dinas_sources.json`.
- Butuh fitur baru? Minta admin IT atau buat issue di GitHub repo ini.

---

Dokumentasi lengkap ada di `README.md` dan `SKILL.md`. Untuk tenaga kependidikan,
file ini dan `references/prompt_tendik.md` sudah cukup.
