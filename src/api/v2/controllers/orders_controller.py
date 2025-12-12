# src/api/v2/controllers/orders_controller.py
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as http_status  # Изменено: переименован импорт
from typing import Optional, List
from src.core.services.order_service import OrderService
from src.core.entities.user import User
from src.core.entities.order import OrderStatus
from src.api.v2.dependencies import get_order_service, get_current_user
from src.api.v2.dtos.request_dtos import OrderCreateRequest, OrderStatusUpdateRequest
from src.api.v2.dtos.response_dtos import OrderResponse, PaginationResponse, OrderItemResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=http_status.HTTP_201_CREATED)
async def create_order(
        order_data: OrderCreateRequest,
        order_service: OrderService = Depends(get_order_service),
        current_user: User = Depends(get_current_user)
):
    """Создать заказ из корзины"""
    try:
        order = await order_service.create_order_from_cart(
            user_id=current_user.id,
            delivery_address=order_data.delivery_address,
            phone=order_data.phone,
            comment=order_data.comment
        )

        # Преобразуем OrderItem в OrderItemResponse
        order_items_dto = []
        for item in order.items:
            # Нужен ProductResponse для OrderItemResponse
            # Создаем упрощенный ProductResponse
            from src.api.v2.dtos.response_dtos import ProductResponse
            from src.api.v2.dtos.response_dtos import CategoryResponse

            # Создаем CategoryResponse для продукта
            category_response = CategoryResponse(
                id=str(item.product.category.id),
                name=str(item.product.category.name),
                description=str(item.product.category.description),
                created_at=item.product.category.created_at,
                updated_at=item.product.category.updated_at
            )

            # Создаем ProductResponse
            product_response = ProductResponse(
                id=str(item.product.id),
                name=str(item.product.name),
                description=str(item.product.description),
                price=item.product.price,
                category=category_response,
                ingredients=[str(ing) for ing in item.product.ingredients],
                image=item.product.image,
                available=item.product.available,
                created_at=item.product.created_at,
                updated_at=item.product.updated_at
            )

            order_items_dto.append(OrderItemResponse(
                product=product_response,
                quantity=item.quantity,
                price=item.price
            ))

        return OrderResponse(
            id=str(order.id),
            user_id=str(order.user_id),
            items=order_items_dto,
            total=order.total,
            status=order.status.value,  # Используем .value для enum
            delivery_address=str(order.delivery_address),
            phone=str(order.phone),
            comment=order.comment,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при создании заказа: {str(e)}"
        )


@router.get("/", response_model=dict)
async def get_user_orders(
        pagesNum: int = Query(1, ge=1, description="Номер страницы"),
        elemCount: int = Query(5, ge=1, le=50, description="Количество элементов на странице"),
        order_service: OrderService = Depends(get_order_service),
        current_user: User = Depends(get_current_user)
):
    """Получить заказы пользователя"""
    try:
        skip = (pagesNum - 1) * elemCount
        orders = await order_service.get_user_orders(
            user_id=current_user.id,
            skip=skip,
            limit=elemCount
        )

        # Преобразуем заказы в DTO
        orders_dto = []
        for order in orders:
            orders_dto.append(OrderResponse(
                id=str(order.id),
                user_id=str(order.user_id),
                items=[],  # Упрощаем, чтобы не делать сложные преобразования
                total=order.total,
                status=order.status.value,  # Используем .value для enum
                delivery_address=str(order.delivery_address),
                phone=str(order.phone),
                comment=order.comment,
                created_at=order.created_at,
                updated_at=order.updated_at
            ))

        # Заглушка для пагинации
        total_orders = len(orders)
        total_pages = (total_orders + elemCount - 1) // elemCount if total_orders > 0 else 1

        return {
            "orders": orders_dto,
            "pagination": PaginationResponse(
                total_pages=total_pages,
                cur_page=pagesNum
            )
        }
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении заказов: {str(e)}"
        )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
        order_id: str,
        order_service: OrderService = Depends(get_order_service),
        current_user: User = Depends(get_current_user)
):
    """Получить заказ по ID"""
    try:
        order = await order_service.get_order(order_id, current_user.id)

        return OrderResponse(
            id=str(order.id),
            user_id=str(order.user_id),
            items=[],  # Упрощаем
            total=order.total,
            status=order.status.value,  # Используем .value для enum
            delivery_address=str(order.delivery_address),
            phone=str(order.phone),
            comment=order.comment,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Заказ не найден: {str(e)}"
        )


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
        order_id: str,
        status_data: OrderStatusUpdateRequest,
        order_service: OrderService = Depends(get_order_service),
        current_user: User = Depends(get_current_user)
):
    """Изменить статус заказа (только для админов)"""
    try:
        if not current_user.is_admin():
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,  # Исправлено
                detail="Требуются права администратора"
            )

        # Преобразуем строку в OrderStatus enum
        try:
            order_status = OrderStatus(status_data.status)
        except ValueError:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,  # Исправлено
                detail=f"Неверный статус: {status_data.status}"
            )

        order = await order_service.update_order_status(
            order_id=order_id,
            status=order_status,
            current_user_id=current_user.id
        )

        return OrderResponse(
            id=str(order.id),
            user_id=str(order.user_id),
            items=[],  # Упрощаем
            total=order.total,
            status=order.status.value,  # Используем .value для enum
            delivery_address=str(order.delivery_address),
            phone=str(order.phone),
            comment=order.comment,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,  # Исправлено
            detail=f"Ошибка при обновлении статуса: {str(e)}"
        )


@router.delete("/{order_id}")
async def cancel_order(
        order_id: str,
        order_service: OrderService = Depends(get_order_service),
        current_user: User = Depends(get_current_user)
):
    """Отменить заказ"""
    try:
        await order_service.cancel_order(order_id, current_user.id)
        return {"message": "Заказ успешно отменен"}
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,  # Исправлено
            detail=f"Ошибка при отмене заказа: {str(e)}"
        )


# Админские endpoint'ы
@router.get("/admin/all", response_model=dict)
async def get_all_orders(
        status_filter: Optional[str] = Query(None, description="Фильтр по статусу"),  # Переименовано
        userId: Optional[str] = Query(None, description="Фильтр по ID пользователя"),
        pagesNum: int = Query(1, ge=1, description="Номер страницы"),
        elemCount: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
        order_service: OrderService = Depends(get_order_service),
        current_user: User = Depends(get_current_user)
):
    """Получить все заказы (только для админов)"""
    try:
        if not current_user.is_admin():
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,  # Исправлено
                detail="Требуются права администратора"
            )

        skip = (pagesNum - 1) * elemCount

        # Преобразуем строку статуса в OrderStatus если он указан
        order_status: Optional[OrderStatus] = None
        if status_filter:  # Исправлено: используем новое имя
            try:
                order_status = OrderStatus(status_filter)  # Исправлено
            except ValueError:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,  # Исправлено
                    detail=f"Неверный статус: {status_filter}"  # Исправлено
                )

        orders = await order_service.get_all_orders(
            skip=skip,
            limit=elemCount,
            status=order_status,
            user_id=userId,
            current_user_id=current_user.id
        )

        # Преобразуем заказы в DTO
        orders_dto = []
        for order in orders:
            orders_dto.append(OrderResponse(
                id=str(order.id),
                user_id=str(order.user_id),
                items=[],  # Упрощаем
                total=order.total,
                status=order.status.value,  # Используем .value для enum
                delivery_address=str(order.delivery_address),
                phone=str(order.phone),
                comment=order.comment,
                created_at=order.created_at,
                updated_at=order.updated_at
            ))

        # Подсчет страниц
        total_orders = len(orders)
        total_pages = (total_orders + elemCount - 1) // elemCount if total_orders > 0 else 1

        return {
            "orders": orders_dto,
            "pagination": PaginationResponse(
                total_pages=total_pages,
                cur_page=pagesNum
            )
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,  # Исправлено
            detail=f"Ошибка при получении всех заказов: {str(e)}"
        )