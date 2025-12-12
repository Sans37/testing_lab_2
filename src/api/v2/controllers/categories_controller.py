# src/api/v2/controllers/categories_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from src.core.services.category_service import CategoryService  # Изменили импорт
from src.core.entities.user import User
from src.api.v2.dependencies import get_current_user
# Добавляем зависимость для CategoryService
from src.api.v2.dependencies import get_category_service  # Нужно создать
from src.api.v2.dtos.request_dtos import CategoryCreateRequest, CategoryUpdateRequest
from src.api.v2.dtos.response_dtos import CategoryResponse

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=dict)
async def get_categories(
        category_service: CategoryService = Depends(get_category_service)  # Изменили
):
    """Получить список категорий"""
    try:
        # Используем сервис категорий
        categories = await category_service.get_all_categories()  # Теперь метод существует

        # Преобразуем сущности Category в CategoryResponse
        categories_dto = []
        for category in categories:
            categories_dto.append(CategoryResponse(
                id=str(category.id),
                name=str(category.name),
                description=str(category.description),
                created_at=category.created_at,
                updated_at=category.updated_at
            ))

        return {"categories": categories_dto}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении категорий: {str(e)}"
        )


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
        category_data: CategoryCreateRequest,
        category_service: CategoryService = Depends(get_category_service),  # Изменили
        current_user: User = Depends(get_current_user)
):
    """Создать новую категорию (только для админов)"""
    try:
        if not current_user.is_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Требуются права администратора"
            )

        # Используем сервис категорий
        category = await category_service.create_category(  # Теперь метод существует
            name=category_data.name,
            description=category_data.description or "",
            current_user=current_user
        )

        # Преобразуем сущность Category в CategoryResponse
        return CategoryResponse(
            id=str(category.id),
            name=str(category.name),
            description=str(category.description),
            created_at=category.created_at,
            updated_at=category.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при создании категории: {str(e)}"
        )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
        category_id: str,
        category_data: CategoryUpdateRequest,
        category_service: CategoryService = Depends(get_category_service),  # Изменили
        current_user: User = Depends(get_current_user)
):
    """Обновить категорию (только для админов)"""
    try:
        if not current_user.is_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Требуются права администратора"
            )

        # Подготавливаем данные для обновления
        update_data = {}
        if category_data.name is not None:
            update_data['name'] = category_data.name
        if category_data.description is not None:
            update_data['description'] = category_data.description

        # Используем сервис категорий
        category = await category_service.update_category(  # Теперь метод существует
            category_id=category_id,
            update_data=update_data,
            current_user=current_user
        )

        return CategoryResponse(
            id=str(category.id),
            name=str(category.name),
            description=str(category.description),
            created_at=category.created_at,
            updated_at=category.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при обновлении категории: {str(e)}"
        )


@router.delete("/{category_id}")
async def delete_category(
        category_id: str,
        category_service: CategoryService = Depends(get_category_service),  # Изменили
        current_user: User = Depends(get_current_user)
):
    """Удалить категорию (только для админов)"""
    try:
        if not current_user.is_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Требуются права администратора"
            )

        await category_service.delete_category(  # Теперь метод существует
            category_id=category_id,
            current_user=current_user
        )

        return {"message": "Категория успешно удалена"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при удалении категории: {str(e)}"
        )