# src/core/services/product_service.py
from typing import List, Optional
from src.core.entities.product import Product
from src.core.repositories.product_repository import ProductRepository
from src.core.repositories.category_repository import CategoryRepository
from src.core.exceptions import EntityNotFoundException, ValidationException


class ProductService:
    """Сервис для работы с товарами"""

    def __init__(
            self,
            product_repository: ProductRepository,
            category_repository: CategoryRepository
    ):
        self.product_repository = product_repository
        self.category_repository = category_repository

    async def get_product(self, product_id: str) -> Product:
        """Получить товар по ID"""
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise EntityNotFoundException("Товар", product_id)
        return product

    async def get_all_products(
            self,
            skip: int = 0,
            limit: int = 100,
            category_id: Optional[str] = None,
            available_only: bool = False
    ) -> List[Product]:
        """Получить все товары с фильтрацией"""
        return await self.product_repository.get_all(
            skip=skip,
            limit=limit,
            category_id=category_id,
            available_only=available_only
        )

    async def create_product(
            self,
            name: str,
            description: str,
            price: float,
            category_id: str,
            ingredients: List,
            available: bool = True,
            image: Optional[str] = None
    ) -> Product:
        """Создать новый товар"""
        # Валидация цены
        if price <= 0:
            raise ValidationException("Цена должна быть положительной")

        # Проверка существования категории
        category = await self.category_repository.get_by_id(category_id)
        if not category:
            raise EntityNotFoundException("Категория", category_id)

        # Создание сущности товара
        product_entity = Product.create(
            name=name,
            description=description,
            price=price,
            category=category,
            ingredients=ingredients,
            available=available,
            image=image
        )

        return await self.product_repository.create(product_entity)

    async def update_product(
            self,
            product_id: str,
            update_data: dict
    ) -> Product:
        """Обновить товар"""
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise EntityNotFoundException("Товар", product_id)

        # Валидация цены если она обновляется
        if 'price' in update_data and update_data['price'] <= 0:
            raise ValidationException("Цена должна быть положительной")

        # Если обновляется категория, проверяем её существование
        if 'category_id' in update_data:
            category = await self.category_repository.get_by_id(update_data['category_id'])
            if not category:
                raise EntityNotFoundException("Категория", update_data['category_id'])

        return await self.product_repository.update(product_id, update_data)

    async def delete_product(self, product_id: str) -> bool:
        """Удалить товар"""
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise EntityNotFoundException("Товар", product_id)

        return await self.product_repository.delete(product_id)

    async def search_products(self, query: str, skip: int = 0, limit: int = 50) -> List[Product]:
        """Поиск товаров по названию"""
        if not query or len(query.strip()) < 2:
            raise ValidationException("Поисковый запрос должен содержать минимум 2 символа")

        return await self.product_repository.search_by_name(query.strip(), skip, limit)

    async def update_product_availability(self, product_id: str, available: bool) -> Product:
        """Обновить доступность товара"""
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise EntityNotFoundException("Товар", product_id)

        return await self.product_repository.update_availability(product_id, available)
