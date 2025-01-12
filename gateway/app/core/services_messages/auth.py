import json
from multiprocessing import process
import uuid

from aio_pika.abc import AbstractQueue
from fastapi import HTTPException
from gateway.app.core.dto.user import CreateUserModel, UserModel
from gateway.app.infrastructure.brokers.rabbit_broker import RabbitBroker
from gateway.app.infrastructure.config.enums import AuthServiceRoutes, BrokerQueues


class AuthMessages:
    def __init__(self, broker: RabbitBroker, queue: AbstractQueue):
        self.broker = broker
        self.queue = queue

    async def raise_exception(self, error: dict):
        raise HTTPException(
            status_code=error.get("status"),
            detail=error.get("detail")
        )
        
    async def get_current_user(self, correlation_id: str) -> UserModel:
        return await self.broker.send_message(
            BrokerQueues.AUTH,
            correlation_id
        )
    
    async def register_user(self, user_dto: CreateUserModel) -> dict:
        response_id = str(uuid.uuid4())
        correlation_id = f"{AuthServiceRoutes.REGISTER.value}__{response_id}"
        await self.broker.send_message(
            BrokerQueues.AUTH,
            user_dto.model_dump(),
            correlation_id=correlation_id
        )

        async with self.queue.iterator() as gateway_queue:
            async for message in gateway_queue:
                print(f"message_get {message.correlation_id}", response_id)
                try:
                    if message.correlation_id.split("__")[-1] == response_id:
                        message_body = json.loads(message.body)
                        if isinstance(message_body, str):
                            message_body = json.loads(message_body)

                        error = message_body.get("error")
                        if error:
                            await self.raise_exception(error)
                        return message_body
                finally:
                    await message.ack()

