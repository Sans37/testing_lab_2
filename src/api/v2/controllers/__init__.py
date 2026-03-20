# src/api/v2/controllers/__init__.py
from .auth_controller import router as auth_router
from .products_controller import router as products_router
from .categories_controller import router as categories_router
from .cart_controller import router as cart_router
from .orders_controller import router as orders_router
from .reviews_controller import router as reviews_router
from .integrations_controller import router as integrations_router

__all__ = [
    "auth_router",
    "products_router",
    "categories_router",
    "cart_router",
    "orders_router",
    "reviews_router",
    "integrations_router",
]
