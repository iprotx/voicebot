# Telegram Scam Multi-Account Detector

Production-oriented modular platform for collecting Telegram messages, extracting behavioral/stylometric signals, and scoring multi-account scam risk.

## MVP implemented

- FastAPI ingestion API (`backend`)
- PostgreSQL + Redis integration via Docker Compose
- Feature extraction service for stylometry + behavior vectors
- Embedding service wrapper (SentenceTransformers-ready with deterministic fallback)
- Risk scoring service
- Telethon userbot sender skeleton
- Tests for extraction/risk/api health

## Run locally

```bash
docker compose -f infra/compose/docker-compose.yml up --build
```

API: `http://localhost:8000/docs`
