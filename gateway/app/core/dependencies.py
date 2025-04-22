import uuid
from fastapi import Depends, Request

from app.core.services_messages.auth import AuthMessages
from app.core.services_messages.task import TaskMessages
from app.core.services_messages.user import UserMessages
from app.infrastructure.brokers.rabbit_broker import RabbitBroker
from app.infrastructure.config.enums import BrokerQueues


async def get_broker(request: Request) -> RabbitBroker:
    return request.app.state.broker


async def get_auth_messages(broker: RabbitBroker = Depends(get_broker)) -> AuthMessages:
    return AuthMessages(
        broker,
        await broker.channel.get_queue(BrokerQueues.GATEWAY)
    )


async def get_current_user(
    request: Request,
    auth_messages: AuthMessages = Depends(get_auth_messages),
) -> dict:
    token = request.cookies.get('access_token')
    return await auth_messages.get_current_user(token)
    


async def get_user_messages(broker: RabbitBroker = Depends(get_broker)) -> UserMessages:
    return UserMessages(
        broker,
        await broker.channel.get_queue(BrokerQueues.GATEWAY)
    )


async def get_tasks_messages(broker: RabbitBroker = Depends(get_broker)) -> TaskMessages:
    return TaskMessages(
        broker,
        await broker.channel.get_queue(BrokerQueues.GATEWAY)
    )
