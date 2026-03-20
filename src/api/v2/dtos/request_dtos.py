# src/api/v2/dtos/request_dtos.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List

# Auth DTOs
class UserRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str
    address: str

    @validator('password')
    def password_length(cls, v):
        if len(v) < 6:
            raise ValueError('Пароль должен содержать минимум 6 символов')
        return v

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

# Two-factor DTOs
class TwoFactorVerifyRequest(BaseModel):
    session_id: str
    code: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    otp_code: str

class PasswordChangeOtpRequest(BaseModel):
    email: EmailStr

class UnlockRequest(BaseModel):
    email: EmailStr

class UnlockConfirmRequest(BaseModel):
    email: EmailStr
    code: str

# Product DTOs
class ProductCreateRequest(BaseModel):
    name: str
    description: str
    price: float
    category_id: str
    ingredients: List[str] = []
    image: Optional[str] = None
    available: bool = True

    @validator('price')
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError('Цена должна быть положительной')
        return v

class ProductUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[str] = None
    ingredients: Optional[List[str]] = None
    image: Optional[str] = None
    available: Optional[bool] = None

    @validator('price')
    def price_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Цена должна быть положительной')
        return v

# Category DTOs
class CategoryCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# Cart DTOs
class CartItemAddRequest(BaseModel):
    product_id: str
    quantity: int = 1

    @validator('quantity')
    def quantity_positive(cls, v):
        if v <= 0:
            raise ValueError('Количество должно быть положительным')
        return v

class CartItemUpdateRequest(BaseModel):
    quantity: int

    @validator('quantity')
    def quantity_positive(cls, v):
        if v <= 0:
            raise ValueError('Количество должно быть положительным')
        return v

# Order DTOs
class OrderCreateRequest(BaseModel):
    delivery_address: str
    phone: str
    comment: Optional[str] = None

class OrderStatusUpdateRequest(BaseModel):
    status: str

# Review DTOs
class ReviewCreateRequest(BaseModel):
    product_id: str
    rating: int
    comment: str

    @validator('rating')
    def rating_range(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Рейтинг должен быть от 1 до 5')
        return v

class ReviewUpdateRequest(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None

    @validator('rating')
    def rating_range(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Рейтинг должен быть от 1 до 5')
        return v
