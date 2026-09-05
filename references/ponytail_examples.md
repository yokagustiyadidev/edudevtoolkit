# Ponytail Examples — Refactor Kode Sekolah (Part B)

Before/after nyata untuk dashboard sekolah. Prinsip: berhenti di rung ladder pertama
yang cukup; jangan bangun yang tak diminta.

## 1. Export CSV: loop manual → fputcsv
BEFORE (over-built):
```php
$csv = '';
foreach ($rows as $r) {
    $csv .= '"'.str_replace('"','""',$r['nama']).'","'
                .str_replace('"','""',$r['nilai']).'"'."\n";
}
file_put_contents('rekap.csv', $csv);
```
AFTER (ponytail: native fungsi):
```php
$fh = fopen('rekap.csv','w');
foreach ($rows as $r) fputcsv($fh, $r);   // ponytail: built-in handle quoting
fclose($fh);
```
→ skipped: class CSV writer sendiri. add when: butuh format non-standard (pipe/TSV+dialect).

## 2. Verifikasi token: cek JS → verifikasi server
BEFORE (bypass-able): token dicek di JS sebelum buka ujian.
AFTER (ponytail + security wajib):
```php
// verify_token_aksi.php
if (!Auth::verifyExamToken($conn, $id_mapel, $token)) {
    http_response_code(403); exit;
}
```
→ security bukan "lazy away": validasi di trust boundary harus ada.

## 3. Cache sederhana: class → array statis
BEFORE: `class TokenCache { private $store=[]; ... }`
AFTER:
```php
static $cache = [];
$cache[$key] ??= Auth::verifyExamToken($conn, $id_mapel, $token);
```
→ skipped: class cache + invalidation. add when: butuh TTL / shared antar-proses (pakai APCu/Redis).

## 4. HTML tabel: template engine → heredoc/printf
BEFORE: pasang library template hanya untuk tabel.
AFTER: `printf('<tr><td>%s</td></tr>', htmlspecialchars($nama));`
→ skipped: dependency template. add when: UI kompleks butuh komponen reusable.
