"""Базовый репозиторий с общими операциями для всех таблиц."""

from typing import Generic, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar('ModelType', bound=Base)  # noqa: WPS462


class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий: очистка и массовая вставка записей."""

    def __init__(self, model: type[ModelType]) -> None:
        """Инициализирует репозиторий с конкретной ORM-моделью.

        Args:
            model: Класс ORM-модели (не экземпляр).
        """
        self._model = model

    async def clear_table(self, session: AsyncSession) -> None:
        """Удаляет все строки из таблицы модели."""
        await session.execute(delete(self._model))

    async def bulk_insert(
        self,
        session: AsyncSession,
        records: list[dict],
    ) -> None:
        """Массово вставляет записи в таблицу модели."""
        session.add_all([self._model(**record) for record in records])

    async def get_all(self, session: AsyncSession) -> list[ModelType]:
        """Возвращает все записи из таблицы модели."""
        return (await session.execute(select(self._model))).scalars().all()
