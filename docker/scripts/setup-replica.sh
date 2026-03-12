#!/bin/sh
echo "Setting up replica database..."

# Ждем пока master будет готов
sleep 10

# Проверяем, есть ли уже данные
if [ ! -f /var/lib/postgresql/data/PG_VERSION ]; then
    echo "Creating replica from master..."

    # Удаляем старые данные если есть
    rm -rf /var/lib/postgresql/data/*

    # Создаем реплику
    PGPASSWORD=replicator123 pg_basebackup \
      -h db-master \
      -p 5432 \
      -D /var/lib/postgresql/data \
      -U replicator \
      -P \
      -v \
      -R
else
    echo "Replica already exists, skipping creation..."
fi

echo "Replica setup completed!"