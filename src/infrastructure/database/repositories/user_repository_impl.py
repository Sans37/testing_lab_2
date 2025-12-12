# src/infrastructure/database/repositories/user_repository_impl.py
from typing import List, Optional
from sqlalchemy.orm import Session
from src.core.entities.user import User
from src.core.repositories.user_repository import UserRepository
from src.core.exceptions.repository_exceptions import EntityNotFoundException, DuplicateEntityException
from src.infrastructure.database.models.user_model import UserModel
import traceback


class UserRepositoryImpl(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, user_id: str) -> Optional[User]:
        user_model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return user_model.to_entity() if user_model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        user_model = self.db.query(UserModel).filter(UserModel.email == email).first()
        return user_model.to_entity() if user_model else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        user_models = self.db.query(UserModel).offset(skip).limit(limit).all()
        return [user_model.to_entity() for user_model in user_models]

    async def create(self, user_entity) -> User:
        try:
            print(f"🔧 UserRepositoryImpl.create: создание пользователя {user_entity.email}")

            # Проверка на дубликат email
            existing_user = await self.get_by_email(user_entity.email)
            if existing_user:
                raise DuplicateEntityException("Пользователь", "email", user_entity.email)

            print("✅ Дубликатов нет")

            user_model = UserModel.from_entity(user_entity)
            print(f"🔧 Модель создана: {user_model.id}")

            self.db.add(user_model)
            self.db.commit()
            self.db.refresh(user_model)
            print("✅ Пользователь сохранен в БД")

            result = user_model.to_entity()
            print(f"✅ Сущность преобразована: {result.id}")

            return result

        except Exception as e:
            print(f"❌ Ошибка в UserRepositoryImpl.create: {e}")
            print(traceback.format_exc())
            self.db.rollback()
            raise

    async def update(self, user_id: str, user_data: dict) -> User:
        user_model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user_model:
            raise EntityNotFoundException("Пользователь", user_id)

        for key, value in user_data.items():
            if hasattr(user_model, key):
                setattr(user_model, key, value)

        self.db.commit()
        self.db.refresh(user_model)
        return user_model.to_entity()

    async def delete(self, user_id: str) -> bool:
        user_model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user_model:
            raise EntityNotFoundException("Пользователь", user_id)

        self.db.delete(user_model)
        self.db.commit()
        return True

    async def exists_by_email(self, email: str) -> bool:
        user_model = self.db.query(UserModel).filter(UserModel.email == email).first()
        return user_model is not None