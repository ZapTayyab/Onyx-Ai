# Onyx — Enterprise AI Assurance Platform

Onyx replaces manual red-teaming with a repeatable, auditable evaluation pipeline for production AI agents. Stress-test LLMs using synthetic personas, chaos injection, and LLM-as-a-Judge grading — all gated in CI/CD.

---

## Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Available Scripts](#available-scripts)
- [Docker Deployment](#docker-deployment)
- [Project Structure](#project-structure)
- [Routes](#routes)
- [User Workflow](#user-workflow)
- [API Endpoints](#api-endpoints)
- [Component Architecture](#component-architecture)
- [Testing](#testing)
- [Production Readiness](#production-readiness)

---

## Architecture

```
┌──────────────────────────────────────┐      ┌──────────────────────────┐
│  Next.js 14 Frontend (this repo)     │      │  External API Backend    │
│                                      │  ╱  │                          │
│  Landing pages (static)              │──────│  /v1/evaluations/*       │
│  Dashboard pages (client CSR)        │  ╲  │  /v1/suites/*             │
│  API client (lib/api.ts)             │      │  /v1/agents/*            │
│  Proxy rewrite /v1/* → API_URL       │      │  /v1/organizations/*     │
└──────────────────────────────────────┘      │  /v1/auth/*              │
                                              └──────────────────────────┘
```

- **Frontend:** Next.js 14 App Router with route groups for auth and dashboard layouts
- **Backend:** Not included — the frontend calls an external REST API via proxy rewrites
- **Auth:** Placeholder — login form exists but requires backend integration
- **Deployment:** Docker multi-stage build with `output: standalone`

---

## Prerequisites

- [Node.js](https://nodejs.org/) 20+ (LTS recommended)
- npm (ships with Node.js)
- A running API backend (or deploy alongside one)

---

## Quick Start

```bash
# 1. Clone the repository
git clone <repo-url>
cd frontend

# 2. Copy environment variables
cp .env.example .env.local

# 3. Install dependencies
npm install

# 4. Start the development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

The landing page is fully static and works without a backend. Dashboard pages require the API to serve real data (they render fallback/mock content when the API is unavailable).

---

## Environment Variables

| Variable | Default | Required | Description |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000/v1` | Yes | Backend API base URL used by the client and the Next.js proxy rewrite |

Create a `.env.local` file in the project root:

```bash
NEXT_PUBLIC_API_URL=https://api.yourapp.com/v1
```

---

## Available Scripts

| Script | Command | Description |
|---|---|---|
| `npm run dev` | `next dev` | Start development server with hot reload |
| `npm run build` | `next build` | Production build |
| `npm start` | `next start` | Start production server (after build) |
| `npm run lint` | `next lint` | Run ESLint across the codebase |
| `npm test` | `vitest run` | Run tests once |
| `npm run test:watch` | `vitest` | Run tests in watch mode |

---

## Docker Deployment

A multi-stage Dockerfile is included:

```bash
# Build the image (production mode)
docker build -t onyx .

# Run the container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://api.yourapp.com/v1 \
  onyx
```

The image uses:
- `node:20-alpine` base
- Next.js standalone output (minimal runtime)
- Non-root `nextjs` user
- Healthcheck on port 3000

---

## Project Structure

```
frontend/
├── public/
│   └── hero/
│       └── hero-loop.mp4          # Landing page hero background video
├── src/
│   ├── app/
│   │   ├── (auth)/login/          # Login page
│   │   ├── (dashboard)/           # Dashboard pages (requires auth)
│   │   │   ├── dashboard/         # Overview with metrics & charts
│   │   │   ├── evaluations/       # Evaluation run history
│   │   │   ├── traces/            # Multi-turn trace viewer
│   │   │   ├── alerts/            # Alert configuration & history
│   │   │   ├── reports/           # Report generation & export
│   │   │   ├── settings/          # Profile, API keys, notifications
│   │   │   │   ├── team/          # Team member management
│   │   │   │   └── billing/       # Subscription & billing
│   │   │   └── layout.tsx         # Dashboard shell (sidebar + topbar)
│   │   ├── globals.css            # Tailwind + CSS custom properties
│   │   ├── layout.tsx             # Root layout (Inter font, metadata)
│   │   └── page.tsx               # Landing page composition
│   ├── components/
│   │   ├── dashboard/             # Dashboard widgets (charts, metrics, lists)
│   │   ├── landing/               # 9 marketing page sections
│   │   ├── layout/                # Sidebar + Topbar navigation shell
│   │   └── ui/                    # Reusable primitives (shadcn-style, Radix-based)
│   ├── hooks/
│   │   └── use-api.ts             # Generic fetch hook with loading/error states
│   ├── lib/
│   │   ├── api.ts                 # Typed API client for all backend endpoints
│   │   ├── landing-content.ts     # All marketing copy & site data
│   │   └── utils.ts               # cn(), formatScore(), formatDate(), getScoreColor()
│   └── types/
│       └── index.ts               # TypeScript interfaces for all domain models
├── Dockerfile                     # Multi-stage production build
├── next.config.js                 # Standalone output + proxy rewrites
├── tailwind.config.ts             # Tailwind with dark mode (class), Radix theme vars
└── tsconfig.json                  # Strict TypeScript, bundler module resolution
```

---

## Routes

| Route | Page | Description |
|---|---|---|
| `/` | Landing page | Marketing site (9 sections: hero, problem, pipeline, capabilities, security, CTA, footer) |
| `/login` | Login | Sign-in form (placeholder — no real auth backend) |
| `/dashboard` | Dashboard | KPI metrics, score trends, recent runs, persona distribution |
| `/evaluations` | Evaluations | Historical evaluation runs with status badges |
| `/traces` | Traces | Multi-turn conversation trace viewer with per-turn verdicts |
| `/alerts` | Alerts | Alert rules and notification history |
| `/reports` | Reports | JUnit & compliance report generation |
| `/settings` | Settings | Profile, API keys, notification preferences |
| `/settings/team` | Team | Team member management (roles, invitations) |
| `/settings/billing` | Billing | Subscription plans and usage |

---

## User Workflow

```
Define Personas ──▶ Configure Suite ──▶ Run Evaluation ──▶ Review Results ──▶ Gate Deploys
```

### 1. Create Target Agents

Register your AI agent endpoints so the evaluation runner can interact with them.

### 2. Define Personas

Synthesize 8+ user archetypes across three categories:
- **Standard:** HelpSeeker, FactualInquirer, MultiTurnExplorer
- **Edge-case:** RapidTyper, ContextOverloader, NonEnglishSpeaker
- **Adversarial:** Jailbreaker, PromptInjector

### 3. Build Evaluation Suites

Configure a suite by selecting personas, enabling chaos injection profiles (latency, context bloat, guardrail interruptions), and setting judge scoring criteria.

### 4. Run Evaluations

Trigger runs via:
- **Manual:** Use the Evaluations page to start a run
- **CI/CD:** POST to the webhook endpoint from GitHub Actions, GitLab CI, or Jenkins
- **Scheduled:** Recurring cron-based evaluation runs

### 5. Review Results

Each run produces:
- **Aggregate score** (0–100%) per persona and overall
- **Per-turn verdicts** with pass/fail and reasoning
- **Conversation traces** showing every LLM interaction
- **Regression deltas** comparing current run against a baseline
- **Latency & token metrics** (p50, p90, p99)

### 6. Set Alerts

Create alert rules that trigger on:
- Score drops below a threshold
- Latency regressions
- Behavioral drift between deployments

### 7. Export Audit Reports

Generate:
- **JUnit XML** for CI/CD pipeline integration
- **Signed evidence snapshots** with hash-chain verification
- **Compliance packages** for SOC 2, ISO 27001, and internal audits

---

## API Endpoints

The frontend API client (`src/lib/api.ts`) consumes the following endpoints. All routes are prefixed with the `NEXT_PUBLIC_API_URL` value and proxied through Next.js rewrites.

| Group | Endpoints | Description |
|---|---|---|
| **Evaluations** | `list`, `get`, `run`, `webhookRun`, `getTraces`, `getMetrics`, `compare` | Run and review evaluation results |
| **Suites** | `list`, `get`, `create` | Manage evaluation configurations |
| **Agents** | `list`, `get`, `create` | Register target AI agents |
| **Organization** | `get`, `update`, `members`, `usage`, `billing` | Org profile, team, and billing |
| **Auth** | `me` | Get current authenticated user |

---

## Component Architecture

### UI Primitives (`components/ui/`)
Reusable, accessible components built on Radix UI primitives with Tailwind styling:
`Avatar`, `Badge`, `Button`, `Card`, `Input`, `Progress`, `Separator`, `Skeleton`, `Tabs`, `Tooltip`

### Landing Sections (`components/landing/`)
Nine server components (except `Header` and `Reveal` which are client components for scroll behavior):
`Header`, `Hero` (fullscreen video), `LogoStrip`, `ProblemSection`, `HowItWorks` (6-stage pipeline), `Capabilities` (3×2 grid), `SecuritySection`, `CTASection`, `Footer`

### Dashboard Widgets (`components/dashboard/`)
Data visualization components using Recharts and mock fallback data:
`MetricCards`, `ScoreChart`, `CategoryChart`, `RecentRuns`, `PersonaDistribution`

### Layout Shell (`components/layout/`)
Collapsible `Sidebar` (16px/64px) with animated menu items and route highlighting; `Topbar` with search, notifications, and user avatar.

---

## Testing

Vitest is configured but no project tests have been written yet.

```bash
# Run tests
npm test

# Run tests in watch mode
npm run test:watch
```

Test files should be placed alongside their source files with `.test.ts` or `.spec.ts` extensions. The test runner looks in the `src/` directory by default.

---

## Production Readiness

### Ready Now
- Landing/marketing page — fully static, deployable standalone
- Dashboard UI — all pages built with navigation shell
- API client — fully typed for all backend endpoints
- Dockerfile — production-ready multi-stage build
- Build pipeline — `npm run build` passes with zero errors

### Required Before Production
| Area | Details | Priority |
|---|---|---|
| **Authentication** | Login is a placeholder. Integrate Auth0, Clerk, NextAuth, or a custom provider. Add middleware for route protection. | Critical |
| **Backend API** | The frontend requires a running API at `NEXT_PUBLIC_API_URL`. Deploy or build the backend service. | Critical |
| **Environment config** | Create `.env` files for dev, staging, and production environments with proper secrets management. | High |
| **Tests** | Write unit and integration tests for components, hooks, and API client. | High |
| **CI/CD pipeline** | Add GitHub Actions (or equivalent) for lint, test, build, and deploy. | Medium |
| **Documentation** | This README covers setup. Add architecture decision records (ADRs) for significant choices. | Low |
| **Error boundaries** | Add React error boundaries for graceful failure UX. | Low |

---

## License

Proprietary — Onyx. All rights reserved.
