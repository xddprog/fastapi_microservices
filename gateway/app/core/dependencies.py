import uuid
from fastapi import Depends, Request

from gateway.app.core.services_messages.auth import AuthMessages
from gateway.app.core.services_messages.task import TaskMessages
from gateway.app.core.services_messages.user import UserMessages
from gateway.app.infrastructure.brokers.rabbit_broker import RabbitBroker
from gateway.app.infrastructure.config.enums import BrokerQueues


async def get_broker(request: Request) -> RabbitBroker:
    return request.app.state.broker


async def get_current_user(broker: RabbitBroker = Depends(get_broker)) -> dict:
    correlation_id = str(uuid.uuid4())
    user = await broker.send_message(
        BrokerQueues.AUTH, 
        correlation_id
    )
    if not user:
        raise


async def get_auth_messages(broker: RabbitBroker = Depends(get_broker)) -> AuthMessages:
    return AuthMessages(
        broker,
        await broker.channel.get_queue(BrokerQueues.GATEWAY)
    )


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
