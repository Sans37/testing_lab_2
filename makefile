.PHONY: build up down logs restart clean status ps

# Основные команды
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

clean:
	docker-compose down -v
	docker system prune -f

status:
	docker-compose ps

ps: status

# Специфичные команды
api-logs:
	docker-compose logs -f api

nginx-logs:
	docker-compose logs -f nginx

db-shell:
	docker-compose exec postgres psql -U user -d appdb

api-shell:
	docker-compose exec api bash

nginx-reload:
	docker-compose exec nginx nginx -s reload

# Проверка сервисов
check-api:
	curl -f http://localhost:8000/health || echo "API недоступен"

check-nginx:
	curl -f http://localhost/ || echo "Nginx недоступен"

check-all: check-api check-nginx