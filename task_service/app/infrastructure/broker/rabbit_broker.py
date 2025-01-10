from typing import Any, Awaitable
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
        reply_to: str | None = None,
        on_response: Awaitable = None
    ):
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=message.encode("utf-8"),
                reply_to=reply_to,
                correlation_id=correlation_id,
                on_response=on_response
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
    
    async def on_response(self, message: aio_pika.IncomingMessage):
        if message.correlation_id == self.correlation_id:
            self.response = message.body.decode()
            await message.ack()

    async def close(self):
        await self.connection.close()
        await self.channel.close()