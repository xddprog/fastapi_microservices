
from task_service.app.core.dto import CreateTaskModel, TaskModel, UpdateTaskModel
from task_service.app.core.repository import TaskRepository


class TaskService:

    async def __init__(self, repository: TaskRepository, channel):
        self.repository = repository
        self.channel = channel

    async def create_task(self, task_dto: CreateTaskModel):
        new_task = await self.repository.add_item(task_dto)
        return TaskModel.model_validate(new_task, from_attributes=True)

    async def update_task(self, task_dto: UpdateTaskModel):
        updated_task = await self.repository.update_item(task_dto)
        return TaskModel.model_validate(updated_task, from_attributes=True)

    async def delete_task(self, task_id: int):
        task = await self.repository.get_item(task_id)
        await self.repository.delete_item(task)

    async def get_task(self, task_id: int):
        task = await self.repository.get_item(task_id)
        return TaskModel.model_validate(task, from_attributes=True)

    async def get_all_tasks(self):
        tasks = await self.repository.get_all_items()
        return [TaskModel.model_validate(task, from_attributes=True) for task in tasks]