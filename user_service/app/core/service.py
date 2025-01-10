import json
import aio_pika
from core.dto import CreateUserModel, UpdateUserModel, UserModel
from core.repository import UserRepository


class UserService:
    def __init__(
        self, 
        repository: UserRepository, 
        channel: aio_pika.Channel, 
    ):
        self.repository = repository
        self.channel = channel

    async def create_user(self, message: aio_pika.IncomingMessage):
        decoded_body = message.body.decode("utf-8")
        user_data = json.loads(decoded_body)
        if isinstance(user_data, str):
            user_data = json.loads(user_data)
        new_user = await self.repository.add_item(**user_data)
        new_user = UserModel.model_validate(new_user, from_attributes=True)

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
    