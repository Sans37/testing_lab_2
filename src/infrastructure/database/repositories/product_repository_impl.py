# src/infrastructure/database/repositories/product_repository_impl.py
from typing import List, Optional
from sqlalchemy.orm import Session
from src.core.entities.product import Product
from src.core.repositories.product_repository import ProductRepository
from src.core.exceptions.repository_exceptions import EntityNotFoundException
from src.infrastructure.database.models.product_model import ProductModel


class ProductRepositoryImpl(ProductRepository):
    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, product_id: str) -> Optional[Product]:
        product_model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        return product_model.to_entity() if product_model else None

    async def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            category_id: Optional[str] = None,
            available_only: bool = False
    ) -> List[Product]:
        query = self.db.query(ProductModel)

        if category_id:
            query = query.filter(ProductModel.category_id == category_id)

        if available_only:
            query = query.filter(ProductModel.available)  # Исправлено: убрано == True

        product_models = query.offset(skip).limit(limit).all()
        return [product_model.to_entity() for product_model in product_models]

    async def create(self, product_entity) -> Product:
        product_model = ProductModel.from_entity(product_entity)
        self.db.add(product_model)
        self.db.commit()
        self.db.refresh(product_model)
        return product_model.to_entity()

    async def update(self, product_id: str, product_data: dict) -> Product:
        product_model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product_model:
            raise EntityNotFoundException("Товар", product_id)

        for key, value in product_data.items():
            if hasattr(product_model, key):
                setattr(product_model, key, value)

        self.db.commit()
        self.db.refresh(product_model)
        return product_model.to_entity()

    async def delete(self, product_id: str) -> bool:
        product_model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product_model:
            raise EntityNotFoundException("Товар", product_id)

        self.db.delete(product_model)
        self.db.commit()
        return True

    async def update_availability(self, product_id: str, available: bool) -> Product:
        product_model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product_model:
            raise EntityNotFoundException("Товар", product_id)

        product_model.available = available
        self.db.commit()
        self.db.refresh(product_model)
        return product_model.to_entity()

    async def search_by_name(self, name: str, skip: int = 0, limit: int = 50) -> List[Product]:
        product_models = self.db.query(ProductModel).filter(
            ProductModel.name.ilike(f"%{name}%")
        ).offset(skip).limit(limit).all()

        return [product_model.to_entity() for product_model in product_models]

    async def get_by_category(self, category_id: str, skip: int = 0, limit: int = 100) -> List[Product]:
        product_models = self.db.query(ProductModel).filter(
            ProductModel.category_id == category_id
        ).offset(skip).limit(limit).all()

        return [product_model.to_entity() for product_model in product_models]