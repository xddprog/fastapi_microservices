import asyncio
from infrastructure.database.connection import DatabaseConnection
from infrastructure.broker.rabbit_broker import RabbitBroker
from core.controller import TaskController


async def start_service():
    db_connection = await DatabaseConnection()()
    rabbit_client = await RabbitBroker()()
    user_controller = TaskController(rabbit_client, db_connection)
    await user_controller.start()


if __name__ == "__main__":
    asyncio.run(start_service())