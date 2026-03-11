# MVP Scope

Included:
- Async message/user ingestion API
- Admin JWT authentication
- Protected integration management API for adding bot/userbot connectors
- SQL-backed repositories (SQLite for local tests, PostgreSQL in compose)
- Feature vectors
- Embedding generation interface
- Deterministic risk scoring
- Analysis API for pairwise account similarity and risk
- Persistent risk score history per user
- Auto alert creation for high-risk detections

Deferred:
- Billing/pricing engine
- Multi-tenant organizations
- Graph clustering jobs
- Dashboard UI
- Alerts channels integration
- Background queue workers
