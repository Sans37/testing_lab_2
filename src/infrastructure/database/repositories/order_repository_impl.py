# src/infrastructure/database/repositories/order_repository_impl.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from src.core.entities.order import Order, OrderStatus
from src.core.repositories.order_repository import OrderRepository
from src.core.exceptions.repository_exceptions import EntityNotFoundException
from src.infrastructure.database.models.order_model import OrderModel, OrderItemModel
from src.infrastructure.database.models.order_model import OrderStatus as ModelOrderStatus


class OrderRepositoryImpl(OrderRepository):
    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, order_id: str) -> Optional[Order]:
        order_model = self.db.query(OrderModel).filter(OrderModel.id == order_id).first()
        return order_model.to_entity() if order_model else None

    async def get_by_user_id(self, user_id: str, skip: int = 0, limit: int = 50) -> List[Order]:
        order_models = self.db.query(OrderModel).filter(
            OrderModel.user_id == user_id
        ).order_by(desc(OrderModel.created_at)).offset(skip).limit(limit).all()

        return [order_model.to_entity() for order_model in order_models]

    async def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            status: Optional[OrderStatus] = None,
            user_id: Optional[str] = None
    ) -> List[Order]:
        query = self.db.query(OrderModel)

        if status:
            query = query.filter(OrderModel.status == status)

        if user_id:
            query = query.filter(OrderModel.user_id == user_id)

        order_models = query.order_by(desc(OrderModel.created_at)).offset(skip).limit(limit).all()
        return [order_model.to_entity() for order_model in order_models]

    async def create(self, order_entity) -> Order:
        # Создаем заказ
        order_model = OrderModel.from_entity(order_entity)
        self.db.add(order_model)

        # Создаем элементы заказа
        for item in order_entity.items:
            order_item = OrderItemModel(
                id=f"order_item_{item.product.id}_{order_entity.id}",
                order_id=order_entity.id,
                product_id=item.product.id,
                quantity=item.quantity,
                price=item.price
            )
            self.db.add(order_item)

        self.db.commit()
        self.db.refresh(order_model)
        return order_model.to_entity()

    async def update_status(self, order_id: str, status: OrderStatus) -> Order:
        order_model = self.db.query(OrderModel).filter(OrderModel.id == order_id).first()
        if not order_model:
            raise EntityNotFoundException("Заказ", order_id)

        # Исправлено: Присваиваем значение enum напрямую
        order_model.status = ModelOrderStatus(status.value)
        self.db.commit()
        self.db.refresh(order_model)
        return order_model.to_entity()

    async def update(self, order_id: str, order_data: dict) -> Order:
        order_model = self.db.query(OrderModel).filter(OrderModel.id == order_id).first()
        if not order_model:
            raise EntityNotFoundException("Заказ", order_id)

        for key, value in order_data.items():
            if hasattr(order_model, key):
                setattr(order_model, key, value)

        self.db.commit()
        self.db.refresh(order_model)
        return order_model.to_entity()

    async def delete(self, order_id: str) -> bool:
        order_model = self.db.query(OrderModel).filter(OrderModel.id == order_id).first()
        if not order_model:
            raise EntityNotFoundException("Заказ", order_id)

        self.db.delete(order_model)
        self.db.commit()
        return True

    async def get_orders_count(self, user_id: Optional[str] = None) -> int:
        query = self.db.query(OrderModel)

        if user_id:
            query = query.filter(OrderModel.user_id == user_id)

        return query.count()