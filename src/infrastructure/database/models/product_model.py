# src/infrastructure/database/models/product_model.py
from sqlalchemy import Column, String, DateTime, Text, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.infrastructure.database.database import Base


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category_id = Column(String, ForeignKey("categories.id"), nullable=False)
    ingredients = Column(JSON)
    image = Column(String(255))
    available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Связи как строковые ссылки
    category = relationship("CategoryModel", back_populates="products")
    reviews = relationship("ReviewModel", back_populates="product")

    def to_entity(self):
        from src.core.entities.product import Product
        from src.core.entities.category import Category

        category_entity = Category(
            id=self.category.id,
            name=self.category.name,
            description=self.category.description or "",
            created_at=self.category.created_at,
            updated_at=self.category.updated_at
        )

        ingredients = self.ingredients or []

        return Product(
            id=self.id,
            name=self.name,
            description=self.description or "",
            price=self.price,
            category=category_entity,
            ingredients=ingredients,
            available=self.available,
            created_at=self.created_at,
            updated_at=self.updated_at,
            image=self.image
        )

    @classmethod
    def from_entity(cls, product_entity):
        return cls(
            id=product_entity.id,
            name=product_entity.name,
            description=product_entity.description,
            price=product_entity.price,
            category_id=product_entity.category.id,
            ingredients=product_entity.ingredients,
            available=product_entity.available,
            image=product_entity.image
        )