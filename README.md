# Telegram Scam Multi-Account Detector

Production-oriented modular platform for collecting Telegram messages, extracting behavioral/stylometric signals, and scoring multi-account scam risk.

## MVP implemented

- FastAPI ingestion API (`backend`)
- SQLAlchemy async repositories (`users`, `messages`) with DB auto-init on startup
- PostgreSQL + Redis + Neo4j integration via Docker Compose
- Feature extraction service for stylometry + behavior vectors
- Embedding service wrapper (SentenceTransformers-ready with deterministic fallback)
- Risk scoring service
- Telethon userbot sender skeleton
- Unit + API integration tests

## Run locally

```bash
docker compose -f infra/compose/docker-compose.yml up --build
```

API docs: `http://localhost:8000/docs`
