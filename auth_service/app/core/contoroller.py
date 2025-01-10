import aio_pika
from core.service import AuthService
from infrastructure.broker.rabbit_broker import RabbitBroker
from infrastructure.config.enums import AuthServiceRoutes, BrokerQueues


class AuthController:
    def __init__(self, service: AuthService, rabbit_client: RabbitBroker):
        self.service = service
        self.broker = rabbit_client

    async def on_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            route = message.correlation_id.split("__")[0]
            if route == AuthServiceRoutes.REGISTER.value:
                await self.service.register_user(message)

    async def start(self):
        try:
            queue = await self.broker.declare_queue(BrokerQueues.AUTH)
            async with queue.iterator() as auth_queue:
                async for message in auth_queue:
                    print("message_get")
                    await self.on_message(message)
        finally:
            await self.broker.close(BrokerQueues.AUTH)