import pytest
from unittest.mock import AsyncMock
from src.core.services.product_service import ProductService
from src.core.entities.product import Product
from src.core.entities.category import Category
from src.core.exceptions import EntityNotFoundException, ValidationException
from src.tests.unit.builders.product_builder import ProductBuilder
from src.tests.unit.builders.category_builder import CategoryBuilder

@pytest.mark.classical
@pytest.mark.offline
class TestProductService:
    """Test suite для ProductService в Лондонском стиле (с моками)"""

    @pytest.fixture
    def mock_product_repository(self) -> AsyncMock:
        """Фикстура для мока ProductRepository"""
        return AsyncMock()

    @pytest.fixture
    def mock_category_repository(self) -> AsyncMock:
        """Фикстура для мока CategoryRepository"""
        return AsyncMock()

    @pytest.fixture
    def product_service(self, mock_product_repository: AsyncMock, mock_category_repository: AsyncMock) -> ProductService:
        """Фикстура для ProductService с моками репозиториев"""
        return ProductService(mock_product_repository, mock_category_repository)

    @pytest.mark.asyncio
    async def test_get_product_success(self, product_service: ProductService, mock_product_repository: AsyncMock) -> None:
        """Позитивный тест: успешное получение товара по ID"""
        # Arrange
        product_id: str = "prod_123"
        expected_product: Product = ProductBuilder().with_id(product_id).build()

        mock_product_repository.get_by_id.return_value = expected_product

        # Act
        result: Product = await product_service.get_product(product_id)

        # Assert
        assert result == expected_product
        mock_product_repository.get_by_id.assert_called_once_with(product_id)

    @pytest.mark.asyncio
    async def test_get_product_not_found(self, product_service: ProductService, mock_product_repository: AsyncMock) -> None:
        """Негативный тест: товар не найден"""
        # Arrange
        product_id: str = "prod_999"
        mock_product_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(EntityNotFoundException, match="Товар"):
            await product_service.get_product(product_id)

    @pytest.mark.asyncio
    async def test_create_product_success(self, product_service: ProductService, mock_product_repository: AsyncMock, mock_category_repository: AsyncMock) -> None:
        """Позитивный тест: успешное создание товара"""
        # Arrange
        name: str = "Test Product"
        description: str = "Test Description"
        price: float = 99.99
        category_id: str = "cat_123"

        category: Category = CategoryBuilder().with_id(category_id).build()
        expected_product: Product = ProductBuilder().build()

        mock_category_repository.get_by_id.return_value = category
        mock_product_repository.create.return_value = expected_product

        # Act
        result: Product = await product_service.create_product(
            name=name,
            description=description,
            price=price,
            category_id=category_id,
            ingredients=[]
        )

        # Assert
        assert result == expected_product
        mock_category_repository.get_by_id.assert_called_once_with(category_id)
        mock_product_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_product_invalid_price(self, product_service: ProductService) -> None:
        """Негативный тест: создание товара с отрицательной ценой"""
        # Arrange
        name: str = "Test Product"
        description: str = "Test Description"
        price: float = -10.0  # невалидная цена
        category_id: str = "cat_123"

        # Act & Assert
        with pytest.raises(ValidationException, match="Цена должна быть положительной"):
            await product_service.create_product(
                name=name,
                description=description,
                price=price,
                category_id=category_id,
                ingredients=[]
            )

    @pytest.mark.asyncio
    async def test_create_product_category_not_found(self, product_service: ProductService, mock_category_repository: AsyncMock) -> None:
        """Негативный тест: категория не найдена при создании товара"""
        # Arrange
        name: str = "Test Product"
        description: str = "Test Description"
        price: float = 99.99
        category_id: str = "cat_999"

        mock_category_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(EntityNotFoundException, match="Категория"):
            await product_service.create_product(
                name=name,
                description=description,
                price=price,
                category_id=category_id,
                ingredients=[]
            )

    @pytest.mark.asyncio
    async def test_update_product_success(self, product_service: ProductService, mock_product_repository: AsyncMock, mock_category_repository: AsyncMock) -> None:
        """Позитивный тест: успешное обновление товара"""
        # Arrange
        product_id: str = "prod_123"
        update_data: dict = {"name": "Updated Name", "price": 149.99}

        existing_product: Product = ProductBuilder().with_id(product_id).build()
        updated_product: Product = ProductBuilder().with_id(product_id).with_name("Updated Name").build()

        mock_product_repository.get_by_id.return_value = existing_product
        mock_product_repository.update.return_value = updated_product

        # Act
        result: Product = await product_service.update_product(product_id, update_data)

        # Assert
        assert result == updated_product
        mock_product_repository.get_by_id.assert_called_once_with(product_id)
        mock_product_repository.update.assert_called_once_with(product_id, update_data)

    @pytest.mark.asyncio
    async def test_update_product_invalid_price(self, product_service: ProductService, mock_product_repository: AsyncMock) -> None:
        """Негативный тест: обновление с отрицательной ценой"""
        # Arrange
        product_id: str = "prod_123"
        update_data: dict = {"price": -50.0}  # невалидная цена

        existing_product: Product = ProductBuilder().with_id(product_id).build()
        mock_product_repository.get_by_id.return_value = existing_product

        # Act & Assert
        with pytest.raises(ValidationException, match="Цена должна быть положительной"):
            await product_service.update_product(product_id, update_data)

    @pytest.mark.asyncio
    async def test_search_products_success(self, product_service: ProductService, mock_product_repository: AsyncMock) -> None:
        """Позитивный тест: успешный поиск товаров"""
        # Arrange
        query: str = "test"
        expected_products: list[Product] = [
            ProductBuilder().with_name("Test Product 1").build(),
            ProductBuilder().with_name("Test Product 2").build()
        ]

        mock_product_repository.search_by_name.return_value = expected_products

        # Act
        result: list[Product] = await product_service.search_products(query)

        # Assert
        assert result == expected_products
        mock_product_repository.search_by_name.assert_called_once_with("test", 0, 50)

    @pytest.mark.asyncio
    async def test_search_products_short_query(self, product_service: ProductService) -> None:
        """Негативный тест: поиск с коротким запросом"""
        # Arrange
        query: str = "a"  # слишком короткий запрос

        # Act & Assert
        with pytest.raises(ValidationException, match="минимум 2 символа"):
            await product_service.search_products(query)

    @pytest.mark.asyncio
    async def test_update_product_availability_success(self, product_service: ProductService, mock_product_repository: AsyncMock) -> None:
        """Позитивный тест: обновление доступности товара"""
        # Arrange
        product_id: str = "prod_123"
        available: bool = False

        existing_product: Product = ProductBuilder().with_id(product_id).build()
        updated_product: Product = ProductBuilder().with_id(product_id).as_unavailable().build()

        mock_product_repository.get_by_id.return_value = existing_product
        mock_product_repository.update_availability.return_value = updated_product

        # Act
        result: Product = await product_service.update_product_availability(product_id, available)

        # Assert
        assert result == updated_product
        mock_product_repository.get_by_id.assert_called_once_with(product_id)
        mock_product_repository.update_availability.assert_called_once_with(product_id, available)