import json
from multiprocessing import process
import uuid

from aio_pika.abc import AbstractQueue
from gateway.app.core.dto import CreateUserModel
from gateway.app.infrastructure.brokers.rabbit_broker import RabbitBroker
from gateway.app.infrastructure.config.enums import AuthServiceRoutes, BrokerQueues


class AuthMessages:
    def __init__(self, broker: RabbitBroker, queue: AbstractQueue):
        self.broker = broker
        self.queue = queue
        
    async def get_current_user(self, correlation_id: str) -> dict:
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
            correlation_id=correlation_id,
            reply_to=BrokerQueues.GATEWAY
        )

        async with self.queue.iterator() as gateway_queue:
            async for message in gateway_queue:
                if message.correlation_id == response_id:
                    message_body = json.loads(message.body.decode())
                    error = message_body.get("error")
                    if error:
                        return error
                    return message_body
