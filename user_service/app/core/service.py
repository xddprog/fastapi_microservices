import json
from re import A
import aio_pika
from aio_pika.abc import AbstractQueue
from passlib.context import CryptContext
from core.dto import CreateUserModel, UpdateUserModel, UserModel
from core.repository import UserRepository
from infrastructure.config.enums import AuthServiceRoutes
from infrastructure.broker.rabbit_broker import RabbitBroker
from infrastructure.config.enums import BrokerQueues
from core.errors import UserAlreadyExistsError, UserNotFoundError


class UserService:
    def __init__(
        self, 
        repository: UserRepository, 
        rabbit_client: RabbitBroker,
        queue: AbstractQueue
    ):
        self.repository = repository
        self.broker = rabbit_client
        self.queue = queue


    async def _get_user_by_email(self, email: str):
        return await self.repository.get_by_attribute(
            self.repository.model.email, email
        )

    async def check_user_exist_by_email(self, message: aio_pika.IncomingMessage):
        email = json.loads(json.loads(message.body.decode("utf-8")))
        user_exist = await self._get_user_by_email(email)
        if not user_exist:
            return await self.broker.send_message(
                queue_name=BrokerQueues.AUTH,
                message=json.dumps(UserNotFoundError),
                correlation_id=message.correlation_id
            )
        return await self.broker.send_message(
            queue_name=BrokerQueues.AUTH,
            message=json.dumps(
                UserModel
                .model_validate(user_exist[0], from_attributes=True)
                .model_dump()
            ),
            correlation_id=message.correlation_id
        )

    async def create_user(self, message: aio_pika.IncomingMessage):
        user_data = json.loads(json.loads(message.body.decode("utf-8")))

        user_exist = await self._get_user_by_email(user_data.get("email"))
        if user_exist:
            return await self.broker.send_message(
                queue_name=BrokerQueues.AUTH,
                message=json.dumps(UserAlreadyExistsError),
                correlation_id=message.correlation_id
            )
        
        new_user = await self.repository.add_item(**user_data)
        new_user = UserModel.model_validate(new_user, from_attributes=True)
        return await self.broker.send_message(
            queue_name=BrokerQueues.AUTH,
            message=json.dumps(new_user.model_dump()),
            correlation_id=message.correlation_id
        )

    async def update_user(self, message: aio_pika.IncomingMessage):
        user_dto = json.loads(message.body.decode("utf-8"))
        updated_user = await self.repository.update_item(user_dto)
        updated_user = UserModel.model_validate(updated_user, from_attributes=True)

        return await self.broker.send_message(
            queue_name=BrokerQueues.AUTH,
            message=json.dumps(updated_user.model_dump()),
            correlation_id=message.correlation_id
        )
