# src/infrastructure/database/repositories/review_repository_impl.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from src.core.entities.review import Review
from src.core.repositories.review_repository import ReviewRepository
from src.core.exceptions.repository_exceptions import EntityNotFoundException, DuplicateEntityException
from src.infrastructure.database.models.review_model import ReviewModel


class ReviewRepositoryImpl(ReviewRepository):
    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, review_id: str) -> Optional[Review]:
        review_model = self.db.query(ReviewModel).filter(ReviewModel.id == review_id).first()
        return review_model.to_entity() if review_model else None

    async def get_by_product_id(self, product_id: str, skip: int = 0, limit: int = 50) -> List[Review]:
        review_models = self.db.query(ReviewModel).filter(
            ReviewModel.product_id == product_id
        ).order_by(desc(ReviewModel.created_at)).offset(skip).limit(limit).all()

        return [review_model.to_entity() for review_model in review_models]

    async def get_by_user_id(self, user_id: str, skip: int = 0, limit: int = 50) -> List[Review]:
        review_models = self.db.query(ReviewModel).filter(
            ReviewModel.user_id == user_id
        ).order_by(desc(ReviewModel.created_at)).offset(skip).limit(limit).all()

        return [review_model.to_entity() for review_model in review_models]

    async def create(self, review_entity) -> Review:
        # Проверка на дубликат отзыва
        existing_review = self.db.query(ReviewModel).filter(
            ReviewModel.user_id == review_entity.user_id,
            ReviewModel.product_id == review_entity.product_id
        ).first()

        if existing_review:
            raise DuplicateEntityException("Отзыв", "товар", review_entity.product_id)

        review_model = ReviewModel.from_entity(review_entity)
        self.db.add(review_model)
        self.db.commit()
        self.db.refresh(review_model)
        return review_model.to_entity()

    async def update(self, review_id: str, review_data: dict) -> Review:
        review_model = self.db.query(ReviewModel).filter(ReviewModel.id == review_id).first()
        if not review_model:
            raise EntityNotFoundException("Отзыв", review_id)

        for key, value in review_data.items():
            if hasattr(review_model, key):
                setattr(review_model, key, value)

        self.db.commit()
        self.db.refresh(review_model)
        return review_model.to_entity()

    async def delete(self, review_id: str) -> bool:
        review_model = self.db.query(ReviewModel).filter(ReviewModel.id == review_id).first()
        if not review_model:
            raise EntityNotFoundException("Отзыв", review_id)

        self.db.delete(review_model)
        self.db.commit()
        return True

    async def get_product_rating_stats(self, product_id: str) -> dict:
        stats = self.db.query(
            func.count(ReviewModel.id).label('total_reviews'),
            func.avg(ReviewModel.rating).label('average_rating'),
            func.min(ReviewModel.rating).label('min_rating'),
            func.max(ReviewModel.rating).label('max_rating')
        ).filter(ReviewModel.product_id == product_id).first()

        return {
            'total_reviews': stats.total_reviews or 0,
            'average_rating': float(stats.average_rating or 0),
            'min_rating': stats.min_rating or 0,
            'max_rating': stats.max_rating or 0
        }

    async def user_has_reviewed_product(self, user_id: str, product_id: str) -> bool:
        review_model = self.db.query(ReviewModel).filter(
            ReviewModel.user_id == user_id,
            ReviewModel.product_id == product_id
        ).first()

        return review_model is not None