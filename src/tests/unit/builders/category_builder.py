from faker import Faker
from datetime import datetime
from src.core.entities.category import Category


class CategoryBuilder:
    def __init__(self):
        self.faker = Faker()
        self._id = f"cat_{self.faker.uuid4()}"
        self._name = self.faker.word()
        self._description = self.faker.text()
        self._created_at = datetime.now()
        self._updated_at = datetime.now()

    def with_id(self, category_id: str) -> 'CategoryBuilder':
        self._id = category_id
        return self

    def with_name(self, name: str) -> 'CategoryBuilder':
        self._name = name
        return self

    def with_description(self, description: str) -> 'CategoryBuilder':
        self._description = description
        return self

    def build(self) -> Category:
        return Category(
            id=self._id,
            name=self._name,
            description=self._description,
            created_at=self._created_at,
            updated_at=self._updated_at
        )

    @staticmethod
    def create_valid_category() -> Category:
        return CategoryBuilder().build()