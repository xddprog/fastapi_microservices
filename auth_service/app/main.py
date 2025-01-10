import asyncio
from infrastructure.broker.rabbit_broker import RabbitBroker
from core.contoroller import AuthController
from core.service import AuthService
from infrastructure.config.enums import BrokerQueues


async def start_service():
    rabbit_client: RabbitBroker = await RabbitBroker()()
    auth_service = AuthService(
        rabbit_client, 
    )
    auth_controller = AuthController(auth_service, rabbit_client)

    await auth_controller.start()


if __name__ == "__main__":
    asyncio.run(start_service())