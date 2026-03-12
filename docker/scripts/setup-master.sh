#!/bin/sh
echo "Setting up master database..."

# Ждем пока PostgreSQL запустится
sleep 5

# Настраиваем репликацию
psql -U nady_user -d nady_bakery <<-EOSQL
    -- Создаем пользователя для репликации
    CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'replicator123';

    -- Настраиваем параметры репликации
    ALTER SYSTEM SET wal_level = replica;
    ALTER SYSTEM SET max_wal_senders = 10;
    ALTER SYSTEM SET max_replication_slots = 10;
    ALTER SYSTEM SET hot_standby = on;

    -- Перезагружаем конфигурацию
    SELECT pg_reload_conf();

    -- Создаем слот для репликации
    SELECT pg_create_physical_replication_slot('replication_slot');

    -- Даем права
    GRANT CONNECT ON DATABASE nady_bakery TO replicator;
    GRANT USAGE ON SCHEMA public TO replicator;
EOSQL

echo "Master setup completed!"