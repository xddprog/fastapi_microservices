from pydantic import BaseModel


class CreateUserModel(BaseModel):
    username: str
    email: str
    password: str


class LoginUserModel(BaseModel):
    email: str
    password: str


class UserModel(BaseModel):
    id: int
    username: str
    email: str


class UpdateUserModel(BaseModel):
    username: str
    email: str
