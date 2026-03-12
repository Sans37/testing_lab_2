import pytest
from sqlalchemy.orm import Session
from src.infrastructure.database.repositories.category_repository_impl import CategoryRepositoryImpl
from src.core.entities.category import Category
from src.core.exceptions.repository_exceptions import DuplicateEntityException


@pytest.mark.integration
class TestCategoryRepositoryIntegration:
    """Интеграционные тесты для CategoryRepository"""

    @pytest.mark.asyncio
    async def test_create_category(self, test_db_session: Session):
        """Тест создания категории"""
        # Arrange
        repo = CategoryRepositoryImpl(test_db_session)
        category = Category.create(
            name="Тестовая категория",
            description="Описание тестовой категории"
        )

        # Act
        created = await repo.create(category)

        # Assert
        assert created.id is not None
        assert created.name == "Тестовая категория"
        assert created.description == "Описание тестовой категории"
        assert created.created_at is not None
        assert created.updated_at is not None

    @pytest.mark.asyncio
    async def test_create_duplicate_category_name(self, test_db_session: Session):
        """Тест создания категории с дублирующимся именем"""
        # Arrange
        repo = CategoryRepositoryImpl(test_db_session)
        category1 = Category.create(
            name="Уникальная категория",
            description="Описание 1"
        )
        await repo.create(category1)

        category2 = Category.create(
            name="Уникальная категория",  # То же имя
            description="Описание 2"
        )

        # Act & Assert
        with pytest.raises(DuplicateEntityException) as exc_info:
            await repo.create(category2)

        assert "Категория" in str(exc_info.value)
        assert "Уникальная категория" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_category_by_id(self, test_db_session: Session):
        """Тест получения категории по ID"""
        # Arrange
        repo = CategoryRepositoryImpl(test_db_session)
        category = Category.create(
            name="Категория для поиска",
            description="Будем искать по ID"
        )
        created = await repo.create(category)

        # Act
        found = await repo.get_by_id(created.id)

        # Assert
        assert found is not None
        assert found.id == created.id
        assert found.name == "Категория для поиска"

    @pytest.mark.asyncio
    async def test_get_category_by_name(self, test_db_session: Session):
        """Тест получения категории по имени"""
        # Arrange
        repo = CategoryRepositoryImpl(test_db_session)
        category = Category.create(
            name="УникальноеИмя123",
            description="Будем искать по имени"
        )
        await repo.create(category)

        # Act
        found = await repo.get_by_name("УникальноеИмя123")

        # Assert
        assert found is not None
        assert found.name == "УникальноеИмя123"
        assert found.description == "Будем искать по имени"

    @pytest.mark.asyncio
    async def test_get_all_categories(self, test_db_session: Session):
        """Тест получения всех категорий"""
        # Arrange
        repo = CategoryRepositoryImpl(test_db_session)

        # Создаем несколько категорий
        categories = []
        for i in range(3):
            category = Category.create(
                name=f"Категория {i}",
                description=f"Описание {i}"
            )
            created = await repo.create(category)
            categories.append(created)

        # Act
        all_categories = await repo.get_all()

        # Assert
        assert len(all_categories) >= 3
        # Проверяем, что все созданные категории есть в списке
        created_ids = [c.id for c in categories]
        found_ids = [c.id for c in all_categories]
        for cat_id in created_ids:
            assert cat_id in found_ids

    @pytest.mark.asyncio
    async def test_update_category(self, test_db_session: Session):
        """Тест обновления категории"""
        # Arrange
        repo = CategoryRepositoryImpl(test_db_session)
        category = Category.create(
            name="Старое название",
            description="Старое описание"
        )
        created = await repo.create(category)

        # Act
        updated = await repo.update(
            created.id,
            {
                "name": "Новое название",
                "description": "Новое описание"
            }
        )

        # Assert
        assert updated.name == "Новое название"
        assert updated.description == "Новое описание"
        assert updated.id == created.id

    @pytest.mark.asyncio
    async def test_delete_category(self, test_db_session: Session):
        """Тест удаления категории"""
        # Arrange
        repo = CategoryRepositoryImpl(test_db_session)
        category = Category.create(
            name="Для удаления",
            description="Будет удалена"
        )
        created = await repo.create(category)

        # Act
        result = await repo.delete(created.id)

        # Assert
        assert result is True

        # Проверяем, что категория действительно удалена
        deleted = await repo.get_by_id(created.id)
        assert deleted is None

    @pytest.mark.asyncio
    async def test_update_nonexistent_category(self, test_db_session: Session):
        """Тест обновления несуществующей категории"""
        # Arrange
        repo = CategoryRepositoryImpl(test_db_session)

        # Act & Assert
        from src.core.exceptions.repository_exceptions import EntityNotFoundException

        with pytest.raises(EntityNotFoundException):
            await repo.update(
                "nonexistent-id",
                {"name": "Новое название"}
            )

    @pytest.mark.asyncio
    async def test_delete_nonexistent_category(self, test_db_session: Session):
        """Тест удаления несуществующей категории"""
        # Arrange
        repo = CategoryRepositoryImpl(test_db_session)

        # Act & Assert
        from src.core.exceptions.repository_exceptions import EntityNotFoundException

        with pytest.raises(EntityNotFoundException):
            await repo.delete("nonexistent-id")