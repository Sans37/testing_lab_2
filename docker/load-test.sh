# Отправьте 100 GET запросов
for i in {1..100}; do
  curl -s "http://localhost/api/v2/docs" > /dev/null
done

# Подсчитайте распределение
echo "Master: $(docker-compose logs api-master | grep -c 'GET /api/v2')"
echo "Replica 1: $(docker-compose logs api-replica-1 | grep -c 'GET /api/v2')"
echo "Replica 2: $(docker-compose logs api-replica-2 | grep -c 'GET /api/v2')"

# Примерное распределение должно быть около 50:25:25