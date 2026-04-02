from fastapi import FastAPI

from app.api.v1.routers import calc as calc_router
from app.config import settings


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name
    )

    application.include_router(calc_router.router, prefix="/v1")

    return application


app = create_app()
