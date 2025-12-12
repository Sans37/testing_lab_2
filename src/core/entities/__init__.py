# src/core/entities/__init__.py
# Убираем циклические импорты, импортируем только когда нужно
from .user import User, UserRole
from .category import Category
from .ingredient import Ingredient
from .product import Product
from .cart import Cart, CartItem
from .order import Order, OrderItem, OrderStatus
from .review import Review

__all__ = [
    "User", "UserRole",
    "Category",
    "Ingredient",
    "Product",
    "Cart", "CartItem",
    "Order", "OrderItem", "OrderStatus",
    "Review",
]