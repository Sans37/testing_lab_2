# src/api/v2/dtos/response_dtos.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base DTOs
class PaginationResponse(BaseModel):
    total_pages: int
    cur_page: int

# User DTOs
class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    address: str
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Auth DTOs
class AuthResponse(BaseModel):
    token: str
    user: UserResponse

# Category DTOs
class CategoryResponse(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Product DTOs
class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: CategoryResponse
    ingredients: List[str]
    image: Optional[str] = None
    available: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Cart DTOs
class CartItemResponse(BaseModel):
    product: ProductResponse
    quantity: int
    subtotal: float

class CartResponse(BaseModel):
    id: str
    user_id: str
    items: List[CartItemResponse]
    total: float
    created_at: datetime
    updated_at: datetime

# Order DTOs
class OrderItemResponse(BaseModel):
    product: ProductResponse
    quantity: int
    price: float

class OrderResponse(BaseModel):
    id: str
    user_id: str
    items: List[OrderItemResponse]
    total: float
    status: str
    delivery_address: str
    phone: str
    comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# Review DTOs
class ReviewResponse(BaseModel):
    id: str
    user_id: str
    product_id: str
    rating: int
    comment: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# External integration DTOs
class ExternalPostResponse(BaseModel):
    id: int
    user_id: int
    title: str
    body: str
    source: str
