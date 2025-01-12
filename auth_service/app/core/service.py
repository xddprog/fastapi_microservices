import json
from jwt import encode
from datetime import datetime, timedelta
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
        expire = datetime.now() + timedelta(minutes=jwt_config.JWT_ACCESS_TOKEN_TIME)
        data = {"exp": expire, "sub": username}
        return encode(
            data,
            jwt_config.JWT_SECRET, 
            algorithm=jwt_config.JWT_ALGORITHM
        )
    
    async def create_refresh_token(self, username: str ):
        expire = datetime.now() + timedelta(minutes=jwt_config.JWT_ACCESS_TOKEN_TIME)
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
            correlation_id=f"{UserServiceRoutes.CREATE.value}__{correlation_id}"
        )
        
        queue = await self.broker.channel.get_queue(BrokerQueues.AUTH)

        async with queue.iterator() as auth_queue:
            async for user_service_message in auth_queue:
                print(f"message get reply {user_service_message.correlation_id} {user_service_message.routing_key}")
                if user_service_message.correlation_id.split("__")[-1] == correlation_id:
                    user_service_message_body = json.loads(user_service_message.body)
                    error = user_service_message_body.get("error")
                    
                    await user_service_message.ack()

                    if error:

                        await self.broker.send_message(
                            queue_name=BrokerQueues.GATEWAY,
                            message=user_service_message_body,
                            correlation_id=message.correlation_id
                        )
                        return error

                    access_token = await self.create_access_token(user_service_message_body["username"])
                    refresh_token = await self.create_refresh_token(user_service_message_body["username"])
                    return await self.broker.send_message(
                        queue_name=BrokerQueues.GATEWAY,
                        message=json.dumps(
                            {
                                "access_token": access_token, 
                                "refresh_token": refresh_token,
                                "user": user_service_message_body
                            }
                        ),
                        correlation_id=message.correlation_id
                    )
