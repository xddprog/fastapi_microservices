import asyncio
from infrastructure.database.connection import DatabaseConnection
from infrastructure.broker.rabbit_broker import RabbitBroker
from core.controller import UserController


async def start_service():
    db_connection = await DatabaseConnection()()
    rabbit_client = await RabbitBroker()()
    user_controller = UserController(rabbit_client, db_connection)
    try:
        await user_controller.start()
        await user_controller.consuming()
    finally:
        await user_controller.close()

if __name__ == "__main__":
    asyncio.run(start_service())