# MVP Architecture (v3)

## Services

- `userbot`: Telethon listener that forwards Telegram messages to API.
- `backend/api`: FastAPI ingestion + admin auth + integration management endpoints.
- `backend/storage/repositories.py`: SQLAlchemy async repositories for admins/users/messages/integrations.
- `backend/db`: DB engine/session and ORM entities.
- `backend/services/feature_service.py`: stylometry and temporal feature extraction.
- `ml/feature_extractor/embedding_service.py`: text embeddings (SentenceTransformers + fallback).
- `backend/services/risk_service.py`: weighted risk scoring.

## Data flow

Telegram -> Userbot -> FastAPI `/messages` -> PostgreSQL -> feature extraction + embedding -> risk score.

## Analysis flow

API `/analysis/similarity` -> FeatureExtractor -> style/activity cosine -> RiskService score.

## Control plane flow

Admin -> `/auth/login` -> JWT -> `/integrations` CRUD-lite for bot/userbot connectors.
