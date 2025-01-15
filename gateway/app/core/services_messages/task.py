import json
import uuid
from aio_pika.abc import AbstractQueue
from fastapi import HTTPException
from gateway.app.core.services_messages.base import BaseMessages
from gateway.app.infrastructure.brokers.rabbit_broker import RabbitBroker
from gateway.app.infrastructure.config.enums import BrokerQueues, TaskServiceRoutes
from gateway.app.core.dto.task import CreateTaskModel, TaskModel, UpdateTaskModel


class TaskMessages(BaseMessages):    
    async def get_user_tasks(self, user_id: int) -> list[TaskModel]:
        correlation_id = str(uuid.uuid4())
        await self.broker.send_message(
            queue_name=BrokerQueues.TASKS,
            message=json.dumps({"user_id": user_id}),
            correlation_id=f"{TaskServiceRoutes.GET_USER_TASKS.value}__{correlation_id}"
        )

        data = await self._consume_message(correlation_id)
        return [TaskModel.model_validate(task) for task in data["tasks"]]
    
    async def get_task(self, task_id: int) -> TaskModel:
        correlation_id = str(uuid.uuid4())
        await self.broker.send_message(
            queue_name=BrokerQueues.TASKS,
            message=json.dumps({"task_id": task_id}),
            correlation_id=f"{TaskServiceRoutes.GET.value}__{correlation_id}"
        )

        task = await self._consume_message(correlation_id)
        return TaskModel.model_validate(task)
    
    async def create_task(self, task_dto: CreateTaskModel, user_id: int):
        correlation_id = str(uuid.uuid4())
        task_dto = task_dto.model_dump()
        task_dto.update({"user_id": user_id})

        await self.broker.send_message(
            queue_name=BrokerQueues.TASKS,
            message=json.dumps(task_dto),
            correlation_id=f"{TaskServiceRoutes.CREATE.value}__{correlation_id}"
        )

        task = await self._consume_message(correlation_id)
        return TaskModel.model_validate(task)

    async def update_task(self, task_id: int, task_dto: UpdateTaskModel):
        correlation_id = str(uuid.uuid4())
        task_dto = task_dto.model_dump()
        task_dto.update({"task_id": task_id})
        await self.broker.send_message(
            queue_name=BrokerQueues.TASKS,
            message=json.dumps(task_dto),
            correlation_id=f"{TaskServiceRoutes.UPDATE.value}__{correlation_id}"
        )

        task = await self._consume_message(correlation_id)
        return TaskModel.model_validate(task)

    async def delete_task(self, task_id: int):
        correlation_id = str(uuid.uuid4())
        await self.broker.send_message(
            queue_name=BrokerQueues.TASKS,
            message=json.dumps({"task_id": task_id}),
            correlation_id=f"{TaskServiceRoutes.DELETE.value}__{correlation_id}"
        )

        task = await self._consume_message(correlation_id)
        return task