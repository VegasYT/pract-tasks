"""Точка входа FastAPI приложения rest-api-async."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.v1.endpoints.aggregates import router as aggregates_router
from app.api.v1.endpoints.companies import router as companies_router
from app.api.v1.endpoints.regions import router as regions_router
from app.api.v1.endpoints.upload import router as upload_router
from app.core.logging import setup_logging
from app.core.users import auth_backend, fastapi_users
from app.kafka.producer import start_producer, stop_producer
from app.schemas.user import UserCreate, UserRead

setup_logging()

logger = logging.getLogger(__name__)

_API_PREFIX = '/api/v1'  # noqa: WPS226
_AUTH_PREFIX = '/api/v1/auth'  # noqa: WPS226


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """Запускает Kafka producer при старте, останавливает при завершении."""
    await start_producer()
    logger.info('application startup complete')
    yield
    await stop_producer()
    logger.info('application shutdown complete')


app = FastAPI(title='REST API Async', lifespan=lifespan)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix=_AUTH_PREFIX,
    tags=['auth'],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix=_AUTH_PREFIX,
    tags=['auth'],
)

app.include_router(upload_router, prefix=_API_PREFIX)
app.include_router(companies_router, prefix=_API_PREFIX)
app.include_router(regions_router, prefix=_API_PREFIX)
app.include_router(aggregates_router, prefix=_API_PREFIX)
