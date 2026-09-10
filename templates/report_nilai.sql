-- TEMPLATE query rekap (Part A2). Bobot diambil dari tb_mapel, TIDAK hardcode.
-- Ganti ? dengan parameter (id_mapel, kelas, periode).

-- 1) Rekap rata-rata nilai per siswa dalam 1 mapel & kelas
SELECT s.nama,
       m.nama_mapel,
       ROUND(AVG(h.poin), 2)                    AS rata2,
       COUNT(*)                                 AS jumlah_soal,
       SUM(h.tipe_soal = 'pg')                  AS pg,
       SUM(h.tipe_soal = 'isian')               AS isian,
       SUM(h.tipe_soal = 'essay')               AS essay
FROM tb_hasil h
JOIN tb_siswa s  ON s.id = h.id_siswa
JOIN tb_mapel m  ON m.id = h.id_mapel
WHERE h.id_mapel = ? AND s.kelas = ?
GROUP BY s.id, m.id
ORDER BY rata2 DESC;

-- 2) Total skor berbobot (pakai bobot dari DB)
SELECT s.nama,
       SUM(
         h.poin * CASE h.tipe_soal
           WHEN 'pg'    THEN m.bobot_pg
           WHEN 'isian' THEN m.bobot_isian
           WHEN 'essay' THEN m.bobot_essay
           ELSE 1 END
       ) AS skor_berbobot
FROM tb_hasil h
JOIN tb_siswa s ON s.id = h.id_siswa
JOIN tb_mapel m ON m.id = h.id_mapel
WHERE h.id_mapel = ? AND s.kelas = ?
GROUP BY s.id
ORDER BY skor_berbobot DESC;

-- 3) Rekap absen per siswa dalam periode (WIB)
SELECT s.nama,
       SUM(status = 'hadir') AS hadir,
       SUM(status = 'izin')  AS izin,
       SUM(status = 'sakit') AS sakit,
       SUM(status = 'alpa')  AS alpa
FROM tb_absen a
JOIN tb_siswa s ON s.id = a.id_siswa
WHERE a.tanggal BETWEEN DATE(?) AND DATE(?) AND s.kelas = ?
GROUP BY s.id
ORDER BY s.nama;

-- 4) Rekap GABUNGAN semua mapel per siswa (untuk rapor/liga)
--    LEFT JOIN supaya siswa yang belum punya hasil di mapel tertentu tetap muncul
--    dengan rata2 = NULL (tampilkan "-" di aplikasi).
SELECT s.nama,
       s.kelas,
       m.nama_mapel,
       ROUND(AVG(h.poin), 2)  AS rata2,
       COUNT(h.id)            AS jumlah_soal,
       COALESCE(SUM(h.tipe_soal = 'pg'), 0)    AS pg,
       COALESCE(SUM(h.tipe_soal = 'isian'), 0) AS isian,
       COALESCE(SUM(h.tipe_soal = 'essay'), 0) AS essay
FROM tb_siswa s
CROSS JOIN tb_mapel m
LEFT JOIN tb_hasil h ON h.id_siswa = s.id AND h.id_mapel = m.id
WHERE s.kelas = ?
GROUP BY s.id, m.id
ORDER BY s.nama, m.nama_mapel;

-- 5) Ranking kelas: rata-rata semua mapel per siswa, beserta peringkat
SELECT nama, kelas, rata2_all,
       RANK() OVER (PARTITION BY kelas ORDER BY rata2_all DESC) AS peringkat
FROM (
  SELECT s.nama, s.kelas,
         ROUND(AVG(h.poin), 2) AS rata2_all
  FROM tb_hasil h
  JOIN tb_siswa s ON s.id = h.id_siswa
  WHERE s.kelas = ?
  GROUP BY s.id
) sub
ORDER BY peringkat;

-- 6) Export CSV (di PHP pakai fputcsv; jangan echo manual)
--    $rows = mysqli_query($conn, $query_di_atas);
--    while ($r = mysqli_fetch_assoc($rows)) fputcsv($fh, $r);
