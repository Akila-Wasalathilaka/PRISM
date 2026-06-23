# Contributing to PRISM

Thank you for considering contributing to PRISM! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites

- **Node.js 22+** — [Download](https://nodejs.org)
- **Python 3.12+** — [Download](https://python.org)
- **Docker & Docker Compose** — [Download](https://docker.com)

### First-Time Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/<your-username>/prism.git
cd prism

# 2. Copy environment template
cp .env.example .env

# 3. Start PostgreSQL and Redis
docker compose up -d

# 4. Setup Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev,test]"
alembic upgrade head

# 5. Setup Frontend
cd ../frontend
npm install
```

### Running Locally

```bash
# Terminal 1 — Backend
cd backend && uvicorn prism.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend && npm run dev
```

## Code Standards

### Python (Backend)

- **Formatter:** Ruff
- **Linter:** Ruff
- **Type Checker:** MyPy (strict mode)
- **Tests:** Pytest with pytest-asyncio

```bash
cd backend
ruff check .          # Lint
ruff format .         # Format
mypy prism/           # Type check
pytest                # Test
```

### TypeScript (Frontend)

- **Linter:** ESLint
- **Type Checker:** tsc

```bash
cd frontend
npm run lint          # Lint
npm run build         # Type check + build
```

## Pull Request Guidelines

1. **Create an issue first** — Discuss the change before implementing
2. **Branch from `main`** — Use descriptive branch names: `feature/risk-scoring`, `fix/webhook-timeout`
3. **Keep PRs small** — Aim for <400 lines of changes
4. **Write tests** — Backend changes need pytest coverage, frontend needs component tests
5. **Update documentation** — If your change affects the API or architecture
6. **PRISM dogfoods itself** — Your PR will get a risk analysis from PRISM!

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add blast radius visualization
fix: handle webhook timeout for large PRs
docs: update risk engine architecture doc
test: add file classifier unit tests
chore: update FastAPI to 0.115.0
```

## Architecture Decision Records

Significant design decisions are documented as ADRs in `docs/architecture/ADR/`. If your contribution involves an architectural change, please add an ADR.

## Community

- **Issues:** [GitHub Issues](https://github.com/your-username/prism/issues)
- **Discussions:** [GitHub Discussions](https://github.com/your-username/prism/discussions)

## License

By contributing to PRISM, you agree that your contributions will be licensed under the [AGPL-3.0 License](LICENSE).
