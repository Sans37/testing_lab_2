from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import uuid
from .category import Category
from .ingredient import Ingredient


@dataclass
class Product:
    id: str
    name: str
    description: str
    price: float
    category: Category
    ingredients: List[Ingredient]
    available: bool
    created_at: datetime
    updated_at: datetime
    image: Optional[str] = None

    @classmethod
    def create(
            cls,
            name: str,
            description: str,
            price: float,
            category: Category,
            ingredients: List[Ingredient],
            available: bool = True,
            image: Optional[str] = None
    ) -> 'Product':
        now = datetime.now()
        product_id = f"prod_{uuid.uuid4()}"

        return cls(
            id=product_id,
            name=name,
            description=description,
            price=price,
            category=category,
            ingredients=ingredients,
            available=available,
            created_at=now,
            updated_at=now,
            image=image
        )

    def update(
            self,
            name: Optional[str] = None,
            description: Optional[str] = None,
            price: Optional[float] = None,
            available: Optional[bool] = None,
            image: Optional[str] = None
    ) -> None:
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if price is not None:
            self.price = price
        if available is not None:
            self.available = available
        if image is not None:
            self.image = image
        self.updated_at = datetime.now()

    def update_category(self, category: Category) -> None:
        self.category = category
        self.updated_at = datetime.now()

    def update_ingredients(self, ingredients: List[Ingredient]) -> None:
        self.ingredients = ingredients
        self.updated_at = datetime.now()

    def is_available(self) -> bool:
        return self.available

    def get_price(self) -> float:
        return self.price

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category": self.category.to_dict() if hasattr(self.category, 'to_dict') else self.category,
            "ingredients": [ing.to_dict() if hasattr(ing, 'to_dict') else ing for ing in self.ingredients],
            "image": self.image,
            "available": self.available,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }