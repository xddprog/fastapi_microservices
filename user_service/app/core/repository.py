from asyncio import Task
from typing import Any, Self

from sqlalchemy import Result, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import MappedColumn

from infrastructure.database.connection import DatabaseConnection
from infrastructure.database.models import User

from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository:
    model = User
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_item(self, item_id: int | str) -> User | None:
        item = await self.session.get(User, item_id)
        return item

    async def get_all_items(self) -> list[User]:
        query = select(User)
        items: Result = await self.session.execute(query)
        return items.scalars().all()

    async def get_by_attribute(
        self, attribute: MappedColumn[Any], value: str  | int
    ) -> list[User] | None:
        query = select(User).where(attribute == value)
        items: Result = await self.session.execute(query)
        return items.scalars().all()

    async def add_item(self, **kwargs: int | str) -> Task:
        item = User(**kwargs)
        
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def delete_item(self, item: User) -> None:
        await self.session.delete(item)
        await self.session.commit()

    async def update_item(self, item_id: int | str, **update_values) -> User:
        query = (
            update(User)
            .where(User.id == item_id)
            .values(update_values)
            .returning(User)
        )   
        item: Result = (await self.session.execute(query)).scalars().all()[0]
        await self.session.commit()
        await self.session.refresh(item)
        return item
