from datetime import datetime, timezone

from backend.models.schemas import MessageIn, MessageOut, UserIn, UserOut


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._users: dict[int, UserOut] = {}
        self._counter = 1

    def upsert(self, payload: UserIn) -> UserOut:
        now = datetime.now(timezone.utc)
        existing = next((u for u in self._users.values() if u.telegram_id == payload.telegram_id), None)
        if existing:
            updated = UserOut(
                **payload.model_dump(),
                id=existing.id,
                first_seen=existing.first_seen,
                last_seen=now,
            )
            self._users[existing.id] = updated
            return updated

        created = UserOut(**payload.model_dump(), id=self._counter, first_seen=now, last_seen=now)
        self._users[self._counter] = created
        self._counter += 1
        return created

    def get(self, user_id: int) -> UserOut | None:
        return self._users.get(user_id)


class InMemoryMessageRepository:
    def __init__(self) -> None:
        self._messages: dict[int, MessageOut] = {}
        self._counter = 1

    def create(self, payload: MessageIn) -> MessageOut:
        created = MessageOut(id=self._counter, **payload.model_dump())
        self._messages[self._counter] = created
        self._counter += 1
        return created

    def batch_create(self, payloads: list[MessageIn]) -> list[MessageOut]:
        return [self.create(payload) for payload in payloads]

    def get(self, message_id: int) -> MessageOut | None:
        return self._messages.get(message_id)
