from asyncio import Task
from typing import Any, Self

from sqlalchemy import Result, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import MappedColumn


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_item(self, item_id: int | str) -> Task | None:
        item = await self.session.get(Task, item_id)
        return item

    async def get_all_items(self) -> list[Self]:
        query = select(Task)
        items: Result = await self.session.execute(query)
        return items.scalars().all()

    async def get_by_attribute(
        self, attribute: MappedColumn[Any], value: str  | int
    ) -> list[Task] | None:
        query = select(Task).where(attribute == value)
        items: Result = await self.session.execute(query)
        return items.scalars().all()

    async def add_item(self, **kwargs: int | str) -> Task:
        item = Task(**kwargs)

        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def delete_item(self, item: Task) -> None:
        await self.session.delete(item)
        await self.session.commit()

    async def update_item(self, item_id: int | str, **update_values) -> Task:
        query = (
            update(Task)
            .where(Task.id == item_id)
            .values(update_values)
            .returning(Task)
        )

        item: Result = (await self.session.execute(query)).scalars().all()[0]
        await self.session.commit()
        await self.session.refresh(item)
        return item
