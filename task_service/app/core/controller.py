import aio_pika
from sqlalchemy.testing.pickleable import User
from infrastructure.database.connection import DatabaseConnection
from core.service import TaskService
from infrastructure.broker.rabbit_broker import RabbitBroker
from core.repository import TaskRepository
from infrastructure.config.enums import BrokerQueues


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
            route = message.correlation_id.split("_")[0]
            if route:
                self.service = TaskService(
                    TaskRepository(self.db_connection.get_session()), 
                    self.broker
                )

    async def start(self):
        try:
            queue = await self.broker.declare_queue(BrokerQueues.USERS)
            async with queue.iterator() as auth_queue:
                async for message in auth_queue:
                    await self.on_message(message)
        finally:
            await self.broker.close()