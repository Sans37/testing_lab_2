from abc import ABC, abstractmethod
from typing import Optional
from src.core.entities.cart import Cart


class CartRepository(ABC):
    """Интерфейс репозитория для корзин"""

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> Optional[Cart]:
        """Получить корзину пользователя"""
        pass

    @abstractmethod
    async def create(self, cart: Cart) -> Cart:
        """Создать новую корзину"""
        pass

    @abstractmethod
    async def update(self, cart_id: str, cart_data: dict) -> Cart:
        """Обновить корзину"""
        pass

    @abstractmethod
    async def clear(self, cart_id: str) -> Cart:
        """Очистить корзину"""
        pass

    @abstractmethod
    async def delete(self, cart_id: str) -> bool:
        """Удалить корзину"""
        pass

    @abstractmethod
    async def get_or_create_by_user(self, user_id: str) -> Cart:
        """Получить или создать корзину для пользователя"""
        pass