from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    voicebox_base_url: str = "http://localhost:17493"
    default_language: str = "ru"



def load_settings() -> Settings:
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")

    return Settings(
        telegram_token=token,
        voicebox_base_url=os.getenv("VOICEBOX_BASE_URL", "http://localhost:17493").rstrip("/"),
        default_language=os.getenv("VOICEBOX_DEFAULT_LANGUAGE", "ru").strip() or "ru",
    )
