# Telegram Scam Multi-Account Detector

Production-oriented modular platform for collecting Telegram messages, extracting behavioral/stylometric signals, and scoring multi-account scam risk.

## Current SaaS increment

- FastAPI ingestion API (`backend`)
- Admin authentication (`/auth/register`, `/auth/login`) with JWT
- Protected integrations management for `bot` and `userbot` connectors (`/integrations`)
- SQLAlchemy async repositories with DB auto-init on startup
- PostgreSQL + Redis + Neo4j integration via Docker Compose
- Feature extraction + embedding wrapper + risk scoring services
- Analysis endpoint `/analysis/similarity` for account similarity + risk evaluation
- Risk scoring persistence + auto alerts (dashboard/telegram/email) for high-risk users
- Telethon userbot sender skeleton
- Unit + API integration tests

## Run locally

```bash
docker compose -f infra/compose/docker-compose.yml up --build
```

API docs: `http://localhost:8000/docs`
