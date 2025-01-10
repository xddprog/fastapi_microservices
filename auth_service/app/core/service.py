import json
from jwt import encode
import datetime
import uuid
import aio_pika
from aio_pika.abc import AbstractQueue

from infrastructure.broker.rabbit_broker import RabbitBroker
from infrastructure.config.enums import BrokerQueues, UserServiceRoutes
from infrastructure.config.config import jwt_config


class AuthService:
    def __init__(self, rabbit_client: RabbitBroker):
        self.broker = rabbit_client
        self.queue = None

    async def create_access_token(self, username: str) -> str:
        expire = datetime.now() + datetime.timedelta(minutes=jwt_config.JWT_ACCESS_TOKEN_TIME)
        data = {"exp": expire, "sub": username}
        return encode(
            data,
            jwt_config.JWT_SECRET, 
            algorithm=jwt_config.JWT_ALGORITHM
        )

    async def register_user(self, message: aio_pika.IncomingMessage):
        correlation_id = str(uuid.uuid4())
        user_dto = json.loads(message.body)
        await self.broker.send_message(
            queue_name=BrokerQueues.USERS,
            message=json.dumps(user_dto),
            correlation_id=f"{UserServiceRoutes.CREATE.value}__{correlation_id}",
            reply_to=message.reply_to
        )
        
        queue = await self.broker.channel.get_queue(BrokerQueues.AUTH)
        async with queue.iterator() as auth_queue:
            async for message in auth_queue:
                print("message get reply")
                if message.correlation_id == correlation_id:
                    message = json.loads(message.body)
                    error = message.get("error")
                    if error:
                        return error
                    token = await self.create_access_token(message["username"])
                    return {"token": token}
        