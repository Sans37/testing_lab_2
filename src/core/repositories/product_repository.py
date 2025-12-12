# src/core/repositories/product_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.entities.product import Product


class ProductRepository(ABC):
    """Интерфейс репозитория для товаров"""

    @abstractmethod
    async def get_by_id(self, product_id: str) -> Optional[Product]:
        """Получить товар по ID"""
        pass

    @abstractmethod
    async def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            category_id: Optional[str] = None,
            available_only: bool = False
    ) -> List[Product]:
        """Получить все товары с фильтрацией"""
        pass

    @abstractmethod
    async def create(self, product: Product) -> Product:
        """Создать новый товар"""
        pass

    @abstractmethod
    async def update(self, product_id: str, product_data: dict) -> Product:
        """Обновить данные товара"""
        pass

    @abstractmethod
    async def delete(self, product_id: str) -> bool:
        """Удалить товар"""
        pass

    @abstractmethod
    async def update_availability(self, product_id: str, available: bool) -> Product:
        """Обновить доступность товара"""
        pass

    @abstractmethod
    async def search_by_name(self, name: str, skip: int = 0, limit: int = 50) -> List[Product]:
        """Поиск товаров по названию"""
        pass

    @abstractmethod
    async def get_by_category(self, category_id: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """Получить товары по категории"""
        pass