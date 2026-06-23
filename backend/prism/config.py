"""
PRISM Configuration — Environment-based settings with Pydantic.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── Application ──
    APP_NAME: str = "PRISM"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # ── Server ──
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── Database ──
    DATABASE_URL: str = "postgresql+asyncpg://prism:prism@localhost:5432/prism"

    # ── Redis ──
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── CORS ──
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # ── GitHub App ──
    GITHUB_APP_ID: str = ""
    GITHUB_APP_PRIVATE_KEY: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""

    # ── LLM ──
    GEMINI_API_KEY: str = ""
    MISTRAL_API_KEY: str = ""
    LLM_TIER2_MODEL: str = "gemini-2.0-flash"
    LLM_TIER3_MODEL: str = "gemini-2.5-pro"

    # ── Auth ──
    JWT_SECRET_KEY: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
