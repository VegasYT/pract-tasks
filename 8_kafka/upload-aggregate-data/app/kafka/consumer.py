"""Kafka consumer для обработки сообщений о загрузке CSV."""

import base64
import json
import logging

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

from app.config import settings
from app.db.session import async_session_maker
from app.services import company as company_service

_MAX_FETCH_MB = 20

logger = logging.getLogger(__name__)


async def _process_message(raw_value: bytes) -> None:
    """Декодирует сообщение и запускает загрузку CSV в БД."""
    payload = json.loads(raw_value)
    filename = payload.get('filename', 'unknown')
    file_bytes = base64.b64decode(payload['content'])

    logger.info('processing file: %s', filename)

    async with async_session_maker() as session:
        rows = await company_service.load_companies(session, file_bytes)

    logger.info('file %s loaded, rows: %d', filename, rows)


async def _consume_messages(consumer: AIOKafkaConsumer) -> None:
    """Читает сообщения из consumer в бесконечном цикле."""
    async for msg in consumer:
        logger.info(
            'message received, partition=%d offset=%d',
            msg.partition,
            msg.offset,
        )
        try:
            await _process_message(msg.value)
        except (KeyError, ValueError, json.JSONDecodeError) as format_exc:
            logger.error('invalid message format: %s', format_exc)
        except Exception as process_exc:  # noqa: WPS broad-except
            logger.error('error processing message: %s', process_exc)


async def run_consumer() -> None:
    """Запускает Kafka consumer и слушает топик бесконечно."""
    consumer = AIOKafkaConsumer(
        settings.kafka_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_group_id,
        auto_offset_reset='earliest',
        max_partition_fetch_bytes=_MAX_FETCH_MB * 1024 * 1024,
    )
    await consumer.start()
    logger.info('consumer started, topic: %s', settings.kafka_topic)

    try:
        await _consume_messages(consumer)
    except KafkaError as exc:
        logger.error('kafka error: %s', exc)
    finally:
        await consumer.stop()
        logger.info('consumer stopped')
