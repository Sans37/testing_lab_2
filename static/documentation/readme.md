[file name]: nginx/readme.md
[file content begin]
# WebLab#4 - Веб-сервер для маршрутизации

## Описание проекта
Асинхронный веб-сервер для работы веб-приложения в части маршрутизации.

## Технологии
- **Веб-сервер:** Nginx
- **Backend API:** FastAPI (Python)
- **База данных:** PostgreSQL
- **Администрирование БД:** Adminer
- **Контейнеризация:** Docker

## Маршрутизация
- `/` - Главная страница (SPA приложение)
- `/api/v2` - REST API версии 2
- `/api/v2/docs` - Swagger документация API
- `/legacy` - Legacy система
- `/documentation` - Документация проекта
- `/admin` - Админка базы данных
- `/status` - Статус сервера
- `/managment` - Панель управления
- `/reserved/` - Резервный путь

## API Endpoints
- `/api/v2/auth` - Аутентификация
- `/api/v2/products` - Продукты
- `/api/v2/categories` - Категории
- `/api/v2/cart` - Корзина
- `/api/v2/orders` - Заказы
- `/api/v2/reviews` - Отзывы

## Запуск проекта
```bash
docker-compose up -d --build