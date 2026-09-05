<?php
/**
 * TEMPLATE: CRUD akun guru/staf (Part A1).
 * Generik — sesuaikan koneksi & nama tabel. Sudah menerapkan aturan skill:
 *   - password_hash() wajib
 *   - soft delete (status=0), bukan hard delete
 *   - guard role (hanya admin yang boleh CRUD user)
 *   - reset password -> set must_change_pw=1
 * CATATAN: tambahkan validasi CSRF (lihat Part A3) di setiap POST.
 */
require_once __DIR__ . '/koneksi.php';
use User\Asaj\Core\Auth;

Auth::guard(['admin']); // hanya admin

// ---------- CREATE ----------
if (isset($_POST['add'])) {
    $nama     = trim($_POST['nama'] ?? '');
    $username = trim($_POST['username'] ?? '');
    $role     = in_array($_POST['role'] ?? '', ['admin','guru','staf']) ? $_POST['role'] : 'guru';
    $pw       = $_POST['password'] ?? '';

    if ($nama === '' || $username === '' || $pw === '') {
        $err = 'Nama, username, dan password wajib diisi.';
    } elseif (mysqli_num_rows(mysqli_query($conn, "SELECT id FROM tb_users WHERE username='".mysqli_real_escape_string($conn,$username)."'")) > 0) {
        $err = 'Username sudah dipakai.';
    } else {
        $hash = password_hash($pw, PASSWORD_DEFAULT);
        mysqli_query($conn, "INSERT INTO tb_users (nama,username,role,password,status)
                             VALUES ('$nama','$username','$role','$hash',1)");
        $ok = 'Akun ditambahkan.';
    }
}

// ---------- EDIT (nama/role; password opsional) ----------
if (isset($_POST['edit'])) {
    $id   = (int)($_POST['id'] ?? 0);
    $nama = trim($_POST['nama'] ?? '');
    $role = in_array($_POST['role'] ?? '', ['admin','guru','staf']) ? $_POST['role'] : 'guru';
    $pw   = $_POST['password'] ?? '';
    $set  = "nama='$nama', role='$role'";
    if ($pw !== '') { // hanya rehash kalau diisi
        $set .= ", password='" . password_hash($pw, PASSWORD_DEFAULT) . "'";
    }
    mysqli_query($conn, "UPDATE tb_users SET $set WHERE id=$id");
    $ok = 'Akun diperbarui.';
}

// ---------- DEACTIVATE (soft delete) ----------
if (isset($_GET['deactivate'])) {
    $id = (int)$_GET['deactivate'];
    mysqli_query($conn, "UPDATE tb_users SET status=0 WHERE id=$id"); // soft delete, data relasional aman
    $ok = 'Akun dinonaktifkan (soft delete).';
}

// ---------- RESET PASSWORD ----------
if (isset($_GET['reset'])) {
    $id = (int)$_GET['reset'];
    $tmp = bin2hex(random_bytes(8)); // password sementara
    mysqli_query($conn, "UPDATE tb_users SET password='".password_hash($tmp,PASSWORD_DEFAULT)."', must_change_pw=1 WHERE id=$id");
    $ok = "Password direset. Temp: $tmp (beri ke user, lalu ganti saat login).";
}

// ---------- LIST ----------
$users = mysqli_query($conn, "SELECT id,nama,username,role,status FROM tb_users ORDER BY nama");
?>
<!doctype html><meta charset="utf-8">
<?php if (isset($err)) echo "<p style='color:red'>$err</p>"; ?>
<?php if (isset($ok))  echo "<p style='color:green'>$ok</p>"; ?>
<table border="1" cellpadding="6">
  <tr><th>Nama</th><th>Username</th><th>Role</th><th>Status</th><th>Aksi</th></tr>
  <?php while ($u = mysqli_fetch_assoc($users)): ?>
  <tr>
    <td><?= htmlspecialchars($u['nama']) ?></td>
    <td><?= htmlspecialchars($u['username']) ?></td>
    <td><?= $u['role'] ?></td>
    <td><?= $u['status'] ? 'aktif' : 'nonaktif' ?></td>
    <td>
      <a href="?reset=<?= $u['id'] ?>">Reset PW</a> |
      <?php if ($u['status']): ?><a href="?deactivate=<?= $u['id'] ?>">Nonaktifkan</a><?php endif; ?>
    </td>
  </tr>
  <?php endwhile; ?>
</table>
<!-- Form add/edit: tambahkan input + token CSRF di sini -->
