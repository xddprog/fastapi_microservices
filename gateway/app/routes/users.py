from typing import Annotated
from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, get_user_messages
from app.core.dto.user import UpdateUserModel, UserModel
from app.core.services_messages.user import UserMessages


router = APIRouter(prefix="/users", tags=["users"])


@router.put("/")
async def update_user(
    form: UpdateUserModel,
    user_messages: Annotated[UserMessages, Depends(get_user_messages)],
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    return await user_messages.update_user(current_user.id, form)
