# SaaS-платформа поиска мультиаккаунтов в Telegram
## Полная спецификация и пошаговый план реализации для новой команды

> Документ предназначен для команды, которая стартует проект с нуля и должна реализовать систему без повторения ранее допущенных архитектурных и продуктовых ошибок.

---

## 0. Цели документа

Этот документ фиксирует:
1. **Целевую архитектуру** SaaS решения для поиска мультиаккаунтов.
2. **Нефункциональные требования** (безопасность, масштабирование, наблюдаемость).
3. **Пошаговую реализацию** от нулевого состояния до production-ready версии.
4. **Антипаттерны и ошибки**, которые нельзя повторять.
5. **Definition of Done** для каждого этапа.

---

## 1. Продуктовая цель и границы

### 1.1 Цель продукта
Построить SaaS-систему, которая:
- принимает Telegram-данные (users/messages/events),
- строит признаки и эмбеддинги,
- вычисляет риск того, что несколько аккаунтов принадлежат одному оператору/схеме,
- предоставляет API для расследований, алертов и отчетности,
- поддерживает **мультиарендность (multi-tenant)** на уровне данных и доступа.

### 1.2 Что входит в MVP (обязательно)
- Multi-tenant backend API (FastAPI).
- AuthN/AuthZ с JWT + tenant claims.
- Интеграции (bot/userbot connectors) с защищенным хранением секретов.
- Безопасный ingestion pipeline.
- Сервис similarity/risk scoring.
- История risk score + алерты.
- Аудит действий администратора.
- Базовые дашборд-эндпоинты (API-only).

### 1.3 Что отложено (после MVP)
- Billing/subscription engine.
- Self-service UI с кабинетом клиента.
- Онлайн graph-clustering для миллионов узлов.
- Автоматический retraining ML-моделей.

---

## 2. Ключевые принципы (обязательные)

1. **Tenant isolation by design** — данные каждого клиента изолированы физически логикой запросов и проверяются на каждом уровне.
2. **Security first** — никаких токенов/секретов в ответах API и логах.
3. **Contract-first API** — сначала схемы и тесты контрактов, затем реализация.
4. **Idempotent ingestion** — повторная доставка событий не ломает состояние.
5. **Traceable decisions** — каждый риск-скор можно объяснить (feature contributions).
6. **Observability** — метрики, structured logs, трассировка критичных маршрутов.

---

## 3. Роли команды и ответственность

### Оркестратор (Tech Lead / Engineering Manager)
- Поддерживает roadmap и очередность этапов.
- Контролирует архитектурные решения и DoD.
- Проводит weekly architecture review.

### Программисты (Backend/Data/ML)
- Реализуют модули по спецификации.
- Пишут unit/integration tests.
- Гарантируют backward compatibility контрактов.

### Doc Writer
- Поддерживает актуальные ADR, API docs, runbook.
- Фиксирует изменения контракта и миграций.

### QA/DevOps
- Поддерживает CI/CD quality gates.
- Настраивает staging/prod окружения, алертинг, SLO.

---

## 4. Высокоуровневая архитектура

### 4.1 Компоненты
- `backend/api` — REST API (FastAPI).
- `backend/services` — бизнес-логика (feature, analysis, risk, auth).
- `backend/storage` — репозитории, транзакции, filtering by tenant.
- `backend/db` — ORM-модели, миграции, engine/session.
- `userbot` — сборщик сообщений из Telegram.
- `ml/feature_extractor` — embeddings + fallback strategy.
- `graph` — хранение связей (позже, не блокирует MVP).
- `infra` — Docker Compose, позже Kubernetes манифесты.

### 4.2 Поток данных
1. Connector получает событие из Telegram.
2. Connector отправляет событие в ingestion endpoint с сервисным ключом.
3. API валидирует ключ, tenant, схему payload.
4. Сообщение сохраняется idempotent-методом.
5. Запускается feature/risk pipeline.
6. Результаты пишутся в risk history + создаются alerts.

---

## 5. Модель данных (обновленная, правильная)

## 5.1 Обязательные сущности
- `organizations` (tenant).
- `admin_users`.
- `integrations`.
- `users`.
- `messages`.
- `risk_scores`.
- `alerts`.
- `audit_logs`.

### 5.2 Ключевая инварианта
Во всех доменных таблицах, где есть клиентские данные, должно быть поле:
- `tenant_id` (FK -> organizations.id, indexed, not null).

### 5.3 Обязательные ограничения
- Unique `(tenant_id, telegram_id)` в `users`.
- Unique `(tenant_id, integration_key_hash)` в `integrations`.
- Unique `(tenant_id, source, external_message_id)` в `messages` для идемпотентности.
- Check constraints для нормированных скоров (`0..1` и `0..100`).

---

## 6. API-контракты и безопасность

### 6.1 Аутентификация
Два типа auth:
1. **Admin JWT**: для панели, расследований и управления интеграциями.
2. **Integration Token/API key**: только для ingestion.

JWT claims (минимум):
- `sub` (admin email/ID)
- `tenant_id`
- `role`
- `iat`, `exp`, `jti`

### 6.2 Авторизация
- Каждый endpoint явно определяет требуемую роль.
- Роуты ingestion запрещены для публичного доступа.
- Каждый repository query содержит фильтр по `tenant_id` из auth context.

### 6.3 Секреты
- `api_hash`, `bot_token`, integration secrets хранятся зашифрованно.
- В API ответах — только masked values (`****abcd`).
- Полные значения недоступны после первичной записи.

---

## 7. Частые ошибки прошлого и как не повторять

1. **Ошибка: отсутствие tenant_id в таблицах**  
   Последствие: утечка данных между клиентами.  
   Правильный подход: tenant-aware schema + repository guards + тесты изоляции.

2. **Ошибка: открытые ingestion endpoints**  
   Последствие: произвольная запись мусора в систему.  
   Правильный подход: сервисные ключи + rate limit + подпись запроса.

3. **Ошибка: несоответствие telegram_id и internal user_id**  
   Последствие: сломанные внешние ключи и неверная аналитика.  
   Правильный подход: в ingestion передаем `telegram_id`, внутри делаем resolve/upsert user.

4. **Ошибка: возврат секретов интеграции в ответах API**  
   Последствие: компрометация аккаунтов и поставщиков.  
   Правильный подход: secret never returned + шифрование at rest.

5. **Ошибка: слабая валидация payload**  
   Последствие: silent data corruption и ложные risk score.  
   Правильный подход: строгие Pydantic validators + negative tests.

---

## 8. Пошаговый план реализации (с нуля)

## Этап 1: Базовый каркас проекта

### Шаги
1. Создать монорепо структуру:
   - `backend/`, `userbot/`, `ml/`, `graph/`, `infra/`, `docs/`.
2. Подготовить `pyproject.toml`, линтеры (`ruff`, `black`, `mypy`), pre-commit.
3. Настроить CI pipeline:
   - lint
   - unit tests
   - integration tests
   - security checks (pip-audit, bandit)
4. Поднять локальную инфраструктуру (`postgres`, `redis`, `neo4j`) в compose.

### DoD
- `docker compose up` поднимает все сервисы.
- CI зеленый на пустом baseline-проекте.

---

## Этап 2: Мультиарендная модель данных и миграции

### Шаги
1. Ввести ORM-модель `Organization`.
2. Добавить `tenant_id` в нужные таблицы.
3. Создать миграции Alembic.
4. Добавить индексы по `tenant_id` + композитные уникальные ограничения.
5. Написать миграционные тесты и smoke test на rollback.

### DoD
- БД создается миграциями без ручных правок.
- Все tenant-критичные таблицы имеют `tenant_id NOT NULL`.

---

## Этап 3: AuthN/AuthZ и tenant context propagation

### Шаги
1. Реализовать регистрацию/логин администратора в рамках организации.
2. Генерировать JWT с `tenant_id`, `role`, `jti`.
3. Добавить dependency `get_current_context()` возвращающую `{admin_id, tenant_id, role}`.
4. Внедрить role checks в роуты.
5. Добавить token revoke/rotation policy (минимум blacklist по `jti` в Redis).

### DoD
- Невозможно получить доступ к данным другого tenant.
- Тесты на 401/403/tenant isolation проходят.

---

## Этап 4: Безопасный ingestion

### Шаги
1. Ввести интеграционные ключи (`integrations`):
   - создание,
   - ротация,
   - деактивация.
2. Реализовать middleware/dependency валидации ключа.
3. Ограничить ingestion endpoint только integration auth.
4. Добавить idempotency keys (`external_message_id`, source).
5. Внедрить rate limiting и basic abuse protection.

### DoD
- Без валидного integration key ingestion возвращает 401/403.
- Повторная отправка одного сообщения не дублирует запись.

---

## Этап 5: Нормализация user/message pipeline

### Шаги
1. Изменить контракт ingestion:
   - вход: `telegram_id`, `chat_id`, `message_id`, `timestamp`, `text`.
2. На backend сделать `upsert_user_by_telegram_id(tenant_id, telegram_id)`.
3. Сохранять `messages.user_id` как внутренний FK.
4. Добавить обработку частично пустых профилей пользователя.
5. Добавить дедупликацию и нормализацию timestamp/timezone.

### DoD
- Нет FK-ошибок при ingestion.
- История пользователя и сообщений консистентна.

---

## Этап 6: Feature engineering и risk scoring

### Шаги
1. Формализовать feature schema:
   - style,
   - activity,
   - lexical,
   - temporal.
2. Реализовать валидацию входных данных для similarity API.
3. Обновить `AnalysisService` с explainability output:
   - итоговый score,
   - вклады признаков,
   - confidence.
4. Добавить версионирование моделей/правил (`model_version`).
5. Сохранять каждое вычисление в risk history.

### DoD
- Score воспроизводим при одинаковом входе.
- Есть explainable output для расследований.

---

## Этап 7: Alerts и workflow расследований

### Шаги
1. Добавить политики алертов:
   - порог по score,
   - cooldown,
   - дедупликация.
2. Реализовать таблицу `alerts` со статусами (`new`, `ack`, `closed`).
3. Добавить endpoint подтверждения/закрытия алерта.
4. Вести аудит действий администратора (`audit_logs`).

### DoD
- Алёрты не создаются лавинообразно.
- Любое действие администратора имеет audit trail.

---

## Этап 8: Наблюдаемость и операционная готовность

### Шаги
1. Structured logs (JSON) с `tenant_id`, `request_id`, `route`, `latency_ms`.
2. Метрики Prometheus:
   - request count/latency/error rate,
   - ingestion throughput,
   - scoring latency,
   - alerts created.
3. Health/readiness endpoints.
4. Sentry/ошибки + алертинг в Slack/Telegram для SRE.
5. Runbook (инциденты, ротация ключей, деградация зависимостей).

### DoD
- У сервиса есть SLO и реальные алерты на нарушения.
- Инженер on-call может восстановить систему по runbook.

---

## Этап 9: Тестирование (обязательно перед продом)

### 9.1 Unit tests
- validators,
- risk formula,
- auth utilities,
- repository filters by tenant.

### 9.2 Integration tests
- auth flow,
- ingestion flow,
- risk and alerts flow,
- tenant isolation end-to-end.

### 9.3 Security tests
- access control bypass attempts,
- token tampering,
- secret exposure checks.

### 9.4 Performance tests
- ingestion burst tests,
- p95 latency для `/analysis/similarity` и `/risk/score`.

### DoD
- Все блокирующие тесты зеленые в CI.
- Покрытие критичных модулей не ниже целевого порога (например, 85%).

---

## 9. Рекомендованная последовательность внедрения по существующему репозиторию

1. **Сначала безопасность и мультиарендность**:
   - схемы БД,
   - auth context,
   - tenant filters.
2. Затем исправить ingestion контракты и ID mapping.
3. Затем закрыть утечки секретов.
4. Затем усилить валидацию и explainability scoring.
5. В конце — observability, SLO и hardening.

> Нельзя начинать с «новых фич», пока не закрыты пункты 1–3.

---

## 10. Технические стандарты кода

- Python 3.11+.
- Типизация обязательна (mypy strict на новые модули).
- Никаких «магических» констант в коде (только через config).
- Мелкие функции, один уровень абстракции на метод.
- Один модуль — одна ответственность.
- Любая бизнес-логика покрыта тестом.

---

## 11. Definition of Done для релиза MVP

Релиз считается готовым, если:
1. Реализована tenant isolation во всех пользовательских данных.
2. Ingestion endpoints недоступны без integration auth.
3. Секреты не утекают через API/логи.
4. Risk scoring объясним и валиден.
5. Есть audit trail критичных операций.
6. CI/CD и эксплуатационные метрики настроены.
7. Документация (API, runbook, ADR) актуальна.

---

## 12. Чек-лист для команды перед merge в main

- [ ] Миграции применяются и откатываются.
- [ ] Нет endpoint без проверки auth.
- [ ] Нет query без tenant filter для tenant-bound сущностей.
- [ ] Нет secret fields в response DTO.
- [ ] Все новые endpoints имеют негативные тесты.
- [ ] Обновлены docs и changelog.
- [ ] Проведен security review PR.

---

## 13. Организация работы команды (практический процесс)

1. Оркестратор формирует weekly backlog по этапам (из этого документа).
2. Каждый PR должен быть маленьким и атомарным.
3. На каждый архитектурный выбор — ADR в `docs/architecture/`.
4. Doc Writer обновляет спецификацию в день merge.
5. Каждую пятницу — демо + ретроспектива ошибок.

---

## 14. Заключение

Если команда последовательно выполнит этапы выше, система будет:
- безопасной для SaaS-модели,
- масштабируемой,
- проверяемой,
- готовой к развитию без повторения базовых архитектурных ошибок.

Главный приоритет: **изоляция данных, безопасный ingestion, защита секретов, объяснимый risk scoring**.
