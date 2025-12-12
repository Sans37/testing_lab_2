from dataclasses import dataclass
from datetime import datetime
import uuid
from typing import Optional


@dataclass
class Category:
    id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, name: str, description: str = "") -> 'Category':
        now = datetime.now()
        category_id = f"cat_{uuid.uuid4()}"

        return cls(
            id=category_id,
            name=name,
            description=description,
            created_at=now,
            updated_at=now
        )

    def update(self, name: Optional[str] = None, description: Optional[str] = None) -> None:
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }