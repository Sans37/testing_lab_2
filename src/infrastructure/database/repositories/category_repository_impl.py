# src/infrastructure/database/repositories/category_repository_impl.py
from typing import List, Optional
from sqlalchemy.orm import Session
from src.core.entities.category import Category
from src.core.repositories.category_repository import CategoryRepository
from src.core.exceptions.repository_exceptions import EntityNotFoundException, DuplicateEntityException
from src.infrastructure.database.models.category_model import CategoryModel


class CategoryRepositoryImpl(CategoryRepository):
    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, category_id: str) -> Optional[Category]:
        category_model = self.db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        return category_model.to_entity() if category_model else None

    async def get_by_name(self, name: str) -> Optional[Category]:
        category_model = self.db.query(CategoryModel).filter(CategoryModel.name == name).first()
        return category_model.to_entity() if category_model else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Category]:
        category_models = self.db.query(CategoryModel).offset(skip).limit(limit).all()
        return [category_model.to_entity() for category_model in category_models]

    async def create(self, category_entity) -> Category:
        # Проверка на дубликат названия
        existing_category = await self.get_by_name(category_entity.name)
        if existing_category:
            raise DuplicateEntityException("Категория", "название", category_entity.name)

        category_model = CategoryModel.from_entity(category_entity)
        self.db.add(category_model)
        self.db.commit()
        self.db.refresh(category_model)
        return category_model.to_entity()

    async def update(self, category_id: str, category_data: dict) -> Category:
        category_model = self.db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        if not category_model:
            raise EntityNotFoundException("Категория", category_id)

        # Проверка на дубликат названия при обновлении
        if 'name' in category_data:
            existing_category = await self.get_by_name(category_data['name'])
            if existing_category and existing_category.id != category_id:
                raise DuplicateEntityException("Категория", "название", category_data['name'])

        for key, value in category_data.items():
            if hasattr(category_model, key):
                setattr(category_model, key, value)

        self.db.commit()
        self.db.refresh(category_model)
        return category_model.to_entity()

    async def delete(self, category_id: str) -> bool:
        category_model = self.db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        if not category_model:
            raise EntityNotFoundException("Категория", category_id)

        # Проверка на наличие товаров в категории
        from src.infrastructure.database.models.product_model import ProductModel
        product_count = self.db.query(ProductModel).filter(ProductModel.category_id == category_id).count()
        if product_count > 0:
            raise Exception("Невозможно удалить категорию, в ней есть товары")

        self.db.delete(category_model)
        self.db.commit()
        return True

    async def exists_by_name(self, name: str) -> bool:
        category_model = self.db.query(CategoryModel).filter(CategoryModel.name == name).first()
        return category_model is not None