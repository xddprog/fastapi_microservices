from pydantic import BaseModel


class TaskModel(BaseModel):
    id: int
    title: str
    description: str


class CreateTaskModel(BaseModel):
    title: str
    description: str
    user_id: int


class UpdateTaskModel(BaseModel):
    title: str
    description: str
    