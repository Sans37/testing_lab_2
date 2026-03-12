-- docker/init.sql
-- Создание базы данных и пользователей

-- Создаем пользователя для записи
-- Создаем базу данных если не существует
SELECT 'CREATE DATABASE nady_bakery'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'nady_bakery')\gexec

-- Создаем пользователя
CREATE USER IF NOT EXISTS nady_user WITH PASSWORD 'f6whs7ez';
GRANT ALL PRIVILEGES ON DATABASE nady_bakery TO nady_user;

-- Создаем read-only пользователя
CREATE USER IF NOT EXISTS nady_user_ro WITH PASSWORD 'readonly123';
GRANT CONNECT ON DATABASE nady_bakery TO nady_user_ro;

-- Даем права nady_user
ALTER USER nady_user WITH SUPERUSER;

-- Даем права на подключение реплике
GRANT CONNECT ON DATABASE nady_bakery TO nady_user_ro;

-- Создаем таблицы для теста балансировки
CREATE TABLE IF NOT EXISTS request_logs (
    id SERIAL PRIMARY KEY,
    instance_name VARCHAR(50),
    request_method VARCHAR(10),
    endpoint VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    client_ip VARCHAR(45)
);

CREATE TABLE IF NOT EXISTS test_balance (
    id SERIAL PRIMARY KEY,
    instance VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Предоставляем права
GRANT ALL PRIVILEGES ON DATABASE nady_bakery TO nady_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nady_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO nady_user;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO nady_user_ro;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO nady_user_ro;

-- Создаем представление для мониторинга
CREATE OR REPLACE VIEW api_metrics AS
SELECT
    instance_name,
    COUNT(*) as total_requests,
    COUNT(DISTINCT client_ip) as unique_clients,
    MIN(timestamp) as first_request,
    MAX(timestamp) as last_request
FROM request_logs
GROUP BY instance_name;

-- Создаем mirror базу данных (если не существует)
SELECT 'CREATE DATABASE nady_bakery_mirror'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'nady_bakery_mirror')\gexec

-- Подключаемся к mirror БД и создаем таблицы
\c nady_bakery_mirror

-- Создаем таблицы для mirror БД
CREATE TABLE IF NOT EXISTS request_logs (
    id SERIAL PRIMARY KEY,
    instance_name VARCHAR(50),
    request_method VARCHAR(10),
    endpoint VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    client_ip VARCHAR(45)
);

CREATE TABLE IF NOT EXISTS test_balance (
    id SERIAL PRIMARY KEY,
    instance VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Даем права пользователю nady_user на mirror БД
GRANT ALL PRIVILEGES ON DATABASE nady_bakery_mirror TO nady_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nady_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO nady_user;

-- Возвращаемся к основной БД для последующих команд
\c nady_bakery