# Self-Hosting Guide — SNT AI Assurance Platform

## Minimum Hardware Requirements

| Component | Minimum | Recommended (>50 concurrent evals) |
|-----------|---------|-------------------------------------|
| **CPU**   | 4 vCPUs | 8 vCPUs                             |
| **RAM**   | 8 GB    | 16 GB                               |
| **Disk**  | 50 GB SSD (Postgres + ClickHouse volumes) | 100 GB SSD |

## Required Environment Variables

These map to `backend/app/config.py`, which reads env vars with the `SNT_` prefix (only `SNT_`-prefixed names are honored).

| Variable | Purpose | Example |
|----------|---------|---------|
| `SNT_ENVIRONMENT` | `production` or `development`. Production runs a startup safety check (refuses dev secrets, `localhost` CORS, and `SNT_AUTH_PROVIDER=local`) | `production` |
| `SNT_POSTGRES_DSN` | PostgreSQL async connection string | `postgresql+asyncpg://user:pass@host:5432/snt_ai` |
| `SNT_CLICKHOUSE_HOST` | ClickHouse server hostname | `clickhouse` |
| `SNT_CLICKHOUSE_PORT` | ClickHouse HTTP port | `8123` |
| `SNT_CLICKHOUSE_PASSWORD` | ClickHouse password | — |
| `SNT_REDIS_DSN` | Redis connection string (rate-limiting, caching) | `redis://:password@redis:6379/0` |
| `SNT_ENCRYPTION_KEY` | JWT/HMAC signing secret (auth tokens, webhook signatures). No field-level encryption is implemented — see the encryption section below | 32+ random characters |
| `SNT_AUTH_PROVIDER` | `clerk` or `auth0` for production. `local` is a dev-only code path and is refused by the production safety check | `clerk` |
| `SNT_CORS_ORIGINS` | Comma-separated allowed frontend origins (must not contain `localhost` in production) | `https://app.example.com` |

## Encryption Coverage — What `SNT_ENCRYPTION_KEY` Actually Protects

### Currently Signed / Protected

| Field / Usage | Location | Mechanism |
|---------------|----------|-----------|
| **JWT token signing & validation** | `app/routers/auth.py`, `app/core/security.py` | HS256 symmetric signing via `PyJWT` |
| **Stripe webhook signature** | `app/routers/billing.py` | Signature verification uses `encryption_key` (custom HMAC, not Stripe's native scheme) |

### NOT Currently Encrypted (Known Gaps)

| Field | Location | Status |
|-------|----------|--------|
| **Agent API keys** | `TargetAgent.api_key_encrypted` (Postgres column) | The column is named `api_key_encrypted` but stores **plaintext** — no crypto library or encryption logic exists in the app. Real encryption is not yet implemented |
| **ClickHouse turn traces** | `turn_traces` table | Stored as plaintext; encryption-at-rest depends on ClickHouse volume-level encryption |
| **Organization settings** | `organizations.settings` (Text column) | Plaintext JSON; no field-level encryption |

> **Recommendation for regulated deployments:** Enable volume-level encryption (LUKS/dm-crypt) on Postgres and ClickHouse data directories. For field-level encryption of ClickHouse traces and agent API keys, implement an encryption wrapper in the `ClickHouseFlusher` service and in the agent persistence layer.

## Network Egress Requirements

The platform runs primarily self-contained within your VPC. **Required outbound egress:**

| Destination | Purpose | Required? |
|-------------|---------|-----------|
| Your LLM provider API (e.g. `api.openai.com`, `api.anthropic.com`, or private vLLM endpoint) | Evaluation judge & persona generation | **Yes** (only when using LLM-powered judge) |
| Clerk/Auth0 JWKS endpoint | JWT key rotation | **Only if using Clerk or Auth0 auth** |
| Stripe API | Billing webhook verification | **Only if billing is enabled** |

**No telemetry, analytics, or phone-home calls are made.** The platform is not fully air-gapped: it requires external egress to the destinations listed above when the corresponding feature is enabled.

## TLS Setup

- Place a reverse proxy (nginx, Caddy, or cloud LB) in front of the backend on port 8000.
- Terminate TLS at the proxy. The backend runs HTTP internally.
- For internal service-to-service communication (Postgres, ClickHouse, Redis), use Docker network isolation or mTLS if required by your security policy.

## Deployment

### Using the self-hosted compose file

```bash
docker compose -f infra/docker-compose.selfhosted.yml up -d --build
```

This variant:
- Bundles Postgres, ClickHouse, Redis, and the backend (no frontend container — run `cd frontend && npm run build && npm start` separately or add it to the compose file)
- Requires `SNT_AUTH_PROVIDER` set to `clerk` or `auth0` — there is **no supported local-auth mode for production**: the production safety check refuses `SNT_AUTH_PROVIDER=local`, and no `basic` provider exists in the app. For a no-cloud-auth trial deployment, run with `SNT_ENVIRONMENT=development` and `SNT_AUTH_PROVIDER=local` (dev-only code path, not for production)
- `SNT_ENVIRONMENT` defaults to `production`; override with `SNT_ENVIRONMENT=development` in your `.env` if you intend to use the local auth path

### Using the standard compose file (requires all infra)

```bash
docker compose -f infra/docker-compose.yml up -d --build
```

## Backup & Disaster Recovery

| Service | Backup Method | Script | Frequency |
|---------|--------------|--------|-----------|
| **Postgres** | `pg_dump` custom format (`-Fc`), gzip-compressed | `infra/scripts/backup_postgres.sh` | Daily (02:00 UTC) |
| **ClickHouse** | `TabSeparated` stream per table, gzip-compressed | `infra/scripts/backup_clickhouse.sh` | Daily (03:00 UTC) |
| **Redis** | RDB snapshots | Docker volume persistence | Continuous |

> **Validation status:** The restore procedures below have been validated against **synthetic data only** — they have not yet been exercised against real production volumes. Treat them as documented procedures, not production-proven runbooks.

### 1. PostgreSQL Disaster Recovery Restore

The backup script produces a gzipped custom-format dump named `snt_ai_<timestamp>.dump.gz`. To restore it (substitute the actual container name — `snt-postgres` for the standard compose, `snt-postgres-selfhosted` for the self-hosted variant):

```bash
# 1. Copy the compressed dump into the target container
docker cp /path/to/snt_ai_YYYYMMDD_HHMMSS.dump.gz snt-postgres:/tmp/backup.dump.gz

# 2. Decompress inside the container
docker exec -i snt-postgres sh -c 'gunzip -c /tmp/backup.dump.gz > /tmp/backup.dump'

# 3. Execute pg_restore against the snt_ai database
docker exec -i -e PGPASSWORD=$POSTGRES_PASSWORD snt-postgres \
  pg_restore -U $POSTGRES_USER -d snt_ai --no-owner /tmp/backup.dump

# 4. Verify record counts
docker exec -i snt-postgres psql -U $POSTGRES_USER -d snt_ai \
  -c "SELECT count(*) FROM organizations;"
```

### 2. ClickHouse Disaster Recovery Restore

The backup script produces one gzipped `TabSeparated` file per table, named `snt_ai_<timestamp>_<table>.tsv.gz`. This example restores `turn_traces` (substitute the actual container name — `snt-clickhouse` for the standard compose, `snt-clickhouse-selfhosted` for the self-hosted variant):

```bash
# 1. Copy TSV dump to target ClickHouse container
docker cp /path/to/snt_ai_turn_traces.tsv.gz snt-clickhouse:/tmp/turn_traces.tsv.gz

# 2. Recreate schema (if the target table does not exist) — must match the real
#    DDL from backend/app/models/clickhouse/traces.py / infra/init/clickhouse/01_init.sql
docker exec -i snt-clickhouse clickhouse-client -u default --password $CLICKHOUSE_PASSWORD --query "
CREATE TABLE IF NOT EXISTS snt_ai.turn_traces
(
    organization_id   UUID,
    session_id        String,
    run_id            UUID,
    turn_id           Int32,
    timestamp         DateTime64(3, 'UTC'),
    speaker           Enum8('user' = 1, 'agent' = 2),
    turn_text         String,
    token_count       Int32,
    latency_ms        Float64,
    model_name        String,
    chaos_injected    String,
    scores            String,
    metadata          String
)
ENGINE = ReplacingMergeTree()
PARTITION BY (organization_id, toYYYYMM(timestamp))
ORDER BY (organization_id, session_id, turn_id, timestamp)
SETTINGS index_granularity = 8192;"

# 3. Import the gzipped TSV stream (column order must match the SELECT * order
#    used by the backup script; tr -d '\r' handles Windows CRLF line endings)
zcat /path/to/snt_ai_turn_traces.tsv.gz | tr -d '\r' | docker exec -i snt-clickhouse \
  clickhouse-client -u default --password $CLICKHOUSE_PASSWORD \
  --query "INSERT INTO snt_ai.turn_traces (organization_id, session_id, run_id, turn_id, timestamp, speaker, turn_text, token_count, latency_ms, model_name, chaos_injected, scores, metadata) FORMAT TabSeparated"

# 4. Verify row count
docker exec -i snt-clickhouse clickhouse-client -u default --password $CLICKHOUSE_PASSWORD \
  --query "SELECT count(*) FROM snt_ai.turn_traces"
```

## Upgrade Procedure

1. Pull the latest image or rebuild: `docker compose -f infra/docker-compose.selfhosted.yml build`
2. Run database migrations (if any): `docker compose exec backend alembic upgrade head`
3. Rolling restart: `docker compose -f infra/docker-compose.selfhosted.yml up -d`
4. Verify health: `curl http://localhost:8000/health`

## Troubleshooting

- **Port conflict on 8123**: Another ClickHouse or service is using the port. Stop it or remap in the compose file.
- **`Insecure JWT secret configuration in production`**: You must set `SNT_ENCRYPTION_KEY` to a real secret when `SNT_ENVIRONMENT=production`.
- **`SNT_AUTH_PROVIDER=local uses a dev-only code path`**: `local` is refused in production; set `SNT_AUTH_PROVIDER=clerk`/`auth0`, or run with `SNT_ENVIRONMENT=development` for a trial deployment.
- **ClickHouse initialization failed (non-fatal)**: The backend continues without ClickHouse. Traces won't be stored until ClickHouse is reachable.