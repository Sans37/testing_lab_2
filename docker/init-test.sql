-- docker/init-test.sql
-- Инициализация тестовой базы данных

-- Создаем тестовую базу данных если не существует
SELECT 'CREATE DATABASE test_nady_bakery'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'test_nady_bakery')\gexec

-- Подключаемся к тестовой БД
\c test_nady_bakery

-- Создаем тестового пользователя если не существует
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'test_user') THEN
      CREATE USER test_user WITH PASSWORD 'test_pass' SUPERUSER;
   END IF;
END
$do$;

-- Даем права
GRANT ALL PRIVILEGES ON DATABASE test_nady_bakery TO test_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO test_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO test_user;

-- Создаем расширения
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Создаем схему public если не существует
CREATE SCHEMA IF NOT EXISTS public;

-- Устанавливаем владельца
ALTER SCHEMA public OWNER TO test_user;