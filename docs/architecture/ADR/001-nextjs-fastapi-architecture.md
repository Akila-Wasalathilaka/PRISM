# ADR-001: Next.js + FastAPI Architecture

**Date:** 2026-06-23
**Status:** Accepted
**Decision Makers:** Architecture Team

## Context

PRISM needs a frontend for dashboards and a backend for webhook processing, risk analysis, and LLM orchestration. We evaluated three architecture options:

| Option | Stack | Verdict |
|:---|:---|:---|
| A | Next.js + Go | Rejected — Go's ML ecosystem is weak; two type systems to maintain |
| **B** | **Next.js + FastAPI** | **Accepted** |
| C | Next.js Monolith | Rejected — Node.js poorly suited for CPU-intensive analysis; low portfolio signal |

## Decision

We use **Next.js (App Router)** for the frontend and **FastAPI (Python 3.12)** for the backend.

## Rationale

1. **AI is the core of PRISM.** Python's ecosystem (LangChain, tiktoken, prompt engineering libraries) is unmatched for the risk engine and LLM orchestration layer.

2. **Performance is adequate.** FastAPI with async handles webhook throughput. The bottleneck is LLM API latency, not the web framework.

3. **Modular monolith.** Two deployable units (frontend + backend), not microservices. Right complexity for a solo engineer.

4. **Portfolio value.** Demonstrates full-stack competency across TypeScript AND Python — exactly what companies building AI products hire for.

5. **Go is premature optimization.** Go's concurrency advantages matter at scale PRISM won't reach in year one.

## Consequences

- **Positive:** Fastest AI/ML development velocity. Strong type safety via TypeScript + Pydantic. Two separate CI pipelines allow independent deployment.
- **Negative:** Two languages means context switching. Two build systems. Slightly higher operational complexity than a pure Next.js monolith.
- **Mitigation:** Shared API types via OpenAPI schema generation. Single Docker Compose for local development.

## Alternatives Considered

See implementation plan Phase 3 for the full evaluation matrix.
