#!/usr/bin/env python
"""
Скрипт для очистки тестовой базы данных
"""
import os
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from src.infrastructure.database.database import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Тестовая БД - используем переменную окружения
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://test_user:test_pass@localhost:5432/test_nady_bakery"
)


def reset_test_db():
    """Полный сброс БД (удаление и создание таблиц)"""
    logger.info("🔄 Полный сброс тестовой базы данных...")
    logger.info(f"📦 БД: {TEST_DATABASE_URL}")

    engine = create_engine(TEST_DATABASE_URL)

    # Удаляем все таблицы
    Base.metadata.drop_all(engine)
    logger.info("   ✅ Таблицы удалены")

    # Создаем заново
    Base.metadata.create_all(engine)
    logger.info("   ✅ Таблицы созданы")

    logger.info("✅ Тестовая БД сброшена")
    return True


if __name__ == "__main__":
    reset_test_db()