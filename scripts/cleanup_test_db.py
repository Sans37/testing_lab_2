#!/usr/bin/env python
"""
Скрипт для очистки тестовой базы данных
Откатывает состояние до начального
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

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://test_user:test_pass@localhost:5433/test_nady_bakery"
)


def cleanup_test_db():
    """Очистка тестовой БД (удаление данных)"""
    logger.info("🧹 Очистка тестовой базы данных...")

    engine = create_engine(TEST_DATABASE_URL)

    with engine.connect() as conn:
        # Отключаем проверку внешних ключей
        conn.execute(text("SET session_replication_role = 'replica';"))
        conn.commit()

        # Получаем список всех таблиц
        result = conn.execute(text("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """))

        tables = [row[0] for row in result]

        # Очищаем таблицы
        for table in tables:
            if table != 'alembic_version':  # Не удаляем миграции
                logger.info(f"   Очистка таблицы: {table}")
                conn.execute(text(f"TRUNCATE TABLE {table} CASCADE;"))
                conn.commit()

        # Включаем проверку внешних ключей
        conn.execute(text("SET session_replication_role = 'origin';"))
        conn.commit()

    logger.info("✅ Тестовая БД очищена")
    return True


def reset_test_db():
    """Полный сброс БД (удаление и создание таблиц)"""
    logger.info("🔄 Полный сброс тестовой базы данных...")

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
    import argparse

    parser = argparse.ArgumentParser(description="Очистка тестовой БД")
    parser.add_argument("--reset", action="store_true", help="Полный сброс таблиц")
    args = parser.parse_args()

    if args.reset:
        reset_test_db()
    else:
        cleanup_test_db()