import pytest
from sqlalchemy.orm import Session
from src.infrastructure.database.repositories.product_repository_impl import ProductRepositoryImpl
from src.infrastructure.database.repositories.category_repository_impl import CategoryRepositoryImpl
from src.core.entities.product import Product
from src.core.entities.category import Category
from src.core.entities.ingredient import Ingredient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def category_repository(test_db_session: Session):
    return CategoryRepositoryImpl(test_db_session)


@pytest.fixture
def product_repository(test_db_session: Session):
    return ProductRepositoryImpl(test_db_session)


@pytest.mark.integration
class TestProductRepositoryIntegration:
    """Интеграционные тесты для ProductRepository"""

    @pytest.mark.asyncio
    async def test_create_product_with_category(self, product_repository, category_repository, test_db_session):
        # Arrange - сначала создаем категорию
        category = Category.create(
            name="Bakery",
            description="Fresh baked goods"
        )
        created_category = await category_repository.create(category)

        product = Product.create(
            name="Fresh Bread",
            description="Delicious bread",
            price=299.99,
            category=created_category,
            ingredients=[
                Ingredient.create(name="Flour", allergen=False),
                Ingredient.create(name="Water", allergen=False)
            ]
        )

        # Act
        created_product = await product_repository.create(product)

        # Assert
        assert created_product.name == "Fresh Bread"
        assert created_product.price == 299.99
        assert created_product.category.id == created_category.id
        assert len(created_product.ingredients) == 2

    @pytest.mark.asyncio
    async def test_get_products_by_category(self, product_repository, category_repository, test_db_session):
        # Arrange
        category = Category.create(name="Drinks", description="Beverages")
        created_category = await category_repository.create(category)

        # Создаем несколько товаров
        for i in range(3):
            product = Product.create(
                name=f"Drink {i}",
                description=f"Description {i}",
                price=100 + i,
                category=created_category,
                ingredients=[]
            )
            await product_repository.create(product)

        # Act
        products = await product_repository.get_by_category(
            category_id=created_category.id,
            limit=10
        )

        # Assert
        assert len(products) == 3
        assert all(p.category.id == created_category.id for p in products)

    @pytest.mark.asyncio
    async def test_search_products_by_name(self, product_repository, category_repository, test_db_session):
        # Arrange
        category = Category.create(name="Test Category", description="Desc")
        created_category = await category_repository.create(category)

        products_data = [
            ("Apple Pie", "Delicious pie", 399.99),
            ("Apple Juice", "Fresh juice", 199.99),
            ("Banana Bread", "Sweet bread", 299.99)
        ]

        for name, desc, price in products_data:
            product = Product.create(
                name=name,
                description=desc,
                price=price,
                category=created_category,
                ingredients=[]
            )
            await product_repository.create(product)

        # Act
        apple_products = await product_repository.search_by_name("Apple")

        # Assert
        assert len(apple_products) == 2
        assert all("Apple" in p.name for p in apple_products)

    @pytest.mark.asyncio
    async def test_update_product_availability(self, product_repository, category_repository, test_db_session):
        # Arrange
        category = Category.create(name="Test", description="Test")
        created_category = await category_repository.create(category)

        product = Product.create(
            name="Test Product",
            description="Test",
            price=100,
            category=created_category,
            ingredients=[]
        )
        created = await product_repository.create(product)

        # Act - делаем товар недоступным
        updated = await product_repository.update_availability(
            product_id=created.id,
            available=False
        )

        # Assert
        assert not updated.available

        # Проверяем через get_all с фильтром
        all_products = await product_repository.get_all(available_only=True)
        assert created.id not in [p.id for p in all_products]

    @pytest.mark.asyncio
    async def test_get_products_available_only(
            self,
            test_db_session: Session,
            test_category
    ):
        # Arrange
        repo = ProductRepositoryImpl(test_db_session)
        # test_category - это УЖЕ Category (entity)
        category_entity = test_category

        # Create products with different availability
        products = []
        for i in range(3):
            product = Product.create(
                name=f"Product {i}",
                description="Test",
                price=100 + i,
                category=category_entity,
                ingredients=[],
                available=(i % 2 == 0)
            )
            await repo.create(product)
            products.append(product)

        # Act
        available_products = await repo.get_all(available_only=True)

        # Assert
        assert all(p.available for p in available_products)
        assert len(available_products) >= 2