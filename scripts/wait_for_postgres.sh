# scripts/wait_for_postgres.sh
#!/bin/bash
set -e

echo "⏳ Ожидание PostgreSQL..."
for i in {1..30}; do
    if pg_isready -h localhost -p 5432 -U test_user; then
        echo "✅ PostgreSQL готов!"
        exit 0
    fi
    echo "Ждем... ($i/30)"
    sleep 2
done

echo "❌ PostgreSQL не запустился за 60 секунд"
exit 1