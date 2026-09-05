# Edu Dev Toolkit

Toolkit terpadu untuk **pendidik yang merawat sistem web sekolah DAN membantu proses
belajar-mengajar**. Enam pilar dalam satu skill:

| Pilar | Isi |
|-------|-----|
| **Part A — School Operations** | CRUD akun guru/staf, rekap nilai/absen, dashboard runbook & baseline keamanan |
| **Part B — Build Simply (Ponytail)** | Filosofi kode paling pendek yang tetap bekerja (YAGNI, stdlib dulu) |
| **Part C — Knowledge & Notes (Obsidian)** | Baca/cari/buat/edit catatan di vault Obsidian |
| **Part D — Building Educational Apps** | Rancang & bangun aplikasi/web pembelajaran simpel & berdampak |
| **Part E — Reasoning & Thinking** | Berpikir terstruktur, jawab pertanyaan pedagogik & teknis dengan relevan |
| **Part F — Kurikulum Merdeka (Indonesia)** | Rujukan kebijakan, struktur, & implementasi Kurmer |

Contoh kasus: kelola akun guru, buat rekap nilai, audit keamanan dashboard, refactor
kode sekolah, dokumentasikan SOP, bangun aplikasi pembelajaran, jawab pertanyaan guru/
siswa secara rasional, atau menjawab soal seputar Kurikulum Merdeka.

## Struktur

```
edu-dev-toolkit/
├── SKILL.md                      # Panduan utama (6 pilar)
├── LICENSE                      # MIT
├── README.md                    # File ini
├── references/
│   ├── db_schema.sql            # Skema tb_users / tb_siswa / tb_mapel / tb_hasil / tb_absen
│   ├── security_checklist.md    # Checklist audit keamanan dashboard
│   ├── ponytail_examples.md     # Contoh refactor kode sekolah (before/after)
│   ├── kurikulum_merdeka.md     # Ringkasan konsep & istilah Kurmer (Part F)
│   └── build_app_checklist.md   # Checklist rancang & bangun aplikasi edukasi (Part D)
└── templates/
    ├── user_crud.php            # Template CRUD akun guru/staf
    ├── report_nilai.sql         # Query rekap nilai berbobot & absen
    ├── obsidian_note.md         # Template catatan audit/SOP Obsidian
    └── modul_ajar.md            # Template modul ajar / TP Kurikulum Merdeka (Part F)
```

## Cara Pakai (di Hermes Agent)

1. Letakkan folder `edu-dev-toolkit/` di dalam direktori `skills/` profil Hermes
   (mis. `~/.hermes/skills/edu-dev-toolkit/`).
2. Skill otomatis ke-load saat tugas terkait muncul (kelola akun, laporan, audit,
   refactor kode sekolah, catatan Obsidian, bangun app, Kurikulum Merdeka).
3. Saat butuh detail, Hermes membaca file di `references/` dan `templates/`.

## Catatan

- Semua contoh **generik** (PHP/MySQL). Sesuaikan nama tabel/kolom dengan sistemmu.
- Keamanan & backup mutlak di Part A — jangan "ponytail away" validasi/backup.
- Part E berlaku untuk semua pilar: jawab langsung, beri langkah konkret, sebut batas.
- Aturan Kurikulum Merdeka dapat berubah; verifikasi ke platform resmi Kemdikbud
  sebelum memberi angka/aturan pasti. Skill ini ringkasan, bukan pengganti regulasi.
- Lisensi: MIT. Bebas dipakai, dimodifikasi, dan didistribusikan.

## Kontribusi

Pull request terbuka. Tambahkan `reference`/`template` bila memperluas cakupan
pendidikan & pengembangan web sekolah.
