from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.entities.review import Review


class ReviewRepository(ABC):
    """Интерфейс репозитория для отзывов"""

    @abstractmethod
    async def get_by_id(self, review_id: str) -> Optional[Review]:
        """Получить отзыв по ID"""
        pass

    @abstractmethod
    async def get_by_product_id(self, product_id: str, skip: int = 0, limit: int = 50) -> List[Review]:
        """Получить отзывы по товару"""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: str, skip: int = 0, limit: int = 50) -> List[Review]:
        """Получить отзывы пользователя"""
        pass

    @abstractmethod
    async def create(self, review: Review) -> Review:
        """Создать новый отзыв"""
        pass

    @abstractmethod
    async def update(self, review_id: str, review_data: dict) -> Review:
        """Обновить отзыв"""
        pass

    @abstractmethod
    async def delete(self, review_id: str) -> bool:
        """Удалить отзыв"""
        pass

    @abstractmethod
    async def get_product_rating_stats(self, product_id: str) -> dict:
        """Получить статистику рейтингов для товара"""
        pass

    @abstractmethod
    async def user_has_reviewed_product(self, user_id: str, product_id: str) -> bool:
        """Проверить, оставлял ли пользователь отзыв на товар"""
        pass