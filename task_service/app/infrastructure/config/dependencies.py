from typing import AsyncGenerator
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from task_service.app.infrastructure.cache.redis_cache import RedisCache



async def get_session(request: Request,) -> AsyncGenerator[AsyncSession, None]:
    session = await request.app.state.db_connection.get_session()
    try:
        yield session
    finally:
        await session.close()


async def get_redis(request: Request) -> RedisCache:
    return request.app.state.redis_cache