from pydantic import BaseModel


class CreateUserModel(BaseModel):
    username: str
    email: str
    password: str


class UserModel(BaseModel):
    username: str
    email: str