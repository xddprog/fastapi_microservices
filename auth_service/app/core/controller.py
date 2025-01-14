import aio_pika
from core.service import AuthService
from infrastructure.broker.rabbit_broker import RabbitBroker
from infrastructure.config.enums import AuthServiceRoutes, BrokerQueues


class AuthController:
    def __init__(self, service: AuthService, rabbit_client: RabbitBroker):
        self.service = service
        self.broker = rabbit_client
        self.queue = None

    async def on_message(self, message: aio_pika.IncomingMessage):
        print(f"message_get {message.correlation_id}")
        async with message.process():
            route = message.correlation_id.split("__")[0]
            if route == AuthServiceRoutes.REGISTER.value:
                await self.service.register_user(message)
            elif route == AuthServiceRoutes.LOGIN.value:
                await self.service.login_user(message)
            elif route == AuthServiceRoutes.GET_CURRENT_USER.value:
                await self.service.get_current_user(message)
            elif route == AuthServiceRoutes.REFRESH.value:
                await self.service.logout_user(message)
            elif route == AuthServiceRoutes.REFRESH.value:
                await self.service.refresh_token(message)

    async def start(self):
        self.queue = await self.broker.declare_queue(BrokerQueues.AUTH)

    async def close(self):
        await self.broker.close(BrokerQueues.AUTH)

    async def consuming(self):
        while True:
            message = await self.get_message()
            await self.on_message(message)

    async def get_message(self):
        async with self.queue.iterator() as auth_queue:
            async for message in auth_queue:
                return message