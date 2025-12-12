from faker import Faker
from datetime import datetime
from src.core.entities.product import Product
from src.core.entities.category import Category
from src.core.entities.ingredient import Ingredient


class ProductBuilder:
    def __init__(self) -> None:
        self.faker: Faker = Faker()
        self._id: str = f"prod_{self.faker.uuid4()}"
        self._name: str = self.faker.word()
        self._description: str = self.faker.text()
        self._price: float = round(self.faker.random_number(digits=2), 2)

        # Создаем CategoryEntity с правильными параметрами
        self._category: Category = Category(
            id=f"cat_{self.faker.uuid4()}",
            name=self.faker.word(),
            description=self.faker.text(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Создаем список ингредиентов используя IngredientEntity
        self._ingredients: list[Ingredient] = [Ingredient(
                id=f"ing_{self.faker.uuid4()}",
                name=self.faker.word(),
                allergen=self.faker.boolean(),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            for _ in range(2)  # 2 ингредиента для простоты
        ]

        self._available: bool = True
        self._image: str = self.faker.image_url()
        self._created_at: datetime = datetime.now()
        self._updated_at: datetime = datetime.now()

    def with_id(self, product_id: str) -> 'ProductBuilder':
        self._id = product_id
        return self

    def with_name(self, name: str) -> 'ProductBuilder':
        self._name = name
        return self

    def with_price(self, price: float) -> 'ProductBuilder':
        self._price = price
        return self

    def with_category(self, category: Category) -> 'ProductBuilder':
        self._category = category
        return self

    def as_unavailable(self) -> 'ProductBuilder':
        self._available = False
        return self

    def with_empty_ingredients(self) -> 'ProductBuilder':
        """Добавляем метод для создания продукта без ингредиентов"""
        self._ingredients = []
        return self

    def with_ingredients(self, ingredients: list[Ingredient]) -> 'ProductBuilder':
        """Добавляем метод для установки конкретных ингредиентов"""
        self._ingredients = ingredients
        return self

    def build(self) -> Product:
        return Product(
            id=self._id,
            name=self._name,
            description=self._description,
            price=self._price,
            category=self._category,
            ingredients=self._ingredients,
            available=self._available,
            created_at=self._created_at,
            updated_at=self._updated_at,
            image=self._image
        )

    @staticmethod
    def create_valid_product() -> Product:
        return ProductBuilder().build()

    @staticmethod
    def create_unavailable_product() -> Product:
        return ProductBuilder().as_unavailable().build()

    @staticmethod
    def create_product_without_ingredients() -> Product:
        return ProductBuilder().with_empty_ingredients().build()