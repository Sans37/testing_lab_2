# src/infrastructure/database/repositories/cart_repository_impl.py
from typing import Optional, List, Dict, Any, cast
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime
from src.core.entities.cart import Cart, CartItem
from src.core.repositories.cart_repository import CartRepository
from src.core.exceptions.repository_exceptions import EntityNotFoundException
from src.infrastructure.database.models.cart_model import CartModel
from src.infrastructure.database.models.product_model import ProductModel


class CartRepositoryImpl(CartRepository):
    def __init__(self, db: Session):
        self.db = db

    async def get_by_user_id(self, user_id: str) -> Optional[Cart]:
        cart_model = self.db.query(CartModel).filter(CartModel.user_id == user_id).first()
        if not cart_model:
            return None

        # Получаем items из модели - используем cast чтобы указать тип
        items_data_raw = cart_model.items
        items_data: List[Dict[str, Any]]

        if items_data_raw is None:
            items_data = []
        elif isinstance(items_data_raw, list):
            items_data = items_data_raw
        else:
            # Если это не список, преобразуем в пустой список
            items_data = []

        # Загружаем продукты для корзины
        cart_items: List[CartItem] = []
        for item_data in items_data:  # Теперь items_data точно list
            if not isinstance(item_data, dict):
                continue

            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity', 1)

            if product_id:
                product_model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
                if product_model:
                    cart_items.append(CartItem(
                        product=product_model.to_entity(),
                        quantity=quantity
                    ))

        # Получаем datetime значения - используем каст
        created_at_raw = cart_model.created_at
        updated_at_raw = cart_model.updated_at

        created_at: datetime
        updated_at: datetime

        if isinstance(created_at_raw, datetime):
            created_at = created_at_raw
        else:
            # Если это не datetime, используем текущее время
            created_at = datetime.now()

        if isinstance(updated_at_raw, datetime):
            updated_at = updated_at_raw
        else:
            updated_at = datetime.now()

        # Создаем сущность корзины с загруженными продуктами
        return Cart(
            id=str(cart_model.id),
            user_id=str(cart_model.user_id),
            items=cart_items,
            created_at=created_at,
            updated_at=updated_at
        )

    async def create(self, cart_entity: Cart) -> Cart:
        cart_model = CartModel.from_entity(cart_entity)
        self.db.add(cart_model)
        self.db.commit()
        self.db.refresh(cart_model)

        # Вызываем get_by_user_id, который может вернуть None
        result = await self.get_by_user_id(str(cart_entity.user_id))
        if result is None:
            raise EntityNotFoundException("Корзина", f"для пользователя {cart_entity.user_id}")
        return result

    async def update(self, cart_id: str, cart_data: dict) -> Cart:
        cart_model = self.db.query(CartModel).filter(CartModel.id == cart_id).first()
        if not cart_model:
            raise EntityNotFoundException("Корзина", cart_id)

        for key, value in cart_data.items():
            if hasattr(cart_model, key):
                # Для поля items обрабатываем особо
                if key == "items":
                    # Убедимся, что значение - список
                    if not isinstance(value, list):
                        raise ValueError("Поле items должно быть списком")
                    # Используем setattr чтобы избежать проблем с типами
                    setattr(cart_model, 'items', value)
                    flag_modified(cart_model, "items")
                else:
                    setattr(cart_model, key, value)

        self.db.commit()
        self.db.refresh(cart_model)

        result = await self.get_by_user_id(str(cart_model.user_id))
        if result is None:
            raise EntityNotFoundException("Корзина", cart_id)
        return result

    async def clear(self, cart_id: str) -> Cart:
        cart_model = self.db.query(CartModel).filter(CartModel.id == cart_id).first()
        if not cart_model:
            raise EntityNotFoundException("Корзина", cart_id)

        # Используем setattr
        setattr(cart_model, 'items', [])
        flag_modified(cart_model, "items")
        self.db.commit()
        self.db.refresh(cart_model)

        result = await self.get_by_user_id(str(cart_model.user_id))
        if result is None:
            raise EntityNotFoundException("Корзина", cart_id)
        return result

    async def delete(self, cart_id: str) -> bool:
        cart_model = self.db.query(CartModel).filter(CartModel.id == cart_id).first()
        if not cart_model:
            raise EntityNotFoundException("Корзина", cart_id)

        self.db.delete(cart_model)
        self.db.commit()
        return True

    async def get_or_create_by_user(self, user_id: str) -> Cart:
        cart = await self.get_by_user_id(user_id)
        if cart:
            return cart

        # Создаем новую корзину
        new_cart_entity = Cart.create(user_id)
        result = await self.create(new_cart_entity)
        return result