<div align="center">

# 🔷 PRISM

### Pull Request Risk & Intelligence System

**Know before you merge.**

PRISM tells you the deployment risk of every pull request — before a single reviewer opens it.

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](LICENSE)
[![Built with FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Built with Next.js](https://img.shields.io/badge/Frontend-Next.js-000000?logo=next.js)](https://nextjs.org)

</div>

---

## What is PRISM?

PRISM is **not** another AI code review tool. It's a **deployment risk intelligence system** that identifies architecture impact, dependency dangers, migration risks, and historical incident patterns to surface the PRs that cause outages — before they're merged.

### What makes it different?

| Every other tool asks: | PRISM asks: |
|:---|:---|
| "Is this code correct?" | "Is this code **safe to deploy**?" |
| "Does this follow style guides?" | "Does this **cross critical boundaries**?" |
| "Are there vulnerabilities?" | "Will this **cause an incident**?" |

### Core Features

- 🎯 **Deployment Risk Scoring** — Every PR gets a risk score (0–100) based on what it touches
- 🏗️ **Architecture Intelligence** — Detects boundary violations and cross-module impact
- 💥 **Blast Radius Analysis** — Maps which services and teams are affected
- 📊 **Historical Correlation** — "The last time someone touched auth + migrations, it caused a P1"
- 🤖 **AI-Powered Analysis** — LLM enrichment for high-risk PRs (Gemini + Mistral)
- 📈 **Risk Analytics** — Trends, heatmaps, and team-level insights

## Tech Stack

| Layer | Technology |
|:---|:---|
| **Frontend** | Next.js 15 (App Router), TypeScript, React |
| **Backend** | FastAPI, Python 3.12, SQLAlchemy (async) |
| **Database** | PostgreSQL 16, Redis 7 |
| **AI** | Gemini 2.0 Flash / 2.5 Pro, Mistral Small / Large |
| **Infrastructure** | Docker, Cloudflare (Pages + Workers + R2), Terraform |
| **CI/CD** | GitHub Actions |

## Quick Start

### Prerequisites

- Node.js 22+
- Python 3.12+
- Docker & Docker Compose

### 1. Clone & Setup

```bash
git clone https://github.com/your-username/prism.git
cd prism
cp .env.example .env
```

### 2. Start Infrastructure

```bash
docker compose up -d
```

### 3. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev,test]"
alembic upgrade head
uvicorn prism.main:app --reload --port 8000
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 5. Open

- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/api/docs
- **Health Check:** http://localhost:8000/api/health

## Project Structure

```
prism/
├── frontend/          # Next.js app (TypeScript)
├── backend/           # FastAPI app (Python)
│   ├── prism/
│   │   ├── api/       # API routes
│   │   ├── core/      # Risk engine, architecture analyzer, LLM
│   │   ├── db/        # Database models, sessions, migrations
│   │   └── workers/   # Background processing
│   └── tests/
├── infrastructure/    # Terraform, Docker configs
├── docs/              # Architecture docs, ADRs
├── risk-patterns/     # Community risk detection rules
└── docker-compose.yml # Local dev dependencies
```

## Architecture

PRISM uses a **tiered analysis approach**:

1. **Deterministic Layer** (free, <100ms) — File classification, pattern matching, scoring
2. **LLM Enrichment** (paid, only for risky PRs) — Contextual analysis, explanations, suggestions

This means 70–80% of PRs are analyzed with zero LLM cost.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding standards, and PR guidelines.

## License

PRISM is licensed under [AGPL-3.0](LICENSE). Commercial licenses are available for organizations that need to embed PRISM without AGPL obligations.

---

<div align="center">
  <sub>Built with 🔷 by the PRISM community</sub>
</div>
