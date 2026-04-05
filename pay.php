<?php

declare(strict_types=1);

require_once __DIR__ . '/robokassa_lib.php';

const ROBOKASSA_MERCHANT_URL = 'https://auth.robokassa.ru/Merchant/Index.aspx';

header('Content-Type: application/json; charset=UTF-8');

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Метод не поддерживается'], JSON_UNESCAPED_UNICODE);
    exit;
}

$raw = file_get_contents('php://input');
$data = json_decode($raw ?? '', true);
if (!is_array($data)) {
    http_response_code(400);
    echo json_encode(['error' => 'Некорректный запрос'], JSON_UNESCAPED_UNICODE);
    exit;
}

$emailRaw = isset($data['email']) ? (string) $data['email'] : '';
$email = robokassa_normalize_email($emailRaw);
if ($email === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(422);
    echo json_encode(['error' => 'Введите корректный адрес электронной почты.'], JSON_UNESCAPED_UNICODE);
    exit;
}

try {
    $config = robokassa_load_config();
    $r = $config['robokassa'];
    $plan = $r['plan_krugi'];
    $amount = (string) $plan['amount'];
    $description = (string) $plan['description'];
    $pdo = robokassa_pdo($config['db']);
    $invId = robokassa_create_payment($pdo, $email, $amount);
    $invIdStr = (string) $invId;
    $signature = robokassa_signature_init(
        $r['merchant_login'],
        $amount,
        $invIdStr,
        $r['password1']
    );
    $isTest = !empty($r['is_test']) ? '1' : '0';

    echo json_encode([
        'action' => ROBOKASSA_MERCHANT_URL,
        'fields' => [
            'MerchantLogin' => $r['merchant_login'],
            'OutSum' => $amount,
            'InvId' => $invIdStr,
            'Description' => $description,
            'SignatureValue' => $signature,
            'Email' => $email,
            'Culture' => 'ru',
            'IsTest' => $isTest,
        ],
    ], JSON_UNESCAPED_UNICODE);
} catch (\Throwable) {
    http_response_code(500);
    echo json_encode(['error' => 'Оплата временно недоступна. Попробуйте позже.'], JSON_UNESCAPED_UNICODE);
}
