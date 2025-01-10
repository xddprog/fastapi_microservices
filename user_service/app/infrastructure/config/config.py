from environs import Env
from pydantic import BaseModel


env = Env()
env.read_env()


class DatabaseConfig(BaseModel):
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str

    def get_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class RabbitConfig(BaseModel):
    RABBIT_HOST: str
    RABBIT_PORT: int


def load_database_config() -> DatabaseConfig:
    return DatabaseConfig(
        DB_NAME=env.str("DB_NAME"),
        DB_USER=env.str("DB_USER"),
        DB_PASS=env.str("DB_PASS"),
        DB_HOST=env.str("DB_HOST"),
        DB_PORT=env.str("DB_PORT"),
    )


def load_rabbit_config() -> RabbitConfig:
    return RabbitConfig(
        RABBIT_HOST=env.str("RABBIT_HOST"),
        RABBIT_PORT=env.int("RABBIT_PORT")
    )


rabbit_config = load_rabbit_config()
database_config = load_database_config()