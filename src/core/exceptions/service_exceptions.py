class ServiceException(Exception):
    """Базовое исключение для сервисов"""
    pass

class AuthenticationException(ServiceException):
    """Исключение аутентификации"""
    def __init__(self, message: str = "Неверные учетные данные"):
        super().__init__(message)

class AuthorizationException(ServiceException):
    """Исключение авторизации"""
    def __init__(self, message: str = "Доступ запрещен"):
        super().__init__(message)

class ValidationException(ServiceException):
    """Исключение валидации"""
    def __init__(self, message: str = "Неверные данные"):
        super().__init__(message)

class BusinessRuleException(ServiceException):
    """Исключение бизнес-правил"""
    def __init__(self, message: str = "Нарушение бизнес-правил"):
        super().__init__(message)