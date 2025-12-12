from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.entities.category import Category


class CategoryRepository(ABC):
    """Интерфейс репозитория для категорий"""

    @abstractmethod
    async def get_by_id(self, category_id: str) -> Optional[Category]:
        """Получить категорию по ID"""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Category]:
        """Получить категорию по названию"""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Category]:
        """Получить все категории"""
        pass

    @abstractmethod
    async def create(self, category: Category) -> Category:
        """Создать новую категорию"""
        pass

    @abstractmethod
    async def update(self, category_id: str, category_data: dict) -> Category:
        """Обновить данные категории"""
        pass

    @abstractmethod
    async def delete(self, category_id: str) -> bool:
        """Удалить категорию"""
        pass

    @abstractmethod
    async def exists_by_name(self, name: str) -> bool:
        """Проверить существование категории по названию"""
        pass