import asyncio
import aio_pika
from sqlalchemy.testing.pickleable import User
from infrastructure.database.connection import DatabaseConnection
from core.service import TaskService
from infrastructure.broker.rabbit_broker import RabbitBroker
from core.repository import TaskRepository
from infrastructure.config.enums import BrokerQueues, TaskServiceRoutes


class TaskController:
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
            TaskServiceRoutes.CREATE.value: self.service.create_task,
            TaskServiceRoutes.UPDATE.value: self.service.update_task,
            TaskServiceRoutes.DELETE.value: self.service.delete_task,
            TaskServiceRoutes.GET.value: self.service.get_task,
            TaskServiceRoutes.GET_USER_TASKS.value: self.service.get_user_tasks,
        }
        return handlers.get(route)

    async def on_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            route = message.correlation_id.split("__")[0]
            handler = await self.get_handler(route)
            if handler:
                try:
                    session = await self.db_connection.get_session()
                    self.service = TaskService(
                        TaskRepository(session), 
                        self.broker,
                        await self.broker.channel.get_queue(BrokerQueues.USERS)
                    )
                    await handler(message)
                finally:
                    await session.close()

    async def start(self):
        self.queue = await self.broker.declare_queue(BrokerQueues.TASKS)

    async def close(self):
        await self.broker.close(BrokerQueues.TASKS)

    async def consuming(self):
        async with self.queue.iterator() as auth_queue:
            async for message in auth_queue:
                asyncio.create_task(self.on_message(message))