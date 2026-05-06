"""Репозиторий для таблиц industry_data и common_info_industry."""

from app.models.industry import CommonInfoIndustry, IndustryDataORM
from app.repositories.base import BaseRepository

industry_repository = BaseRepository(IndustryDataORM)
common_info_industry_repository = BaseRepository(CommonInfoIndustry)
