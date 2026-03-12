#!/bin/bash
# tests/load_test.sh
echo "========================================"
echo "НАГРУЗОЧНОЕ ТЕСТИРОВАНИЕ WEBLAB#5"
echo "========================================"

BASE_URL="http://localhost"
CONCURRENT_USERS=10
NUM_REQUESTS=100

echo "🔍 Тестируем балансировку GET запросов..."
echo "------------------------------------------------"

echo "📊 ТЕСТ 1: GET запросы на /api/v2/* (балансировка 2:1:1)"
for i in {1..5}; do
    curl -s "$BASE_URL/api/v2/instance-info" | grep -o '"instance":"[^"]*"' | cut -d'"' -f4
done | sort | uniq -c

echo ""
echo "📊 Проверяем распределение 20 запросов:"
for i in {1..20}; do
    curl -s "$BASE_URL/api/v2/instance-info" | grep -o '"instance":"[^"]*"' | cut -d'"' -f4
done | sort | uniq -c | sort -rn

echo ""
echo "🔍 Проверяем что POST идёт только на master..."
for i in {1..5}; do
    curl -s -X POST "$BASE_URL/api/v2/test-write" \
         -H "Content-Type: application/json" \
         -d '{"test": "data"}' | grep -o '"instance":"[^"]*"' | cut -d'"' -f4
done | sort | uniq -c

echo ""
echo "✅ Нагрузочное тестирование завершено!"