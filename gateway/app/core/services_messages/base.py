import json
import uuid

from aio_pika.abc import AbstractQueue
from fastapi import HTTPException
from gateway.app.core.dto.user import CreateUserModel, LoginUserModel, UserModel
from gateway.app.infrastructure.brokers.rabbit_broker import RabbitBroker
from gateway.app.infrastructure.config.enums import AuthServiceRoutes, BrokerQueues


class BaseMessages:
    def __init__(self, broker: RabbitBroker, queue: AbstractQueue):
        self.broker = broker
        self.queue = queue

    async def _raise_exception(self, error: dict):
        raise HTTPException(
            status_code=error.get("status"),
            detail=error.get("detail")
        )
    
    async def _consume_message(self, response_id: str) -> dict:
        async with self.queue.iterator() as gateway_queue:
            async for message in gateway_queue:
                try:
                    if message.correlation_id.split("__")[-1] == response_id:
                        message_body = json.loads(message.body)
                        if isinstance(message_body, str):
                            message_body = json.loads(message_body)

                        error = message_body.get("error")
                        if error:
                            await self._raise_exception(error)
                        return message_body
                except Exception as e:
                    raise e
                finally:
                    await message.ack()
    