<?php

declare(strict_types=1);

/**
 * Лендинг и оплата рассчитаны на PHP 8.1+ (см. composer.json).
 * Зависимости на хостинге: расширения pdo и pdo_mysql.
 */

/**
 * @return array{db: array, robokassa: array}
 */
function robokassa_load_config(): array
{
    $path = __DIR__ . '/config.local.php';
    if (!is_readable($path)) {
        throw new RuntimeException('Файл config.local.php не найден. Скопируйте config.local.example.php.');
    }
    /** @var array $cfg */
    $cfg = require $path;
    if (!isset($cfg['db'], $cfg['robokassa'])) {
        throw new RuntimeException('Неверная структура config.local.php');
    }
    return $cfg;
}

function robokassa_pdo(array $dbConfig): PDO
{
    $dsn = sprintf(
        'mysql:host=%s;dbname=%s;charset=%s',
        $dbConfig['host'],
        $dbConfig['name'],
        $dbConfig['charset'] ?? 'utf8mb4'
    );
    $pdo = new PDO($dsn, $dbConfig['user'], $dbConfig['pass'], [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false,
    ]);
    return $pdo;
}

function robokassa_signature_init(
    string $merchantLogin,
    string $outSum,
    string $invId,
    string $password1
): string {
    $base = $merchantLogin . ':' . $outSum . ':' . $invId . ':' . $password1;
    return md5($base);
}

function robokassa_signature_result(string $outSum, string $invId, string $password2): string
{
    $base = $outSum . ':' . $invId . ':' . $password2;
    return md5($base);
}

/**
 * @return array{id: int, email: string, amount: string, status: string}|null
 */
function robokassa_get_payment(PDO $pdo, int $invId): ?array
{
    $st = $pdo->prepare(
        'SELECT id, email, amount, status FROM robokassa_payments WHERE id = ? LIMIT 1'
    );
    $st->execute([$invId]);
    $row = $st->fetch();
    return $row === false ? null : $row;
}

function robokassa_create_payment(PDO $pdo, string $email, string $amount): int
{
    $st = $pdo->prepare(
        'INSERT INTO robokassa_payments (email, amount, status, created_at) VALUES (?, ?, ?, NOW())'
    );
    $st->execute([$email, $amount, 'pending']);
    return (int) $pdo->lastInsertId();
}

function robokassa_mark_paid(PDO $pdo, int $invId): void
{
    $st = $pdo->prepare(
        "UPDATE robokassa_payments SET status = 'paid', paid_at = NOW() WHERE id = ? AND status = 'pending'"
    );
    $st->execute([$invId]);
}

function robokassa_normalize_email(string $raw): string
{
    return strtolower(trim($raw));
}

function robokassa_amounts_match(string $receivedOutSum, string $storedAmount): bool
{
    return abs((float) $receivedOutSum - (float) $storedAmount) < 0.000001;
}
