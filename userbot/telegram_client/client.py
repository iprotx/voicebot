from telethon import TelegramClient


class UserbotClientFactory:
    def __init__(self, api_id: int, api_hash: str, session_name: str = "collector") -> None:
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name

    def build(self) -> TelegramClient:
        return TelegramClient(self.session_name, self.api_id, self.api_hash)
