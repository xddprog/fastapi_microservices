from fastapi import APIRouter, Depends
from gateway.app.core.dependencies import get_current_user
from gateway.app.routes.auth import router as auth_router
from gateway.app.routes.tasks import router as tasks_router
from gateway.app.routes.users import router as users_router


router = APIRouter(prefix="/api")
PROTECTED = Depends(get_current_user)


router.include_router(auth_router)
router.include_router(tasks_router, dependencies=[PROTECTED])
router.include_router(users_router, dependencies=[PROTECTED])