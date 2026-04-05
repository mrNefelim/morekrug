<?php

declare(strict_types=1);

require_once __DIR__ . '/robokassa_lib.php';

header('Content-Type: text/plain; charset=UTF-8');

try {
    $config = robokassa_load_config();
} catch (\Throwable) {
    http_response_code(500);
    exit;
}

$outSum = isset($_POST['OutSum']) ? (string) $_POST['OutSum'] : '';
$invIdRaw = isset($_POST['InvId']) ? (string) $_POST['InvId'] : '';
$signature = isset($_POST['SignatureValue']) ? (string) $_POST['SignatureValue'] : '';

if ($outSum === '' || $invIdRaw === '' || $signature === '') {
    http_response_code(400);
    exit;
}

if (!ctype_digit($invIdRaw)) {
    http_response_code(400);
    exit;
}

$invId = (int) $invIdRaw;
$expectedSig = robokassa_signature_result(
    $outSum,
    $invIdRaw,
    $config['robokassa']['password2']
);

if (!hash_equals(strtolower($expectedSig), strtolower($signature))) {
    http_response_code(400);
    exit;
}

$pdo = robokassa_pdo($config['db']);
$row = robokassa_get_payment($pdo, $invId);

if ($row === null) {
    http_response_code(404);
    exit;
}

if ($row['status'] === 'paid') {
    echo 'OK' . $invId;
    exit;
}

if ($row['status'] !== 'pending') {
    http_response_code(400);
    exit;
}

if (!robokassa_amounts_match($outSum, (string) $row['amount'])) {
    http_response_code(400);
    exit;
}

robokassa_mark_paid($pdo, $invId);
$rowAfter = robokassa_get_payment($pdo, $invId);

if ($rowAfter !== null && $rowAfter['status'] === 'paid') {
    echo 'OK' . $invId;
    exit;
}

http_response_code(500);
