# src/infrastructure/database/models/category_model.py
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.infrastructure.database.database import Base


class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Связь как строковая ссылка
    products = relationship("ProductModel", back_populates="category")

    def to_entity(self):
        from src.core.entities.category import Category
        return Category(
            id=self.id,
            name=self.name,
            description=self.description or "",
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @classmethod
    def from_entity(cls, category_entity):
        return cls(
            id=category_entity.id,
            name=category_entity.name,
            description=category_entity.description
        )