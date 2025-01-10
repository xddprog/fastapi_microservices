from fastapi import APIRouter


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/")
async def get_all_tasks():
    return {"message": "Tasks"}


@router.get("/{task_id}")
async def get_task(task_id: int):
    return {"message": f"Task {task_id}"}


@router.post("/")
async def create_task():
    return {"message": "Task created"}


@router.put("/{task_id}")
async def update_task(task_id: int):
    return {"message": f"Task {task_id} updated"}


@router.delete("/{task_id}")
async def delete_task(task_id: int):
    return {"message": f"Task {task_id} deleted"}