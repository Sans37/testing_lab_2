import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.main import app
from src.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from src.infrastructure.database.repositories.product_repository_impl import ProductRepositoryImpl
from src.infrastructure.database.repositories.category_repository_impl import CategoryRepositoryImpl
from src.core.entities.user import User, UserRole
from src.core.entities.product import Product
from src.core.entities.category import Category
from src.core.entities.ingredient import Ingredient

pytestmark = pytest.mark.e2e

class TestCompleteOrderFlow:
    """E2E тест: полный поток оформления заказа через API"""

    async def test_complete_order_flow_via_api(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_db_cleanup
    ):
        """
        Сценарий:
        1. Регистрация нового пользователя
        2. Создание категории (админ)
        3. Добавление товаров (админ)
        4. Просмотр каталога (пользователь)
        5. Добавление товаров в корзину
        6. Оформление заказа
        """
        print("\n" + "=" * 60)
        print("🚀 ЗАПУСК E2E ТЕСТА: ПОЛНЫЙ СЦЕНАРИЙ ПОКУПКИ ЧЕРЕЗ API")
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
        user = response.json()
        print(f"   ✅ Пользователь создан: {user['name']} (ID: {user['id']})")
        print(f"   ✅ Email: {user['email']}")

        # Шаг 2: Логин (получение токена)
        print("\n2. 🔑 АВТОРИЗАЦИЯ")
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        response = await client.post("/api/v2/auth/login", data=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"   ✅ Токен получен")

        # Шаг 3: Создание категории (админ)
        print("\n3. 🏷️  СОЗДАНИЕ КАТЕГОРИИ")

        # Сначала сделаем пользователя админом (в тестовых целях)
        user_repo = UserRepositoryImpl(db_session)
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

        # Шаг 4: Добавление товаров
        print("\n4. 🍞 ДОБАВЛЕНИЕ ТОВАРОВ")
        products_data = [
            {
                "name": "Хлеб ржаной",
                "description": "Свежий ржаной хлеб",
                "price": 150.0,
                "category_id": category["id"],
                "ingredients": [
                    {"name": "Мука ржаная", "allergen": False},
                    {"name": "Соль", "allergen": False}
                ],
                "available": True
            },
            {
                "name": "Булочка с маком",
                "description": "Ароматная булочка",
                "price": 80.0,
                "category_id": category["id"],
                "ingredients": [
                    {"name": "Мука пшеничная", "allergen": True},
                    {"name": "Мак", "allergen": False}
                ],
                "available": True
            },
            {
                "name": "Пирог с яблоками",
                "description": "Домашний пирог",
                "price": 300.0,
                "category_id": category["id"],
                "ingredients": [
                    {"name": "Яблоки", "allergen": False},
                    {"name": "Корица", "allergen": False}
                ],
                "available": True
            }
        ]

        created_products = []
        for product_data in products_data:
            response = await client.post(
                "/api/v2/products/",
                json=product_data,
                headers=headers
            )
            assert response.status_code == 201
            product = response.json()
            created_products.append(product)
            print(f"   ✅ Товар добавлен: {product['name']} - {product['price']} руб.")

        # Шаг 5: Просмотр каталога
        print("\n5. 📋 ПРОСМОТР КАТАЛОГА")
        response = await client.get("/api/v2/products/")
        assert response.status_code == 200
        catalog = response.json()
        print(f"   ✅ Всего товаров в каталоге: {len(catalog)}")

        # Шаг 6: Поиск товаров
        print("\n6. 🔍 ПОИСК ТОВАРОВ")
        response = await client.get("/api/v2/products/search/?q=хлеб")
        assert response.status_code == 200
        search_results = response.json()
        print(f"   ✅ Найдено товаров по запросу 'хлеб': {len(search_results)}")
        assert len(search_results) > 0

        # Шаг 7: Добавление в корзину
        print("\n7. 🛒 ДОБАВЛЕНИЕ В КОРЗИНУ")
        cart_items = [
            {"product_id": created_products[0]["id"], "quantity": 2},
            {"product_id": created_products[1]["id"], "quantity": 3}
        ]

        for item in cart_items:
            response = await client.post(
                "/api/v2/cart/add",
                json=item,
                headers=headers
            )
            assert response.status_code == 200
            print(f"   ✅ Добавлен товар {item['product_id']} в количестве {item['quantity']}")

        # Шаг 8: Просмотр корзины
        print("\n8. 👀 ПРОСМОТР КОРЗИНЫ")
        response = await client.get("/api/v2/cart/", headers=headers)
        assert response.status_code == 200
        cart = response.json()
        total_items = sum(item["quantity"] for item in cart["items"])
        total_price = cart["total_price"]
        print(f"   ✅ В корзине: {total_items} товаров")
        print(f"   💰 Сумма: {total_price} руб.")

        # Шаг 9: Оформление заказа
        print("\n9. 📦 ОФОРМЛЕНИЕ ЗАКАЗА")
        order_data = {
            "delivery_address": user_data["address"],
            "payment_method": "card",
            "comment": "Позвонить за час"
        }

        response = await client.post(
            "/api/v2/orders/",
            json=order_data,
            headers=headers
        )
        assert response.status_code == 201
        order = response.json()

        print(f"   ✅ Заказ №{order['id']} создан")
        print(f"   📍 Адрес доставки: {order['delivery_address']}")
        print(f"   💰 Сумма заказа: {order['total_amount']} руб.")
        print(f"   📊 Статус: {order['status']}")

        # Шаг 10: Проверка истории заказов
        print("\n10. 📜 ПРОВЕРКА ИСТОРИИ ЗАКАЗОВ")
        response = await client.get("/api/v2/orders/my", headers=headers)
        assert response.status_code == 200
        orders = response.json()
        print(f"   ✅ Найдено заказов: {len(orders)}")
        assert len(orders) >= 1
        assert orders[0]["id"] == order["id"]

        print("\n" + "=" * 60)
        print("🎉 E2E ТЕСТ УСПЕШНО ЗАВЕРШЕН!")
        print("=" * 60)
        print("Итоги:")
        print(f"   👤 Пользователей: 1")
        print(f"   🏷️  Категорий: 1")
        print(f"   🍞 Товаров: 3")
        print(f"   🛒 Позиций в заказе: {total_items}")
        print(f"   💰 Сумма заказа: {total_price} руб.")
        print(f"   📦 Заказ №: {order['id']}")
        print("=" * 60)