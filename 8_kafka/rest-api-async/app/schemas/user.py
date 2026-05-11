"""Pydantic схемы пользователя."""

import uuid

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    """Схема для чтения данных пользователя."""


class UserCreate(schemas.BaseUserCreate):
    """Схема для создания (регистрации) пользователя."""


class UserUpdate(schemas.BaseUserUpdate):
    """Схема для обновления данных пользователя."""
