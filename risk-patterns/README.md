# PRISM Risk Patterns — Community-Contributed

This directory contains community-contributed risk detection patterns organized by language/framework.

## Structure

```
risk-patterns/
├── python/       # Python-specific risk patterns
├── javascript/   # JavaScript/TypeScript patterns
├── go/           # Go patterns
└── general/      # Language-agnostic patterns (CI/CD, Docker, Terraform)
```

## Contributing a Pattern

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on submitting risk patterns.

Each pattern should include:
- **Name** — Descriptive identifier
- **File patterns** — Glob patterns for files this applies to
- **Content patterns** — Regex patterns to detect the risk
- **Severity** — Risk severity score (1-40)
- **Explanation** — Why this pattern is risky
- **False positive guidance** — When this is a false alarm
