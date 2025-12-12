# src/api/v2/dtos/__init__.py
from .request_dtos import (
    UserRegisterRequest, UserLoginRequest, ProductCreateRequest,
    ProductUpdateRequest, CategoryCreateRequest, CategoryUpdateRequest,
    CartItemAddRequest, CartItemUpdateRequest, OrderCreateRequest,
    OrderStatusUpdateRequest, ReviewCreateRequest, ReviewUpdateRequest
)

from .response_dtos import (
    UserResponse, ProductResponse, CategoryResponse, CartResponse,
    CartItemResponse, OrderResponse, OrderItemResponse, ReviewResponse,
    AuthResponse, PaginationResponse
)

__all__ = [
    # Request DTOs
    "UserRegisterRequest", "UserLoginRequest", "ProductCreateRequest",
    "ProductUpdateRequest", "CategoryCreateRequest", "CategoryUpdateRequest",
    "CartItemAddRequest", "CartItemUpdateRequest", "OrderCreateRequest",
    "OrderStatusUpdateRequest", "ReviewCreateRequest", "ReviewUpdateRequest",

    # Response DTOs
    "UserResponse", "ProductResponse", "CategoryResponse", "CartResponse",
    "CartItemResponse", "OrderResponse", "OrderItemResponse", "ReviewResponse",
    "AuthResponse", "PaginationResponse"
]