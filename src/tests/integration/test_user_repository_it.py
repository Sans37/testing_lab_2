import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infrastructure.database.models.user_model import UserModel
from src.infrastructure.database.models.product_model import ProductModel
from src.infrastructure.database.models.category_model import CategoryModel
from src.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from src.core.entities.user import User, UserRole
from src.infrastructure.database.database import Base
import uuid
from datetime import datetime


@pytest.fixture(scope="function")
def test_db_session():
    """Фикстура для тестовой БД PostgreSQL"""
    # Используем отдельную тестовую БД
    TEST_DATABASE_URL = "postgresql://test_user:test_pass@localhost:5433/test_nady_bakery"

    engine = create_engine(TEST_DATABASE_URL)

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


@pytest.fixture
def user_repository(test_db_session):
    return UserRepositoryImpl(test_db_session)


@pytest.mark.integration
class TestUserRepositoryIntegration:
    """Интеграционные тесты для UserRepository с реальной БД"""

    @pytest.mark.asyncio
    async def test_create_and_get_user(self, user_repository, test_db_session):
        # Arrange
        user = User.create(
            name="Test User",
            email="test@example.com",
            password="hashed_password",
            phone="+1234567890",
            address="Test Address"
        )

        # Act
        created_user = await user_repository.create(user)

        # Assert
        assert created_user.id == user.id
        assert created_user.email == "test@example.com"
        assert created_user.name == "Test User"

        # Проверяем, что сохранилось в БД
        retrieved = await user_repository.get_by_id(created_user.id)
        assert retrieved is not None
        assert retrieved.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_by_email(self, user_repository, test_db_session):
        # Arrange
        user = User.create(
            name="Email Test",
            email="unique@example.com",
            password="hashed",
            phone="+1111111111",
            address="Address"
        )
        await user_repository.create(user)

        # Act
        found = await user_repository.get_by_email("unique@example.com")

        # Assert
        assert found is not None
        assert found.email == "unique@example.com"

    @pytest.mark.asyncio
    async def test_update_user(self, user_repository, test_db_session):
        # Arrange
        user = User.create(
            name="Original",
            email="update@example.com",
            password="hashed",
            phone="+0000000000",
            address="Old Address"
        )
        created = await user_repository.create(user)

        # Act
        updated = await user_repository.update(
            created.id,
            {"name": "Updated Name", "phone": "+9999999999"}
        )

        # Assert
        assert updated.name == "Updated Name"
        assert updated.phone == "+9999999999"
        assert updated.email == "update@example.com"  # Не изменилось

    @pytest.mark.asyncio
    async def test_delete_user(self, user_repository, test_db_session):
        # Arrange
        user = User.create(
            name="To Delete",
            email="delete@example.com",
            password="hashed",
            phone="+1234567890",
            address="Address"
        )
        created = await user_repository.create(user)

        # Act
        result = await user_repository.delete(created.id)

        # Assert
        assert result is True
        deleted = await user_repository.get_by_id(created.id)
        assert deleted is None