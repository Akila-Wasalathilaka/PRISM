"""
PRISM Backend — Pull Request Risk & Intelligence System

FastAPI application entry point.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from prism.api.analyses import router as analyses_router
from prism.api.health import router as health_router
from prism.api.webhooks import router as webhooks_router
from prism.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifecycle manager."""
    # Startup
    import structlog

    logger = structlog.get_logger()
    logger.info("prism.startup", version=settings.APP_VERSION, environment=settings.ENVIRONMENT)
    yield
    # Shutdown
    logger.info("prism.shutdown")


app = FastAPI(
    title="PRISM API",
    description="Pull Request Risk & Intelligence System",
    version=settings.APP_VERSION,
    docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# CORS — restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(webhooks_router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(analyses_router, prefix="/api/analyses", tags=["analyses"])
