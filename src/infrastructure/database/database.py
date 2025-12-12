# src/infrastructure/database/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Получаем DATABASE_URL из .env или используем значение по умолчанию
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql:postgresql://nady_user:f6whs7ez@localhost:5432/nady_bakery"  # fallback
)

print(f"🔧 DATABASE_URL: {DATABASE_URL}")  # Для отладки

# Создание движка БД
engine = create_engine(DATABASE_URL)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Функция для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция для создания таблиц
def create_tables():
    Base.metadata.create_all(bind=engine)