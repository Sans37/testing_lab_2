# src/core/services/auth_service.py
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta
from src.core.entities.user import User, UserRole
from src.core.repositories.user_repository import UserRepository
from src.core.exceptions import AuthenticationException, ValidationException
import traceback


class AuthService:
    def __init__(self, user_repository: UserRepository, secret_key: str, algorithm: str = "HS256"):
        self.user_repository = user_repository
        self.secret_key = secret_key
        self.algorithm = algorithm

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
            print(f"🔧 Начало регистрации: {email}")

            # Валидация email
            if not self._is_valid_email(email):
                raise ValidationException("Неверный формат email")
            print("✅ Email валиден")

            # Проверка существования пользователя
            if await self.user_repository.exists_by_email(email):
                raise ValidationException("Пользователь с таким email уже существует")
            print("✅ Пользователь не существует")

            # Хэширование пароля
            hashed_password = self._hash_password(password)
            print("✅ Пароль хэширован")

            # Создание пользователя
            user_entity = User.create(
                name=name,
                email=email,
                password=hashed_password,
                phone=phone,
                address=address,
                role=role
            )
            print("✅ Сущность пользователя создана")

            # Сохранение в репозитории
            user = await self.user_repository.create(user_entity)
            print("✅ Пользователь сохранен в БД")

            # Генерация токена
            token = self._generate_token(user.id, user.email, user.role.value)
            print("✅ Токен сгенерирован")

            return {
                "user": user,
                "token": token
            }

        except Exception as e:
            print(f"❌ Ошибка в register_user: {e}")
            print(traceback.format_exc())
            raise

    async def login_user(self, email: str, password: str) -> dict:
        try:
            user = await self.user_repository.get_by_email(email)
            if not user:
                raise AuthenticationException("Пользователь не найден")

            if not self._verify_password(password, user.password):
                raise AuthenticationException("Неверный пароль")

            # Генерация токена
            token = self._generate_token(user.id, user.email, user.role.value)

            return {
                "user": user,
                "token": token
            }
        except Exception as e:
            print(f"❌ Ошиб+ка в login_user: {e}")
            print(traceback.format_exc())
            raise

    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except ExpiredSignatureError:
            raise AuthenticationException("Токен истек")
        except JWTError:
            raise AuthenticationException("Неверный токен")

    def _hash_password(self, password: str) -> str:
        """Временное хэширование пароля"""
        print(f"🔧 Хэширование пароля: {password}")
        return f"hashed_{password}"

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Временная проверка пароля"""
        print(f"🔧 Проверка пароля: {password} vs {hashed_password}")
        return f"hashed_{password}" == hashed_password

    def _generate_token(self, user_id: str, email: str, role: str) -> str:
        """Генерация JWT токена"""
        print(f"🔧 Генерация токена для: {user_id}, {email}")
        payload = {
            "user_id": user_id,
            "email": email,
            "role": role,
            "exp": datetime.utcnow() + timedelta(days=7),
            "iat": datetime.utcnow()
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)  # Теперь работает!
        print(f"✅ Токен сгенерирован: {token[:50]}...")
        return token

    def _is_valid_email(self, email: str) -> bool:
        """Простая валидация email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))