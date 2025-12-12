import pytest
from unittest.mock import AsyncMock
from typing import Optional
from src.core.services.user_service import UserService
from src.core.entities.user import User, UserRole
from src.core.exceptions import EntityNotFoundException, AuthorizationException
from src.tests.unit.builders.user_builder import UserBuilder


@pytest.mark.classical
@pytest.mark.offline
class TestUserService:
    """Test suite для UserService в Лондонском стиле (с моками)"""

    @pytest.fixture
    def mock_user_repository(self) -> AsyncMock:
        """Фикстура для мока UserRepository"""
        return AsyncMock()

    @pytest.fixture
    def user_service(self, mock_user_repository: AsyncMock) -> UserService:
        """Фикстура для UserService с моком репозитория"""
        return UserService(mock_user_repository)

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, user_service: UserService, mock_user_repository: AsyncMock) -> None:
        """Позитивный тест: успешное получение пользователя по ID"""
        # Arrange
        user_id: str = "user_123"
        current_user: User = UserBuilder().with_id(user_id).build()  # Тот же пользователь!
        expected_user: User = UserBuilder().with_id(user_id).build()

        mock_user_repository.get_by_id.return_value = expected_user

        # Act
        result: Optional[User] = await user_service.get_user_by_id(user_id, current_user)

        # Assert
        assert result is not None
        assert result == expected_user
        mock_user_repository.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, user_service: UserService, mock_user_repository: AsyncMock) -> None:
        """Негативный тест: пользователь не найден"""
        # Arrange
        user_id: str = "user_999"
        current_user: User = UserBuilder().create_valid_user()

        mock_user_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(EntityNotFoundException, match="Пользователь"): #Ожидание
            await user_service.get_user_by_id(user_id, current_user)

    @pytest.mark.asyncio
    async def test_get_user_by_id_unauthorized(self, user_service: UserService,
                                               mock_user_repository: AsyncMock) -> None:
        """Негативный тест: нет прав для просмотра другого пользователя"""
        # Arrange
        user_id: str = "user_other"
        current_user: User = UserBuilder().create_valid_user()  # обычный пользователь
        other_user: User = UserBuilder().with_id(user_id).build()

        mock_user_repository.get_by_id.return_value = other_user

        # Act & Assert
        with pytest.raises(AuthorizationException, match="Нет прав для просмотра"): # Ожидание
            await user_service.get_user_by_id(user_id, current_user)

    @pytest.mark.asyncio
    async def test_get_user_by_id_admin_access(self, user_service: UserService,
                                               mock_user_repository: AsyncMock) -> None:
        """Позитивный тест: админ может просматривать любого пользователя"""
        # Arrange
        user_id: str = "user_other"
        current_user: User = UserBuilder().as_admin().build()  # админ
        other_user: User = UserBuilder().with_id(user_id).build()

        mock_user_repository.get_by_id.return_value = other_user

        # Act
        result: Optional[User] = await user_service.get_user_by_id(user_id, current_user)

        # Assert
        assert result is not None
        assert result == other_user
        mock_user_repository.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_current_user_profile(self, user_service: UserService, mock_user_repository: AsyncMock) -> None:
        """Позитивный тест: получение профиля текущего пользователя"""
        # Arrange
        current_user: User = UserBuilder().create_valid_user()
        expected_user: User = UserBuilder().with_id(current_user.id).build()

        mock_user_repository.get_by_id.return_value = expected_user

        # Act
        result: Optional[User] = await user_service.get_current_user_profile(current_user)

        # Assert
        assert result is not None
        assert result == expected_user
        mock_user_repository.get_by_id.assert_called_once_with(current_user.id)

    @pytest.mark.asyncio
    async def test_get_all_users_admin_success(self, user_service: UserService,
                                               mock_user_repository: AsyncMock) -> None:
        """Позитивный тест: админ получает список пользователей"""
        # Arrange
        current_user: User = UserBuilder().as_admin().build()
        expected_users: list[User] = [
            UserBuilder().with_id("user_1").build(),
            UserBuilder().with_id("user_2").build()
        ]

        mock_user_repository.get_all.return_value = expected_users

        # Act
        result: list[User] = await user_service.get_all_users(
            skip=0,
            limit=100,
            current_user=current_user
        )

        # Assert
        assert result == expected_users
        mock_user_repository.get_all.assert_called_once_with(0, 100)

    @pytest.mark.asyncio
    async def test_get_all_users_unauthorized(self, user_service: UserService, mock_user_repository: AsyncMock) -> None:
        """Негативный тест: обычный пользователь не может получить список"""
        # Arrange
        current_user: User = UserBuilder().create_valid_user()  # не админ

        # Act & Assert
        with pytest.raises(AuthorizationException, match="Требуются права администратора"):# Ожидание
            await user_service.get_all_users(current_user=current_user)

    @pytest.mark.asyncio
    async def test_change_user_role_success(self, user_service: UserService, mock_user_repository: AsyncMock) -> None:
        """Позитивный тест: админ меняет роль пользователя"""
        # Arrange
        admin_user: User = UserBuilder().as_admin().build()
        target_user: User = UserBuilder().with_id("user_target").build()
        new_role: UserRole = UserRole.ADMIN

        mock_user_repository.get_by_id.return_value = target_user
        mock_user_repository.update.return_value = target_user

        # Act
        result: Optional[User] = await user_service.change_user_role(
            user_id="user_target",
            new_role=new_role,
            current_user=admin_user
        )

        # Assert
        assert result is not None
        assert result == target_user
        mock_user_repository.get_by_id.assert_called_once_with("user_target")
        mock_user_repository.update.assert_called_once_with("user_target", {"role": new_role})

    @pytest.mark.asyncio
    async def test_change_user_role_unauthorized(self, user_service: UserService,
                                                 mock_user_repository: AsyncMock) -> None:
        """Негативный тест: обычный пользователь не может менять роли"""
        # Arrange
        current_user: User = UserBuilder().create_valid_user()  # не админ

        # Act & Assert
        with pytest.raises(AuthorizationException, match="Требуются права администратора"):
            await user_service.change_user_role(
                user_id="user_target",
                new_role=UserRole.ADMIN,
                current_user=current_user
            )