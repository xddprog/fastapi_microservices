from environs import Env
from pydantic import BaseModel


env = Env()
env.read_env()


class RabbitConfig(BaseModel):
    RABBIT_HOST: str
    RABBIT_PORT: int


def load_rabbit_config() -> RabbitConfig:
    return RabbitConfig(
        RABBIT_HOST=env.str("RABBIT_HOST"),
        RABBIT_PORT=env.int("RABBIT_PORT"),
    )


rabbit_config = load_rabbit_config()