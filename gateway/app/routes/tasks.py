from typing import Annotated
from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, get_tasks_messages
from app.core.dto.task import CreateTaskModel, TaskModel, UpdateTaskModel
from app.core.dto.user import UserModel
from app.core.services_messages.task import TaskMessages


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/")
async def get_user_tasks(
    tasks_messages: Annotated[TaskMessages, Depends(get_tasks_messages)],
    current_user: UserModel = Depends(get_current_user)
) -> list[TaskModel]:
    return await tasks_messages.get_user_tasks(current_user.id)


@router.get("/{task_id}")
async def get_task(
    task_id: int,
    tasks_messages: Annotated[TaskMessages, Depends(get_tasks_messages)],
) -> TaskModel:
    return await tasks_messages.get_task(task_id)


@router.post("/")
async def create_task(
    form: CreateTaskModel,
    tasks_messages: Annotated[TaskMessages, Depends(get_tasks_messages)],
    current_user: UserModel = Depends(get_current_user)
) -> TaskModel:
    return await tasks_messages.create_task(form, current_user.id)


@router.put("/{task_id}")
async def update_task(
    task_id: int,
    form: UpdateTaskModel,
    tasks_messages: Annotated[TaskMessages, Depends(get_tasks_messages)]
) -> TaskModel:
    return await tasks_messages.update_task(task_id, form)


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    tasks_messages: Annotated[TaskMessages, Depends(get_tasks_messages)]
) -> None:
    return await tasks_messages.delete_task(task_id)