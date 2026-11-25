<?php
require __DIR__ . '/vendor/autoload.php';
$app = require_once __DIR__ . '/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

use Illuminate\Support\Facades\DB;

echo "=== PELANGGAN USER (karine65@example.com) ===" . PHP_EOL;
$user = DB::table('users')->where('email', 'karine65@example.com')->first();
if ($user) {
    echo "User ID: $user->id_user, Nama: $user->nama, Role: $user->role" . PHP_EOL;
    $pel = DB::table('pelanggan')->where('id_user', $user->id_user)->first();
    if ($pel) {
        echo "Pelanggan ID: $pel->id_pelanggan, Telepon: $pel->no_telepon" . PHP_EOL;
    } else {
        echo "TIDAK ADA record pelanggan!" . PHP_EOL;
    }
} else {
    echo "User tidak ditemukan!" . PHP_EOL;
}

echo PHP_EOL . "=== SEMUA PESANAN (jumlah) ===" . PHP_EOL;
echo "Total pesanan: " . DB::table('pesanan')->count() . PHP_EOL;

echo PHP_EOL . "=== VALIDATOR LANG (id) ===" . PHP_EOL;
$langPath = lang_path('id/validation.php');
if (file_exists($langPath)) {
    $v = require $langPath;
    echo "min.string: " . ($v['min']['string'] ?? 'DEFAULT') . PHP_EOL;
    echo "required: " . ($v['required'] ?? 'DEFAULT') . PHP_EOL;
} else {
    echo "Tidak ada file lang/id/validation.php (pakai default Laravel English)" . PHP_EOL;
}
