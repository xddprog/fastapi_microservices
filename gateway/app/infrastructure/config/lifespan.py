from fastapi import FastAPI

from gateway.app.infrastructure.brokers.rabbit_broker import RabbitBroker
from gateway.app.infrastructure.config.enums import BrokerQueues


async def lifespan(app: FastAPI):
    broker = await RabbitBroker()()
    await broker.declare_queue(BrokerQueues.GATEWAY)
    app.state.broker = broker
    yield
    await broker.close()