<?php

declare(strict_types=1);

/**
 * Скопируйте в config.local.php и заполните. Файл config.local.php в .gitignore.
 * Требуется PHP 8.1+ (см. composer.json в каталоге landing).
 *
 * Старт оплаты: POST JSON на pay.php (см. index.html, модальное окно).
 *
 * В личном кабинете Robokassa:
 * - Алгоритм подписи: MD5 (или тот же, что в настройках магазина).
 * - ResultURL: https://ваш-домен/robokassa_result.php
 * - SuccessURL: https://ваш-домен/pay-success.html
 * - FailURL: https://ваш-домен/pay-fail.html
 */

return [
    'db' => [
        'host' => 'localhost',
        'name' => 'your_database',
        'user' => 'your_user',
        'pass' => 'your_password',
        'charset' => 'utf8mb4',
    ],
    'robokassa' => [
        'merchant_login' => 'your_merchant_login',
        'password1' => 'password_1_from_cabinet',
        'password2' => 'password_2_from_cabinet',
        /** true = тестовый режим (IsTest=1 и тестовые пароли из кабинета) */
        'is_test' => true,
        'plan_krugi' => [
            'amount' => '199.00',
            'description' => 'Подписка Круги 1 мес',
        ],
    ],
];
