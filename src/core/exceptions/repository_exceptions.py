class RepositoryException(Exception):
    """Базовое исключение для репозиториев"""
    pass

class EntityNotFoundException(RepositoryException):
    """Исключение когда сущность не найдена"""
    def __init__(self, entity_name: str, entity_id: str):
        self.entity_name = entity_name
        self.entity_id = entity_id
        super().__init__(f"{entity_name} с ID {entity_id} не найден")

class DuplicateEntityException(RepositoryException):
    """Исключение когда сущность уже существует"""
    def __init__(self, entity_name: str, field: str, value: str):
        self.entity_name = entity_name
        self.field = field
        self.value = value
        super().__init__(f"{entity_name} с {field} '{value}' уже существует")