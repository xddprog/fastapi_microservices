import json
from multiprocessing import process
import uuid

from aio_pika.abc import AbstractQueue
from fastapi import HTTPException
from gateway.app.core.dto.user import CreateUserModel, LoginUserModel, UserModel
from gateway.app.infrastructure.brokers.rabbit_broker import RabbitBroker
from gateway.app.infrastructure.config.enums import AuthServiceRoutes, BrokerQueues


class AuthMessages:
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
    
    async def get_current_user(self, token: str) -> UserModel:
        response_id = str(uuid.uuid4())
        correlation_id = f"{AuthServiceRoutes.GET_CURRENT_USER.value}__{response_id}"
        await self.broker.send_message(BrokerQueues.AUTH,token,correlation_id)

        user = await self._consume_message(response_id)
        return UserModel.model_validate(user)
    
    async def register_user(self, user_dto: CreateUserModel) -> tuple[UserModel, str, str]:
        response_id = str(uuid.uuid4())
        correlation_id = f"{AuthServiceRoutes.REGISTER.value}__{response_id}"
        await self.broker.send_message(
            BrokerQueues.AUTH,
            user_dto.model_dump(),
            correlation_id=correlation_id
        )

        data = await self._consume_message(response_id)
        return (
            UserModel.model_validate(data["user"]),
            data["access_token"],
            data["refresh_token"]
        )

    async def login_user(self, user_dto: LoginUserModel) -> dict:
        response_id = str(uuid.uuid4())
        correlation_id = f"{AuthServiceRoutes.LOGIN.value}__{response_id}"
        await self.broker.send_message(
            BrokerQueues.AUTH,
            user_dto.model_dump(),
            correlation_id=correlation_id
        )

        data = await self._consume_message(response_id)
        return (
            UserModel(**data["user"]),
            data["access_token"],
            data["refresh_token"]
        )
    