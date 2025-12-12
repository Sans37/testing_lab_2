# src/infrastructure/database/models/order_model.py
import enum
from typing import Optional
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from src.infrastructure.database.database import Base


class OrderStatus(enum.Enum):
    NEW = "новый"
    CONFIRMED = "подтвержден"
    READY = "готов"
    DELIVERING = "доставляется"
    COMPLETED = "завершен"
    CANCELLED = "отменен"


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.NEW, nullable=False)
    delivery_address: Mapped[str] = mapped_column(Text, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Связи как строковые ссылки
    user = relationship("UserModel", back_populates="orders")
    items = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan")

    def to_entity(self):
        from src.core.entities.order import Order, OrderItem

        order_items = []
        for item_model in self.items:
            order_items.append(OrderItem(
                product=item_model.product.to_entity(),
                quantity=item_model.quantity,
                price=item_model.price
            ))

        return Order(
            id=self.id,
            user_id=self.user_id,
            items=order_items,
            total=self.total,
            status=self.status.value,
            delivery_address=self.delivery_address,
            phone=self.phone,
            created_at=self.created_at,
            updated_at=self.updated_at,
            comment=self.comment
        )

    @classmethod
    def from_entity(cls, order_entity):
        return cls(
            id=order_entity.id,
            user_id=order_entity.user_id,
            total=order_entity.total,
            status=order_entity.status,
            delivery_address=order_entity.delivery_address,
            phone=order_entity.phone,
            comment=order_entity.comment
        )


class OrderItemModel(Base):
    __tablename__ = "order_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    order_id: Mapped[str] = mapped_column(String, ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(String, ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Связи как строковые ссылки
    order = relationship("OrderModel", back_populates="items")
    product = relationship("ProductModel")

    def to_entity(self):
        from src.core.entities.order import OrderItem
        return OrderItem(
            product=self.product.to_entity(),
            quantity=self.quantity,
            price=self.price
        )