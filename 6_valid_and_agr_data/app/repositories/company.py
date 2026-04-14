"""Репозиторий для работы с таблицей CompanyDataORM."""

from app.models.company import CompanyDataORM
from app.repositories.base import BaseRepository

company_repository = BaseRepository(CompanyDataORM)
