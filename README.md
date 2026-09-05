# Edu Dev Toolkit

Toolkit terpadu untuk **pendidik yang merawat sistem web sekolah**: operasikan data
sekolah, bangun fitur dengan cara paling simpel, dan dokumentasikan pengetahuan.

Skill ini menggabungkan tiga pilar menjadi satu:

| Pilar | Isi |
|-------|-----|
| **Part A — School Operations** | CRUD akun guru/staf, rekap nilai/absen, dashboard runbook & baseline keamanan |
| **Part B — Build Simply (Ponytail)** | Filosofi kode paling pendek yang tetap bekerja (YAGNI, stdlib dulu) |
| **Part C — Knowledge & Notes (Obsidian)** | Baca/cari/buat/edit catatan di vault Obsidian |

Contoh kasus: kelola akun guru, buat rekap nilai, audit keamanan dashboard,
tulis/menyederhanakan kode fitur sekolah, atau dokumentasikan SOP di Obsidian.

## Struktur

```
edu-dev-toolkit/
├── SKILL.md                    # Panduan utama (3 pilar)
├── LICENSE                    # MIT
├── README.md                  # File ini
├── references/
│   ├── db_schema.sql           # Skema tb_users / tb_siswa / tb_mapel / tb_hasil / tb_absen
│   ├── security_checklist.md   # Checklist audit keamanan dashboard
│   └── ponytail_examples.md    # Contoh refactor kode sekolah (before/after)
└── templates/
    ├── user_crud.php           # Template CRUD akun guru/staf
    ├── report_nilai.sql        # Query rekap nilai berbobot & absen
    └── obsidian_note.md        # Template catatan audit/SOP Obsidian
```

## Cara Pakai (di Hermes Agent)

1. Letakkan folder `edu-dev-toolkit/` di dalam direktori `skills/` profil Hermes
   (mis. `~/.hermes/skills/edu-dev-toolkit/`).
2. Skill otomatis ke-load saat tugas terkait muncul (kelola akun, laporan, audit,
   refactor kode sekolah, catatan Obsidian).
3. Saat butuh detail, Hermes membaca file di `references/` dan `templates/`.

## Catatan

- Semua contoh **generik** (PHP/MySQL). Sesuaikan nama tabel/kolom dengan sistemmu.
- Keamanan & backup mutlak di Part A — jangan "ponytail away" validasi/backup.
- Lisensi: MIT. Bebas dipakai, dimodifikasi, dan didistribusikan.

## Kontribusi

Pull request terbuka. Tambahkan `reference`/`template` bila memperluas cakupan
pendidikan & pengembangan web sekolah.
