# Prompt Siap-Salin untuk Tenaga Kependidikan (Tendik)

File ini buat tendik / admin sekolah yang bukan programmer. Tidak perlu paham
teknis — cukup salin satu blok di bawah ke chat Hermes, lalu isi bagian dalam
kurung [ ]. Hermes akan memakai skill `edu-dev-toolkit` secara otomatis.

Aturan tulis: ganti teks dalam [ ] dengan data sekolahmu. Jangan hapus tanda [ ].

======================================================================
## 1. Tambah akun guru / staf baru
----------------------------------------------------------------------
Salin ke Hermes:

    Tambah akun untuk [Nama Lengkap] dengan username [user_login],
    role [guru/staf/admin], password awal [rahasia123].
    Pakai template user_crud.php dari skill edu-dev-toolkit.
    Setelah dibuat, beri tahu user untuk ganti password saat login pertama.

======================================================================
## 2. Nonaktifkan akun (guru resign / pindah)
----------------------------------------------------------------------
Salin ke Hermes:

    Nonaktifkan akun [username atau nama] karena [alasan: resign/pindah tugas].
    Pakai soft delete (status=0) dari skill edu-dev-toolkit, jangan hapus datanya.
    Backup dulu sebelum ubah.

======================================================================
## 3. Reset password guru yang lupa
----------------------------------------------------------------------
Salin ke Hermes:

    Reset password untuk [username atau nama]. Generate password sementara,
    set must_change_pw=1, lalu kasih tahu password sementaranya lewat WA/onsite.
    Pakai template user_crud.php (skill edu-dev-toolkit).

======================================================================
## 4. Bikin rekap nilai per kelas (CSV/PDF untuk wali murid)
----------------------------------------------------------------------
Salin ke Hermes:

    Buat rekap nilai mapel [Nama Mapel] untuk kelas [VI A] periode [Sept 2026].
    Ambil dari tb_hasil + tb_siswa + tb_mapel (bobot dari DB, jangan hardcode).
    Output: rata-rata per siswa + jumlah soal PG/isian/essay + skor berbobot.
    Export ke CSV. Pakai query di templates/report_nilai.sql (skill edu-dev-toolkit).

======================================================================
## 5. Bikin rekap absen per periode
----------------------------------------------------------------------
Salin ke Hermes:

    Rekap absen kelas [VI A] dari tanggal [01-09-2026] sampai [30-09-2026].
    Hitung hadir / izin / sakit / alpa per siswa. Output CSV.
    Pakai query no.3 di templates/report_nilai.sql (skill edu-dev-toolkit).

======================================================================
## 6. Audit keamanan dashboard sekolah
----------------------------------------------------------------------
Salin ke Hermes:

    Audit keamanan dashboard ujian sekolah kami. Cek: password sudah hash?
    CSRF di POST? token ujian diverifikasi di server? session regenerate setelah
    login? soft delete untuk user? Pakai security_checklist.md dari skill
    edu-dev-toolkit, beri laporan centang-item + apa yang masih kurang.

======================================================================
## 7. Bikin modul ajar Kurikulum Merdeka
----------------------------------------------------------------------
Salin ke Hermes:

    Buat draft modul ajar Kurmer untuk mapel [Informatika] kelas [VI],
    elemen [Berpikir Komputasional], 2 pertemuan. Sertakan TP, kegiatan,
    LKPD, dan rubrik penilaian. Pakai templates/modul_ajar.md sebagai kerangka,
    dan contoh nyatanya ada di templates/Modul_Ajar_Informatika_Kelas6.docx.

======================================================================
## 8. Dokumentasikan SOP / cara kerja sistem di Obsidian
----------------------------------------------------------------------
Salin ke Hermes:

    Tulis catatan SOP untuk [nama proses, mis. "cara reset password guru"]
    ke vault Obsidian, pakai templates/obsidian_note.md. Sertakan langkah,
    siapa yang berwenang, dan link ke catatan terkait.

======================================================================
## 9. Rapikan kode sistem sekolah yang ruwet
----------------------------------------------------------------------
Salin ke Hermes:

    Ini kode fitur [nama fitur] dari web sekolah kami:

    [tempel kode di sini]

    Sederhanakan menurut prinsip Ponytail (skill edu-dev-toolkit Part B):
    hapus yang tidak perlu, pakai stdlib/fitur native, jangan tambah dependency.
    Jelaskan apa yang di-skip dan kapan perlu ditambah lagi.

======================================================================
## 10. Tanya kebijakan Kurikulum Merdeka
----------------------------------------------------------------------
Salin ke Hermes:

    Jelaskan [CP / TP / ATP / P5 / rapor narasi] dalam Kurikulum Merdeka
    untuk guru kelas [VI]. Bahasa sederhana, beri contoh konkret.
    Rujuk references/kurikulum_merdeka.md (skill edu-dev-toolkit).
    Ingatkan untuk verifikasi ke platform resmi Kemdikbud.

======================================================================
CATATAN KEAMANAN (baca sebelum pakai):
- Jangan tempel password asli / NIK / data siswa ke chat publik.
- Prompt di atas hanya instruksi ke Hermes; data sensitif tetap di server sekolah.
- File skill ini GENERIK — sesuaikan nama tabel/kolom dengan sistemmu.
