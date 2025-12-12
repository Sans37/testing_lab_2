# src/infrastructure/database/models/user_model.py
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.infrastructure.database.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)
    role = Column(String(20), default='customer', nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Связи как строковые ссылки
    cart = relationship("CartModel", back_populates="user", uselist=False)
    orders = relationship("OrderModel", back_populates="user")
    reviews = relationship("ReviewModel", back_populates="user")

    def to_entity(self):
        from src.core.entities.user import User, UserRole

        # Приводим роль к нижнему регистру для корректного преобразования в enum
        role_lower = self.role.lower()
        return User(
            id=self.id,
            name=self.name,
            email=self.email,
            password=self.password,
            phone=self.phone,
            address=self.address,
            role=UserRole(role_lower),
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @classmethod
    def from_entity(cls, user_entity):
        return cls(
            id=user_entity.id,
            name=user_entity.name,
            email=user_entity.email,
            password=user_entity.password,
            phone=user_entity.phone,
            address=user_entity.address,
            role=user_entity.role.value  # Уже в нижнем регистре
        )