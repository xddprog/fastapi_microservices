import json

import aio_pika
from aio_pika.abc import AbstractQueue
from core.dto import CreateTaskModel, TaskModel, UpdateTaskModel
from core.repository import TaskRepository
from infrastructure.config.enums import BrokerQueues
from infrastructure.broker.rabbit_broker import RabbitBroker
from core.errors import TaskNotFoundError


class TaskService:
    def __init__(
        self, 
        repository: TaskRepository, 
        rabbit_client: RabbitBroker,
        queue: AbstractQueue
    ):
        self.repository = repository
        self.broker = rabbit_client
        self.queue = queue

    async def create_task(self, message: aio_pika.IncomingMessage):
        task_data = json.loads(json.loads(message.body.decode("utf-8")))

        new_task = await self.repository.add_item(**task_data)
        new_task = TaskModel.model_validate(new_task, from_attributes=True)
        await self.broker.send_message(
            queue_name=BrokerQueues.GATEWAY,
            message=json.dumps(new_task.model_dump()),
            correlation_id=message.correlation_id,
        )

    async def update_task(self, message: aio_pika.IncomingMessage):
        task_data = json.loads(json.loads(message.body.decode("utf-8")))
        task_id = task_data.pop("task_id")
        updated_task = await self.repository.update_item(task_id, **task_data)
        if not updated_task:
            return await self.broker.send_message(
                queue_name=BrokerQueues.GATEWAY,
                message=json.dumps(TaskNotFoundError),
                correlation_id=message.correlation_id,
            )
        updated_task = TaskModel.model_validate(updated_task, from_attributes=True)

        await self.broker.send_message(
            queue_name=BrokerQueues.GATEWAY,
            message=json.dumps(updated_task.model_dump()),
            correlation_id=message.correlation_id,
        )

    async def delete_task(self, message: aio_pika.IncomingMessage):
        task_data = json.loads(json.loads(message.body.decode("utf-8")))
        task = await self.repository.get_item(task_data.get("task_id"))
        if not task:
            return await self.broker.send_message(
                queue_name=BrokerQueues.GATEWAY,
                message=json.dumps(TaskNotFoundError),
                correlation_id=message.correlation_id,
            )
        
        await self.repository.delete_item(task)
        await self.broker.send_message(
            queue_name=BrokerQueues.GATEWAY,
            message=json.dumps({"detail": f"Task {task_data.get("task_id")} deleted"}),
            correlation_id=message.correlation_id,
        )

    async def get_task(self, message: aio_pika.IncomingMessage):
        task_data = json.loads(json.loads(message.body.decode("utf-8")))
        task = await self.repository.get_item(task_data.get("task_id"))
        if not task:
            return await self.broker.send_message(
                queue_name=BrokerQueues.GATEWAY,
                message=json.dumps(TaskNotFoundError),
                correlation_id=message.correlation_id,
            )
        task = TaskModel.model_validate(task, from_attributes=True)

        await self.broker.send_message(
            queue_name=BrokerQueues.GATEWAY,
            message=json.dumps(task.model_dump()),
            correlation_id=message.correlation_id,
        )

    async def get_user_tasks(self, message: aio_pika.IncomingMessage):
        user_data = json.loads(json.loads(message.body.decode("utf-8")))
        tasks = await self.repository.get_user_tasks(user_data.get("user_id"))
        tasks = [
            TaskModel
            .model_validate(task, from_attributes=True)
            .model_dump()
            for task in tasks
        ]

        await self.broker.send_message(
            queue_name=BrokerQueues.GATEWAY,
            message=json.dumps({"tasks": tasks}),
            correlation_id=message.correlation_id,
        )