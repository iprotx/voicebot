from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.routes import health, messages, users
from backend.db.database import engine
from backend.db.models import Base


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Telegram Scam Detector API", version="0.2.0", lifespan=lifespan)
    app.include_router(health.router)
    app.include_router(users.router, prefix="/users", tags=["users"])
    app.include_router(messages.router, prefix="/messages", tags=["messages"])
    return app


app = create_app()
