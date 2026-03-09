from __future__ import annotations

import httpx
from telethon import events


class MessageListener:
    def __init__(self, api_url: str) -> None:
        self.api_url = api_url.rstrip("/")

    def register(self, client) -> None:
        @client.on(events.NewMessage)
        async def handler(event):
            sender = await event.get_sender()
            payload = {
                "message_id": event.message.id,
                "user_id": getattr(sender, "id", 0),
                "chat_id": event.chat_id,
                "timestamp": event.message.date.isoformat(),
                "text": event.raw_text or "",
                "reply_to": getattr(event.message.reply_to, "reply_to_msg_id", None),
                "username": getattr(sender, "username", None),
                "display_name": getattr(sender, "first_name", None),
            }
            async with httpx.AsyncClient(timeout=5) as cli:
                await cli.post(f"{self.api_url}/messages", json=payload)
