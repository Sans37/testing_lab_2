#!/usr/bin/env python
"""
Скрипт для инициализации тестовой базы данных
Создает таблицы и загружает тестовые данные
"""
import os
import sys
import logging
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.infrastructure.database.database import Base
from src.infrastructure.database.models.user_model import UserModel
from src.infrastructure.database.models.category_model import CategoryModel
from src.infrastructure.database.models.product_model import ProductModel
from src.core.entities.user import User, UserRole
from src.core.entities.category import Category
from src.core.entities.product import Product
from src.core.entities.ingredient import Ingredient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Тестовая БД
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://test_user:test_pass@localhost:5433/test_nady_bakery"
)


def init_test_db():
    """Инициализация тестовой БД"""
    logger.info("=" * 50)
    logger.info("🚀 Инициализация тестовой базы данных")
    logger.info("=" * 50)

    # Создаем движок
    engine = create_engine(TEST_DATABASE_URL)

    # Удаляем старые таблицы
    logger.info("🗑️  Удаление старых таблиц...")
    Base.metadata.drop_all(engine)

    # Создаем новые таблицы
    logger.info("🏗️  Создание новых таблиц...")
    Base.metadata.create_all(engine)

    # Создаем сессию
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Создаем тестовые данные
        logger.info("📦 Загрузка тестовых данных...")

        # Категории
        categories = [
            Category.create("Хлеб", "Различные виды хлеба"),
            Category.create("Выпечка", "Сладкая и соленая выпечка"),
            Category.create("Торты", "Праздничные торты"),
            Category.create("Напитки", "Горячие и холодные напитки"),
        ]

        for category in categories:
            cat_model = CategoryModel.from_entity(category)
            session.add(cat_model)
        session.commit()
        logger.info(f"   ✅ Создано категорий: {len(categories)}")

        # Получаем ID категорий
        cat_models = session.query(CategoryModel).all()
        cat_map = {cat.name: cat for cat in cat_models}

        # Товары
        products = [
            Product.create(
                name="Бородинский хлеб",
                description="Ржаной хлеб по классическому рецепту",
                price=120.0,
                category=cat_map["Хлеб"].to_entity(),
                ingredients=[
                    Ingredient.create("Мука ржаная", False),
                    Ingredient.create("Солод", False),
                    Ingredient.create("Соль", False),
                ]
            ),
            Product.create(
                name="Круассан с шоколадом",
                description="Слоеное тесто с шоколадной начинкой",
                price=180.0,
                category=cat_map["Выпечка"].to_entity(),
                ingredients=[
                    Ingredient.create("Мука пшеничная", True),
                    Ingredient.create("Масло сливочное", False),
                    Ingredient.create("Шоколад", False),
                ]
            ),
            Product.create(
                name="Наполеон",
                description="Классический торт Наполеон",
                price=850.0,
                category=cat_map["Торты"].to_entity(),
                ingredients=[
                    Ingredient.create("Мука пшеничная", True),
                    Ingredient.create("Заварной крем", False),
                    Ingredient.create("Сахарная пудра", False),
                ]
            ),
        ]

        for product in products:
            prod_model = ProductModel.from_entity(product)
            session.add(prod_model)
        session.commit()
        logger.info(f"   ✅ Создано товаров: {len(products)}")

        # Пользователи
        users = [
            User.create(
                name="Администратор",
                email="admin@example.com",
                password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj2cDqjQvS8S",  # admin123
                phone="+79990000000",
                address="Москва, ул. Административная, д. 1",
                role=UserRole.ADMIN
            ),
            User.create(
                name="Тестовый пользователь",
                email="user@example.com",
                password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj2cDqjQvS8S",  # admin123
                phone="+79991111111",
                address="Москва, ул. Тестовая, д. 2",
                role=UserRole.CUSTOMER
            ),
        ]

        for user in users:
            user_model = UserModel.from_entity(user)
            session.add(user_model)
        session.commit()
        logger.info(f"   ✅ Создано пользователей: {len(users)}")

        logger.info("=" * 50)
        logger.info("✅ Тестовая база данных успешно инициализирована!")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"❌ Ошибка при инициализации БД: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    init_test_db()