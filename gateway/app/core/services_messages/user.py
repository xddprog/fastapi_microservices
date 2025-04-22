import json
import uuid
from aio_pika.abc import AbstractQueue
from fastapi import HTTPException
from app.core.dto.user import UpdateUserModel, UserModel
from app.infrastructure.brokers.rabbit_broker import RabbitBroker
from app.infrastructure.config.enums import BrokerQueues, UserServiceRoutes


class UserMessages:    
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
                finally:
                    await message.ack()

    async def update_user(self, user_id: int, user_dto: UpdateUserModel):
        correlation_id = str(uuid.uuid4())
        user = user_dto.model_dump()
        user.update({"user_id": user_id})
        await self.broker.send_message(
            queue_name=BrokerQueues.USERS,
            message=json.dumps(user),
            correlation_id=f"{UserServiceRoutes.UPDATE.value}__{correlation_id}"
        )

        user = await self._consume_message(correlation_id)
        return UserModel.model_validate(user)
    