"""Репозиторий для работы с таблицей RegionDataORM."""

from app.models.region import RegionDataORM
from app.repositories.base import BaseRepository

region_repository = BaseRepository(RegionDataORM)
