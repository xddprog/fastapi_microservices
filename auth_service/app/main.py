import asyncio
from infrastructure.broker.rabbit_broker import RabbitBroker
from core.controller import AuthController
from core.service import AuthService
from infrastructure.config.enums import BrokerQueues


async def start_service():
    try:
        rabbit_client: RabbitBroker = await RabbitBroker()()
        auth_service = AuthService(
            rabbit_client, 
        )
        auth_controller = AuthController(auth_service, rabbit_client)
        
        await auth_controller.start()
        await auth_controller.consuming()
    finally:
        await auth_controller.close()


if __name__ == "__main__":
    asyncio.run(start_service())