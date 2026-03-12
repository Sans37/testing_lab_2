#!/bin/bash
# Скрипт настройки репликации

echo "Setting up PostgreSQL replication..."

# Ожидаем запуска master базы
sleep 10

# Создаем пользователя для репликации на master
docker exec weblab5-db-master psql -U nady_user -d nady_bakery -c \
    "CREATE USER nady_user_ro WITH PASSWORD 'readonly123' REPLICATION;"
docker exec weblab5-db-master psql -U nady_user -d nady_bakery -c \
    "GRANT CONNECT ON DATABASE nady_bakery TO nady_user_ro;"
docker exec weblab5-db-master psql -U nady_user -d nady_bakery -c \
    "GRANT USAGE ON SCHEMA public TO nady_user_ro;"
docker exec weblab5-db-master psql -U nady_user -d nady_bakery -c \
    "GRANT SELECT ON ALL TABLES IN SCHEMA public TO nady_user_ro;"

# Настраиваем слот репликации
docker exec weblab5-db-master psql -U nady_user -d nady_bakery -c \
    "SELECT pg_create_physical_replication_slot('replica_slot');"

echo "Replication setup complete!"