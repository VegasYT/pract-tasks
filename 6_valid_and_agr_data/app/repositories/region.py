"""Репозитории для таблиц region_data и common_info_region."""

from app.models.region import CommonInfoRegion, RegionDataORM
from app.repositories.base import BaseRepository

region_repository = BaseRepository(RegionDataORM)
common_info_region_repository = BaseRepository(CommonInfoRegion)
