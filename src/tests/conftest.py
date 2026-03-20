import pytest
import os
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from httpx import AsyncClient, ASGITransport
import psycopg2

from src.core.entities.product import Product
from src.core.entities.user import User
from src.core.entities.ingredient import Ingredient
from src.infrastructure.database.database import Base
from src.infrastructure.database.models.user_model import UserModel
from src.infrastructure.database.models.product_model import ProductModel
from src.infrastructure.database.models.category_model import CategoryModel
from src.core.entities.category import Category
from src.api.main import app
import uuid

from src.infrastructure.database.repositories.category_repository_impl import CategoryRepositoryImpl
from src.infrastructure.database.repositories.product_repository_impl import ProductRepositoryImpl
from src.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from sqlalchemy.engine import make_url


# Тестовая БД
_DEFAULT_TEST_DB_URL = "postgresql://test_user:test_pass@localhost:5432/test_nady_bakery"
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", _DEFAULT_TEST_DB_URL)
# Sanitize env value (non-breaking spaces / non-ASCII)
TEST_DATABASE_URL = TEST_DATABASE_URL.replace("\u00A0", "").strip()
TEST_DATABASE_URL = "".join(ch for ch in TEST_DATABASE_URL if 32 <= ord(ch) <= 126)
try:
    TEST_DATABASE_URL.encode("ascii")
except Exception:
    TEST_DATABASE_URL = _DEFAULT_TEST_DB_URL


@pytest.fixture(scope="function")
def test_db_session() -> Generator[Session, None, None]:
    """Фикстура для синхронной сессии БД (для всех тестов)"""
    print(f"🔌 Подключение к БД: {TEST_DATABASE_URL}")
    # Clear libpq environment variables that may contain hidden characters
    for key in [
        "PGHOST",
        "PGPORT",
        "PGUSER",
        "PGPASSWORD",
        "PGDATABASE",
        "PGSSLMODE",
        "PGOPTIONS",
        "PGAPPNAME",
        "PGPASSFILE",
        "PGSERVICE",
        "PGSERVICEFILE",
        "PGCLIENTENCODING",
        "PGSSLCERT",
        "PGSSLKEY",
        "PGSSLROOTCERT",
        "PGSSLCRL",
        "PGSSLCRLDIR",
    ]:
        os.environ.pop(key, None)
    # Force sane client encoding and avoid parsing .pgpass with bad bytes
    os.environ["PGCLIENTENCODING"] = "UTF8"
    os.environ["PGPASSFILE"] = "NUL"
    url = make_url(TEST_DATABASE_URL)
    def _connect():
        return psycopg2.connect(
            host=url.host or "localhost",
            dbname=url.database or "test_nady_bakery",
            user=url.username or "test_user",
            password=url.password or "test_pass",
            port=url.port or 5432,
            options="-c client_encoding=UTF8",
        )

    engine = create_engine("postgresql+psycopg2://", creator=_connect)

    # Создаем таблицы
    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        # Очищаем таблицы после теста
        Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
async def test_category(test_db_session: Session) -> Category:
    """Фикстура для создания тестовой категории"""
    repo = CategoryRepositoryImpl(test_db_session)
    category = Category.create(
        name=f"Test Category {uuid.uuid4()}",
        description="Test Description"
    )
    created = await repo.create(category)
    return created


@pytest.fixture(scope="function")
async def test_user(test_db_session: Session) -> UserModel:
    """Асинхронная фикстура для создания тестового пользователя"""
    repo = UserRepositoryImpl(test_db_session)
    user = User.create(
        name="Test User",
        email=f"test_{uuid.uuid4()}@example.com",
        password="hashed_password",
        phone="+1234567890",
        address="Test Address"
    )
    created = await repo.create(user)
    return created


@pytest.fixture(scope="function")
async def test_product(test_db_session: Session, test_category: Category) -> ProductModel:
    """Асинхронная фикстура для создания тестового товара"""
    repo = ProductRepositoryImpl(test_db_session)
    product = Product.create(
        name="Test Product",
        description="Test Description",
        price=100.0,
        category=test_category,
        ingredients=[
            Ingredient.create("Test Ingredient", False)
        ]
    )
    created = await repo.create(product)
    return created


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Фикстура для HTTP клиента для E2E тестов.
    Создает тестовый клиент для FastAPI приложения.
    """
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(scope="function")
async def test_db_cleanup():
    """
    Фикстура для очистки БД после E2E тестов.
    """
    yield
    # Очистка происходит автоматически в test_db_session
    pass

