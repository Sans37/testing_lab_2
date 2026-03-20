# src/core/services/auth_service.py
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta
import os
import uuid
from src.core.entities.user import User, UserRole
from src.core.repositories.user_repository import UserRepository
from src.core.exceptions import AuthenticationException, ValidationException
import traceback


# In-memory auth state for lab 4 (sufficient for single-process tests)
_LOGIN_ATTEMPTS = {}
_LOCKED_UNTIL = {}
_OTP_SESSIONS = {}  # session_id -> {email, code, expires_at}
_OTP_BY_EMAIL = {}  # email -> {code, expires_at, purpose}


def _now_utc() -> datetime:
    return datetime.utcnow()


def _generate_code() -> str:
    return f"{uuid.uuid4().int % 1000000:06d}"


def _is_expired(expires_at: datetime) -> bool:
    return _now_utc() > expires_at


class AuthService:
    def __init__(self, user_repository: UserRepository, secret_key: str, algorithm: str = "HS256"):
        self.user_repository = user_repository
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.max_attempts = int(os.getenv("AUTH_MAX_ATTEMPTS", "3"))
        self.lockout_seconds = int(os.getenv("AUTH_LOCKOUT_SECONDS", "60"))
        self.otp_ttl_seconds = int(os.getenv("AUTH_OTP_TTL_SECONDS", "300"))
        self.two_fa_enabled = os.getenv("TWO_FA_ENABLED", "false").lower() == "true"

    async def register_user(
            self,
            name: str,
            email: str,
            password: str,
            phone: str,
            address: str,
            role: UserRole = UserRole.CUSTOMER
    ) -> dict:
        try:
            print(f"рџ”§ РќР°С‡Р°Р»Рѕ СЂРµРіРёСЃС‚СЂР°С†РёРё: {email}")

            # Р’Р°Р»РёРґР°С†РёСЏ email
            if not self._is_valid_email(email):
                raise ValidationException("РќРµРІРµСЂРЅС‹Р№ С„РѕСЂРјР°С‚ email")
            print("вњ… Email РІР°Р»РёРґРµРЅ")

            # РџСЂРѕРІРµСЂРєР° СЃСѓС‰РµСЃС‚РІРѕРІР°РЅРёСЏ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ
            if await self.user_repository.exists_by_email(email):
                raise ValidationException("РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ СЃ С‚Р°РєРёРј email СѓР¶Рµ СЃСѓС‰РµСЃС‚РІСѓРµС‚")
            print("вњ… РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ РЅРµ СЃСѓС‰РµСЃС‚РІСѓРµС‚")

            # РҐСЌС€РёСЂРѕРІР°РЅРёРµ РїР°СЂРѕР»СЏ
            hashed_password = self._hash_password(password)
            print("вњ… РџР°СЂРѕР»СЊ С…СЌС€РёСЂРѕРІР°РЅ")

            # РЎРѕР·РґР°РЅРёРµ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ
            user_entity = User.create(
                name=name,
                email=email,
                password=hashed_password,
                phone=phone,
                address=address,
                role=role
            )
            print("вњ… РЎСѓС‰РЅРѕСЃС‚СЊ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ СЃРѕР·РґР°РЅР°")

            # РЎС…Р°РЅРµРЅРёРµ РІ СЂРµРїРѕР·РёС‚РѕСЂРёРё
            user = await self.user_repository.create(user_entity)
            print("вњ… РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ СЃРѕС…СЂР°РЅРµРЅ РІ Р‘Р”")

            # Р“РµРЅРµСЂР°С†РёСЏ С‚РѕРєРµРЅР°
            token = self._generate_token(user.id, user.email, user.role.value)
            print("вњ… РўРѕРєРµРЅ СЃРіРµРЅРµСЂРёСЂРѕРІР°РЅ")

            return {
                "user": user,
                "token": token
            }

        except Exception as e:
            print(f"вќЊ РћС€РёР±РєР° РІ register_user: {e}")
            print(traceback.format_exc())
            raise

    async def login_user(self, email: str, password: str) -> dict:
        try:
            # Check lockout
            locked_until = _LOCKED_UNTIL.get(email)
            if locked_until and _now_utc() < locked_until:
                raise AuthenticationException("ACCOUNT_LOCKED")

            user = await self.user_repository.get_by_email(email)
            if not user:
                raise AuthenticationException("РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ РЅРµ РЅР°Р№РґРµРЅ")

            if not self._verify_password(password, user.password):
                attempts = _LOGIN_ATTEMPTS.get(email, 0) + 1
                _LOGIN_ATTEMPTS[email] = attempts
                if attempts >= self.max_attempts:
                    _LOCKED_UNTIL[email] = _now_utc() + timedelta(seconds=self.lockout_seconds)
                    raise AuthenticationException("ACCOUNT_LOCKED")
                raise AuthenticationException("РќРµРІРµСЂРЅС‹Р№ РїР°СЂРѕР»СЊ")

            # Reset attempts after successful password check
            _LOGIN_ATTEMPTS[email] = 0

            if self.two_fa_enabled:
                session_id = f"2fa_{uuid.uuid4()}"
                code = _generate_code()
                _OTP_SESSIONS[session_id] = {
                    "email": email,
                    "code": code,
                    "expires_at": _now_utc() + timedelta(seconds=self.otp_ttl_seconds),
                }
                return {
                    "two_fa_required": True,
                    "session_id": session_id
                }

            # Р“РµРЅРµСЂР°С†РёСЏ С‚РѕРєРµРЅР°
            token = self._generate_token(user.id, user.email, user.role.value)

            return {
                "user": user,
                "token": token
            }
        except Exception as e:
            print(f"вќЊ РћС€РёР±+РєР° РІ login_user: {e}")
            print(traceback.format_exc())
            raise

    async def verify_2fa(self, session_id: str, code: str) -> dict:
        session = _OTP_SESSIONS.get(session_id)
        if not session:
            raise AuthenticationException("INVALID_2FA_SESSION")
        if _is_expired(session["expires_at"]):
            _OTP_SESSIONS.pop(session_id, None)
            raise AuthenticationException("EXPIRED_2FA_CODE")
        if session["code"] != code:
            raise AuthenticationException("INVALID_2FA_CODE")

        user = await self.user_repository.get_by_email(session["email"])
        if not user:
            raise AuthenticationException("РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ РЅРµ РЅР°Р№РґРµРЅ")

        _OTP_SESSIONS.pop(session_id, None)
        token = self._generate_token(user.id, user.email, user.role.value)
        return {"user": user, "token": token}

    def generate_email_otp(self, email: str, purpose: str) -> str:
        code = _generate_code()
        _OTP_BY_EMAIL[email] = {
            "code": code,
            "purpose": purpose,
            "expires_at": _now_utc() + timedelta(seconds=self.otp_ttl_seconds),
        }
        return code

    def verify_email_otp(self, email: str, code: str, purpose: str) -> None:
        entry = _OTP_BY_EMAIL.get(email)
        if not entry or entry["purpose"] != purpose:
            raise AuthenticationException("INVALID_OTP")
        if _is_expired(entry["expires_at"]):
            _OTP_BY_EMAIL.pop(email, None)
            raise AuthenticationException("EXPIRED_OTP")
        if entry["code"] != code:
            raise AuthenticationException("INVALID_OTP")
        _OTP_BY_EMAIL.pop(email, None)

    async def unlock_account(self, email: str, code: str) -> None:
        self.verify_email_otp(email, code, "unlock")
        _LOGIN_ATTEMPTS[email] = 0
        _LOCKED_UNTIL.pop(email, None)

    async def change_password(self, email: str, current_password: str, new_password: str, otp_code: str) -> None:
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise AuthenticationException("РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ РЅРµ РЅР°Р№РґРµРЅ")
        if not self._verify_password(current_password, user.password):
            raise AuthenticationException("РќРµРІРµСЂРЅС‹Р№ РїР°СЂРѕР»СЊ")

        self.verify_email_otp(email, otp_code, "password_change")
        hashed = self._hash_password(new_password)
        await self.user_repository.update(user.id, {"password": hashed})

    # Test helpers (only to be used in APP_ENV=test)
    def test_get_otp_for_email(self, email: str) -> str:
        entry = _OTP_BY_EMAIL.get(email)
        if not entry:
            return ""
        return entry["code"]

    def test_get_otp_for_session(self, session_id: str) -> str:
        session = _OTP_SESSIONS.get(session_id)
        if not session:
            return ""
        return session["code"]

    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except ExpiredSignatureError:
            raise AuthenticationException("РўРѕРєРµРЅ РёСЃС‚РµРє")
        except JWTError:
            raise AuthenticationException("РќРµРІРµСЂРЅС‹Р№ С‚РѕРєРµРЅ")

    def _hash_password(self, password: str) -> str:
        """Р’СЂРµРјРµРЅРЅРѕРµ С…СЌС€РёСЂРѕРІР°РЅРёРµ РїР°СЂРѕР»СЏ"""
        print(f"рџ”§ РҐСЌС€РёСЂРѕРІР°РЅРёРµ РїР°СЂРѕР»СЏ: {password}")
        return f"hashed_{password}"

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Р’СЂРµРјРµРЅРЅР°СЏ РїСЂРѕРІРµСЂРєР° РїР°СЂРѕР»СЏ"""
        print(f"рџ”§ РџСЂРѕРІРµСЂРєР° РїР°СЂРѕР»СЏ: {password} vs {hashed_password}")
        return f"hashed_{password}" == hashed_password

    def _generate_token(self, user_id: str, email: str, role: str) -> str:
        """Р“РµРЅРµСЂР°С†РёСЏ JWT С‚РѕРєРµРЅР°"""
        print(f"рџ”§ Р“РµРЅРµСЂР°С†РёСЏ С‚РѕРєРµРЅР° РґР»СЏ: {user_id}, {email}")
        payload = {
            "user_id": user_id,
            "email": email,
            "role": role,
            "exp": datetime.utcnow() + timedelta(days=7),
            "iat": datetime.utcnow()
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)  # Теперь работает!
        print(f"вњ… РўРѕРєРµРЅ СЃРіРµРЅРµСЂРёСЂРѕРІР°РЅ: {token[:50]}...")
        return token

    def _is_valid_email(self, email: str) -> bool:
        """РџСЂРѕСЃС‚Р°СЏ РІР°Р»РёРґР°С†РёСЏ email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
