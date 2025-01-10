from typing import Annotated
from fastapi import APIRouter, Depends

from gateway.app.core.dependencies import get_auth_messages
from gateway.app.core.dto import CreateUserModel, UserModel
from gateway.app.core.services_messages.auth import AuthMessages


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login():
    return {"message": "Login"}


@router.post("/register")
async def register(
    form: CreateUserModel,
    auth_messages: Annotated[AuthMessages, Depends(get_auth_messages)]
) -> UserModel:
    return await auth_messages.register_user(form)