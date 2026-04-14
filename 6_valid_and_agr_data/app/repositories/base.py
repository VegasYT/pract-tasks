"""Базовый репозиторий с общими операциями для всех таблиц."""

from typing import Generic, TypeVar

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar('ModelType', bound=Base)  # noqa: WPS462


class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий: очистка и массовая вставка записей"""

    def __init__(self, model: type[ModelType]) -> None:
        """Инициализирует репозиторий с конкретной ORM-моделью.

        Args:
            model: Класс ORM-модели (не экземпляр).
        """
        self._model = model

    async def clear_table(self, session: AsyncSession) -> None:
        """Удаляет все строки из таблицы модели.

        Args:
            session: Асинхронная сессия SQLAlchemy.
        """
        await session.execute(delete(self._model))

    async def bulk_insert(
        self,
        session: AsyncSession,
        records: list[dict],
    ) -> None:
        """Массово вставляет записи в таблицу модели

        Args:
            session: Асинхронная сессия SQLAlchemy.
            records: Список словарей с данными для вставки.
        """
        session.add_all([self._model(**record) for record in records])
