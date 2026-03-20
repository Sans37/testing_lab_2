# Лабораторная работа №7 — Интеграция с внешним сервисом

## Цель
Добавить в проект интеграцию с внешним сервисом (как с "черным ящиком"),
реализовать mock-сервер и E2E тесты для mock и реального сервиса.

## Выбранный внешний сервис
JSONPlaceholder (posts): https://jsonplaceholder.typicode.com
Контракт: GET /posts/{id} → JSON { id, userId, title, body }

## Реализация в проекте
1. Клиент внешнего сервиса:
   - `src/infrastructure/services/external_posts_client.py`
2. Контроллер интеграции:
   - `src/api/v2/controllers/integrations_controller.py`
   - Endpoint: `GET /api/v2/integrations/posts/{id}`
3. DTO ответа:
   - `src/api/v2/dtos/response_dtos.py` (ExternalPostResponse)

## Mock-сервер
- `src/mock_external_service.py`
- Endpoint: `GET /posts/{id}`
- Запуск через Docker: `docker/docker-compose.lab7.yml`

## Переключение mock / real
Через переменные окружения:
- `EXTERNAL_SERVICE_MODE=mock|real`
- `EXTERNAL_POSTS_BASE_URL` (URL mock или real)

## E2E тесты
- Mock: `src/tests/e2e/test_external_integration.py::test_external_integration_with_mock`
- Real (опционально): `src/tests/e2e/test_external_integration.py::test_external_integration_with_real_service`

## CI/CD
В CI:
- Поднимается mock-сервер на 8081
- E2E тесты идут в режиме mock
- Реальные тесты отключены по умолчанию, включаются `RUN_EXTERNAL_SERVICE_TESTS=true`

## Как демонстрировать преподавателю
1. Mock-режим:
   - `docker compose -f docker/docker-compose.lab7.yml up -d --build`
   - `curl http://localhost:8010/api/v2/integrations/posts/1`
2. Real-режим:
   - `EXTERNAL_POSTS_BASE_URL=https://jsonplaceholder.typicode.com`
   - `curl http://localhost:8000/api/v2/integrations/posts/1`

