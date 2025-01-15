import asyncio
from infrastructure.database.connection import DatabaseConnection
from infrastructure.broker.rabbit_broker import RabbitBroker
from core.controller import TaskController


async def start_service():
    db_connection = await DatabaseConnection()()
    rabbit_client = await RabbitBroker()()
    task_controller = TaskController(rabbit_client, db_connection)
    try:
        await task_controller.start()
        await task_controller.consuming()
    finally:
        await task_controller.close()

if __name__ == "__main__":
    asyncio.run(start_service())