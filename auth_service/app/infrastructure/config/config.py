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


class JwtConfig(BaseModel):
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_TIME: int
    JWT_REFRESH_TOKEN_TIME: int


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


def load_jwt_config() -> JwtConfig:
    return JwtConfig(
        JWT_SECRET=env.str("JWT_SECRET"),
        JWT_ALGORITHM=env.str("JWT_ALGORITHM"),
        JWT_ACCESS_TOKEN_TIME=env.int("JWT_ACCESS_TOKEN_TIME"),
        JWT_REFRESH_TOKEN_TIME=env.int("JWT_REFRESH_TOKEN_TIME")
    )


def load_rabbit_config() -> RabbitConfig:
    return RabbitConfig(
        RABBIT_HOST=env.str("RABBIT_HOST"),
        RABBIT_PORT=env.int("RABBIT_PORT")
    )


rabbit_config = load_rabbit_config()
jwt_config = load_jwt_config()
database_config = load_database_config()