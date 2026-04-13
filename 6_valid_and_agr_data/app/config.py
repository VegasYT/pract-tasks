"""Настройки приложения."""

from pydantic_settings import BaseSettings

_DSN_TEMPLATE = (
    'postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}'
)


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения."""

    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    model_config = {'env_file': '.env'}

    @property
    def database_url(self) -> str:
        """Собирает DSN для подключения к PostgreSQL."""
        return _DSN_TEMPLATE.format(
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            name=self.db_name,
        )


settings = Settings()
