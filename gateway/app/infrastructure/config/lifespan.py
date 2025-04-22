from fastapi import FastAPI

from app.infrastructure.brokers.rabbit_broker import RabbitBroker
from app.infrastructure.config.enums import BrokerQueues


async def lifespan(app: FastAPI):
    broker = await RabbitBroker()()
    await broker.declare_queue(BrokerQueues.GATEWAY)
    app.state.broker = broker
    yield
    try:
        await broker.close(BrokerQueues.GATEWAY)
    finally:
        await broker.close(BrokerQueues.GATEWAY)