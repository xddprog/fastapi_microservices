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

    async def on_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            route = message.correlation_id.split("__")[0]
            if route:
                try:
                    session = await self.db_connection.get_session()
                    self.service = UserService(
                        UserRepository(session), 
                        self.broker,
                        await self.broker.channel.get_queue(BrokerQueues.USERS)
                    )
                    if route == UserServiceRoutes.CREATE.value:
                        await self.service.create_user(message)
                    elif route == UserServiceRoutes.UPDATE.value:
                        await self.service.update_user(message)
                    elif route == UserServiceRoutes.GET.value:
                        await self.service.get_user(message)
                    elif route == UserServiceRoutes.GET_ALL.value:
                        await self.service.get_all_users()
                    elif route == UserServiceRoutes.DELETE.value:
                        await self.service.delete_user(message)
                    elif route == UserServiceRoutes.CHECK_USER_EXIST.value:
                        await self.service.check_user_exist_by_email(message)
                finally:
                    await session.close()

    async def start(self):
        self.queue = await self.broker.declare_queue(BrokerQueues.USERS)

    async def close(self):
        await self.broker.close(BrokerQueues.USERS)

    async def consuming(self):
        while True:
            message = await self.get_message()
            await self.on_message(message)

    async def get_message(self):
        async with self.queue.iterator() as users_queue:
            async for message in users_queue:
                return message