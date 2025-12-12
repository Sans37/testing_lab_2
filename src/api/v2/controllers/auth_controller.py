# src/api/v2/controllers/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from src.core.services.auth_service import AuthService
from src.api.v2.dependencies import get_auth_service
from src.api.v2.dtos.request_dtos import UserRegisterRequest, UserLoginRequest
from src.api.v2.dtos.response_dtos import AuthResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Регистрация нового пользователя"""
    try:
        result = await auth_service.register_user(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password,
            phone=user_data.phone,
            address=user_data.address
        )
        return AuthResponse(
            token=result["token"],
            user=UserResponse(**result["user"].to_dict())
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=AuthResponse)
async def login(
    login_data: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Авторизация пользователя"""
    try:
        result = await auth_service.login_user(
            email=login_data.email,
            password=login_data.password
        )
        return AuthResponse(
            token=result["token"],
            user=UserResponse(**result["user"].to_dict())
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )