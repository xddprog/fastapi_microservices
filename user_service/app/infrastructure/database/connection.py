from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from infrastructure.config.config import database_config
from infrastructure.database.models import Base


class DatabaseConnection:
    def __init__(self):
        self._engine = create_async_engine(
            url=database_config.get_url(),
            poolclass=NullPool
        )

    async def get_session(self) -> AsyncSession:
        return AsyncSession(bind=self._engine)

    async def __call__(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return self