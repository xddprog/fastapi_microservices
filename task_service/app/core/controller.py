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

    async def on_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            route = message.correlation_id.split("__")[0]
            if route:
                try:
                    session = await self.db_connection.get_session()
                    self.service = TaskService(
                        TaskRepository(session), 
                        self.broker,
                        await self.broker.channel.get_queue(BrokerQueues.USERS)
                    )
                    if route == TaskServiceRoutes.CREATE.value:
                        await self.service.create_task(message)
                    elif route == TaskServiceRoutes.UPDATE.value:
                        await self.service.update_task(message)
                    elif route == TaskServiceRoutes.GET.value:
                        await self.service.get_task(message)
                    elif route == TaskServiceRoutes.GET_USER_TASKS.value:
                        await self.service.get_user_tasks(message)
                    elif route == TaskServiceRoutes.DELETE.value:
                        await self.service.delete_task(message)
                finally:
                    await session.close()

    async def start(self):
        self.queue = await self.broker.declare_queue(BrokerQueues.TASKS)

    async def close(self):
        await self.broker.close(BrokerQueues.TASKS)

    async def consuming(self):
        while True:
            message = await self.get_message()
            await self.on_message(message)

    async def get_message(self):
        async with self.queue.iterator() as tasks_queue:
            print("start get message")
            async for message in tasks_queue:
                print(message)
                return message