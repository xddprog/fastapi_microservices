import asyncio
import aio_pika
from sqlalchemy.testing.pickleable import User
from infrastructure.database.connection import DatabaseConnection
from core.service import UserService
from infrastructure.broker.rabbit_broker import RabbitBroker
from infrastructure.config.enums import BrokerQueues, UserServiceRoutes
from core.repository import UserRepository


class UserController:
    def __init__(
        self, 
        rabbit_client: RabbitBroker,
        db_connection: DatabaseConnection
    ):
        self.service = None
        self.broker = rabbit_client
        self.db_connection = db_connection

    async def get_handler(self, route: str):
        handlers = {
            UserServiceRoutes.CREATE.value: self.service.create_user,
            UserServiceRoutes.UPDATE.value: self.service.update_user,
            UserServiceRoutes.CHECK_USER_EXIST.value: self.service.check_user_exist_by_email,
        }
        return handlers.get(route)
    
    async def on_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            route = message.correlation_id.split("__")[0]
            handler = self.get_handler(route)
            if handler:
                try:
                    session = await self.db_connection.get_session()
                    self.service = UserService(
                        UserRepository(session), 
                        self.broker,
                        await self.broker.channel.get_queue(BrokerQueues.USERS)
                    )
                    await handler(message)
                except Exception as e:
                    print(e)
                finally:
                    await session.close()

    async def start(self):
        self.queue = await self.broker.declare_queue(BrokerQueues.USERS)

    async def close(self):
        await self.broker.close(BrokerQueues.USERS)

    async def consuming(self):
        async with self.queue.iterator() as auth_queue:
            async for message in auth_queue:
                asyncio.create_task(self.on_message(message))