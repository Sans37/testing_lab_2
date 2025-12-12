from dataclasses import dataclass
from datetime import datetime
import uuid
from typing import Optional


@dataclass
class Ingredient:
    id: str
    name: str
    allergen: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, name: str, allergen: bool = False) -> 'Ingredient':
        now = datetime.now()
        ingredient_id = f"ing_{uuid.uuid4()}"

        return cls(
            id=ingredient_id,
            name=name,
            allergen=allergen,
            created_at=now,
            updated_at=now
        )

    def update(self, name: Optional[str] = None, allergen: Optional[bool] = None) -> None:
        if name is not None:
            self.name = name
        if allergen is not None:
            self.allergen = allergen
        self.updated_at = datetime.now()

    def is_allergen(self) -> bool:
        return self.allergen

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "allergen": self.allergen,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }