"""Kafka producer для отправки сообщений о загрузке CSV."""

import json
import logging

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from app.config import settings

logger = logging.getLogger(__name__)

_producer: AIOKafkaProducer | None = None


def _serialize(payload: dict) -> bytes:
    """Сериализует словарь в JSON-байты."""
    return json.dumps(payload).encode('utf-8')


async def start_producer() -> None:
    """Инициализирует и запускает глобальный producer."""
    global _producer  # noqa: WPS420, WPS442, WPS122
    _producer = AIOKafkaProducer(  # noqa: WPS121
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=_serialize,
        max_request_size=20 * 1024 * 1024,  # noqa: WPS432
    )
    await _producer.start()
    logger.info('kafka producer started')


async def stop_producer() -> None:
    """Останавливает глобальный producer."""
    if _producer is not None:
        await _producer.stop()
        logger.info('kafka producer stopped')


async def send_upload_message(filename: str, content_b64: str) -> None:
    """Отправляет сообщение о загрузке CSV в Kafka.

    Args:
        filename: Имя файла.
        content_b64: Содержимое файла в base64.
    """
    if _producer is None:
        raise RuntimeError('kafka producer is not started')  # noqa: WPS454

    payload = {'filename': filename, 'content': content_b64}
    try:
        await _producer.send_and_wait(settings.kafka_topic, payload)
    except KafkaError as exc:
        logger.error('failed to send message to kafka: %s', exc)
        raise
    logger.info(
        'message sent to topic %s, file: %s', settings.kafka_topic, filename,
    )
