# src/infrastructure/database/models/review_model.py
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.infrastructure.database.database import Base


class ReviewModel(Base):
    __tablename__ = "reviews"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Связи как строковые ссылки
    user = relationship("UserModel", back_populates="reviews")
    product = relationship("ProductModel", back_populates="reviews")

    def to_entity(self):
        from src.core.entities.review import Review
        return Review(
            id=self.id,
            user_id=self.user_id,
            product_id=self.product_id,
            rating=self.rating,
            comment=self.comment or "",
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @classmethod
    def from_entity(cls, review_entity):
        return cls(
            id=review_entity.id,
            user_id=review_entity.user_id,
            product_id=review_entity.product_id,
            rating=review_entity.rating,
            comment=review_entity.comment
        )