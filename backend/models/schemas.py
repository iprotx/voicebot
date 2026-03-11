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


class AccountSample(BaseModel):
    texts: list[str] = Field(default_factory=list)
    timestamps: list[datetime] = Field(default_factory=list)


class SimilarityRequest(BaseModel):
    account_a: AccountSample
    account_b: AccountSample
    scam_pattern_score: float = Field(default=0.0, ge=0.0, le=1.0)


class SimilarityResponse(BaseModel):
    style_similarity: float
    activity_similarity: float
    risk_score: float
    risk_level: str
    is_related: bool


class RiskScoreCreateIn(BaseModel):
    user_id: int
    style_similarity: float = Field(ge=0.0, le=1.0)
    activity_overlap: float = Field(ge=0.0, le=1.0)
    scam_pattern_score: float = Field(ge=0.0, le=1.0)


class RiskScoreOut(BaseModel):
    id: int
    user_id: int
    style_similarity: float
    activity_overlap: float
    scam_pattern_score: float
    risk_score: float
    risk_level: str
    created_at: datetime


class AlertOut(BaseModel):
    id: int
    user_id: int
    risk_score_id: int
    channel: str
    status: str
    message: str
    created_at: datetime
