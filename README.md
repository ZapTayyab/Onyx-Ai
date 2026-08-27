# SNT AI Assurance Platform

**Enterprise-grade evaluation infrastructure for LLM safety, robustness, and regression testing.**

SNT AI is a distributed, multi-tenant AI Assurance and Evaluation SaaS platform that systematically stress-tests customer-facing AI systems through adversarial synthetic personas, programmatic chaos injection, and LLM-as-a-Judge grading. It replaces manual red-teaming with deterministic, replayable evaluation pipelines that integrate directly into your CI/CD workflows.

---

## Architecture

```mermaid
flowchart LR
    subgraph CL[Client Layer]
        B[Browser]
    end

    subgraph FE[Frontend]
        NX[Next.js 14<br/>App Router]
        PX[API Proxy<br/>rewrites &#8594; /v1/*]
        NX --> PX
    end

    subgraph BE[Backend — FastAPI]
        MW[Middeware<br/>CORS · Auth · Rate Limit · Error]
        RT[Routers<br/>6 routers · 37 endpoints]
        SV[Services Layer]
        MW --> RT --> SV
    end

    subgraph PE[Evaluation Pipeline]
        PG[Persona Generator] --> CI[Chaos Injector] --> LJ[LLM-as-a-Judge] --> ER[Evaluation Runner]
        ER --> RG[Report Generator]
        ER --> AD[Anomaly Detector] --> AL[Alerting]
    end

    subgraph DW[Data & Workflow]
        PSQL[(PostgreSQL 16<br/>App DB)]
        CLH[(ClickHouse<br/>Analytics)]
        RED[(Redis 7<br/>Cache · Queue)]
        TMP{{Temporal.io<br/>Workflow Engine}}
    end

    subgraph OBS[Observability]
        OT[OpenTelemetry] --> PR[Prometheus] & JR[Jaeger]
        PR --> GF[Grafana]
    end

    subgraph CI[CI/CD]
        GHA[GitHub Actions] --> DB[Docker Build<br/>ghcr.io]
    end

    B --> NX
    PX --> MW
    SV --> PG
    ER -.-> PSQL & CLH & RED & TMP
    BE -.-> OT
    DB -.-> NX & MW
```

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                                 │
│  ┌─────────┐                                                        │
│  │ Browser │                                                        │
│  └────┬────┘                                                        │
│       │ http://localhost:3000                                        │
├───────┼─────────────────────────────────────────────────────────────┤
│       │                    FRONTEND  (Next.js 14)                    │
│  ┌────┴────────────┐   ┌──────────────────┐                        │
│  │  App Router     │──>│  API Proxy        │                        │
│  │  (pages, dash)  │   │  /api/v1/* → :8000│                        │
│  └─────────────────┘   └────────┬─────────┘                        │
│                                 │ http://backend:8000/v1/*          │
├─────────────────────────────────┼───────────────────────────────────┤
│                                 │     BACKEND  (FastAPI)             │
│  ┌──────────────────────────────┴──────────────────────────────┐    │
│  │  Middleware Stack: CORS → TrustedHost → Error → RateLimit   │    │
│  │  → OrgContext                                               │    │
│  ├──────────────────────────────────────────────────────────────┤    │
│  │  Routers: auth · agents · suites · evaluations · orgs · bill│    │
│  ├──────────────────────────────────────────────────────────────┤    │
│  │  Services: persona_generator · chaos_injector · llm_judge   │    │
│  │  evaluation_runner · clickhouse_flusher · report_generator  │    │
│  │  anomaly_detector · alerting                                │    │
│  └──────────────────────────────────────────────────────────────┘    │
│         │              │              │              │               │
│  ┌──────┴──────┐ ┌─────┴──────┐ ┌────┴──────┐ ┌─────┴──────────┐   │
│  │ PostgreSQL  │ │  ClickHouse │ │   Redis   │ │   Temporal.io │   │
│  │   App DB    │ │Analytics DB │ │Cache/Queue│ │Workflow Engine│   │
│  └─────────────┘ └────────────┘ └───────────┘ └────────────────┘   │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                     OBSERVABILITY  STACK                            │
│  ┌───────────────┐    ┌──────────┐    ┌────────┐                  │
│  │ OpenTelemetry │───>│Prometheus│───>│ Grafana│                  │
│  │   Collector   │─┐  └──────────┘    └────────┘                  │
│  └───────────────┘ │  ┌──────────┐                                │
│                    └─>│  Jaeger  │                                │
│                       └──────────┘                                │
├─────────────────────────────────────────────────────────────────────┤
│                          CI/CD  (GitHub Actions)                    │
│  lint → backend-test → frontend-build → docker push → ghcr.io      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Current Progress

**Phase: MVP Complete** — All core components are built, tested, and deployable.

| Component | Status | Details |
|-----------|--------|---------|
| Backend API | ✅ | 37 endpoints, 8 services, full middleware stack |
| Frontend | ✅ | Dashboard, evaluations, traces, alerts, reports, settings, marketing pages |
| Evaluation Pipeline | ✅ | 8 personas, 3 chaos profiles, dual-mode judge, anomaly detection, alerting |
| Temporal Workflows | ✅ | Fault-tolerant evaluation workflow + background worker |
| CI/CD | ✅ | GitHub Actions: lint → test → build → Docker push to ghcr.io |
| Observability | ✅ | OTel + Prometheus + Grafana + Jaeger, 8 alert rules, 9-panel dashboard |
| Infrastructure | ✅ | 15-service docker-compose, production-ready configuration |
| Tests | ✅ | 131 backend tests, all passing |

**Key Milestones:**
- 131/131 backend tests passing across 14 test suites
- Full 15-service stack runs with a single `docker compose up`
- JUnit XML report generation for CI/CD gating
- 8 built-in adversarial personas + 3 programmatic chaos profiles
- Prometheus alerting (8 rules) + Grafana monitoring (9 panels)

**Next Focus Areas:**
- Production hardening (PgBouncer, ClickHouse replication, TLS)
- Multi-region deployment & DR topology
- Load testing at production scale

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind CSS, Shadcn/ui, Recharts, @xyflow/react |
| **Backend API** | FastAPI (Python 3.12+), async/await, Pydantic v2, OpenAPI/Swagger |
| **Workflow Engine** | Temporal.io (fault-tolerant, long-running evaluations) |
| **Cache & Queue** | Redis 7 (hiredis driver) |
| **Application DB** | PostgreSQL 16 (SQLAlchemy 2.0 async ORM, Alembic async migrations) |
| **Analytics DB** | ClickHouse (ReplacingMergeTree, columnar, partitioned by org+month) |
| **Auth** | Clerk / Auth0 (OIDC, JWKS verification, role-based access control) |
| **LLM Integration** | OpenAI, Anthropic, vLLM (local open-source judges), LiteLLM |
| **Observability** | OpenTelemetry (traces + metrics), Prometheus, Grafana |
| **CI/CD** | GitHub Actions (lint â†’ test â†’ build â†’ Docker push) |

---

## Modules

### Module A â€” Automated Persona & Scenario Generator
Replaces manual/random seed testing. An LLM programmatically synthesizes structured user personas (8 built-in profiles) across three categories:
- **Standard**: HelpSeeker, PowerUser, NewComer
- **Edge Case**: ConfusedUser, RapidTyper, NonEnglishSpeaker
- **Adversarial**: Jailbreaker, DataMiner

### Module B â€” Chaos & Stress Testing Engine
Structured Chaos Profiles with programmatic interceptors:
- **Network Latency / Timeout**: Injects artificial delays (P75/P99 configurable) and timeout exceptions
- **Context Bloat**: Floods token windows with repeated context to test truncation behavior
- **Guardrail Interruption**: Simulates mid-conversation content-moderation blocks

### Module C â€” LLM-as-a-Judge Evaluation Engine
Modular dual-mode grading pipeline:
- **Groundedness / Faithfulness**: Keyword overlap + semantic alignment
- **Instruction Compliance**: Refusal vs violation pattern detection
- **Adversarial Robustness**: Prompt injection, jailbreak, data leak, escalation detection
- **Dual Mode**: Rule-based (always available) + LLM structured output fallback

### Module D â€” Regression Dashboard & Delta Engine
Compare two AI system variants over the identical scenario set:
- Side-by-side score deltas with regression detection
- P50/P90/P99 latency comparison
- Statistical anomaly detection (z-score based)
- JUnit XML report generation for CI/CD gating

### Module E â€” Production & Enterprise
- **Rate Limiting**: Per-client sliding window (200 req/min), route-level decorators
- **Caching**: Redis-backed CacheService with pattern invalidation
- **Error Handling**: Typed exceptions (NotFoundError, ConflictError, ForbiddenError, ServiceUnavailableError)
- **Anomaly Detection**: Statistical regression detection, persona category thresholding, issue clustering
- **Alerting**: Webhook delivery service, automatic score regression and evaluation completion alerts
- **SSO**: SAML/OIDC configuration per organization
- **Billing**: Stripe webhook integration, plan management
- **Team Management**: Member invite/remove, role-based access

---

## Getting Started

### Quick Reference

```bash
# ─── Docker (full stack, builds images) ──────────────────────────
docker compose -f infra/docker-compose.yml up --build  # migrations run automatically on startup

# ─── Backend (local development) ─────────────────────────────────
cd backend
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
docker compose -f ../infra/docker-compose.yml up -d postgres clickhouse redis temporal
alembic upgrade head  # only needed outside Docker — the container runs this automatically
uvicorn app.main:app --reload --port 8000

#Frontend (local development) 
cd frontend
npm install
npm run dev
```

### Prerequisites
- Python 3.12+, Node.js 20+, Docker & Docker Compose
- PostgreSQL 16, ClickHouse, Redis (or use `docker compose up`)
- Temporal Server 1.25+ (included in docker-compose)

### Quick Start (Docker - Full Stack)

```bash
# Clone the repository
git clone <repo-url> && cd snt-ai

# Build and start all services (PostgreSQL, ClickHouse, Redis, Temporal, Backend, Frontend, OTel, Prometheus, Grafana)
docker compose -f infra/docker-compose.yml up --build -d    # migrations run automatically on container start

# Or run in foreground to see live logs:
docker compose -f infra/docker-compose.yml up --build

# Services:
# - Backend API:      http://localhost:8000
# - Swagger Docs:     http://localhost:8000/docs
# - ReDoc:            http://localhost:8000/redoc
# - Frontend:         http://localhost:3000
# - Temporal UI:      http://localhost:8233
# - Grafana:          http://localhost:3001 (admin/admin)
# - Prometheus:       http://localhost:9090
```

### Local Development (Backend)

```bash
# From project root
cd backend

# Create virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings (at minimum set SNT_CLERK_SECRET_KEY for auth, or leave defaults for dev)

# Start supporting services (PostgreSQL, ClickHouse, Redis, Temporal)
docker compose -f infra/docker-compose.yml up -d postgres clickhouse redis temporal

# Run database migrations (only needed outside Docker — the container does this automatically)
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload --port 8000
```

The API is available at `http://localhost:8000/docs` (Swagger UI).

#### Backend Docker (Standalone)

```bash
cd backend
docker build -t snt-backend .
docker run -p 8000:8000 --env-file .env snt-backend
```

### Local Development (Frontend)

```bash
cd frontend
npm install
npm run dev
```

The frontend is available at `http://localhost:3000`. When the backend is not running, pages show empty states with loading skeletons and error banners.

#### Frontend Docker (Standalone)

```bash
cd frontend
docker build -t snt-frontend .
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000/v1 \
  snt-frontend
```

---

## Project Structure

```
snt-ai/
â”œâ”€â”€ backend/
â”‚   â”œâ”€â”€ app/
â”‚   â”‚   â”œâ”€â”€ main.py              # FastAPI entry, lifespan, middleware stack
â”‚   â”‚   â”œâ”€â”€ config.py             # Pydantic-settings (env prefix SNT_)
â”‚   â”‚   â”œâ”€â”€ core/
â”‚   â”‚   â”‚   â”œâ”€â”€ database.py       # Async SQLAlchemy engine/session
â”‚   â”‚   â”‚   â”œâ”€â”€ clickhouse.py     # ClickHouse HTTP client manager
â”‚   â”‚   â”‚   â”œâ”€â”€ security.py       # Clerk/Auth0 JWT verification, RBAC decorators
â”‚   â”‚   â”‚   â”œâ”€â”€ cache.py          # Redis-backed CacheService
â”‚   â”‚   â”‚   â”œâ”€â”€ exceptions.py     # Typed HTTP exceptions + ErrorHandlingMiddleware
â”‚   â”‚   â”‚   â”œâ”€â”€ metrics.py        # OpenTelemetry counters/gauges/histograms
â”‚   â”‚   â”‚   â””â”€â”€ logging.py        # Structured JSON logging with request context
â”‚   â”‚   â”œâ”€â”€ models/
â”‚   â”‚   â”‚   â”œâ”€â”€ postgres/         # 5 ORM models (Organization, User, TargetAgent, Suite, RunMeta)
â”‚   â”‚   â”‚   â””â”€â”€ clickhouse/       # turn_traces ReplacingMergeTree DDL + queries
â”‚   â”‚   â”œâ”€â”€ schemas/              # Pydantic request/response models
â”‚   â”‚   â”‚   â”œâ”€â”€ evaluations.py    # Run, trace, metrics, regression, webhook schemas
â”‚   â”‚   â”‚   â”œâ”€â”€ organizations.py  # Org, member, billing, SSO schemas
â”‚   â”‚   â”‚   â”œâ”€â”€ agents.py
â”‚   â”‚   â”‚   â”œâ”€â”€ suites.py
â”‚   â”‚   â”‚   â””â”€â”€ auth.py
â”‚   â”‚   â”œâ”€â”€ routers/              # 6 routers, 37 endpoints
â”‚   â”‚   â”‚   â”œâ”€â”€ auth.py           # GET /auth/me, /auth/audit-log, POST /auth/audit
â”‚   â”‚   â”‚   â”œâ”€â”€ agents.py         # CRUD /agents (5 endpoints)
â”‚   â”‚   â”‚   â”œâ”€â”€ suites.py         # CRUD /suites (5 endpoints)
â”‚   â”‚   â”‚   â”œâ”€â”€ evaluations.py    # run, list, traces, metrics, regression, webhook (7 endpoints)
â”‚   â”‚   â”‚   â”œâ”€â”€ organizations.py  # org mgmt, members, invite, usage, SSO (10 endpoints)
â”‚   â”‚   â”‚   â””â”€â”€ billing.py        # Stripe webhook, portal (2 endpoints)
â”‚   â”‚   â”œâ”€â”€ services/             # Business logic
â”‚   â”‚   â”‚   â”œâ”€â”€ persona_generator.py    # 8 built-in personas, LLM synthesis, scripts
â”‚   â”‚   â”‚   â”œâ”€â”€ chaos_injector.py       # Latency, context bloat, guardrail interruption
â”‚   â”‚   â”‚   â”œâ”€â”€ llm_judge.py            # Rule-based + LLM dual-mode evaluation
â”‚   â”‚   â”‚   â”œâ”€â”€ evaluation_runner.py    # Orchestrates personaâ†’chaosâ†’judgeâ†’flush
â”‚   â”‚   â”‚   â”œâ”€â”€ clickhouse_flusher.py   # Batch insert + run metadata updates
â”‚   â”‚   â”‚   â”œâ”€â”€ report_generator.py     # JUnit XML + summary text reports
â”‚   â”‚   â”‚   â”œâ”€â”€ anomaly_detector.py     # Z-score regression, persona thresholds, issue clustering
â”‚   â”‚   â”‚   â””â”€â”€ alerting.py             # Webhook delivery, regression + completion alerts
â”‚   â”‚   â”œâ”€â”€ workflows/
â”‚   â”‚   â”‚   â””â”€â”€ evaluation_workflow.py  # Temporal workflow (conditional import)
â”‚   â”‚   â””â”€â”€ middleware/
â”‚   â”‚       â”œâ”€â”€ auth_middleware.py       # OrganizationContextMiddleware
â”‚   â”‚       â””â”€â”€ rate_limiter.py          # Sliding window per-client + route decorator
â”‚   â”œâ”€â”€ migrations/               # Alembic async migrations
â”‚   â”œâ”€â”€ tests/                    # 131 tests across 13 files
â”‚   â”œâ”€â”€ Dockerfile                # Multi-stage (builder â†’ runner)
â”‚   â”œâ”€â”€ pyproject.toml            # Ruff config, pytest config
â”‚   â”œâ”€â”€ .env.example
â”‚   â””â”€â”€ requirements.txt
â”œâ”€â”€ frontend/
â”‚   â”œâ”€â”€ src/
â”‚   â”‚   â”œâ”€â”€ app/
â”‚   â”‚   â”‚   â”œâ”€â”€ layout.tsx               # Root layout (Inter font)
â”‚   â”‚   â”‚   â”œâ”€â”€ page.tsx                 # Redirects to /dashboard
â”‚   â”‚   â”‚   â”œâ”€â”€ globals.css              # Tailwind + CSS variables
â”‚   â”‚   â”‚   â””â”€â”€ (dashboard)/
â”‚   â”‚   â”‚       â”œâ”€â”€ layout.tsx           # Sidebar + Topbar shell
â”‚   â”‚   â”‚       â”œâ”€â”€ dashboard/page.tsx   # MetricCards, ScoreChart, CategoryChart, RecentRuns, PersonaDistribution
â”‚   â”‚   â”‚       â”œâ”€â”€ evaluations/page.tsx # Tabbed evaluation list with API data
â”‚   â”‚   â”‚       â”œâ”€â”€ traces/page.tsx      # Session selector + turn-by-turn viewer
â”‚   â”‚   â”‚       â”œâ”€â”€ alerts/page.tsx      # Alert list with acknowledge + severity tabs
â”‚   â”‚   â”‚       â”œâ”€â”€ reports/page.tsx     # Report generator + evaluation-based report list (API-driven)
â”‚   â”‚   â”‚       â””â”€â”€ settings/
â”‚   â”‚   â”‚           â”œâ”€â”€ page.tsx         # Profile, API keys, notifications
â”‚   â”‚   â”‚           â”œâ”€â”€ team/page.tsx    # Member list + invite form (API-driven)
â”‚   â”‚   â”‚           â””â”€â”€ billing/page.tsx # Plan selector + payment method
â”‚   â”‚   â”œâ”€â”€ components/
â”‚   â”‚   â”‚   â”œâ”€â”€ ui/               # 10 Shadcn/ui primitives (button, card, badge, tabs, etc.)
â”‚   â”‚   â”‚   â”œâ”€â”€ layout/           # sidebar.tsx (animated, collapsible, nested settings), topbar.tsx
â”‚   â”‚   â”‚   â””â”€â”€ dashboard/        # metric-cards.tsx, recent-runs.tsx, persona-distribution.tsx (all API-driven, no mock data)
â”‚   â”‚   â”œâ”€â”€ lib/
â”‚   â”‚   â”‚   â”œâ”€â”€ api.ts            # Type-safe API client (evaluations, suites, agents, org, auth)
â”‚   â”‚   â”‚   â””â”€â”€ utils.ts          # cn(), formatScore(), formatDate(), getScoreColor()
â”‚   â”‚   â”œâ”€â”€ types/index.ts        # All TypeScript interfaces matching backend schemas
â”‚   â”‚   â””â”€â”€ hooks/use-api.ts      # useApi<T>() hook with loading, error, refetch states
â”‚   â”œâ”€â”€ Dockerfile                # Multi-stage (deps â†’ builder â†’ runner, Next.js standalone)
â”‚   â”œâ”€â”€ package.json
â”‚   â”œâ”€â”€ next.config.js            # Standalone output + API rewrites
â”‚   â”œâ”€â”€ tailwind.config.ts        # Tremor colors + Shadcn CSS variables
â”‚   â””â”€â”€ tsconfig.json
â”œâ”€â”€ infra/
â”‚   â”œâ”€â”€ docker-compose.yml        # 10 services (postgres, clickhouse, redis, temporal, backend, frontend, otel, prometheus, grafana)
â”‚   â”œâ”€â”€ otel-collector-config.yml
â”‚   â”œâ”€â”€ prometheus/
â”‚   â”‚   â”œâ”€â”€ prometheus.yml        # Scrape configs + alerting rules reference
â”‚   â”‚   â””â”€â”€ alerting-rules.yml    # 8 alerts (BackendDown, HighErrorRate, ScoreRegression, etc.)
â”‚   â”œâ”€â”€ grafana/
â”‚   â”‚   â”œâ”€â”€ datasources/          # Prometheus + ClickHouse datasources
â”‚   â”‚   â””â”€â”€ dashboards/
â”‚   â”‚       â”œâ”€â”€ dashboards.yml    # Dashboard provisioning config
â”‚   â”‚       â””â”€â”€ snt-ai-overview.json  # 9-panel monitoring dashboard
â”‚   â””â”€â”€ init/
â”‚       â”œâ”€â”€ postgres/01_init.sql  # uuid-ossp, pgcrypto extensions
â”‚       â””â”€â”€ clickhouse/01_init.sql # turn_traces table DDL
â”œâ”€â”€ .github/workflows/ci.yml      # 4 jobs: lint â†’ backend-test â†’ frontend-build â†’ docker-build
â”œâ”€â”€ .pre-commit-config.yaml       # Ruff, mypy, trailing whitespace, YAML/JSON lint
â”œâ”€â”€ .editorconfig                 # Consistent indentation
â”œâ”€â”€ .gitignore
â””â”€â”€ README.md
```

---

## API Reference

All routes are prefixed with `/v1`. Full OpenAPI documentation at `/docs`.

### Auth (`/v1/auth`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/auth/me` | Token | Current user profile |
| GET | `/auth/audit-log` | Member | List audit log entries |
| POST | `/auth/audit` | Member | Record audit event |

### Agents (`/v1/agents`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/agents` | Admin | Register a target agent |
| GET | `/agents` | Member | List agents (paginated) |
| GET | `/agents/{agent_id}` | Member | Get agent details |
| PATCH | `/agents/{agent_id}` | Admin | Update agent |
| DELETE | `/agents/{agent_id}` | Admin | Delete agent |

### Suites (`/v1/suites`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/suites` | Admin | Create evaluation suite |
| GET | `/suites` | Member | List suites (paginated) |
| GET | `/suites/{suite_id}` | Member | Get suite details |
| PATCH | `/suites/{suite_id}` | Admin | Update suite |
| DELETE | `/suites/{suite_id}` | Admin | Delete suite |

### Evaluations (`/v1/evaluations`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/evaluations/run` | Member | Trigger evaluation run |
| GET | `/evaluations/runs` | Member | List runs (paginated) |
| GET | `/evaluations/runs/{run_id}` | Member | Get run status |
| GET | `/evaluations/traces/{run_id}` | Member | Get turn traces (ClickHouse) |
| GET | `/evaluations/metrics/{run_id}` | Member | Get aggregate metrics |
| POST | `/evaluations/regression-delta` | Member | Compute regression deltas |
| POST | `/evaluations/webhook/run` | Member | CI/CD webhook trigger (returns JUnit XML) |

### Organizations (`/v1/organizations`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/organizations/me` | Member | Get organization details |
| PATCH | `/organizations/me` | Admin | Update organization |
| GET | `/organizations/me/members` | Member | List team members |
| POST | `/organizations/me/invite` | Admin | Invite user |
| DELETE | `/organizations/me/members/{user_id}` | Admin | Remove member |
| GET | `/organizations/me/usage` | Member | Usage statistics |
| GET | `/organizations/me/billing` | Admin | Get billing plan |
| PATCH | `/organizations/me/billing` | Admin | Update billing plan |
| GET | `/organizations/me/sso` | Admin | Get SSO configuration |
| PUT | `/organizations/me/sso` | Admin | Configure SSO (SAML/OIDC) |

### Billing (`/v1/billing`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/billing/stripe-webhook` | Webhook | Stripe event handler |
| POST | `/billing/stripe/portal` | Admin | Create Stripe portal session |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check (DB + ClickHouse) |

### CI/CD Webhook Example

```bash
curl -X POST http://localhost:8000/v1/evaluations/webhook/run \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "suite_id": "550e8400-e29b-41d4-a716-446655440000",
    "agent_id": "550e8400-e29b-41d4-a716-446655440001",
    "source": "github-actions",
    "branch": "main",
    "commit_sha": "abc123",
    "pr_number": 42
  }'
```

Returns:
```json
{
  "run_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "completed",
  "suite_name": "Production Regression",
  "aggregate_score": 0.87,
  "total_sessions": 8,
  "completed_sessions": 8,
  "summary": { ... },
  "report_junit": "<?xml version='1.0' encoding='UTF-8'?>..."
}
```

---

## Environment Variables

Key configuration (see `backend/.env.example` for full list).

### Backend (`SNT_` prefix)

| Variable | Default | Purpose |
|----------|---------|---------|
| `SNT_ENVIRONMENT` | `development` | Runtime environment |
| `SNT_DEBUG` | `true` | Debug mode |
| `SNT_LOG_LEVEL` | `INFO` | Logging level |
| `SNT_POSTGRES_DSN` | `postgresql+asyncpg://snt:snt@localhost:5432/snt_ai` | PostgreSQL connection |
| `SNT_CLICKHOUSE_HOST` | `localhost` | ClickHouse host |
| `SNT_CLICKHOUSE_PORT` | `8123` | ClickHouse HTTP port |
| `SNT_CLICKHOUSE_DATABASE` | `snt_ai` | ClickHouse database |
| `SNT_REDIS_DSN` | `redis://localhost:6379/0` | Redis connection |
| `SNT_TEMPORAL_HOST` | `localhost:7233` | Temporal server address |
| `SNT_TEMPORAL_NAMESPACE` | `snt-ai-default` | Temporal namespace |
| `SNT_AUTH_PROVIDER` | `clerk` | Auth provider (`clerk` or `auth0`) |
| `SNT_CLERK_SECRET_KEY` | â€” | Clerk API secret |
| `SNT_CLERK_PUBLISHABLE_KEY` | â€” | Clerk publishable key |
| `SNT_AUTH0_DOMAIN` | â€” | Auth0 tenant domain |
| `SNT_AUTH0_AUDIENCE` | â€” | Auth0 API audience |
| `SNT_ENCRYPTION_KEY` | â€” | Encryption key for sensitive fields |
| `SNT_OPENAI_API_KEY` | â€” | OpenAI key for LLM-as-a-Judge |
| `SNT_ANTHROPIC_API_KEY` | â€” | Anthropic key |
| `SNT_VLLM_ENDPOINT` | â€” | Local vLLM inference endpoint |
| `SNT_CORS_ORIGINS` | `http://localhost:3000,http://localhost:8501` | Allowed CORS origins |
| `SNT_OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4317` | OpenTelemetry collector |

### Frontend (`NEXT_PUBLIC_` prefix)

| Variable | Default | Purpose |
|----------|---------|---------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000/v1` | Backend API base URL |

---

## Running Tests

### Backend (131 tests)

```bash
cd backend
python -m pytest -v

# With coverage
python -m pytest --cov=app --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_anomaly_detector.py -v

# Run by keyword
python -m pytest -k "regression" -v
```

### Frontend

```bash
cd frontend
npm run build    # TypeScript + lint check (no tests configured yet)
```

### CI Pipeline

The `.github/workflows/ci.yml` runs 4 jobs on push/PR:
1. **Lint**: `ruff check backend/`, `mypy backend/app/`
2. **Backend Test**: pytest with PostgreSQL service container
3. **Frontend Build**: `npm ci && npm run build`
4. **Docker Build**: Build and push to `ghcr.io` (main branch only)

---

## Monitoring

### Prometheus Alerting Rules (8 alerts)
- **BackendDown**: Service unreachable for 1m
- **HighErrorRate**: >5% 5xx errors over 5m
- **SlowResponses**: P95 >5s over 5m
- **HighEvaluationFailureRate**: Any failures in 30m
- **ClickHouseDown**: Uptime == 0
- **ScoreRegression**: Aggregate score <0.6
- **TemporalWorkflowFailures**: Any failures in 15m
- **HighLatencyP99**: P99 >10s over 5m

### Grafana Dashboard (9 panels)
- HTTP request rate (by method + route)
- P50/P95/P99 latency timeseries
- Error rate (4xx vs 5xx)
- Evaluation aggregate score (gauge with thresholds)
- Run count (24h stat)
- Active Temporal workflows
- ClickHouse query performance
- Score distribution histogram
- Chaos injection event rate

---

## Deployment

### Production Checklist
1. Set `SNT_ENVIRONMENT=production` and `SNT_DEBUG=false`
2. Configure PostgreSQL with SSL, automated backups, and connection pooling (PgBouncer)
3. Set up ClickHouse replication for HA
4. Point Temporal to external PostgreSQL
5. Configure Clerk or Auth0 with production credentials
6. Set `SNT_CORS_ORIGINS` to your frontend domain
7. Enable OpenTelemetry export to production observability backend
8. Configure Prometheus retention policy and alertmanager
9. Use `docker compose -f infra/docker-compose.yml up -d` with production `.env`

### Horizontal Scaling
- **FastAPI**: Stateless; scale behind a load balancer (multiple replicas + shared PostgreSQL)
- **Temporal Workers**: Scale worker pools independently per task queue
- **ClickHouse**: Native sharding + replication for high-ingestion scenarios

---

## Test Coverage

| File | Tests | What it covers |
|------|-------|----------------|
| `test_config.py` | 7 | Default config, env parsing, enums, status transitions |
| `test_models.py` | 13 | ORM creation, relationships, cascade deletes |
| `test_security.py` | 9 | Clerk/Auth0 role mapping, audit logging |
| `test_llm_judge.py` | 16 | Turn evaluation, scores, injection patterns, grounding |
| `test_chaos_injector.py` | 12 | Profile config, latency, bloat, guardrail, mock agent |
| `test_persona_generator.py` | 10 | Builtin profiles, filtering, scripts, LLM fallback |
| `test_clickhouse_schema.py` | 9 | DDL columns, engine type, partitioning, query correctness |
| `test_report_generator.py` | 7 | JUnit XML, failure elements, summary, anomaly section |
| `test_anomaly_detector.py` | 11 | Regression, latency, persona thresholds, issue clusters |
| `test_alerting.py` | 9 | Webhook register/unregister, send alerts |
| `test_rate_limiter.py` | 6 | Sliding window, key isolation, stale cleanup |
| `test_cache.py` | 7 | Degraded mode, get/set/delete/invalidate |
| `test_exceptions.py` | 9 | Typed exceptions, HTTP inheritance, middleware |
| **Total** | **131** | **All passing (1 skipped: timing-sensitive)** |

---

## License

Proprietary. All rights reserved. SNT AI Confidential.

---

## Support

- Email: support@snt.ai
- Issues: [https://github.com/anomalyco/opencode/issues](https://github.com/anomalyco/opencode/issues)

## Cheatsheet for your agent
- Agent type: Custom (Ollama is OpenAI-compatible)  
- Endpoint URL: http://host.docker.internal:11434/v1/chat/completions  
- Model name: llama3.2
# Onyx
