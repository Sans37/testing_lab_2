from faker import Faker
from datetime import datetime
from src.core.entities.user import User, UserRole


class UserBuilder:
    def __init__(self) -> None:
        self.faker: Faker = Faker()
        self._id: str = f"user_{self.faker.uuid4()}"
        self._name: str = self.faker.name()
        self._email: str = self.faker.email()
        self._password: str = "hashed_password_123"
        self._phone: str = self.faker.phone_number()
        self._address: str = self.faker.address()
        self._role: UserRole = UserRole.CUSTOMER
        self._created_at: datetime = datetime.now()
        self._updated_at: datetime = datetime.now()

    def with_id(self, user_id: str) -> 'UserBuilder':
        self._id = user_id
        return self

    def with_name(self, name: str) -> 'UserBuilder':
        self._name = name
        return self

    def with_email(self, email: str) -> 'UserBuilder':
        self._email = email
        return self

    def with_role(self, role: UserRole) -> 'UserBuilder':
        self._role = role
        return self

    def as_admin(self) -> 'UserBuilder':
        self._role = UserRole.ADMIN
        return self

    def build(self) -> User:
        return User(
            id=self._id,
            name=self._name,
            email=self._email,
            password=self._password,
            phone=self._phone,
            address=self._address,
            role=self._role,
            created_at=self._created_at,
            updated_at=self._updated_at
        )

    @staticmethod
    def create_valid_user() -> User:
        return UserBuilder().build()

    @staticmethod
    def create_admin_user() -> User:
        return UserBuilder().as_admin().build()