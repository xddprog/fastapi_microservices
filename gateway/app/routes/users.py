from fastapi import APIRouter


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
async def get_all_users():
    return {"message": "Users"}


@router.get("/{user_id}")
async def get_user(user_id: int):
    return {"message": f"User {user_id}"}


@router.post("/")
async def create_user():
    return {"message": "User created"}


@router.put("/{user_id}")
async def update_user(user_id: int):
    return {"message": f"User {user_id} updated"}


@router.delete("/{user_id}")
async def delete_user(user_id: int):
    return {"message": f"User {user_id} deleted"}