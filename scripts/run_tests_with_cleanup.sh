# scripts/run_tests_with_cleanup.sh
#!/bin/bash
set -e

echo "🚀 Запуск тестов с очисткой БД..."

# Функция для очистки при ошибке
cleanup_on_error() {
    echo "❌ Тесты упали. Очистка БД..."
    python scripts/cleanup_test_db.py
    exit 1
}

# Устанавливаем обработчик ошибок
trap cleanup_on_error ERR

# Очищаем БД перед тестами
echo "🧹 Очистка БД перед тестами..."
python scripts/cleanup_test_db.py

# Инициализируем БД
echo "🚀 Инициализация БД..."
python scripts/init_test_db.py

# Запускаем тесты
echo "🧪 Запуск $1 тестов..."
python -m pytest $2 \
    -v \
    --junitxml=test-results/$3/junit.xml \
    --alluredir=test-results/$3 \
    --cov=src \
    --cov-report=xml:coverage-report/coverage-$3.xml \
    --cov-report=html:coverage-report/$3

# Очищаем БД после успешных тестов
echo "🧹 Очистка БД после тестов..."
python scripts/cleanup_test_db.py

echo "✅ $1 тесты завершены успешно!"