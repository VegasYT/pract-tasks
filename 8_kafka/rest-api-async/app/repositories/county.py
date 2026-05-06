"""Репозиторий для таблиц county_data и common_info_county."""

from app.models.county import CommonInfoCounty, CountyDataORM
from app.repositories.base import BaseRepository

county_repository = BaseRepository(CountyDataORM)
common_info_county_repository = BaseRepository(CommonInfoCounty)
