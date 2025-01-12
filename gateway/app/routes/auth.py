from typing import Annotated
from fastapi import APIRouter, Depends, Response

from gateway.app.core.dependencies import get_auth_messages
from gateway.app.core.dto.user import CreateUserModel, UserModel
from gateway.app.core.services_messages.auth import AuthMessages


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login():
    return {"message": "Login"}


@router.post("/register")
async def register(
    form: CreateUserModel,
    auth_messages: Annotated[AuthMessages, Depends(get_auth_messages)],
    response: Response
) -> UserModel:
    data = await auth_messages.register_user(form)
    response.set_cookie(data["access_token"], "access_token")
    response.set_cookie(data["refresh_token"], "refresh_token")
    return UserModel(**data["user"])