from typing import Annotated
from fastapi import APIRouter, Depends, Response

from app.core.dependencies import get_auth_messages, get_current_user
from app.core.dto.user import CreateUserModel, LoginUserModel, UserModel
from app.core.services_messages.auth import AuthMessages


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/current_user")
async def get_current_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    return current_user


@router.post("/login")
async def login(
    form: LoginUserModel,
    auth_messages: Annotated[AuthMessages, Depends(get_auth_messages)],
    response: Response
) -> UserModel:
    user, access_token, refresh_token = await auth_messages.login_user(form)
    response.set_cookie("access_token", access_token, httponly=True)
    response.set_cookie("refresh_token", refresh_token, httponly=True)
    return user


@router.post("/register")
async def register(
    form: CreateUserModel,
    auth_messages: Annotated[AuthMessages, Depends(get_auth_messages)],
    response: Response
) -> UserModel:
    print("register route")
    user, access_token, refresh_token = await auth_messages.register_user(form)
    response.set_cookie("access_token", access_token, httponly=True)
    response.set_cookie("refresh_token", refresh_token, httponly=True)
    return user


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
