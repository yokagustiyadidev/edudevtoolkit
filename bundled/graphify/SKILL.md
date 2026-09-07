---
name: graphify
description: "Turn any folder (code/docs/notes) into a navigable knowledge graph with community detection, honest edge audit, and interactive HTML + JSON + report. Adapted for Hermes (stdlib only, no pip/PyPI). Use when user says 'graphify', 'buat graph dari folder', 'peta hubungan kode', 'knowledge graph', or wants to see structure/connections in a directory."
version: "1.0.0-hermes"
author: Hermes Agent (adapted from Graphify-Labs/graphify)
license: MIT
hermes:
  tags: [knowledge-graph, visualization, code-analysis, docs, graphify, structure]
  related_skills: [edu-dev-toolkit]
category: software-development
---

# graphify (Hermes-adapted)

Ubah folder berisi kode / dokumen / catatan menjadi **knowledge graph** dengan:
- **Node**: file + simbol (function/class/def) + heading dokumen + external module + URL.
- **Edge EXTRACTED** (pasti): import/include/require, link markdown, relasi defines/contains.
- **Edge INFERRED** (`--mode deep`): ko-okurensi keyword penting (CamelCase/UPPER_SNAKE) lintas file.
- **Community detection**: union-find (connected components) — komunitas = cluster file terhubung.
- **Audit jujur**: tiap edge ditag `EXTRACTED` / `INFERRED` / `AMBIGUOUS`.

Output (ke `graphify-out/`):
- `graph.json` — graph persisten (query weeks later).
- `graph.html` — interaktif **constellation** (Canvas): bintang = node, garis = edge, latar bintang berkelip.
  Posisi node **statis** (tidak bergerak sendiri) supaya file tetap dikenali; label nama muncul
  saat **hover / zoom-in (>1.4x) / ketik search / node besar (god node)**. Buka di browser.
- `GRAPH_REPORT.md` — god nodes, komunitas terbesar, audit edge, pertanyaan yang bisa dijawab.

## Kapan pakai
- "Buat graph/peta dari folder ini", "lihat hubungan antar file kode", "apa saja modul yang saling import".
- "(Claude Code) /graphify <path>" — kalau user pakai istilah itu, jalankan di sini.
- Audit struktur repo sebelum refactor; temukan god node & komunitas terisolasi.

## Cara jalankan (Hermes)
Script ada di folder skill: `graphify/graphify.py` (Python stdlib murni, TIDAK butuh pip/install).

```bash
# default (current dir)
python "<SKILL_DIR>/graphify.py" .

# folder spesifik
python "<SKILL_DIR>/graphify.py" "C:/path/ke/folder"

# deep mode (tambah edge INFERRED dari keyword)
python "<SKILL_DIR>/graphify.py" "C:/path/ke/folder" --mode deep

# hanya JSON (tanpa HTML)
python "<SKILL_DIR>/graphify.py" "C:/path/ke/folder" --json-only

# output ke folder lain
python "<SKILL_DIR>/graphify.py" "C:/path/ke/folder" --out hasil_graph
```

`<SKILL_DIR>` = direktori skill ini (`~/.hermes/skills/graphify/` atau path profil).
Ganti dengan path absolut saat menjalankan via terminal tool.

## Alur saat diinvoke
1. Tentukan `path` (arg user, atau `.` bila tidak diberi — jangan tanya kalau sudah ada path).
2. Jalankan script dengan `python` (venv Hermes punya 3.11, stdlib cukup).
3. Baca `graphify-out/GRAPH_REPORT.md` → beri ringkasan ke user (god nodes, jumlah komunitas,
   komunitas terisolasi, pertanyaan yang bisa dijawab). JANGAN print raw JSON mentah.
4. Tawarkan buka `graphify-out/graph.html` (kirim file lewat MEDIA ke Telegram bila diminta).

## Batasan (jujur)
- Ekstraksi **semantic via LLM/vision** dari package asli TIDAK ada di sini — ini versi
  structural/AST + keyword. PDF & gambar TIDAK diekstrak (hanya teks/kode/markdown).
- Community detection pakai union-find sederhana, BUKAN Leiden/Louvain — untuk corpus besar
  tetap berguna sebagai cluster kasar.
- Edge INFERRED bersifat heuristik; selalu periksa tag sebelum menyimpulkan hubungan.
- Untuk Python/Ruby/PHP/JS/TS/Go/Java/C#/SQL/Rust ada parser simbol & import. Bahasa lain
  hanya di-level file (tanpa simbol).

## Visualisasi HTML — preferensi user (PENTING)
JANGAN gunakan layout **force-directed** (node bergerak/tarik-menarik otomatis). Bukti dari
sesi nyata: user menolak karena "jadi gatau file filenya" — posisi node yang berpindah-pindah
membuat file tidak bisa dikenali. Pakai **posisi statis** (layout per-komunitas di grid/cluster
tetap; user masih boleh drag manual, tapi tidak ada simulasi fisika otomatis).
JANGAN tampilkan **semua label sekaligus** — 808 node jadi berjejalan ("kayak barisan biasa",
tidak menarik). Label muncul saat **hover / zoom-in / filter / node besar** saja. God node
(degree tinggi) boleh selalu tampil labelnya. Gerak hanya berupa twinkle (kelap-kelip di tempat),
bukan perpindahan posisi.

## Contoh output ringkas ke user
```
Corpus: 23 file · ~4.200 kata
Graph: 61 node, 88 edge, 5 komunitas
God node: koneksi.php (degree 14) — dipakai banyak modul
Komunitas terisolasi: C3 (utils/) tidak ada import ke luar
```
