# scripts/run_all_tests.sh
#!/bin/bash
set -e

echo "=========================================="
echo "🚀 ЗАПУСК ПОЛНОГО ТЕСТИРОВАНИЯ В DOCKER"
echo "=========================================="

# Создаем директории для результатов
mkdir -p test-results/unit test-results/integration test-results/e2e
mkdir -p coverage-report

# Шаг 1: Unit тесты (не требуют БД)
echo ""
echo "1. 🧪 UNIT ТЕСТЫ"
echo "=========================================="
python -m pytest src/tests/unit/ \
    -v \
    --junitxml=test-results/unit/junit.xml \
    --alluredir=test-results/unit \
    --cov=src \
    --cov-report=xml:coverage-report/coverage-unit.xml \
    --cov-report=html:coverage-report/unit

# Шаг 2: Integration тесты (требуют БД)
echo ""
echo "2. 🔗 INTEGRATION ТЕСТЫ"
echo "=========================================="
./scripts/run_tests_with_cleanup.sh "Integration" "src/tests/integration/ -m integration" "integration"

# Шаг 3: E2E тесты (требуют чистую БД)
echo ""
echo "3. 🎯 E2E ТЕСТЫ"
echo "=========================================="
./scripts/run_tests_with_cleanup.sh "E2E" "src/tests/e2e/ -m e2e" "e2e"

# Шаг 4: Генерация Allure отчетов
echo ""
echo "4. 📊 ГЕНЕРАЦИЯ ОТЧЕТОВ"
echo "=========================================="
allure generate test-results/unit --clean -o test-results/reports/unit
allure generate test-results/integration --clean -o test-results/reports/integration
allure generate test-results/e2e --clean -o test-results/reports/e2e

echo ""
echo "=========================================="
echo "🎉 ВСЕ ТЕСТЫ УСПЕШНО ЗАВЕРШЕНЫ!"
echo "=========================================="
echo "📁 Результаты:"
echo "   - JUnit XML: test-results/{unit,integration,e2e}/junit.xml"
echo "   - Allure отчеты: test-results/reports/"
echo "   - Coverage отчеты: coverage-report/"
echo "=========================================="