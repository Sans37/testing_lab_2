from typing import List, Optional
from src.core.entities.user import User, UserRole
from src.core.repositories.user_repository import UserRepository
from src.core.exceptions import EntityNotFoundException, AuthorizationException


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_user_by_id(self, user_id: str, current_user: Optional[User] = None) -> Optional[User]:
        """Получить пользователя по ID"""
        if current_user is None:
            # Просто возвращаем пользователя без проверки прав
            return await self.user_repository.get_by_id(user_id)
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundException("Пользователь", user_id)

        # Проверка прав доступа
        if user.id != current_user.id and not current_user.is_admin():
            raise AuthorizationException("Нет прав для просмотра этого пользователя")

        return user

    async def get_current_user_profile(self, current_user: User) -> Optional[User]:
        """Получить профиль текущего пользователя"""
        return await self.user_repository.get_by_id(current_user.id)

    async def update_user_profile(
            self,
            user_id: str,
            update_data: dict,
            current_user: User
    ) -> User:
        """Обновить профиль пользователя"""
        # Проверка прав доступа
        if user_id != current_user.id and not current_user.is_admin():
            raise AuthorizationException("Нет прав для обновления этого пользователя")

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundException("Пользователь", user_id)

        # Обновление данных
        return await self.user_repository.update(user_id, update_data)

    async def get_all_users(
            self,
            skip: int = 0,
            limit: int = 100,
            current_user: Optional[User] = None
    ) -> List[User]:
        """Получить всех пользователей (только для админов)"""
        if not current_user or not current_user.is_admin():
            raise AuthorizationException("Требуются права администратора")

        return await self.user_repository.get_all(skip, limit)

    async def change_user_role(
            self,
            user_id: str,
            new_role: UserRole,
            current_user: User
    ) -> User:
        """Изменить роль пользователя (только для админов)"""
        if not current_user.is_admin():
            raise AuthorizationException("Требуются права администратора")

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundException("Пользователь", user_id)

        return await self.user_repository.update(user_id, {"role": new_role})