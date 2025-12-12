# user.py (финальный вариант)
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class UserRole(Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"


@dataclass
class User:
    """Класс пользователя с данными и бизнес-логикой"""
    id: str
    name: str
    email: str
    password: str  # хэшированный пароль
    phone: str
    address: str
    role: UserRole
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, name: str, email: str, password: str, phone: str, address: str,
               role: UserRole = UserRole.CUSTOMER) -> 'User':
        """Фабричный метод для создания нового пользователя"""
        now = datetime.now()
        user_id = f"user_{uuid.uuid4()}"

        return cls(
            id=user_id,
            name=name,
            email=email,
            password=password,
            phone=phone,
            address=address,
            role=role,
            created_at=now,
            updated_at=now
        )

    def update_profile(self, name: Optional[str] = None,
                      phone: Optional[str] = None,
                      address: Optional[str] = None) -> None:
        """Обновление профиля пользователя"""
        if name is not None:
            self.name = name
        if phone is not None:
            self.phone = phone
        if address is not None:
            self.address = address
        self.updated_at = datetime.now()

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "role": self.role.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


# НЕ ДЕЛАЙТЕ ЭТО:
# UserEntity = User  # ❌ Избегайте