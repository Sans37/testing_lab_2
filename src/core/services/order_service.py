# src/core/services/order_service.py
from typing import List, Optional
from src.core.entities.order import Order, OrderStatus  # ← убрать дублирование Order
from src.core.repositories.order_repository import OrderRepository
from src.core.repositories.cart_repository import CartRepository
from src.core.repositories.user_repository import UserRepository
from src.core.exceptions import EntityNotFoundException, BusinessRuleException, AuthorizationException


class OrderService:
    """Сервис для работы с заказами"""

    def __init__(
            self,
            order_repository: OrderRepository,
            cart_repository: CartRepository,
            user_repository: UserRepository
    ):
        self.order_repository = order_repository
        self.cart_repository = cart_repository
        self.user_repository = user_repository

    async def create_order_from_cart(
            self,
            user_id: str,
            delivery_address: str,
            phone: str,
            comment: Optional[str] = None
    ) -> Order:
        """Создать заказ из корзины"""
        # Получение корзины пользователя
        cart = await self.cart_repository.get_by_user_id(user_id)
        if not cart or not cart.items:
            raise BusinessRuleException("Корзина пуста")

        # Проверка доступности всех товаров
        for item in cart.items:
            if not item.product.available:
                raise BusinessRuleException(f"Товар '{item.product.name}' временно недоступен")

        # Создание заказа
        order_entity = Order.create(
            user_id=user_id,
            items=cart.items,
            delivery_address=delivery_address,
            phone=phone,
            comment=comment
        )

        # Сохранение заказа
        order = await self.order_repository.create(order_entity)

        # Очистка корзины после создания заказа
        await self.cart_repository.clear(cart.id)

        return order

    async def get_user_orders(self, user_id: str, skip: int = 0, limit: int = 50) -> List[Order]:
        """Получить заказы пользователя"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundException("Пользователь", user_id)

        return await self.order_repository.get_by_user_id(user_id, skip, limit)

    async def get_order(self, order_id: str, current_user_id: str) -> Order:
        """Получить заказ по ID"""
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise EntityNotFoundException("Заказ", order_id)

        # Проверка прав доступа
        user = await self.user_repository.get_by_id(current_user_id)

        # Добавьте проверку на None
        if not user:
            raise AuthorizationException("Пользователь не найден")

        # Теперь mypy знает, что user не None
        if order.user_id != current_user_id and not user.is_admin():
            raise AuthorizationException("Нет прав для просмотра этого заказа")

        return order

    async def get_all_orders(
            self,
            skip: int = 0,
            limit: int = 100,
            status: Optional[OrderStatus] = None,
            user_id: Optional[str] = None,
            current_user_id: Optional[str] = None
    ) -> List[Order]:
        """Получить все заказы (только для админов)"""
        if not current_user_id:
            raise AuthorizationException("Требуется аутентификация")

        user = await self.user_repository.get_by_id(current_user_id)
        if not user:
            raise AuthorizationException("Пользователь не найден")

        if not user.is_admin():  # Теперь mypy знает, что user не None
            raise AuthorizationException("Требуются права администратора")

        return await self.order_repository.get_all(skip, limit, status, user_id)

    async def update_order_status(
            self,
            order_id: str,
            status: OrderStatus,
            current_user_id: str  # Должен быть обязательным
    ) -> Order:
        """Обновить статус заказа (только для админов)"""
        user = await self.user_repository.get_by_id(current_user_id)
        if not user or not user.is_admin():
            raise AuthorizationException("Требуются права администратора")

        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise EntityNotFoundException("Заказ", order_id)

        return await self.order_repository.update_status(order_id, status)

    async def cancel_order(self, order_id: str, user_id: str) -> Order:
        """Отменить заказ"""
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise EntityNotFoundException("Заказ", order_id)

        # Проверка прав доступа
        if order.user_id != user_id:
            raise AuthorizationException("Можно отменять только свои заказы")

        # Проверка возможности отмены
        order_entity = Order(
            id=order.id,
            user_id=order.user_id,
            items=order.items,
            total=order.total,
            status=order.status,
            delivery_address=order.delivery_address,
            phone=order.phone,
            created_at=order.created_at,
            updated_at=order.updated_at,
            comment=order.comment
        )

        if not order_entity.can_be_cancelled():
            raise BusinessRuleException("Невозможно отменить заказ в текущем статусе")

        order_entity.cancel()

        return await self.order_repository.update_status(order_id, OrderStatus.CANCELLED)