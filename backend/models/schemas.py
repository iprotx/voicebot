from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


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


class AdminRegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class AdminLoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class IntegrationIn(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    kind: Literal["bot", "userbot"]
    api_id: str | None = None
    api_hash: str | None = None
    bot_token: str | None = None
    session_name: str | None = None


class IntegrationOut(IntegrationIn):
    id: int
    is_active: bool
    created_at: datetime
