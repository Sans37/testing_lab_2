# src/infrastructure/database/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os
from dotenv import load_dotenv
from typing import Generator
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

# Загружаем переменные из .env файла
load_dotenv()

# Получаем параметры из окружения
DB_ROLE = os.getenv("DB_ROLE", "master")
APP_INSTANCE = os.getenv("APP_INSTANCE", "unknown")
READ_ONLY = os.getenv("READ_ONLY", "false").lower() == "true"
APP_ENV = os.getenv("APP_ENV", "production")  # Добавляем определение окружения

# URL для master и replica баз данных
# Для тестового окружения используем test-db, для продакшена - db-master
if APP_ENV == "test":
    # В тестовом окружении используем переменную или значение по умолчанию для тестов
    MASTER_DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://test_user:test_pass@test-db:5432/test_nady_bakery"
    )
else:
    # В продакшене используем переменную или значение по умолчанию для продакшена
    MASTER_DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://nady_user:f6whs7ez@db-master:5432/nady_bakery"
    )

logger.info(f"🔍 APP_ENV: {APP_ENV}")
logger.info(f"🔍 DATABASE_URL from env: {os.getenv('DATABASE_URL')}")
logger.info(f"🔍 MASTER_DATABASE_URL: {MASTER_DATABASE_URL}")

REPLICA_DATABASE_URL = os.getenv(
    "REPLICA_DB_URL",
    "postgresql://nady_user_ro:readonly123@db-replica:5432/nady_bakery"
)

logger.info(f"🔧 APP_INSTANCE: {APP_INSTANCE}")
logger.info(f"🔧 DB_ROLE: {DB_ROLE}")
logger.info(f"🔧 READ_ONLY: {READ_ONLY}")

# Создание движков для master и replica
master_engine = create_engine(
    MASTER_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=os.getenv("LOG_LEVEL") == "DEBUG"
)

replica_engine = None
if REPLICA_DATABASE_URL and REPLICA_DATABASE_URL != MASTER_DATABASE_URL:
    replica_engine = create_engine(
        REPLICA_DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=os.getenv("LOG_LEVEL") == "DEBUG"
    )

# Фабрики сессий - СОХРАНЯЕМ SessionLocal для обратной совместимости
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=master_engine
)

MasterSessionLocal = SessionLocal  # Псевдоним для обратной совместимости

ReplicaSessionLocal = None
if replica_engine:
    ReplicaSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=replica_engine
    )

# Базовый класс для моделей
Base = declarative_base()


class ReadOnlyError(Exception):
    """Исключение при попытке записи в read-only реплику"""
    pass


def get_db(read_only: bool = False) -> Generator[Session, None, None]:
    """
    Получение сессии БД с учетом режима чтения/записи

    Args:
        read_only: если True, использует replica (если доступна)

    Yields:
        Сессия SQLAlchemy
    """
    if read_only and ReplicaSessionLocal:
        # Используем реплику для чтения
        db = ReplicaSessionLocal()
        logger.debug(f"📖 Using replica database for read-only operation")
    else:
        # Используем master для записи или если реплика недоступна
        db = SessionLocal()
        logger.debug(f"📝 Using master database")

    try:
        yield db
        # Проверяем, не пытаемся ли записать в read-only сессию
        if read_only and db.dirty:
            db.rollback()
            raise ReadOnlyError("Attempt to write to read-only database instance")
    except ReadOnlyError as e:
        logger.error(f"❌ Read-only violation: {e}")
        raise
    finally:
        db.close()


def get_master_db() -> Generator[Session, None, None]:
    """Всегда использует master базу данных"""
    return get_db(read_only=False)


def get_replica_db() -> Generator[Session, None, None]:
    """Всегда использует replica базу данных (только чтение)"""
    if not ReplicaSessionLocal:
        logger.warning("⚠️  Replica database is not configured, falling back to master")
        return get_db(read_only=False)
    return get_db(read_only=True)


# Функция для создания таблиц (только на master)
def create_tables():
    """Создание таблиц только на master базе данных"""
    if READ_ONLY:
        logger.warning("⚠️  Skipping table creation on read-only instance")
        return

    logger.info("🛠️  Creating tables on master database")
    Base.metadata.create_all(bind=master_engine)


# Проверка соединения с БД
def check_db_connections():
    """Проверка соединения с master и replica базами"""
    results = {"master": False, "replica": False}

    try:
        with master_engine.connect() as conn:
            conn.execute("SELECT 1")
        results["master"] = True
        logger.info("✅ Master database connection OK")
    except Exception as e:
        logger.error(f"❌ Master database connection failed: {e}")

    if replica_engine:
        try:
            with replica_engine.connect() as conn:
                conn.execute("SELECT 1")
            results["replica"] = True
            logger.info("✅ Replica database connection OK")
        except Exception as e:
            logger.error(f"❌ Replica database connection failed: {e}")

    return results