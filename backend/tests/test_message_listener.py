import asyncio
from datetime import datetime, timezone

from userbot.listeners.message_listener import MessageListener


class FakeAsyncClient:
    def __init__(self, timeout: int) -> None:
        self.timeout = timeout
        self.calls: list[tuple[str, dict]] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url: str, json: dict):
        self.calls.append((url, json))
        if url.endswith("/users"):
            return FakeResponse({"id": 42})
        return FakeResponse({"id": 7})


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self.payload


class FakeClient:
    def __init__(self) -> None:
        self.handler = None

    def on(self, _event):
        def decorator(func):
            self.handler = func
            return func

        return decorator


class FakeMessage:
    id = 123
    date = datetime.now(timezone.utc)
    reply_to = None


class FakeEvent:
    def __init__(self) -> None:
        self.message = FakeMessage()
        self.chat_id = 999
        self.raw_text = "hello"

    async def get_sender(self):
        class Sender:
            id = 777
            username = "alice"
            first_name = "Alice"

        return Sender()


def test_listener_resolves_internal_user_id_before_forwarding(monkeypatch) -> None:
    fake_http_client = FakeAsyncClient(timeout=5)

    monkeypatch.setattr(
        "userbot.listeners.message_listener.httpx.AsyncClient",
        lambda timeout: fake_http_client,
    )

    listener = MessageListener("http://api")
    client = FakeClient()
    listener.register(client)

    asyncio.run(client.handler(FakeEvent()))

    assert len(fake_http_client.calls) == 2
    assert fake_http_client.calls[0][0] == "http://api/users"
    assert fake_http_client.calls[1][0] == "http://api/messages"
    assert fake_http_client.calls[1][1]["user_id"] == 42
