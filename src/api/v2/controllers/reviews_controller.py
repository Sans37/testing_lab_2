# src/api/v2/controllers/reviews_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from src.core.services.review_service import ReviewService
from src.core.entities.user import User
from src.api.v2.dependencies import get_review_service, get_current_user
from src.api.v2.dtos.request_dtos import ReviewCreateRequest, ReviewUpdateRequest
from src.api.v2.dtos.response_dtos import ReviewResponse

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
        review_data: ReviewCreateRequest,
        review_service: ReviewService = Depends(get_review_service),
        current_user: User = Depends(get_current_user)
):
    """Добавить отзыв"""
    try:
        review = await review_service.create_review(
            user_id=current_user.id,
            product_id=review_data.product_id,
            rating=review_data.rating,
            comment=review_data.comment
        )
        return ReviewResponse(**review.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/product/{product_id}", response_model=dict)
async def get_product_reviews(
        product_id: str,
        review_service: ReviewService = Depends(get_review_service)
):
    """Получить отзывы по товару"""
    try:
        reviews = await review_service.get_product_reviews(product_id)
        reviews_dto = [ReviewResponse(**review.to_dict()) for review in reviews]

        # Получаем статистику рейтингов
        stats = await review_service.get_product_rating_stats(product_id)

        return {
            "reviews": reviews_dto,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/my", response_model=dict)
async def get_my_reviews(
        review_service: ReviewService = Depends(get_review_service),
        current_user: User = Depends(get_current_user)
):
    """Получить отзывы текущего пользователя"""
    try:
        reviews = await review_service.get_user_reviews(current_user.id)
        reviews_dto = [ReviewResponse(**review.to_dict()) for review in reviews]

        return {
            "reviews": reviews_dto
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
        review_id: str,
        review_data: ReviewUpdateRequest,
        review_service: ReviewService = Depends(get_review_service),
        current_user: User = Depends(get_current_user)
):
    """Обновить отзыв"""
    try:
        update_dict = review_data.dict(exclude_unset=True)
        review = await review_service.update_review(
            review_id=review_id,
            user_id=current_user.id,
            rating=update_dict.get('rating'),
            comment=update_dict.get('comment')
        )
        return ReviewResponse(**review.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{review_id}")
async def delete_review(
        review_id: str,
        review_service: ReviewService = Depends(get_review_service),
        current_user: User = Depends(get_current_user)
):
    """Удалить отзыв"""
    try:
        await review_service.delete_review(review_id, current_user.id)
        return {"message": "Отзыв успешно удален"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )