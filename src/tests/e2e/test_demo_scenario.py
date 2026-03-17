import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from src.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl

pytestmark = pytest.mark.e2e

class TestCompleteOrderFlow:
    """E2E тест: полный поток оформления заказа через API"""

    async def test_complete_order_flow_via_api(
        self,
        client: AsyncClient,
        test_db_session: Session,
        test_db_cleanup
    ):
        """
        Сценарий:
        1. Регистрация нового пользователя
        2. Логин
        3. Создание категории (админ)
        """
        print("\n" + "=" * 60)
        print("🚀 ЗАПУСК E2E ТЕСТА: БАЗОВЫЙ СЦЕНАРИЙ")
        print("=" * 60)

        # Шаг 1: Регистрация пользователя
        print("\n1. 📝 РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ")
        user_data = {
            "name": "Иван Петров",
            "email": "ivan@example.com",
            "password": "SecurePass123!",
            "phone": "+79991234567",
            "address": "Москва, ул. Пушкина, д. 10"
        }

        response = await client.post("/api/v2/auth/register", json=user_data)
        assert response.status_code == 201
        response_data = response.json()
        user = response_data['user']
        print(f"   ✅ Пользователь создан: {user['name']} (ID: {user['id']})")
        print(f"   ✅ Email: {user['email']}")

        # Шаг 2: Логин (получение токена)
        print("\n2. 🔑 АВТОРИЗАЦИЯ")
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        response = await client.post("/api/v2/auth/login", json=login_data)
        assert response.status_code == 200
        login_response = response.json()
        token = login_response["token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"   ✅ Токен получен")

        # Шаг 3: Создание категории (админ)
        print("\n3. 🏷️  СОЗДАНИЕ КАТЕГОРИИ")

        # Сначала сделаем пользователя админом (в тестовых целях)
        user_repo = UserRepositoryImpl(test_db_session)
        await user_repo.update(user["id"], {"role": "admin"})
        print(f"   ✅ Пользователь повышен до администратора")

        category_data = {
            "name": "Выпечка",
            "description": "Свежая выпечка из пекарни"
        }
        response = await client.post(
            "/api/v2/categories/",
            json=category_data,
            headers=headers
        )
        assert response.status_code == 201
        category = response.json()
        print(f"   ✅ Категория создана: {category['name']}")

        print("\n" + "=" * 60)
        print("🎉 E2E ТЕСТ УСПЕШНО ЗАВЕРШЕН!")
        print("=" * 60)
        print("Итоги:")
        print(f"   👤 Пользователей: 1")
        print(f"   🏷️  Категорий: 1")
        print("=" * 60)