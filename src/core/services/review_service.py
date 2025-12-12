# src/core/services/review_service.py
from typing import List, Optional, Dict, Any  # Добавьте Dict, Any
from src.core.entities.review import Review
from src.core.repositories.review_repository import ReviewRepository
from src.core.repositories.product_repository import ProductRepository
from src.core.repositories.order_repository import OrderRepository
from src.core.exceptions import EntityNotFoundException, BusinessRuleException


class ReviewService:
    """Сервис для работы с отзывами"""

    def __init__(
            self,
            review_repository: ReviewRepository,
            product_repository: ProductRepository,
            order_repository: OrderRepository
    ):
        self.review_repository = review_repository
        self.product_repository = product_repository
        self.order_repository = order_repository

    async def create_review(
            self,
            user_id: str,
            product_id: str,
            rating: int,
            comment: str
    ) -> Review:
        """Создать отзыв"""
        # Проверка существования товара
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise EntityNotFoundException("Товар", product_id)

        # Проверка, заказывал ли пользователь этот товар
        if not await self._user_ordered_product(user_id, product_id):
            raise BusinessRuleException("Можно оставлять отзывы только на заказанные товары")

        # Проверка, не оставлял ли пользователь уже отзыв
        if await self.review_repository.user_has_reviewed_product(user_id, product_id):
            raise BusinessRuleException("Вы уже оставляли отзыв на этот товар")

        # Создание отзыва
        review_entity = Review.create(
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            comment=comment
        )

        return await self.review_repository.create(review_entity)

    async def get_product_reviews(self, product_id: str, skip: int = 0, limit: int = 50) -> List[Review]:
        """Получить отзывы по товару"""
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise EntityNotFoundException("Товар", product_id)

        return await self.review_repository.get_by_product_id(product_id, skip, limit)

    async def get_user_reviews(self, user_id: str, skip: int = 0, limit: int = 50) -> List[Review]:
        """Получить отзывы пользователя"""
        return await self.review_repository.get_by_user_id(user_id, skip, limit)

    async def update_review(
            self,
            review_id: str,
            user_id: str,
            rating: Optional[int] = None,
            comment: Optional[str] = None
    ) -> Review:
        """Обновить отзыв"""
        review = await self.review_repository.get_by_id(review_id)
        if not review:
            raise EntityNotFoundException("Отзыв", review_id)

        # Проверка прав доступа
        if review.user_id != user_id:
            raise BusinessRuleException("Можно редактировать только свои отзывы")

        # Явное указание типа словаря
        update_data: Dict[str, Any] = {}  # ← Ключевое исправление

        if rating is not None:
            if not (1 <= rating <= 5):
                raise BusinessRuleException("Рейтинг должен быть от 1 до 5")
            update_data['rating'] = rating

        if comment is not None:
            update_data['comment'] = comment

        return await self.review_repository.update(review_id, update_data)

    async def delete_review(self, review_id: str, user_id: str) -> bool:
        """Удалить отзыв"""
        review = await self.review_repository.get_by_id(review_id)
        if not review:
            raise EntityNotFoundException("Отзыв", review_id)

        # Проверка прав доступа
        if review.user_id != user_id:
            raise BusinessRuleException("Можно удалять только свои отзывы")

        return await self.review_repository.delete(review_id)

    async def get_product_rating_stats(self, product_id: str) -> dict:
        """Получить статистику рейтингов товара"""
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise EntityNotFoundException("Товар", product_id)

        return await self.review_repository.get_product_rating_stats(product_id)

    async def _user_ordered_product(self, user_id: str, product_id: str) -> bool:
        """Проверить, заказывал ли пользователь товар"""
        # Получаем все заказы пользователя
        orders = await self.order_repository.get_by_user_id(user_id, 0, 1000)

        for order in orders:
            # Проверяем, есть ли товар в заказе
            for item in order.items:
                if item.product.id == product_id:
                    return True

        return False