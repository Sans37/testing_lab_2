from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import List
import uuid
from .product import Product


@dataclass
class CartItem:
    product: Product
    quantity: int


@dataclass
class Cart:
    id: str
    user_id: str
    items: List[CartItem]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, user_id: str) -> 'Cart':
        now = datetime.now()
        cart_id = f"cart_{uuid.uuid4()}"

        return cls(
            id=cart_id,
            user_id=user_id,
            items=[],
            created_at=now,
            updated_at=now
        )

    def add_item(self, product: Product, quantity: int) -> None:
        for item in self.items:
            if item.product.id == product.id:
                item.quantity += quantity
                self.updated_at = datetime.now()
                return

        self.items.append(CartItem(product=product, quantity=quantity))
        self.updated_at = datetime.now()

    def update_item_quantity(self, product_id: str, quantity: int) -> None:
        for item in self.items:
            if item.product.id == product_id:
                if quantity <= 0:
                    self.remove_item(product_id)
                else:
                    item.quantity = quantity
                self.updated_at = datetime.now()
                return

    def remove_item(self, product_id: str) -> None:
        self.items = [item for item in self.items if item.product.id != product_id]
        self.updated_at = datetime.now()

    def clear(self) -> None:
        self.items = []
        self.updated_at = datetime.now()

    def get_total(self) -> float:
        return sum(item.product.price * item.quantity for item in self.items)

    def get_item_count(self) -> int:
        return sum(item.quantity for item in self.items)

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "items": [
                {
                    "product": item.product.to_dict() if hasattr(item.product, 'to_dict') else item.product,
                    "quantity": item.quantity
                }
                for item in self.items
            ],
            "total": self.get_total(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }