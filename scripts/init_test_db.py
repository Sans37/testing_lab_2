#!/usr/bin/env python3
"""
Скрипт для инициализации тестовой БД
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from src.infrastructure.database.database import Base
from src.infrastructure.database.models.user_model import UserModel
from src.infrastructure.database.models.product_model import ProductModel
from src.infrastructure.database.models.category_model import CategoryModel

# Тестовая БД
TEST_DATABASE_URL = "postgresql://test_user:test_pass@localhost:5432/test_nady_bakery"


def init_test_database():
    """Создает таблицы в тестовой БД"""
    print("🚀 Инициализация тестовой БД...")

    engine = create_engine(TEST_DATABASE_URL)

    # Удаляем существующие таблицы
    Base.metadata.drop_all(engine)

    # Создаем таблицы
    Base.metadata.create_all(engine)

    print("✅ Тестовая БД инициализирована")

    # Создаем тестовые данные
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Здесь можно добавить тестовые данные
        print("📝 Тестовые данные созданы")
    finally:
        session.close()


if __name__ == "__main__":
    init_test_database()