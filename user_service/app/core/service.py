import json
from re import A
import aio_pika
from aio_pika.abc import AbstractQueue
from core.dto import CreateUserModel, UpdateUserModel, UserModel
from core.repository import UserRepository
from infrastructure.config.enums import AuthServiceRoutes
from infrastructure.broker.rabbit_broker import RabbitBroker
from infrastructure.config.enums import BrokerQueues
from core.errors import UserAlreadyExistsError


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

    async def get_user_by_email(self, email: str):
        return await self.repository.get_by_attribute(
            self.repository.model.email, email
        )

    async def create_user(self, message: aio_pika.IncomingMessage):
        decoded_body = message.body.decode("utf-8")
        user_data = json.loads(json.loads(decoded_body))

        user_exist = await self.get_user_by_email(user_data.get("email"))
        if user_exist:
            print(message.correlation_id, "error")
            return await self.broker.send_message(
                queue_name=BrokerQueues.AUTH,
                message=json.dumps(UserAlreadyExistsError),
                correlation_id=message.correlation_id
            )
        
        print(2)
        
        new_user = await self.repository.add_item(**user_data)
        new_user = UserModel.model_validate(new_user, from_attributes=True)
        return await self.broker.send_message(
            queue_name=BrokerQueues.AUTH,
            message=json.dumps(new_user.model_dump()),
            correlation_id=message.correlation_id
        )

    async def update_user(self, user_dto: UpdateUserModel):
        updated_user = await self.repository.update_item(user_dto)
        return UserModel.model_validate(updated_user, from_attributes=True)

    async def delete_user(self, user_id: int):
        user = await self.repository.get_item(user_id)
        await self.repository.delete_item(user)

    async def get_user(self, user_id: int):
        user = await self.repository.get_item(user_id)
        return UserModel.model_validate(user, from_attributes=True)

    async def get_all_tasks(self):
        users = await self.repository.get_all_items()
        return [UserModel.model_validate(user, from_attributes=True) for user in users]
    