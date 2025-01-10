from pydantic.v1 import BaseSettings


class Config(BaseSettings):
    class Config:
        env_file = ".env"


class DatabaseConfig(Config):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    
class RabbitConfig(Config):
    RABBIT_HOST: str
    RABBIT_PORT: int
    

database_config = DatabaseConfig()
rabbit_config = RabbitConfig()