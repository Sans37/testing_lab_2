from datetime import datetime
from src.core.entities.user import User, UserRole
from src.core.entities.product import Product
from src.core.entities.category import Category
from src.core.entities.ingredient import Ingredient


class ObjectMother:
    """Object Mother pattern - готовые объекты для тестов"""

    # User objects
    @staticmethod
    def create_default_customer() -> User:
        return User(
            id="user_customer_123",
            name="John Customer",
            email="customer@example.com",
            password="hashed_password_123",
            phone="+1234567890",
            address="123 Customer St",
            role=UserRole.CUSTOMER,
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 1, 12, 0, 0)
        )

    @staticmethod
    def create_default_admin() -> User:
        return User(
            id="user_admin_456",
            name="Admin User",
            email="admin@example.com",
            password="hashed_admin_123",
            phone="+0987654321",
            address="456 Admin Ave",
            role=UserRole.ADMIN,
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 1, 12, 0, 0)
        )

    @staticmethod
    def create_user_with_specific_email(email: str) -> User:
        user: User = ObjectMother.create_default_customer()
        return User(
            id=user.id,
            name=user.name,
            email=email,
            password=user.password,
            phone=user.phone,
            address=user.address,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    # Category objects
    @staticmethod
    def create_default_category() -> Category:
        return Category(
            id="cat_bakery_123",
            name="Bakery",
            description="Fresh baked goods",
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 1, 12, 0, 0)
        )

    # Product objects
    @staticmethod
    def create_default_product() -> Product:
        category: Category = ObjectMother.create_default_category()

        ingredients: list[Ingredient] = [
            Ingredient(
                id="ing_flour_001",
                name="Flour",
                allergen=False,
                created_at=datetime(2023, 1, 1, 12, 0, 0),
                updated_at=datetime(2023, 1, 1, 12, 0, 0)
            )
        ]

        return Product(
            id="prod_bread_001",
            name="Fresh Bread",
            description="Delicious fresh bread",
            price=299.99,
            category=category,
            ingredients=ingredients,
            available=True,
            image="bread.jpg",
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 1, 12, 0, 0)
        )