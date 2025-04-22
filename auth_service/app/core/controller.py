import asyncio
import aio_pika
from core.service import AuthService
from infrastructure.broker.rabbit_broker import RabbitBroker
from infrastructure.config.enums import AuthServiceRoutes, BrokerQueues


class AuthController:
    def __init__(self, service: AuthService, rabbit_client: RabbitBroker):
        self.service = service
        self.broker = rabbit_client
        self.queue = None

    async def get_handler(self, route: str):
        handlers = {
            AuthServiceRoutes.REGISTER.value: self.service.register_user,
            AuthServiceRoutes.LOGIN.value: self.service.login_user,
            AuthServiceRoutes.GET_CURRENT_USER.value: self.service.get_current_user,
            AuthServiceRoutes.REFRESH.value: self.service.refresh_token,
            AuthServiceRoutes.LOGOUT.value: self.service.logout_user
        }
        return handlers.get(route)

    async def on_message(self, message: aio_pika.IncomingMessage):
        try:
            print("handle message")
            async with message.process():
                print("process message")
                route = message.correlation_id.split("__")[0]
                handler = await self.get_handler(route)
                if handler:
                    await handler(message)
        except Exception as e:
            print(e)
            

    async def start(self):
        self.queue = await self.broker.declare_queue(BrokerQueues.AUTH)

    async def close(self):
        await self.broker.close(BrokerQueues.AUTH)

    async def consuming(self):
        print("start consuming")
        async with self.queue.iterator() as auth_queue:
            async for message in auth_queue:
                print("getting message", message.correlation_id)
                asyncio.create_task(self.on_message(message))