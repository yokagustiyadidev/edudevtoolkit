-- Skema contoh dashboard sekolah (GENERIK — sesuaikan nama/field dengan sistemmu).
-- Jalankan di MySQL/MariaDB. Engine InnoDB + utf8mb4 untuk unicode & FK.

CREATE TABLE tb_users (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  nama          VARCHAR(100) NOT NULL,
  username      VARCHAR(50)  NOT NULL UNIQUE,
  nip           VARCHAR(30)  NULL UNIQUE,
  role          ENUM('admin','guru','staf') NOT NULL DEFAULT 'guru',
  password      VARCHAR(255) NOT NULL,        -- SELALU password_hash() -> "$2y$..."
  foto          VARCHAR(255) NULL,
  status        TINYINT NOT NULL DEFAULT 1,  -- 1=aktif, 0=nonaktif (soft delete)
  must_change_pw TINYINT NOT NULL DEFAULT 0,
  last_login    DATETIME NULL,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_role   (role),
  INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE tb_siswa (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  nama       VARCHAR(100) NOT NULL,
  kelas      VARCHAR(20)  NOT NULL,
  nis        VARCHAR(30)  NULL UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE tb_mapel (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  nama_mapel   VARCHAR(100) NOT NULL,
  bobot_pg     INT NOT NULL DEFAULT 1,
  bobot_isian  INT NOT NULL DEFAULT 3,
  bobot_essay  INT NOT NULL DEFAULT 5,
  token        VARCHAR(64) NULL,             -- token ujian per mapel (hash di server)
  created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE tb_hasil (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  id_siswa   INT NOT NULL,
  id_mapel   INT NOT NULL,
  id_tp      INT NULL,
  tipe_soal  ENUM('pg','isian','essay') NOT NULL,
  poin       DECIMAL(6,2) NOT NULL DEFAULT 0,
  benar      INT NOT NULL DEFAULT 0,
  salah      INT NOT NULL DEFAULT 0,
  waktu      DATETIME NULL,
  FOREIGN KEY (id_siswa) REFERENCES tb_siswa(id) ON DELETE CASCADE,
  FOREIGN KEY (id_mapel) REFERENCES tb_mapel(id) ON DELETE CASCADE,
  INDEX idx_mapel (id_mapel),
  INDEX idx_siswa (id_siswa)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE tb_absen (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  id_siswa   INT NOT NULL,
  tanggal    DATE NOT NULL,
  status     ENUM('hadir','izin','sakit','alpa') NOT NULL DEFAULT 'hadir',
  keterangan VARCHAR(255) NULL,
  FOREIGN KEY (id_siswa) REFERENCES tb_siswa(id) ON DELETE CASCADE,
  UNIQUE KEY uq_siswa_tgl (id_siswa, tanggal)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
