from fastapi import FastAPI

from backend.api.routes import health, messages, users


def create_app() -> FastAPI:
    app = FastAPI(title="Telegram Scam Detector API", version="0.1.0")
    app.include_router(health.router)
    app.include_router(users.router, prefix="/users", tags=["users"])
    app.include_router(messages.router, prefix="/messages", tags=["messages"])
    return app


app = create_app()
