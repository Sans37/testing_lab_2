"""
Простой E2E тест для лабораторной работы
Проверяет полный поток: пользователь → товар → заказ
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infrastructure.database.database import Base
from src.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from src.infrastructure.database.repositories.product_repository_impl import ProductRepositoryImpl
from src.infrastructure.database.repositories.category_repository_impl import CategoryRepositoryImpl
from src.core.entities.user import User
from src.core.entities.product import Product
from src.core.entities.category import Category


@pytest.fixture(scope="function")
def test_db_session():
    """Фикстура для E2E тестов - использует ту же БД, что и integration"""
    TEST_DATABASE_URL = "postgresql://test_user:test_pass@localhost:5433/test_nady_bakery"

    engine = create_engine(TEST_DATABASE_URL)

    # Очищаем таблицы перед тестом
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        # Можно не удалять таблицы, если хотите сохранить для отладки


@pytest.mark.e2e
class TestCompleteOrderFlow:
    """E2E тест: полный поток оформления заказа"""

    @pytest.mark.asyncio
    async def test_complete_order_flow(self, test_db_session):
        """Полный сценарий от регистрации до 'заказа'"""
        print("\n" + "=" * 60)
        print("🚀 ЗАПУСК E2E ТЕСТА: ПОЛНЫЙ СЦЕНАРИЙ ПОКУПКИ")
        print("=" * 60)

        # Шаг 1: Создание пользователя (регистрация)
        print("\n1. 📝 РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ")
        user_repo = UserRepositoryImpl(test_db_session)
        user = User.create(
            name="Иван Петров",
            email="ivan@example.com",
            password="secure_pass",
            phone="+79991234567",
            address="Москва, ул. Пушкина, д. 10"
        )
        created_user = await user_repo.create(user)
        assert created_user.email == "ivan@example.com"
        print(f"   ✅ Пользователь создан: {created_user.name}")

        # Шаг 2: Создание категории товаров
        print("\n2. 🏷️  СОЗДАНИЕ КАТЕГОРИИ")
        category_repo = CategoryRepositoryImpl(test_db_session)
        category = Category.create(
            name="Выпечка",
            description="Свежая выпечка из пекарни"
        )
        created_category = await category_repo.create(category)
        assert created_category.name == "Выпечка"
        print(f"   ✅ Категория создана: {created_category.name}")

        # Шаг 3: Создание товаров
        print("\n3. 🍞 СОЗДАНИЕ ТОВАРОВ")
        product_repo = ProductRepositoryImpl(test_db_session)

        products = [
            ("Хлеб ржаной", "Свежий ржаной хлеб", 150.0),
            ("Булочка с маком", "Ароматная булочка", 80.0),
            ("Пирог с яблоками", "Домашний пирог", 300.0)
        ]

        created_products = []
        for name, description, price in products:
            product = Product.create(
                name=name,
                description=description,
                price=price,
                category=created_category,
                ingredients=[]
            )
            created = await product_repo.create(product)
            created_products.append(created)
            print(f"   ✅ Товар добавлен: {name} - {price} руб.")

        # Шаг 4: Поиск товаров (имитация поиска на сайте)
        print("\n4. 🔍 ПОИСК ТОВАРОВ")
        found_products = await product_repo.search_by_name("хлеб")
        assert len(found_products) > 0
        print(f"   ✅ Найдено товаров по запросу 'хлеб': {len(found_products)}")

        # Шаг 5: Фильтрация товаров по категории
        print("\n5. 📂 ФИЛЬТРАЦИЯ ПО КАТЕГОРИИ")
        category_products = await product_repo.get_by_category(created_category.id)
        assert len(category_products) == 3
        print(f"   ✅ Товаров в категории '{created_category.name}': {len(category_products)}")

        # Шаг 6: 'Добавление в корзину' (имитация)
        print("\n6. 🛒 ДОБАВЛЕНИЕ В КОРЗИНУ")
        cart_items = [
            (created_products[0], 2),  # 2 хлеба
            (created_products[1], 3),  # 3 булочки
        ]

        total_price = sum(product.price * quantity for product, quantity in cart_items)
        print(f"   ✅ В корзине: {len(cart_items)} позиций")
        print(f"   ✅ Общая сумма: {total_price} руб.")

        # Шаг 7: 'Оформление заказа' (имитация)
        print("\n7. 📦 ОФОРМЛЕНИЕ ЗАКАЗА")
        order_summary = {
            "customer": created_user.name,
            "items": [{"product": p.name, "quantity": q} for p, q in cart_items],
            "total": total_price,
            "address": created_user.address,
            "status": "pending"
        }

        print(f"   📋 Заказ от: {order_summary['customer']}")
        print(f"   📍 Адрес доставки: {order_summary['address']}")
        print(f"   💰 Итого к оплате: {order_summary['total']} руб.")

        # Проверяем, что заказ можно 'создать'
        assert order_summary["customer"] == "Иван Петров"
        assert order_summary["total"] == 150 * 2 + 80 * 3  # 540 руб.

        print("\n" + "=" * 60)
        print("🎉 E2E ТЕСТ УСПЕШНО ЗАВЕРШЕН!")
        print("=" * 60)
        print("Итоги:")
        print(f"   👤 Пользователей: 1")
        print(f"   🏷️  Категорий: 1")
        print(f"   🍞 Товаров: 3")
        print(f"   🛒 Позиций в заказе: 2")
        print(f"   💰 Сумма заказа: {total_price} руб.")
        print("=" * 60)