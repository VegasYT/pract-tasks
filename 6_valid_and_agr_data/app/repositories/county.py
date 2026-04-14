"""Репозиторий для работы с таблицей CountyDataORM."""

from app.models.county import CountyDataORM
from app.repositories.base import BaseRepository

county_repository = BaseRepository(CountyDataORM)
