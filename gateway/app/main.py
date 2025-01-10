from fastapi import FastAPI

from gateway.app.routes import router
from gateway.app.infrastructure.config.lifespan import lifespan


app = FastAPI(lifespan=lifespan)


app.include_router(router)