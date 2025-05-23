import json
from typing import Any
import aio_pika
from aio_pika.abc import AbstractQueue

from infrastructure.config.config import rabbit_config


class RabbitBroker:
    def __init__(self):
        self.connection: aio_pika.Connection = None
        self.channel: aio_pika.Channel = None

    async def declare_queue(self, queue_name: str) -> AbstractQueue:
        return await self.channel.declare_queue(queue_name, durable=True)

    async def send_message(
        self, 
        queue_name: str, 
        message: str,
        correlation_id: str | None = None,
        reply_to: str | None = None
    ):
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=(json.dumps(message)).encode("utf-8"),
                reply_to=reply_to,
                correlation_id=correlation_id
            ), 
            routing_key=queue_name,
        )

    async def __call__(self) -> Any:
        self.connection = await aio_pika.connect_robust(
            host=rabbit_config.RABBIT_HOST,
            port=rabbit_config.RABBIT_PORT,
        )
        self.channel = await self.connection.channel()
        return self

    async def close(self, queue_name: str):
        await self.channel.queue_delete(queue_name)
        await self.connection.close()
        await self.channel.close()