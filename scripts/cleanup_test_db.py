#!/usr/bin/env python3
"""
Скрипт для очистки тестовой БД
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from src.infrastructure.database.database import Base

TEST_DATABASE_URL = "postgresql://test_user:test_pass@localhost:5432/test_nady_bakery"


def cleanup_test_database():
    """Очищает тестовую БД"""
    print("🧹 Очистка тестовой БД...")

    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.drop_all(engine)

    print("✅ Тестовая БД очищена")


if __name__ == "__main__":
    cleanup_test_database()