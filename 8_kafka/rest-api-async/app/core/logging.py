"""Настройка логирования приложения."""

import logging
import sys


def setup_logging() -> None:
    """Настраивает корневой логгер с выводом в stdout."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        stream=sys.stdout,
    )
