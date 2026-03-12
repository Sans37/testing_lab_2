#!/usr/bin/env python
"""
Скрипт для инициализации тестовой базы данных
"""
import os
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from src.infrastructure.database.database import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Тестовая БД - используем переменную окружения
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://test_user:test_pass@localhost:5432/test_nady_bakery"
)


def init_test_db():
    """Инициализация тестовой БД"""
    logger.info("=" * 50)
    logger.info(f"🚀 Инициализация тестовой базы данных: {TEST_DATABASE_URL}")
    logger.info("=" * 50)

    engine = create_engine(TEST_DATABASE_URL)

    # Удаляем старые таблицы
    logger.info("🗑️  Удаление старых таблиц...")
    Base.metadata.drop_all(engine)

    # Создаем новые таблицы
    logger.info("🏗️  Создание новых таблиц...")
    Base.metadata.create_all(engine)

    logger.info("=" * 50)
    logger.info("✅ Тестовая база данных успешно инициализирована!")
    logger.info("=" * 50)


if __name__ == "__main__":
    init_test_db()