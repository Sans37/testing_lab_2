# src/core/services/category_service.py
from typing import List, Optional
from src.core.entities.category import Category
from src.core.entities.user import User
from src.core.repositories.category_repository import CategoryRepository
from src.core.exceptions import EntityNotFoundException, AuthorizationException, DuplicateEntityException


class CategoryService:
    """Сервис для работы с категориями"""

    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository

    async def get_all_categories(self) -> List[Category]:
        """Получить все категории"""
        return await self.category_repository.get_all()

    async def get_category_by_id(self, category_id: str) -> Optional[Category]:
        """Получить категорию по ID"""
        return await self.category_repository.get_by_id(category_id)

    async def create_category(self, name: str, description: str = "", current_user: Optional[User] = None) -> Category:
        """Создать новую категорию"""
        if current_user and not current_user.is_admin():
            raise AuthorizationException("Требуются права администратора")

        # Проверяем, есть ли уже категория с таким именем
        existing_category = await self.category_repository.get_by_name(name)
        if existing_category:
            raise DuplicateEntityException("Категория", "название", name)

        # Создаем категорию
        category = Category.create(name, description)
        return await self.category_repository.create(category)

    async def update_category(self, category_id: str, update_data: dict,
                              current_user: Optional[User] = None) -> Category:
        """Обновить категорию"""
        if current_user and not current_user.is_admin():
            raise AuthorizationException("Требуются права администратора")

        # Проверяем существование категории
        category = await self.category_repository.get_by_id(category_id)
        if not category:
            raise EntityNotFoundException("Категория", category_id)

        # Проверяем уникальность имени при обновлении
        if 'name' in update_data:
            existing_category = await self.category_repository.get_by_name(update_data['name'])
            if existing_category and existing_category.id != category_id:
                raise DuplicateEntityException("Категория", "название", update_data['name'])

        return await self.category_repository.update(category_id, update_data)

    async def delete_category(self, category_id: str, current_user: Optional[User] = None) -> bool:
        """Удалить категорию"""
        if current_user and not current_user.is_admin():
            raise AuthorizationException("Требуются права администратора")

        # Проверяем существование категории
        category = await self.category_repository.get_by_id(category_id)
        if not category:
            raise EntityNotFoundException("Категория", category_id)

        return await self.category_repository.delete(category_id)