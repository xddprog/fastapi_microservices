from pydantic import BaseModel


class UserModel(BaseModel):
    id: int
    username: str
    email: str


class CreateUserModel(BaseModel):
    username: str
    email: str
    password: str


class UpdateUserModel(BaseModel):
    username: str
    email: str
    password: str
    