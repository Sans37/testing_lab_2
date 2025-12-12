from src.core.entities.cart import Cart
from src.core.repositories.cart_repository import CartRepository
from src.core.repositories.product_repository import ProductRepository
from src.core.exceptions import EntityNotFoundException, BusinessRuleException


class CartService:
    """Сервис для работы с корзиной"""

    def __init__(
            self,
            cart_repository: CartRepository,
            product_repository: ProductRepository
    ):
        self.cart_repository = cart_repository
        self.product_repository = product_repository

    async def get_user_cart(self, user_id: str) -> Cart:
        """Получить корзину пользователя"""
        cart = await self.cart_repository.get_or_create_by_user(user_id)
        return cart

    async def add_to_cart(self, user_id: str, product_id: str, quantity: int = 1) -> Cart:
        """Добавить товар в корзину"""
        if quantity <= 0:
            raise BusinessRuleException("Количество должно быть положительным")

        # Проверка существования товара
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise EntityNotFoundException("Товар", product_id)

        # Проверка доступности товара
        if not product.available:
            raise BusinessRuleException("Товар временно недоступен")

        # Получение или создание корзины
        cart = await self.cart_repository.get_or_create_by_user(user_id)

        # Добавление товара в корзину
        cart_entity = Cart(
            id=cart.id,
            user_id=cart.user_id,
            items=cart.items,
            created_at=cart.created_at,
            updated_at=cart.updated_at
        )

        cart_entity.add_item(product, quantity)

        # Сохранение изменений
        return await self.cart_repository.update(cart.id, {"items": cart_entity.items})

    async def update_cart_item(self, user_id: str, product_id: str, quantity: int) -> Cart:
        """Обновить количество товара в корзине"""
        cart = await self.cart_repository.get_by_user_id(user_id)
        if not cart:
            raise EntityNotFoundException("Корзина", f"для пользователя {user_id}")

        cart_entity = Cart(
            id=cart.id,
            user_id=cart.user_id,
            items=cart.items,
            created_at=cart.created_at,
            updated_at=cart.updated_at
        )

        cart_entity.update_item_quantity(product_id, quantity)

        return await self.cart_repository.update(cart.id, {"items": cart_entity.items})

    async def remove_from_cart(self, user_id: str, product_id: str) -> Cart:
        """Удалить товар из корзины"""
        cart = await self.cart_repository.get_by_user_id(user_id)
        if not cart:
            raise EntityNotFoundException("Корзина", f"для пользователя {user_id}")

        cart_entity = Cart(
            id=cart.id,
            user_id=cart.user_id,
            items=cart.items,
            created_at=cart.created_at,
            updated_at=cart.updated_at
        )

        cart_entity.remove_item(product_id)

        return await self.cart_repository.update(cart.id, {"items": cart_entity.items})

    async def clear_cart(self, user_id: str) -> Cart:
        """Очистить корзину"""
        cart = await self.cart_repository.get_by_user_id(user_id)
        if not cart:
            raise EntityNotFoundException("Корзина", f"для пользователя {user_id}")

        return await self.cart_repository.clear(cart.id)

    async def get_cart_total(self, user_id: str) -> float:
        """Получить общую стоимость корзины"""
        cart = await self.cart_repository.get_by_user_id(user_id)
        if not cart:
            return 0.0

        cart_entity = Cart(
            id=cart.id,
            user_id=cart.user_id,
            items=cart.items,
            created_at=cart.created_at,
            updated_at=cart.updated_at
        )

        return cart_entity.get_total()