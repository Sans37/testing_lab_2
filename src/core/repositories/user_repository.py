from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.entities.user import User


class UserRepository(ABC):
    """Интерфейс репозитория для пользователей"""

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Получить пользователя по ID"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получить всех пользователей с пагинацией"""
        pass

    @abstractmethod
    async def create(self, user: User) -> User:
        """Создать нового пользователя"""
        pass

    @abstractmethod
    async def update(self, user_id: str, user_data: dict) -> User:
        """Обновить данные пользователя"""
        pass

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Удалить пользователя"""
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Проверить существование пользователя по email"""
        pass