from __future__ import annotations
from .product import Product
from .cart import CartItem
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum
import uuid


class OrderStatus(Enum):
    NEW = "новый"
    CONFIRMED = "подтвержден"
    READY = "готов"
    DELIVERING = "доставляется"
    COMPLETED = "завершен"
    CANCELLED = "отменен"


@dataclass
class OrderItem:
    product: Product
    quantity: int
    price: float


@dataclass
class Order:
    id: str
    user_id: str
    items: List[OrderItem]
    total: float
    status: OrderStatus  # Изменено: OrderStatus вместо str
    delivery_address: str
    phone: str
    created_at: datetime
    updated_at: datetime
    comment: Optional[str] = None

    @classmethod
    def create(
            cls,
            user_id: str,
            items: List[CartItem],
            delivery_address: str,
            phone: str,
            comment: Optional[str] = None
    ) -> 'Order':
        now = datetime.now()
        order_id = f"order_{uuid.uuid4()}"

        order_items = [
            OrderItem(
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            for item in items
        ]

        total = sum(item.price * item.quantity for item in order_items)

        return cls(
            id=order_id,
            user_id=user_id,
            items=order_items,
            total=total,
            status=OrderStatus.NEW,  # Исправлено: OrderStatus.NEW вместо строки
            delivery_address=delivery_address,
            phone=phone,
            created_at=now,
            updated_at=now,
            comment=comment
        )

    def update_status(self, status: OrderStatus) -> None:  # Изменено тип параметра
        self.status = status
        self.updated_at = datetime.now()

    def update_delivery_info(self, address: Optional[str] = None,
                             phone: Optional[str] = None,
                             comment: Optional[str] = None) -> None:
        if address is not None:
            self.delivery_address = address
        if phone is not None:
            self.phone = phone
        if comment is not None:
            self.comment = comment
        self.updated_at = datetime.now()

    def can_be_cancelled(self) -> bool:
        return self.status in [OrderStatus.NEW, OrderStatus.CONFIRMED]  # Исправлено

    def cancel(self) -> None:
        if not self.can_be_cancelled():
            raise ValueError("Невозможно отменить заказ в текущем статусе")
        self.status = OrderStatus.CANCELLED  # Исправлено
        self.updated_at = datetime.now()

    def is_completed(self) -> bool:
        return self.status == OrderStatus.COMPLETED  # Исправлено

    def get_items_count(self) -> int:
        return sum(item.quantity for item in self.items)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "items": [
                {
                    "product": item.product.to_dict() if hasattr(item.product, 'to_dict') else item.product,
                    "quantity": item.quantity,
                    "price": item.price
                }
                for item in self.items
            ],
            "total": self.total,
            "status": self.status.value,  # Исправлено: .value для enum
            "delivery_address": self.delivery_address,
            "phone": self.phone,
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }