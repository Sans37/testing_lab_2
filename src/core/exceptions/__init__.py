# src/core/exceptions/__init__.py
from .repository_exceptions import (
    RepositoryException, EntityNotFoundException, DuplicateEntityException
)

from .service_exceptions import (
    ServiceException, AuthenticationException, AuthorizationException,
    ValidationException, BusinessRuleException
)

__all__ = [
    "RepositoryException", "EntityNotFoundException", "DuplicateEntityException",
    "ServiceException", "AuthenticationException", "AuthorizationException",
    "ValidationException", "BusinessRuleException"
]