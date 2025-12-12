import os
from typing import Generator, Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.core.entities import User
from src.infrastructure.database.database import SessionLocal
from src.core.services.auth_service import AuthService
from src.core.services.user_service import UserService
from src.core.services.product_service import ProductService
from src.core.services.cart_service import CartService
from src.core.services.order_service import OrderService
from src.core.services.review_service import ReviewService
# Добавляем импорт CategoryService
from src.core.services.category_service import CategoryService

# Импортируем реализации репозиториев напрямую
from src.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from src.infrastructure.database.repositories.product_repository_impl import ProductRepositoryImpl
from src.infrastructure.database.repositories.category_repository_impl import CategoryRepositoryImpl
from src.infrastructure.database.repositories.cart_repository_impl import CartRepositoryImpl
from src.infrastructure.database.repositories.order_repository_impl import OrderRepositoryImpl
from src.infrastructure.database.repositories.review_repository_impl import ReviewRepositoryImpl

# Загружаем .env
load_dotenv()

# JWT Bearer схема
security = HTTPBearer()

# Получаем секретный ключ из .env
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Dependency для получения сессии БД
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency для репозитория категорий (если нужен отдельно)
def get_category_repository(db: Session = Depends(get_db)) -> CategoryRepositoryImpl:
    return CategoryRepositoryImpl(db)

# Dependency для сервиса категорий (ДОБАВЬТЕ ЭТО)
def get_category_service(
    db: Session = Depends(get_db)
) -> CategoryService:
    """Получение сервиса категорий"""
    category_repository = CategoryRepositoryImpl(db)
    return CategoryService(category_repository=category_repository)

# Dependency для сервиса аутентификации
def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    user_repository = UserRepositoryImpl(db)
    return AuthService(
        user_repository=user_repository,
        secret_key=JWT_SECRET_KEY,  # из .env
        algorithm=JWT_ALGORITHM
    )

# Dependency для сервиса пользователей
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    user_repository = UserRepositoryImpl(db)
    return UserService(user_repository=user_repository)

# Dependency для сервиса продуктов
def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    product_repository = ProductRepositoryImpl(db)
    category_repository = CategoryRepositoryImpl(db)
    return ProductService(
        product_repository=product_repository,
        category_repository=category_repository
    )

# Dependency для сервиса корзины
def get_cart_service(db: Session = Depends(get_db)) -> CartService:
    cart_repository = CartRepositoryImpl(db)
    product_repository = ProductRepositoryImpl(db)
    return CartService(
        cart_repository=cart_repository,
        product_repository=product_repository
    )

# Dependency для сервиса заказов
def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    order_repository = OrderRepositoryImpl(db)
    cart_repository = CartRepositoryImpl(db)
    user_repository = UserRepositoryImpl(db)
    return OrderService(
        order_repository=order_repository,
        cart_repository=cart_repository,
        user_repository=user_repository
    )

# Dependency для сервиса отзывов
def get_review_service(db: Session = Depends(get_db)) -> ReviewService:
    review_repository = ReviewRepositoryImpl(db)
    product_repository = ProductRepositoryImpl(db)
    order_repository = OrderRepositoryImpl(db)
    return ReviewService(
        review_repository=review_repository,
        product_repository=product_repository,
        order_repository=order_repository
    )

# Dependency для получения текущего пользователя
async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        auth_service: AuthService = Depends(get_auth_service),
        user_service: UserService = Depends(get_user_service)
) -> Optional[User]:
    try:
        payload = auth_service.verify_token(credentials.credentials)
        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный токен"
            )

        # Теперь current_user=None корректно передается
        user = await user_service.get_user_by_id(user_id, current_user=None)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден"
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Ошибка аутентификации: {str(e)}"
        )