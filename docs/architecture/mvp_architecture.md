# MVP Architecture

## Services

- `userbot`: Telethon listener that forwards Telegram messages to API.
- `backend/api`: FastAPI ingestion endpoints for users and messages.
- `backend/services/feature_service.py`: stylometry and temporal feature extraction.
- `ml/feature_extractor/embedding_service.py`: text embeddings (SentenceTransformers + fallback).
- `backend/services/risk_service.py`: weighted risk scoring.

## Data flow

Telegram -> Userbot -> FastAPI `/messages` -> feature extraction + embedding -> risk score.
