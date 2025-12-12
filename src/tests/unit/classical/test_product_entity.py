import pytest
from freezegun import freeze_time
from datetime import datetime

from src.core.entities.product import Product
from src.core.entities.category import Category
from src.core.entities.ingredient import Ingredient
from src.tests.unit.builders.object_mother import ObjectMother
from src.tests.unit.builders.product_builder import ProductBuilder

@pytest.mark.classical
@pytest.mark.offline
class TestProductEntity:
    """Test suite для ProductEntity"""

    def test_product_creation_with_factory_method(self) -> None:
        """Позитивный тест: создание товара через фабричный метод"""
        # Arrange
        name: str = "Test Product"
        description: str = "Test Description"
        price: float = 99.99

        # Создаем тестовую категорию и ингредиенты
        with freeze_time("2023-01-01 12:00:00"):
            category: Category = Category.create(
                name="Test Category",
                description="Test Category Description"
            )

            # Используем IngredientEntity.create() для создания ингредиентов
            ingredients: list[Ingredient] = [
                Ingredient.create(name="Test Ingredient 1", allergen=False),
                Ingredient.create(name="Test Ingredient 2", allergen=True)
            ]

        # Act
        with freeze_time("2023-01-01 12:00:00"):
            product: Product = Product.create(
                name=name,
                description=description,
                price=price,
                category=category,
                ingredients=ingredients
            )

        # Assert
        assert product.name == name
        assert product.description == description
        assert product.price == price
        assert product.available
        assert product.id.startswith("prod_")
        assert product.category.name == "Test Category"
        assert len(product.ingredients) == 2
        assert product.ingredients[0].name == "Test Ingredient 1"
        assert product.ingredients[1].allergen

    def test_update_product_info(self) -> None:
        """Позитивный тест: обновление информации о товаре"""
        # Arrange
        with freeze_time("2023-01-01 12:00:00"):
            product: Product = ProductBuilder().create_valid_product()
            original_updated_at: datetime = product.updated_at

        # Act
        with freeze_time("2023-01-01 12:00:01"):
            product.update(
                name="Updated Name",
                description="Updated Description",
                price=149.99,
                available=False
            )

        # Assert
        assert product.name == "Updated Name"
        assert product.description == "Updated Description"
        assert product.price == 149.99
        assert not product.available
        assert product.updated_at > original_updated_at

    def test_is_available_returns_correct_value(self) -> None:
        """Позитивный тест: проверка доступности товара"""
        # Arrange
        available_product: Product = ProductBuilder().create_valid_product()
        unavailable_product: Product = ProductBuilder().as_unavailable().build()

        # Act & Assert
        assert available_product.is_available()
        assert not unavailable_product.is_available()

    def test_get_price_returns_correct_value(self) -> None:
        """Позитивный тест: получение цены товара"""
        # Arrange
        product: Product = ProductBuilder().with_price(199.99).build()

        # Act & Assert
        assert product.get_price() == 199.99

    def test_update_with_none_values_does_nothing(self) -> None:
        """Негативный тест: обновление с None значениями"""
        # Arrange
        product: Product = ProductBuilder().create_valid_product()
        original_name: str = product.name
        original_price: float = product.price

        # Act
        product.update(name=None, price=None)

        # Assert
        assert product.name == original_name
        assert product.price == original_price

    def test_update_category_updates_timestamp(self) -> None:
        """Позитивный тест: обновление категории меняет updated_at"""
        # Arrange
        with freeze_time("2023-01-01 12:00:00"):
            product: Product = ProductBuilder().create_valid_product()
            original_updated_at: datetime = product.updated_at

            new_category: Category = Category.create(
                name="New Category",
                description="New Category Description"
            )

        # Act
        with freeze_time("2023-01-01 12:00:01"):
            product.update_category(new_category)

        # Assert
        assert product.category.name == "New Category"
        assert product.updated_at > original_updated_at

    def test_update_ingredients_updates_timestamp(self) -> None:
        """Позитивный тест: обновление ингредиентов меняет updated_at"""
        # Arrange
        with freeze_time("2023-01-01 12:00:00"):
            product: Product = ProductBuilder().create_valid_product()
            original_updated_at: datetime = product.updated_at

            new_ingredients: list[Ingredient] = [
                Ingredient.create(name="New Ingredient 1"),
                Ingredient.create(name="New Ingredient 2", allergen=True)
            ]

        # Act
        with freeze_time("2023-01-01 12:00:01"):
            product.update_ingredients(new_ingredients)

        # Assert
        assert len(product.ingredients) == 2
        assert product.ingredients[0].name == "New Ingredient 1"
        assert product.updated_at > original_updated_at

    def test_product_creation_with_object_mother(self) -> None:
        """Позитивный тест: создание товара через Object Mother"""
        # Arrange & Act
        product: Product = ObjectMother.create_default_product()

        # Assert
        assert product.name == "Fresh Bread"
        assert product.price == 299.99
        assert product.available
        assert len(product.ingredients) == 1
        assert product.ingredients[0].name == "Flour"