from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import AdminUser, Alert, Integration, Message, RiskScore, User
from backend.models.schemas import AlertOut, IntegrationIn, IntegrationOut, MessageIn, MessageOut, RiskScoreCreateIn, RiskScoreOut, UserIn, UserOut


class AdminRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, email: str, password_hash: str) -> int:
        admin = AdminUser(
            email=email,
            password_hash=password_hash,
            created_at=datetime.now(timezone.utc),
            is_active=True,
        )
        self.session.add(admin)
        await self.session.commit()
        await self.session.refresh(admin)
        return admin.id

    async def get_by_email(self, email: str) -> AdminUser | None:
        result = await self.session.execute(select(AdminUser).where(AdminUser.email == email))
        return result.scalar_one_or_none()


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(self, payload: UserIn) -> UserOut:
        now = datetime.now(timezone.utc)
        result = await self.session.execute(select(User).where(User.telegram_id == payload.telegram_id))
        existing = result.scalar_one_or_none()

        if existing:
            existing.username = payload.username
            existing.display_name = payload.display_name
            existing.language = payload.language
            existing.last_seen = now
            await self.session.commit()
            await self.session.refresh(existing)
            return self._to_schema(existing)

        user = User(
            telegram_id=payload.telegram_id,
            username=payload.username,
            display_name=payload.display_name,
            language=payload.language,
            first_seen=now,
            last_seen=now,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return self._to_schema(user)

    async def get(self, user_id: int) -> UserOut | None:
        user = await self.session.get(User, user_id)
        return self._to_schema(user) if user else None

    @staticmethod
    def _to_schema(user: User) -> UserOut:
        return UserOut(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            display_name=user.display_name,
            language=user.language,
            first_seen=user.first_seen,
            last_seen=user.last_seen,
        )


class MessageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, payload: MessageIn) -> MessageOut:
        message = Message(**payload.model_dump())
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return self._to_schema(message)

    async def batch_create(self, payloads: list[MessageIn]) -> list[MessageOut]:
        items = [Message(**payload.model_dump()) for payload in payloads]
        self.session.add_all(items)
        await self.session.commit()
        for item in items:
            await self.session.refresh(item)
        return [self._to_schema(item) for item in items]

    async def get(self, message_id: int) -> MessageOut | None:
        message = await self.session.get(Message, message_id)
        return self._to_schema(message) if message else None

    @staticmethod
    def _to_schema(message: Message) -> MessageOut:
        return MessageOut(
            id=message.id,
            message_id=message.message_id,
            user_id=message.user_id,
            chat_id=message.chat_id,
            timestamp=message.timestamp,
            text=message.text,
            reply_to=message.reply_to,
            username=message.username,
            display_name=message.display_name,
        )


class IntegrationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, payload: IntegrationIn) -> IntegrationOut:
        obj = Integration(
            **payload.model_dump(),
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return self._to_schema(obj)

    async def list_all(self) -> list[IntegrationOut]:
        result = await self.session.execute(select(Integration).order_by(Integration.id.desc()))
        return [self._to_schema(row) for row in result.scalars().all()]

    async def set_active(self, integration_id: int, is_active: bool) -> IntegrationOut | None:
        obj = await self.session.get(Integration, integration_id)
        if not obj:
            return None
        obj.is_active = is_active
        await self.session.commit()
        await self.session.refresh(obj)
        return self._to_schema(obj)

    @staticmethod
    def _to_schema(obj: Integration) -> IntegrationOut:
        return IntegrationOut(
            id=obj.id,
            name=obj.name,
            kind=obj.kind,
            api_id=obj.api_id,
            api_hash=obj.api_hash,
            bot_token=obj.bot_token,
            session_name=obj.session_name,
            is_active=obj.is_active,
            created_at=obj.created_at,
        )



class RiskScoreRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, payload: RiskScoreCreateIn, computed_score: float, computed_level: str) -> RiskScoreOut:
        obj = RiskScore(
            user_id=payload.user_id,
            style_similarity=payload.style_similarity,
            activity_overlap=payload.activity_overlap,
            scam_pattern_score=payload.scam_pattern_score,
            risk_score=computed_score,
            risk_level=computed_level,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return self._to_schema(obj)

    async def list_by_user(self, user_id: int) -> list[RiskScoreOut]:
        result = await self.session.execute(
            select(RiskScore).where(RiskScore.user_id == user_id).order_by(RiskScore.id.desc())
        )
        return [self._to_schema(row) for row in result.scalars().all()]

    @staticmethod
    def _to_schema(obj: RiskScore) -> RiskScoreOut:
        return RiskScoreOut(
            id=obj.id,
            user_id=obj.user_id,
            style_similarity=obj.style_similarity,
            activity_overlap=obj.activity_overlap,
            scam_pattern_score=obj.scam_pattern_score,
            risk_score=obj.risk_score,
            risk_level=obj.risk_level,
            created_at=obj.created_at,
        )


class AlertRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_for_risk(self, risk: RiskScoreOut, channels: list[str]) -> list[AlertOut]:
        rows = [
            Alert(
                user_id=risk.user_id,
                risk_score_id=risk.id,
                channel=channel,
                status="new",
                message=f"High risk detected: {risk.risk_score}",
                created_at=datetime.now(timezone.utc),
            )
            for channel in channels
        ]
        self.session.add_all(rows)
        await self.session.commit()
        for row in rows:
            await self.session.refresh(row)
        return [self._to_schema(row) for row in rows]

    async def list_by_user(self, user_id: int) -> list[AlertOut]:
        result = await self.session.execute(select(Alert).where(Alert.user_id == user_id).order_by(Alert.id.desc()))
        return [self._to_schema(row) for row in result.scalars().all()]

    @staticmethod
    def _to_schema(obj: Alert) -> AlertOut:
        return AlertOut(
            id=obj.id,
            user_id=obj.user_id,
            risk_score_id=obj.risk_score_id,
            channel=obj.channel,
            status=obj.status,
            message=obj.message,
            created_at=obj.created_at,
        )
