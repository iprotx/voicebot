from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class VoiceProfile:
    id: str
    name: str
    language: str
    description: str | None = None
    sample_count: int | None = None


class VoiceboxClient:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url
        self._client = httpx.AsyncClient(base_url=base_url, timeout=60)

    async def close(self) -> None:
        await self._client.aclose()

    async def list_profiles(self) -> list[VoiceProfile]:
        data = await self._request_json("GET", "/profiles")
        profiles = data.get("profiles", data if isinstance(data, list) else [])
        result: list[VoiceProfile] = []
        for profile in profiles:
            result.append(
                VoiceProfile(
                    id=profile["id"],
                    name=profile.get("name", profile["id"]),
                    language=profile.get("language", "unknown"),
                    description=profile.get("description"),
                    sample_count=profile.get("sample_count"),
                )
            )
        return result

    async def create_profile(self, name: str, language: str, description: str = "") -> VoiceProfile:
        data = await self._request_json(
            "POST",
            "/profiles",
            json={"name": name, "language": language, "description": description},
        )
        return VoiceProfile(
            id=data["id"],
            name=data.get("name", name),
            language=data.get("language", language),
            description=data.get("description", description),
            sample_count=data.get("sample_count"),
        )

    async def delete_profile(self, profile_id: str) -> None:
        await self._request_json("DELETE", f"/profiles/{profile_id}")

    async def add_sample(self, profile_id: str, filename: str, content: bytes) -> dict[str, Any]:
        files = {"audio": (filename, content, "audio/ogg")}
        return await self._request_json("POST", f"/profiles/{profile_id}/samples", files=files)

    async def generate(self, text: str, profile_id: str, language: str) -> dict[str, Any]:
        return await self._request_json(
            "POST",
            "/generate",
            json={"text": text, "profile_id": profile_id, "language": language},
        )

    async def download_audio(self, audio_url: str) -> bytes:
        url = audio_url if audio_url.startswith("http") else f"{self._base_url}{audio_url}"
        response = await self._client.get(url)
        response.raise_for_status()
        return response.content

    async def _request_json(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        response = await self._client.request(method, url, **kwargs)
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict):
            return payload
        return {"profiles": payload}
