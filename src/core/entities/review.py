from dataclasses import dataclass
from datetime import datetime
import uuid
from typing import Optional


@dataclass
class Review:
    id: str
    user_id: str
    product_id: str
    rating: int  # 1-5
    comment: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, user_id: str, product_id: str, rating: int, comment: str) -> 'Review':
        now = datetime.now()
        review_id = f"review_{uuid.uuid4()}"

        if rating < 1 or rating > 5:
            raise ValueError("Рейтинг должен быть от 1 до 5")

        return cls(
            id=review_id,
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            comment=comment,
            created_at=now,
            updated_at=now
        )

    def update(self, rating: Optional[int] = None, comment: Optional[str] = None) -> None:
        if rating is not None:
            if rating < 1 or rating > 5:
                raise ValueError("Рейтинг должен быть от 1 до 5")
            self.rating = rating

        if comment is not None:
            self.comment = comment

        self.updated_at = datetime.now()

    def get_rating(self) -> int:
        return self.rating

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }