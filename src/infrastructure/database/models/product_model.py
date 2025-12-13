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
        from src.core.entities.ingredient import Ingredient
        from datetime import datetime

        category_entity = Category(
            id=self.category.id,
            name=self.category.name,
            description=self.category.description or "",
            created_at=self.category.created_at,
            updated_at=self.category.updated_at
        )

        # Преобразуем JSON обратно в объекты Ingredient
        ingredients = []
        if self.ingredients:
            for ing_data in self.ingredients:
                # Парсим строки дат обратно в datetime объекты
                created_at = datetime.fromisoformat(ing_data['created_at']) if ing_data.get(
                    'created_at') else datetime.now()
                updated_at = datetime.fromisoformat(ing_data['updated_at']) if ing_data.get(
                    'updated_at') else datetime.now()

                ingredients.append(Ingredient(
                    id=ing_data['id'],
                    name=ing_data['name'],
                    allergen=ing_data['allergen'],
                    created_at=created_at,
                    updated_at=updated_at
                ))

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
        # Преобразуем ингредиенты в словари для JSON сериализации
        ingredients_data = []
        if product_entity.ingredients:
            for ingredient in product_entity.ingredients:
                # Используем метод to_dict из класса Ingredient
                if hasattr(ingredient, 'to_dict'):
                    ingredients_data.append(ingredient.to_dict())
                else:
                    # Если нет метода to_dict, создаем словарь вручную
                    ingredients_data.append({
                        "id": ingredient.id,
                        "name": ingredient.name,
                        "allergen": ingredient.allergen,
                        "created_at": ingredient.created_at.isoformat() if ingredient.created_at else None,
                        "updated_at": ingredient.updated_at.isoformat() if ingredient.updated_at else None
                    })

        return cls(
            id=product_entity.id,
            name=product_entity.name,
            description=product_entity.description,
            price=product_entity.price,
            category_id=product_entity.category.id if hasattr(product_entity.category, 'id') else product_entity.category,
            ingredients=ingredients_data,  # Теперь это список словарей, а не объектов
            available=product_entity.available,
            image=product_entity.image
        )