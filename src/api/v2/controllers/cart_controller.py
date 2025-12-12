# src/api/v2/controllers/cart_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from src.core.services.cart_service import CartService
from src.core.entities.user import User
from src.api.v2.dependencies import get_cart_service, get_current_user
from src.api.v2.dtos.request_dtos import CartItemAddRequest, CartItemUpdateRequest
from src.api.v2.dtos.response_dtos import CartResponse

router = APIRouter(prefix="/carts", tags=["Carts"])

@router.get("/", response_model=CartResponse)
async def get_cart(
    cart_service: CartService = Depends(get_cart_service),
    current_user: User = Depends(get_current_user)
):
    """Получить корзину пользователя"""
    try:
        cart = await cart_service.get_user_cart(current_user.id)
        return CartResponse(**cart.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/items", response_model=CartResponse)
async def add_to_cart(
    item_data: CartItemAddRequest,
    cart_service: CartService = Depends(get_cart_service),
    current_user: User = Depends(get_current_user)
):
    """Добавить товар в корзину"""
    try:
        cart = await cart_service.add_to_cart(
            user_id=current_user.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity
        )
        return CartResponse(**cart.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/items/{product_id}", response_model=CartResponse)
async def update_cart_item(
    product_id: str,
    item_data: CartItemUpdateRequest,
    cart_service: CartService = Depends(get_cart_service),
    current_user: User = Depends(get_current_user)
):
    """Обновить количество товара в корзине"""
    try:
        cart = await cart_service.update_cart_item(
            user_id=current_user.id,
            product_id=product_id,
            quantity=item_data.quantity
        )
        return CartResponse(**cart.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/items/{product_id}", response_model=CartResponse)
async def remove_from_cart(
    product_id: str,
    cart_service: CartService = Depends(get_cart_service),
    current_user: User = Depends(get_current_user)
):
    """Удалить товар из корзины"""
    try:
        cart = await cart_service.remove_from_cart(
            user_id=current_user.id,
            product_id=product_id
        )
        return CartResponse(**cart.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/", response_model=CartResponse)
async def clear_cart(
    cart_service: CartService = Depends(get_cart_service),
    current_user: User = Depends(get_current_user)
):
    """Очистить корзину"""
    try:
        cart = await cart_service.clear_cart(current_user.id)
        return CartResponse(**cart.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )