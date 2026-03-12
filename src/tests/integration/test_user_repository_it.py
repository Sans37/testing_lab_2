import pytest
from sqlalchemy.orm import Session
from src.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from src.core.entities.user import User, UserRole
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def user_repository(test_db_session: Session):
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