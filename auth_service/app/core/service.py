import json
from jwt import InvalidTokenError, decode, encode
from datetime import datetime, timedelta
import uuid
import aio_pika
from aio_pika.abc import AbstractQueue
from passlib.context import CryptContext

from infrastructure.broker.rabbit_broker import RabbitBroker
from infrastructure.config.enums import BrokerQueues, UserServiceRoutes
from infrastructure.config.config import jwt_config
from core.errors import InvalidToken


class AuthService:
    def __init__(self, rabbit_client: RabbitBroker):
        self.broker = rabbit_client
        self.queue = None
        self.context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.context.verify(password, hashed_password)

    async def create_access_token(self, email: str) -> str:
        expire = datetime.now() + timedelta(minutes=jwt_config.JWT_ACCESS_TOKEN_TIME)
        data = {"exp": expire, "sub": email}
        return encode(
            data,
            jwt_config.JWT_SECRET, 
            algorithm=jwt_config.JWT_ALGORITHM
        )
    
    async def create_refresh_token(self, email: str ):
        expire = datetime.now() + timedelta(days=jwt_config.JWT_REFRESH_TOKEN_TIME)
        data = {"exp": expire, "sub": email}
        return encode(
            data, 
            jwt_config.JWT_SECRET, 
            algorithm=jwt_config.JWT_ALGORITHM
        )
    
    async def _get_user_by_email(self, email: str, correlation_id: str, gateway_correlation_id: str) -> dict:
        await self.broker.send_message(
            queue_name=BrokerQueues.USERS,
            message=json.dumps(email),
            correlation_id=f"{UserServiceRoutes.CHECK_USER_EXIST.value}__{correlation_id}"
        )
        
        queue = await self.broker.channel.get_queue(BrokerQueues.AUTH)
        async with queue.iterator() as auth_queue:
            async for user_service_message in auth_queue:
                if user_service_message.correlation_id.split("__")[-1] == correlation_id:
                    user_service_message_body = json.loads(user_service_message.body)
                    await user_service_message.ack()
                    if await self._handle_error(user_service_message_body, gateway_correlation_id):
                        return user_service_message_body
                    return user_service_message_body

    async def _handle_error(self, message_body: dict, correlation_id: str):
        error = message_body.get("error")
        if error:
            await self.broker.send_message(
                queue_name=BrokerQueues.GATEWAY,
                message=message_body,
                correlation_id=correlation_id
            )
            return error
        
    async def _handle_success_auth(self, message_body: dict, correlation_id: str) -> None:
        access_token = await self.create_access_token(message_body["username"])
        refresh_token = await self.create_refresh_token(message_body["username"])
        return await self.broker.send_message(
            queue_name=BrokerQueues.GATEWAY,
            message=json.dumps({
                "access_token": access_token, 
                "refresh_token": refresh_token,
                "user": message_body
            }),
            correlation_id=correlation_id
        )
    
    async def verify_token(self, token: str, correlation_id: str, gateway_correlation_id: str) -> dict:
        if not token:
            return InvalidToken
        try:
            print(1)
            payload = decode(
                token,
                jwt_config.JWT_SECRET,
                algorithms=[jwt_config.JWT_ALGORITHM],
            )
            email = payload.get("sub")
            if not email:
                return InvalidToken
                
            user = await self._get_user_by_email(email, correlation_id, gateway_correlation_id)
            if not user:
                return InvalidToken
            return user
        except (InvalidTokenError, AttributeError) as e:
            return InvalidToken
        except Exception as e:
            print(e)


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
                if user_service_message.correlation_id.split("__")[-1] == correlation_id:
                    user_service_message_body = json.loads(user_service_message.body) 
                    await user_service_message.ack()

                    if await self._handle_error(user_service_message_body, message.correlation_id):
                        return user_service_message_body
                    return await self._handle_success_auth(user_service_message_body, message.correlation_id)

    async def login_user(self, message: aio_pika.IncomingMessage):
        correlation_id = str(uuid.uuid4())
        user_dto = json.loads(message.body)
        await self.broker.send_message(
            queue_name=BrokerQueues.USERS,
            message=json.dumps(user_dto.get("email")),
            correlation_id=f"{UserServiceRoutes.CHECK_USER_EXIST.value}__{correlation_id}"
        )
        
        queue = await self.broker.channel.get_queue(BrokerQueues.AUTH)
        async with queue.iterator() as auth_queue:
            async for user_service_message in auth_queue:
                if user_service_message.correlation_id.split("__")[-1] == correlation_id:
                    user_service_message_body = json.loads(user_service_message.body)
                    await user_service_message.ack()
                    if await self._handle_error(user_service_message_body, message.correlation_id):
                        return user_service_message_body
                    return await self._handle_success_auth(user_service_message_body, message.correlation_id)

    async def get_current_user(self, message: aio_pika.IncomingMessage):
        correlation_id = str(uuid.uuid4())
        token = json.loads(message.body)
        user_data = await self.verify_token(token, correlation_id, message.correlation_id)
        return await self.broker.send_message(
            queue_name=BrokerQueues.GATEWAY,
            message=user_data,
            correlation_id=message.correlation_id
        )
