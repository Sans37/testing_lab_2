# src/api/v2/routers.py
from fastapi import APIRouter
from .controllers import (
    auth_router,
    products_router,
    categories_router,
    cart_router,
    orders_router,
    reviews_router
)

# Главный роутер API v2
api_router = APIRouter()

# Подключаем все роутеры
api_router.include_router(auth_router)
api_router.include_router(products_router)
api_router.include_router(categories_router)
api_router.include_router(cart_router)
api_router.include_router(orders_router)
api_router.include_router(reviews_router)