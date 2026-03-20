# src/api/v2/controllers/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, status, Header
import os
from src.core.services.auth_service import AuthService
from src.core.exceptions import AuthenticationException
from src.api.v2.dependencies import get_auth_service
from src.api.v2.dtos.request_dtos import (
    UserRegisterRequest,
    UserLoginRequest,
    TwoFactorVerifyRequest,
    PasswordChangeRequest,
    UnlockRequest,
    UnlockConfirmRequest,
)
from src.api.v2.dtos.response_dtos import AuthResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

def _auth_response_to_dict(resp: AuthResponse) -> dict:
    dump = getattr(resp, "model_dump", None)
    if callable(dump):
        return dump()
    return resp.dict()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Р РµРіРёСЃС‚СЂР°С†РёСЏ РЅРѕРІРѕРіРѕ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ"""
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


@router.post("/login", response_model=dict)
async def login(
    login_data: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
    x_2fa_required: str = Header(default=""),
):
    """РђРІС‚РѕСЂРёР·Р°С†РёСЏ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ (c 2FA)"""
    try:
        original_flag = auth_service.two_fa_enabled
        if os.getenv("APP_ENV", "") == "test" and x_2fa_required:
            auth_service.two_fa_enabled = x_2fa_required.lower() == "true"

        result = await auth_service.login_user(
            email=login_data.email,
            password=login_data.password
        )
        auth_service.two_fa_enabled = original_flag

        if result.get("two_fa_required"):
            return {
                "two_fa_required": True,
                "session_id": result["session_id"]
            }

        return _auth_response_to_dict(
            AuthResponse(
                token=result["token"],
                user=UserResponse(**result["user"].to_dict()),
            )
        )
    except AuthenticationException as e:
        if str(e) == "ACCOUNT_LOCKED":
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="ACCOUNT_LOCKED"
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/verify-2fa", response_model=AuthResponse)
async def verify_2fa(
    data: TwoFactorVerifyRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Подтверждение 2FA кода"""
    try:
        result = await auth_service.verify_2fa(
            session_id=data.session_id,
            code=data.code
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


@router.post("/request-password-change-otp")
async def request_password_change_otp(
    auth_service: AuthService = Depends(get_auth_service),
    authorization: str = Header(default="")
):
    """Запрос OTP кода для смены пароля"""
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
        token = authorization.split(" ", 1)[1]
        payload = auth_service.verify_token(token)
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        auth_service.generate_email_otp(email, "password_change")
        return {"message": "OTP_SENT"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/change-password")
async def confirm_password_change(
    data: PasswordChangeRequest,
    auth_service: AuthService = Depends(get_auth_service),
    authorization: str = Header(default="")
):
    """Подтверждение смены пароля"""
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
        token = authorization.split(" ", 1)[1]
        payload = auth_service.verify_token(token)
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        await auth_service.change_password(
            email=email,
            current_password=data.current_password,
            new_password=data.new_password,
            otp_code=data.otp_code
        )
        return {"message": "PASSWORD_CHANGED"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/unlock/request")
async def request_unlock(
    data: UnlockRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Запрос кода восстановления после блокировки"""
    try:
        auth_service.generate_email_otp(data.email, "unlock")
        return {"message": "UNLOCK_OTP_SENT"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/unlock/confirm")
async def confirm_unlock(
    data: UnlockConfirmRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Подтверждение восстановления после блокировки"""
    try:
        await auth_service.unlock_account(data.email, data.code)
        return {"message": "UNLOCKED"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/test-otp")
async def test_get_otp(
    email: str = "",
    session_id: str = "",
    auth_service: AuthService = Depends(get_auth_service)
):
    """Тестовый endpoint для получения OTP (только APP_ENV=test)"""
    if os.getenv("APP_ENV", "") != "test":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if session_id:
        return {"code": auth_service.test_get_otp_for_session(session_id)}
    if email:
        return {"code": auth_service.test_get_otp_for_email(email)}
    return {"code": ""}
