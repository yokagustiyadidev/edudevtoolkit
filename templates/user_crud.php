<?php
/**
 * TEMPLATE: CRUD akun guru/staf (Part A1).
 * Generik — sesuaikan koneksi & nama tabel.
 *
 * Keamanan (sesuai Part A3 / security_checklist.md):
 *   - password_hash() wajib (PASSWORD_DEFAULT = bcrypt)
 *   - prepared statement di SELURUH query (tidak ada interpolasi string mentah)
 *   - CSRF token dihasilkan & divalidasi di semua mutasi POST
 *   - GET hanya untuk baca (list); mutasi state wajib POST
 *   - guard role: hanya admin (cek di server, bukan sembunyi tombol)
 *   - soft delete (status=0), bukan hard delete
 *   - reset password -> hash baru + must_change_pw=1
 *
 * Dependency: TIDAK ada. Koneksi mysqli native + session PHP standar.
 */

declare(strict_types=1);
session_start();

/* ---------- KONEKSI (ganti sesuai env) ---------- */
$conn = mysqli_connect('localhost', 'DB_USER', 'DB_PASS', 'DB_NAME');
if (!$conn) {
    http_response_code(500);
    exit('Koneksi database gagal.');
}
mysqli_set_charset($conn, 'utf8mb4');

/* ---------- GUARD ROLE (self-contained, server-side) ---------- */
// Di sistem nyata, ambil role dari session loginmu. Di sini pakai contoh:
$current_role = $_SESSION['role'] ?? 'guest';
if ($current_role !== 'admin') {
    http_response_code(403);
    exit('Akses ditolak: hanya admin.');
}

/* ---------- CSRF ---------- */
function csrf_token(): string {
    if (empty($_SESSION['csrf'])) {
        $_SESSION['csrf'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf'];
}
function csrf_valid(string $token): bool {
    return isset($_SESSION['csrf']) && hash_equals($_SESSION['csrf'], $token);
}

/* ---------- CREATE ---------- */
if ($_SERVER['REQUEST_METHOD'] === 'POST' && ($_POST['action'] ?? '') === 'add') {
    if (!csrf_valid($_POST['csrf'] ?? '')) {
        $err = 'Token CSRF tidak valid.';
    } else {
        $nama     = trim($_POST['nama'] ?? '');
        $username = trim($_POST['username'] ?? '');
        $role     = in_array($_POST['role'] ?? '', ['admin', 'guru', 'staf'], true) ? $_POST['role'] : 'guru';
        $pw       = $_POST['password'] ?? '';

        if ($nama === '' || $username === '' || $pw === '') {
            $err = 'Nama, username, dan password wajib diisi.';
        } else {
            // cek duplikat (prepared)
            $chk = mysqli_prepare($conn, 'SELECT id FROM tb_users WHERE username = ?');
            mysqli_stmt_bind_param($chk, 's', $username);
            mysqli_stmt_execute($chk);
            mysqli_stmt_store_result($chk);
            if (mysqli_stmt_num_rows($chk) > 0) {
                $err = 'Username sudah dipakai.';
            } else {
                $hash = password_hash($pw, PASSWORD_DEFAULT);
                $ins = mysqli_prepare($conn,
                    'INSERT INTO tb_users (nama, username, role, password, status) VALUES (?, ?, ?, ?, 1)');
                mysqli_stmt_bind_param($ins, 'ssss', $nama, $username, $role, $hash);
                mysqli_stmt_execute($ins);
                $ok = 'Akun ditambahkan.';
            }
            mysqli_stmt_close($chk);
        }
    }
}

/* ---------- EDIT (nama/role; password opsional) ---------- */
if ($_SERVER['REQUEST_METHOD'] === 'POST' && ($_POST['action'] ?? '') === 'edit') {
    if (!csrf_valid($_POST['csrf'] ?? '')) {
        $err = 'Token CSRF tidak valid.';
    } else {
        $id   = (int)($_POST['id'] ?? 0);
        $nama = trim($_POST['nama'] ?? '');
        $role = in_array($_POST['role'] ?? '', ['admin', 'guru', 'staf'], true) ? $_POST['role'] : 'guru';
        $pw   = $_POST['password'] ?? '';

        if ($pw !== '') {
            $hash = password_hash($pw, PASSWORD_DEFAULT);
            $upd = mysqli_prepare($conn, 'UPDATE tb_users SET nama = ?, role = ?, password = ? WHERE id = ?');
            mysqli_stmt_bind_param($upd, 'sssi', $nama, $role, $hash, $id);
        } else {
            $upd = mysqli_prepare($conn, 'UPDATE tb_users SET nama = ?, role = ? WHERE id = ?');
            mysqli_stmt_bind_param($upd, 'ssi', $nama, $role, $id);
        }
        mysqli_stmt_execute($upd);
        $ok = 'Akun diperbarui.';
    }
}

/* ---------- DEACTIVATE (soft delete via POST) ---------- */
if ($_SERVER['REQUEST_METHOD'] === 'POST' && ($_POST['action'] ?? '') === 'deactivate') {
    if (!csrf_valid($_POST['csrf'] ?? '')) {
        $err = 'Token CSRF tidak valid.';
    } else {
        $id = (int)($_POST['id'] ?? 0);
        $del = mysqli_prepare($conn, 'UPDATE tb_users SET status = 0 WHERE id = ?');
        mysqli_stmt_bind_param($del, 'i', $id);
        mysqli_stmt_execute($del);
        $ok = 'Akun dinonaktifkan (soft delete).';
    }
}

/* ---------- RESET PASSWORD (via POST) ---------- */
if ($_SERVER['REQUEST_METHOD'] === 'POST' && ($_POST['action'] ?? '') === 'reset') {
    if (!csrf_valid($_POST['csrf'] ?? '')) {
        $err = 'Token CSRF tidak valid.';
    } else {
        $id  = (int)($_POST['id'] ?? 0);
        $tmp = bin2hex(random_bytes(8)); // password sementara
        $hash = password_hash($tmp, PASSWORD_DEFAULT);
        $rst = mysqli_prepare($conn, 'UPDATE tb_users SET password = ?, must_change_pw = 1 WHERE id = ?');
        mysqli_stmt_bind_param($rst, 'si', $hash, $id);
        mysqli_stmt_execute($rst);
        $ok = "Password direset. Temp: $tmp (beri ke user, lalu ganti saat login).";
    }
}

/* ---------- LIST (GET, read-only) ---------- */
$users = mysqli_query($conn, 'SELECT id, nama, username, role, status FROM tb_users ORDER BY nama');
$csrf = csrf_token();
?>
<!doctype html><meta charset="utf-8">
<?php if (isset($err)) echo "<p style='color:red'>" . htmlspecialchars($err) . "</p>"; ?>
<?php if (isset($ok))  echo "<p style='color:green'>" . htmlspecialchars($ok) . "</p>"; ?>
<table border="1" cellpadding="6">
  <tr><th>Nama</th><th>Username</th><th>Role</th><th>Status</th><th>Aksi</th></tr>
  <?php while ($u = mysqli_fetch_assoc($users)): ?>
  <tr>
    <td><?= htmlspecialchars($u['nama']) ?></td>
    <td><?= htmlspecialchars($u['username']) ?></td>
    <td><?= htmlspecialchars($u['role']) ?></td>
    <td><?= $u['status'] ? 'aktif' : 'nonaktif' ?></td>
    <td>
      <form method="post" style="display:inline">
        <input type="hidden" name="action" value="reset">
        <input type="hidden" name="id" value="<?= (int)$u['id'] ?>">
        <input type="hidden" name="csrf" value="<?= $csrf ?>">
        <button type="submit">Reset PW</button>
      </form>
      <?php if ($u['status']): ?>
      <form method="post" style="display:inline">
        <input type="hidden" name="action" value="deactivate">
        <input type="hidden" name="id" value="<?= (int)$u['id'] ?>">
        <input type="hidden" name="csrf" value="<?= $csrf ?>">
        <button type="submit">Nonaktifkan</button>
      </form>
      <?php endif; ?>
    </td>
  </tr>
  <?php endwhile; ?>
</table>

<!-- Form add/edit: tambahkan input nama/username/password/role + hidden csrf + hidden action=add/edit -->
