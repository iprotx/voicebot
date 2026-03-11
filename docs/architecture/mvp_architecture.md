# MVP Architecture (v2)

## Services

- `userbot`: Telethon listener that forwards Telegram messages to API.
- `backend/api`: FastAPI ingestion endpoints for users and messages.
- `backend/storage/repositories.py`: SQLAlchemy async repositories for users/messages.
- `backend/db`: DB engine/session and ORM entities.
- `backend/services/feature_service.py`: stylometry and temporal feature extraction.
- `ml/feature_extractor/embedding_service.py`: text embeddings (SentenceTransformers + fallback).
- `backend/services/risk_service.py`: weighted risk scoring.

## Data flow

Telegram -> Userbot -> FastAPI `/messages` -> PostgreSQL (async SQLAlchemy) -> feature extraction + embedding -> risk score.
