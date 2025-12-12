import pytest
from datetime import datetime
from freezegun import freeze_time

from src.core.entities.user import User, UserRole
from src.tests.unit.builders.object_mother import ObjectMother
from src.tests.unit.builders.user_builder import UserBuilder

@pytest.mark.classical
@pytest.mark.offline
class TestUserEntity:
    """Test suite для UserEntity - позитивные и негативные тесты"""

    def test_user_creation_with_factory_method(self) -> None:
        """Позитивный тест: создание пользователя через фабричный метод"""
        # Arrange
        name: str = "John Doe"
        email: str = "john@example.com"
        password: str = "secure_password"
        phone: str = "+1234567890"
        address: str = "123 Main St"

        # Act
        with freeze_time("2023-01-01 12:00:00"):
            user: User = User.create(
                name=name,
                email=email,
                password=password,
                phone=phone,
                address=address
            )

        # Assert
        assert user.name == name
        assert user.email == email
        assert user.password == password
        assert user.phone == phone
        assert user.address == address
        assert user.role == UserRole.CUSTOMER
        assert user.id.startswith("user_")
        assert user.created_at == user.updated_at

    def test_user_creation_with_builder_pattern(self) -> None:
        """Позитивный тест: создание пользователя через Builder паттерн"""
        # Arrange & Act
        user: User = UserBuilder().create_valid_user()

        # Assert
        assert user.name is not None
        assert "@" in user.email
        assert user.role in [UserRole.CUSTOMER, UserRole.ADMIN]

    def test_update_profile_updates_timestamp(self) -> None:
        """Позитивный тест: обновление профиля меняет updated_at"""
        # Arrange
        with freeze_time("2023-01-01 12:00:00"):
            user: User = UserBuilder().create_valid_user()
            original_updated_at: datetime = user.updated_at

        # Act - "перемещаемся" на 1 секунду вперед во времени
        with freeze_time("2023-01-01 12:00:01"):
            user.update_profile(name="New Name", phone="+0987654321")

        # Assert
        assert user.name == "New Name"
        assert user.phone == "+0987654321"
        assert user.updated_at > original_updated_at
        assert user.updated_at == datetime(2023, 1, 1, 12, 0, 1)

    def test_is_admin_returns_correct_value(self) -> None:
        """Позитивный тест: проверка роли администратора"""
        # Arrange
        customer_user: User = UserBuilder().create_valid_user()
        admin_user: User = UserBuilder().as_admin().build()

        # Act & Assert
        assert not customer_user.is_admin()
        assert admin_user.is_admin()

    def test_to_dict_returns_correct_structure(self) -> None:
        """Позитивный тест: преобразование в dict"""
        # Arrange
        user: User = UserBuilder().create_valid_user()

        # Act
        user_dict: dict = user.to_dict()

        # Assert
        assert user_dict["id"] == user.id
        assert user_dict["name"] == user.name
        assert user_dict["email"] == user.email
        assert user_dict["role"] == user.role.value
        assert "created_at" in user_dict
        assert "updated_at" in user_dict

    def test_update_profile_with_none_values_does_nothing(self) -> None:
        """Негативный тест: обновление с None значениями"""
        # Arrange
        user: User = UserBuilder().create_valid_user()
        original_name: str = user.name
        original_phone: str = user.phone
        original_address: str = user.address

        # Act
        user.update_profile(name=None, phone=None, address=None)

        # Assert
        assert user.name == original_name
        assert user.phone == original_phone
        assert user.address == original_address

    def test_user_creation_with_object_mother(self) -> None:
        """Позитивный тест: создание пользователя через Object Mother"""
        # Arrange
        customer: User = ObjectMother.create_default_customer()
        admin: User = ObjectMother.create_default_admin()

        # Act & Assert
        assert customer.role == UserRole.CUSTOMER
        assert customer.email == "customer@example.com"
        assert admin.role == UserRole.ADMIN
        assert admin.is_admin()

    def test_user_with_specific_email_via_object_mother(self) -> None:
        """Позитивный тест: пользователь с конкретным email через Object Mother"""
        # Arrange & Act
        user: User = ObjectMother.create_user_with_specific_email("test@test.com")

        # Assert
        assert user.email == "test@test.com"
        assert user.role == UserRole.CUSTOMER