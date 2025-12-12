from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.entities.order import Order, OrderStatus


class OrderRepository(ABC):
    """Интерфейс репозитория для заказов"""

    @abstractmethod
    async def get_by_id(self, order_id: str) -> Optional[Order]:
        """Получить заказ по ID"""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: str, skip: int = 0, limit: int = 50) -> List[Order]:
        """Получить заказы пользователя"""
        pass

    @abstractmethod
    async def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            status: Optional[OrderStatus] = None,
            user_id: Optional[str] = None
    ) -> List[Order]:
        """Получить все заказы с фильтрацией"""
        pass

    @abstractmethod
    async def create(self, order: Order) -> Order:
        """Создать новый заказ"""
        pass

    @abstractmethod
    async def update_status(self, order_id: str, status: OrderStatus) -> Order:
        """Обновить статус заказа"""
        pass

    @abstractmethod
    async def update(self, order_id: str, order_data: dict) -> Order:
        """Обновить данные заказа"""
        pass

    @abstractmethod
    async def delete(self, order_id: str) -> bool:
        """Удалить заказ"""
        pass

    @abstractmethod
    async def get_orders_count(self, user_id: Optional[str] = None) -> int:
        """Получить количество заказов"""
        pass