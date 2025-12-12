# src/infrastructure/database/models/cart_model.py
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.infrastructure.database.database import Base


class CartModel(Base):
    __tablename__ = "carts"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    items = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Связь как строковая ссылка
    user = relationship("UserModel", back_populates="cart")

    def to_entity(self):
        from src.core.entities.cart import Cart, CartItem

        cart_items = []
        for item_data in (self.items or []):
            product_model = None
            if product_model:
                cart_items.append(CartItem(
                    product=product_model.to_entity(),
                    quantity=item_data.get('quantity', 1)
                ))

        return Cart(
            id=self.id,
            user_id=self.user_id,
            items=cart_items,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @classmethod
    def from_entity(cls, cart_entity):
        items_data = []
        for item in cart_entity.items:
            items_data.append({
                "product_id": item.product.id,
                "quantity": item.quantity
            })

        return cls(
            id=cart_entity.id,
            user_id=cart_entity.user_id,
            items=items_data
        )