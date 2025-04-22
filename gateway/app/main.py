from fastapi import FastAPI

from app.routes import router
from app.infrastructure.config.lifespan import lifespan


app = FastAPI(lifespan=lifespan)


app.include_router(router)