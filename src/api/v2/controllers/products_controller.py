# src/api/v2/controllers/products_controller.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from src.core.services.product_service import ProductService
from src.core.entities.user import User
from src.api.v2.dependencies import get_product_service, get_current_user
from src.api.v2.dtos.request_dtos import ProductCreateRequest, ProductUpdateRequest
from src.api.v2.dtos.response_dtos import ProductResponse, PaginationResponse

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=dict)
async def get_products(
        category: Optional[str] = Query(None, description="ID категории для фильтрации"),
        pagesNum: int = Query(1, ge=1, description="Номер страницы"),
        elemCount: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
        product_service: ProductService = Depends(get_product_service)
):
    """Получить список товаров"""
    try:
        skip = (pagesNum - 1) * elemCount
        products = await product_service.get_all_products(
            skip=skip,
            limit=elemCount,
            category_id=category,
            available_only=False
        )

        # Преобразуем в DTO
        products_dto = [ProductResponse(**product.to_dict()) for product in products]

        # В реальном приложении нужно получить общее количество для пагинации
        total_pages = 1  # Заглушка

        return {
            "products": products_dto,
            "pagination": PaginationResponse(
                total_pages=total_pages,
                cur_page=pagesNum
            )
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
        product_id: str,
        product_service: ProductService = Depends(get_product_service)
):
    """Получить товар по ID"""
    try:
        product = await product_service.get_product(product_id)
        return ProductResponse(**product.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
        product_data: ProductCreateRequest,
        product_service: ProductService = Depends(get_product_service),
        current_user: User = Depends(get_current_user)
):
    """Создать новый товар (только для админов)"""
    try:
        if not current_user.is_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Требуются права администратора"
            )

        product = await product_service.create_product(
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            category_id=product_data.category_id,
            ingredients=product_data.ingredients,
            available=product_data.available,
            image=product_data.image
        )
        return ProductResponse(**product.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
        product_id: str,
        product_data: ProductUpdateRequest,
        product_service: ProductService = Depends(get_product_service),
        current_user: User = Depends(get_current_user)
):
    """Обновить товар (только для админов)"""
    try:
        if not current_user.is_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Требуются права администратора"
            )

        update_dict = product_data.dict(exclude_unset=True)
        product = await product_service.update_product(product_id, update_dict)
        return ProductResponse(**product.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{product_id}")
async def delete_product(
        product_id: str,
        product_service: ProductService = Depends(get_product_service),
        current_user: User = Depends(get_current_user)
):
    """Удалить товар (только для админов)"""
    try:
        if not current_user.is_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Требуются права администратора"
            )

        await product_service.delete_product(product_id)
        return {"message": "Товар успешно удален"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )