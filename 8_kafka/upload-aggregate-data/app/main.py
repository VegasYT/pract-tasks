"""Точка входа FastAPI приложения."""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.v1.endpoints.upload import router as upload_router
from app.core.logging import setup_logging
from app.kafka.consumer import run_consumer

setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """Запускает Kafka consumer при старте, останавливает при завершении."""
    task = asyncio.create_task(run_consumer())
    logger.info('application startup complete')
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.debug('consumer task cancelled')
    logger.info('application shutdown complete')


app = FastAPI(title='Upload Aggregate Data', lifespan=lifespan)

app.include_router(upload_router, prefix='/api/v1')
