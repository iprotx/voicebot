from datetime import datetime

from pydantic import BaseModel, Field


class UserIn(BaseModel):
    telegram_id: int
    username: str | None = None
    display_name: str | None = None
    language: str | None = None


class UserOut(UserIn):
    id: int
    first_seen: datetime
    last_seen: datetime


class MessageIn(BaseModel):
    message_id: int
    user_id: int
    chat_id: int
    timestamp: datetime
    text: str = Field(default="", max_length=8192)
    reply_to: int | None = None
    username: str | None = None
    display_name: str | None = None


class MessageBatchIn(BaseModel):
    messages: list[MessageIn]


class MessageOut(MessageIn):
    id: int
