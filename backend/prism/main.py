"""
PRISM Backend — Pull Request Risk & Intelligence System

FastAPI application entry point.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from prism.api.analyses import router as analyses_router
from prism.api.health import router as health_router
from prism.api.webhooks import router as webhooks_router
from prism.config import settings
from prism.core.rate_limiter import limiter


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

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

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

# Mount frontend static files
# In production, the frontend out folder will be placed at ~/frontend/out,
# which is parallel to ~/backend.
# So from backend/prism/main.py, the path is ../../../frontend/out
# If running locally, it might be in ../frontend/out relative to the backend root.
# Let's try both paths (local dev vs production).
local_fe_path = Path(__file__).resolve().parent.parent.parent / "frontend" / "out"
prod_fe_path = Path.home() / "frontend" / "out"

if prod_fe_path.exists():
    app.mount("/", StaticFiles(directory=str(prod_fe_path), html=True), name="frontend")
elif local_fe_path.exists():
    app.mount("/", StaticFiles(directory=str(local_fe_path), html=True), name="frontend")

